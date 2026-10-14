"""Independent synthetic risk-budget lab; not the original internship implementation."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

def matrix(value, width=None):
    a=np.asarray(value,dtype=float)
    if a.ndim!=2 or not np.isfinite(a).all() or (width is not None and a.shape[1]!=width):
        raise ValueError('Expected finite two-dimensional numeric matrix')
    return a

def covariance(returns, shrinkage=0.25):
    r=matrix(returns)
    if len(r)<3 or r.shape[1]<2 or not 0<=shrinkage<=1:
        raise ValueError('Need >=3 observations, >=2 assets and shrinkage in [0,1]')
    cov=np.cov(r,rowvar=False,ddof=1)
    # Monthly covariance. Diagonal shrinkage is explicit, not a named estimator claim.
    return (1-shrinkage)*cov+shrinkage*np.diag(np.diag(cov))+np.eye(r.shape[1])*1e-9

def portfolio(alpha, cov, benchmark, annual_te=0.03, box_cap=0.1):
    a=np.asarray(alpha,dtype=float);b=np.asarray(benchmark,dtype=float);c=matrix(cov,len(a))
    if a.ndim!=1 or b.shape!=a.shape or c.shape!=(len(a),len(a)):
        raise ValueError('Alpha, benchmark and covariance shapes differ')
    if not np.isfinite(a).all() or not np.isfinite(b).all() or (b<0).any() or not np.isclose(b.sum(),1):
        raise ValueError('Benchmark must be finite, long-only and sum to one')
    if not np.allclose(c,c.T) or np.linalg.eigvalsh(c).min()<=0:
        raise ValueError('Covariance must be symmetric positive definite')
    if not np.isfinite(annual_te) or not np.isfinite(box_cap) or annual_te<0 or box_cap<0:
        raise ValueError('Risk limits must be finite and nonnegative')
    # Zero-net active solution with covariance risk penalty and full-investment constraint.
    one=np.ones(len(a)); inv_a=np.linalg.solve(c,a);inv_one=np.linalg.solve(c,one)
    d=inv_a-inv_one*(one@inv_a)/(one@inv_one)
    if np.linalg.norm(d)<1e-10 or annual_te==0 or box_cap==0:return b.copy()
    te=float(np.sqrt(d@c@d*12))
    scale=annual_te/te if te>0 else 0
    if np.max(np.abs(d))>0: scale=min(scale,box_cap/np.max(np.abs(d)))
    for i in range(len(d)):
        if d[i]<0:scale=min(scale,b[i]/(-d[i]))
    w=b+max(0,scale)*d
    if not np.isclose(w.sum(),1) or (w<-1e-10).any():raise ValueError('Portfolio constraint failed')
    return w

def backtest(returns, targets, benchmark, lag=2, transaction_cost=0.001):
    r=matrix(returns);w=matrix(targets,r.shape[1]);b=np.asarray(benchmark,dtype=float)
    if w.shape!=r.shape or not isinstance(lag,int) or lag<1 or lag>=len(r):raise ValueError('Invalid lag or target shape')
    if b.shape!=(r.shape[1],) or (b<0).any() or not np.isfinite(b).all() or not np.isclose(b.sum(),1):raise ValueError('Invalid benchmark')
    if not np.allclose(w.sum(axis=1),1) or (w<0).any() or (r<=-1).any() or not np.isfinite(transaction_cost) or transaction_cost<0:raise ValueError('Invalid weights, returns or costs')
    prior=None;prior_b=None;records=[]
    for t in range(lag,len(r)):
        target=w[t-lag]
        trade=float(np.abs(target-(np.zeros_like(b) if prior is None else prior)).sum())
        trade_b=float(np.abs(b-(np.zeros_like(b) if prior_b is None else prior_b)).sum())
        gross=float(target@r[t]);gross_b=float(b@r[t])
        net=gross-transaction_cost*trade; net_b=gross_b-transaction_cost*trade_b
        records.append({'return_month':t,'signal_month':t-lag,'gross':gross,'net':net,
                        'benchmark_net':net_b,'active_net':net-net_b,'traded_notional':trade})
        prior=target*(1+r[t])/(1+gross)
        prior_b=b*(1+r[t])/(1+gross_b)
    return records

def demo():
    data=json.loads((Path(__file__).parent/'samples/synthetic.json').read_text())
    r=matrix(data['monthly_returns']);b=np.array(data['benchmark']);lookback=6
    targets=np.tile(b,(len(r),1)); estimates=[]
    for t in range(lookback,len(r)):
        # At month-end t only data through t are visible. Targets earn first return at t+2.
        c=covariance(r[t-lookback+1:t+1]);a=r[t-lookback+1:t+1].mean(axis=0)
        targets[t]=portfolio(a,c,b)
        d=targets[t]-b; estimates.append(float(np.sqrt(d@c@d*12)))
    rows=backtest(r,targets,b)
    return {'data_kind':'synthetic; not an investment result','months':len(r),'assets':r.shape[1],
            'signal_to_first_return_months':2,'max_estimated_annual_tracking_error':max(estimates),
            'latest_target':targets[-1].tolist(),'ledger':rows,
            'limits':['Short synthetic panel; no claimed alpha or forecast.',
                      'Covariance uses explicit diagonal shrinkage, not an institutional factor model.',
                      'Transaction cost is a constant illustrative notional rate.',
                      'No real prices, corporate actions, delisting ledger or broker integration.']}

if __name__=='__main__':print(json.dumps(demo(),indent=2))

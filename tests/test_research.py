import unittest
import numpy as np
from research import covariance,portfolio,backtest

class RiskTests(unittest.TestCase):
    def setUp(self):
        self.b=np.array([.4,.35,.25]);self.c=np.diag([.002,.001,.003])
    def test_zero_alpha_equals_benchmark(self):
        np.testing.assert_allclose(portfolio([0,0,0],self.c,self.b),self.b)
    def test_long_only_box_and_risk(self):
        w=portfolio([.5,-.7,.2],self.c,self.b,annual_te=.025,box_cap=.07);d=w-self.b
        self.assertAlmostEqual(w.sum(),1);self.assertGreaterEqual(w.min(),0)
        self.assertLessEqual(np.abs(d).max(),.07+1e-10)
        self.assertLessEqual(np.sqrt(d@self.c@d*12),.025+1e-10)
    def test_two_month_alignment(self):
        r=np.array([[0,0],[0,0],[.1,0],[0,.1]]);w=np.array([[1,0],[0,1],[.5,.5],[.5,.5]])
        rows=backtest(r,w,[.5,.5],transaction_cost=0)
        self.assertEqual(rows[0]['signal_month'],0);self.assertEqual(rows[0]['gross'],.1)
        self.assertEqual(rows[1]['gross'],.1)
    def test_benchmark_reproduction_net_cost(self):
        r=np.array([[.01,.02],[.03,-.01],[.02,.05],[-.01,.01]])
        rows=backtest(r,np.tile([.5,.5],(4,1)),[.5,.5])
        self.assertTrue(all(abs(x['active_net'])<1e-12 for x in rows))
        self.assertEqual(rows[0]['traded_notional'],1)
    def test_missing_data_rejected(self):
        with self.assertRaises(ValueError):covariance([[0,0],[.1,float('nan')],[0,.1]])
    def test_non_positive_covariance_rejected(self):
        with self.assertRaises(ValueError):portfolio([1,2,3],np.zeros((3,3)),self.b)
    def test_nonfinite_alpha_rejected(self):
        with self.assertRaises(ValueError):portfolio([float('nan'),0,0],self.c,self.b)
    def test_negative_cost_rejected(self):
        with self.assertRaises(ValueError):backtest([[0,0]]*4,[[.5,.5]]*4,[.5,.5],transaction_cost=-1)
    def test_covariance_positive_definite(self):
        c=covariance([[.01,0],[0,.02],[-.01,.01],[.02,-.01]])
        self.assertGreater(np.linalg.eigvalsh(c).min(),0)

if __name__=='__main__':unittest.main()

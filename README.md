# 月频风险预算研究｜合成面板实验

独立实现的小型风险预算实验：对基准做零净额倾斜，约束跟踪误差、主动权重与做多范围，再对齐收益和成本。

> 公开方法演示 / Public methodology demo。合成数据不代表原项目成果，具体实现由 AI 编程工具辅助完成。

## 功能

- 月频协方差显式对角收缩，检查对称正定。
- 协方差惩罚下的零净額主动权重；共同缩放满足风险与箱型上限。
- 信号月到首次收益间隔两个月，示例估计只使用该时点可见数据。
- 成本按漂移后的权重变动计，包括首次建仓；策略和基准使用相同成本口径。

## 本地运行

Python 3.11+。

```sh
python -m pip install -r requirements.txt
python research.py
python -m unittest discover -s tests -v
```

入口：`research.py`。不需要 API Key、数据库、网络服务或付费模型。

## 流程

```mermaid
flowchart LR
A[历史可见合成收益] --> B[月频协方差]
  B --> C[基准相对权重]
  C --> D[风险/做多/箱型约束]
  D --> E[t+2 收益与成本台账]
```

## 验证

本地验证记录见 [VERIFICATION.md](VERIFICATION.md)。GitHub Actions 在 push 与 PR 时运行相同的离线测试；本地通过不代表远端 CI 已通过。

## 数据与局限

仅三项合成资产、18 个月，不构成收益证据。这里不是原实习的五代完整框架，不宣称实现机构风格风险模型、独立 alpha、预测或实盘。没有真实证券、财报 PIT、公司行为或退市台账；成本率为常数示意。

不包含 CSMAR 数据、原研究报告、公司代码、真实持仓或内部结果表。

## 许可与贡献

独立公开实现代码：MIT。合成样例随仓库发布，不向使用者授予任何第三方商业数据权利。没有捆绑原公司或团队源码。依赖与公开接口归因见 [NOTICE](NOTICE)。

[作品集](https://github.com/Willow-Tokoton-Hitorineko/research-portfolio) · [个人主页](https://github.com/Willow-Tokoton-Hitorineko)

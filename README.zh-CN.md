# TRC-LCS v0.1.0 中文说明

TRC-LCS（Task-Relation Conditioned Loop Closure Scheduling）是一个面向任务驱动 / 具身 SLAM 的模块化回环候选调度工具。它不替代完整 SLAM 系统，而是接收关键帧、可选轨迹、可选语义观测和自然语言任务，在有限的几何验证预算下，对历史回环候选进行任务条件化排序与调度。

## v0.1.0 已包含

- 可安装 Python 包和 `trc-lcs` 命令行工具；
- 视觉候选、任务候选及融合模式；
- 任务相关语义记忆和连续关系表示 CSR；
- 预算约束的 immediate / deferred / suppressed 调度；
- ORB + RANSAC 几何验证；
- `full` / `visual` / `task` 三种消融运行模式；
- 可复现 synthetic demo 和 smoke benchmark；
- KITTI 位姿格式转换工具；
- pytest、GitHub Actions CI、Issue/PR 模板、路线图和贡献指南。

## 一分钟运行

```bash
pip install -e .
python tools/make_demo_dataset.py --out data/demo --num-frames 80
trc-lcs \
  --task "找到客厅里红色椅子旁边的包" \
  --image-dir data/demo/images \
  --traj data/demo/trajectory_tum.txt \
  --semantics data/demo/semantics.jsonl \
  --camera 520 520 320 240 \
  --out outputs/demo
```

运行结果会写入 `candidate_scores.csv`、`loop_constraints.jsonl`、`task_memory.json` 和 `summary.json`。

## 重要说明

v0.1.0 是研究型 alpha 版本。内置 demo 的作用是验证整个软件链能否复现运行，不应把 synthetic demo 的结果当成真实数据集精度。真实实验建议在 KITTI、TUM RGB-D 或你自己的 SLAM 关键帧输出上运行，并明确记录数据序列、关键帧规则、轨迹来源、语义来源和完整参数。

更完整的英文说明、架构、数据格式和 benchmark 规范见主 README 与 `docs/`。

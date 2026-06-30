# Phase 20: Installation and Configuration Docs

Source: [dev-notes/architecture/phase-20-installation-docs.md](../../dev-notes/architecture/phase-20-installation-docs.md)

这一 phase 主要是文档和使用路径整理，让用户知道如何安装、配置和运行 Tau。

## 要抓住的主线

到 Phase 20，Tau 已经有 CLI、TUI、provider config、session、resources。此时需要把这些能力变成用户能跟着走的 docs。

这类 phase 的重点不是新核心代码，而是把已有工作流讲清楚。

## 源码阅读路线

主要读文档：

- [website/src/content/docs/](../../website/src/content/docs/)
- [README.md](../../README.md)
- [dev-notes/architecture/phase-20-installation-docs.md](../../dev-notes/architecture/phase-20-installation-docs.md)

如果要对照命令行为，再读 [src/tau_coding/cli.py](../../src/tau_coding/cli.py)。

## 关键理解

用户文档和 dev-notes 不同。dev-notes 解释系统如何建成，用户文档解释用户如何使用。

## 测试入口

文档 phase 通常没有大量独立测试。可跑 CLI smoke:

```bash
uv run pytest tests/test_cli.py::test_version_command \
              tests/test_cli.py::test_providers_command_lists_default_provider -q
```

## 自检问题

- dev-notes 和 published docs 的读者有什么不同?
- 安装文档应该覆盖哪些最小路径?
- 配置 provider 的用户体验为什么重要?
- 文档 phase 为什么仍然属于 architecture 记录?

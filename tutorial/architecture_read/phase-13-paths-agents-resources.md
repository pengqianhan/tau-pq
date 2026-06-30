# Phase 13: Tau Home, Paths, and `.agents` Resources

Source: [dev-notes/architecture/phase-13-paths-agents-resources.md](../../dev-notes/architecture/phase-13-paths-agents-resources.md)

这一 phase 明确 Tau 的用户目录、项目目录和 `.agents` 资源发现。

## 要抓住的主线

Tau 需要同时支持：

- 用户级资源。
- 项目级资源。
- session 文件。
- `.agents` 目录中的 skills 和 prompts。

这些路径规则必须集中管理，否则 CLI、TUI、session、resource discovery 会各自发明路径。

## 源码阅读路线

读：

- [src/tau_coding/paths.py](../../src/tau_coding/paths.py)
- [src/tau_coding/resources.py](../../src/tau_coding/resources.py)

再看 `CodingSession` 如何接收 `TauResourcePaths`。

## 关键理解

路径属于 application layer。`tau_agent` 不应该知道 `~/.tau`、项目 `.agents`、session 文件名规则。

资源 precedence 很重要：项目资源通常应该覆盖用户级资源，这样项目可以定义自己的局部行为。

## 测试入口

```bash
uv run pytest tests/test_paths.py tests/test_resources.py -q
```

## 自检问题

- Tau home 和 project resources 分别解决什么问题?
- 为什么路径规则要集中在 `tau_coding.paths`?
- `.agents` 资源和 built-in resources 的优先级如何理解?
- Session path 为什么不应该由 TUI 自己拼?

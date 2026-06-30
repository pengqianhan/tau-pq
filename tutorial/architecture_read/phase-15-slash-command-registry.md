# Phase 15: Slash Command Registry

Source: [dev-notes/architecture/phase-15-slash-command-registry.md](../../dev-notes/architecture/phase-15-slash-command-registry.md)

这一 phase 把 slash commands 从临时判断变成注册表。

## 要抓住的主线

Slash command 是 coding app 的控制命令，不是模型 prompt。

Command registry 负责：

- 注册内置命令。
- 解析用户输入。
- 返回结构化 `CommandResult`。
- 支持别名和帮助文本。
- 避免每个前端重复实现命令逻辑。

## 源码阅读路线

读 [src/tau_coding/commands.py](../../src/tau_coding/commands.py)。

重点看：

- `CommandResult`
- `CommandDefinition`
- `CommandRegistry`
- `create_default_command_registry`

再看 `CodingSession.handle_command` 和 TUI/CLI 如何消费 result。

## 关键理解

命令处理应该返回意图，而不是直接操作 UI。例如 `/resume` 可以返回 `resume_picker_requested=True`，由 TUI 决定弹 picker，CLI 可以用另一种方式处理。

## 测试入口

```bash
uv run pytest tests/test_commands.py -q
```

## 自检问题

- slash command 为什么属于 `tau_coding`?
- `CommandResult` 为什么要结构化?
- `/skill:` 和普通 slash command 的区别是什么?
- 为什么 registry 要拒绝重复命令和 alias?

# Phase 12: Textual TUI

Source: [dev-notes/architecture/phase-12-textual-tui.md](../../dev-notes/architecture/phase-12-textual-tui.md)

这一 phase 引入 Textual 交互式 TUI，但保持在 adapter 边界之后。

## 要抓住的主线

TUI 不直接改 agent loop。它做两层事：

1. Adapter 把 `AgentEvent` 转成 UI state。
2. Textual app 显示 state、接收用户输入、调用 `CodingSession`。

这样 Textual 依赖不会污染 `tau_agent`。

## 源码阅读路线

先读：

- [src/tau_coding/tui/adapter.py](../../src/tau_coding/tui/adapter.py)
- [src/tau_coding/tui/state.py](../../src/tau_coding/tui/state.py)

再读：

- [src/tau_coding/tui/app.py](../../src/tau_coding/tui/app.py)
- [src/tau_coding/tui/widgets.py](../../src/tau_coding/tui/widgets.py)

入门不要先读完整 `app.py`，先看 adapter。

## 关键理解

TUI 是前端，不是 agent brain。它应该消费事件、显示 transcript、提交 prompt，而不是决定 agent loop 行为。

Adapter 是关键隔离层：它让 UI 可以有自己的状态模型，同时不反向污染核心事件模型。

## 测试入口

```bash
uv run pytest tests/test_tui_adapter.py -q
```

进阶再读：

```bash
uv run pytest tests/test_tui_app.py -q
```

## 自检问题

- 为什么 Textual 不能成为 `tau_agent` 依赖?
- Adapter 输入是什么，输出是什么?
- TUI app 应该调用 loop 还是 `CodingSession`?
- 为什么 `tests/test_tui_adapter.py` 比 `test_tui_app.py` 更适合入门?

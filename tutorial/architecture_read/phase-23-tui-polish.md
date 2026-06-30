# Phase 23: Advanced TUI and Product Polish

Source: [dev-notes/architecture/phase-23-tui-polish.md](../../dev-notes/architecture/phase-23-tui-polish.md)

这一 phase 聚焦 TUI 产品体验：选择、复制、状态提示、主题、picker、通知等。

## 要抓住的主线

前面的 TUI 已经能跑，但真实使用需要大量细节：

- transcript selection/copy。
- tool result 展开/折叠。
- activity status。
- notifications。
- themes。
- modal/picker 交互。
- terminal command rendering。
- queued steering/follow-up。

## 源码阅读路线

读：

- [src/tau_coding/tui/app.py](../../src/tau_coding/tui/app.py)
- [src/tau_coding/tui/widgets.py](../../src/tau_coding/tui/widgets.py)
- [src/tau_coding/tui/config.py](../../src/tau_coding/tui/config.py)
- [src/tau_coding/tui/state.py](../../src/tau_coding/tui/state.py)

这里可以按测试名反查，不建议从 `app.py` 第一行硬读到最后。

## 关键理解

Polish 不等于随意加 UI 状态。每个交互都要保护底层 session 和 agent run 的一致性。例如运行中取消、新 session、queued prompt 都有明确边界。

## 测试入口

```bash
uv run pytest tests/test_tui_config.py tests/test_tui_app.py::test_tui_app_shows_activity_indicator_while_running -q
```

进阶按功能搜索：

```bash
rg -n "selection|theme|notification|queued|terminal" tests/test_tui_app.py
```

## 自检问题

- TUI polish 哪些只是显示，哪些会改变 session?
- 为什么运行中某些命令必须被 blocking?
- Selection/copy 为什么要考虑 tool result visibility?
- 主题配置为什么需要测试?

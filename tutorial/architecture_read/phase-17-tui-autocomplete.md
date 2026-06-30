# Phase 17: TUI Slash-command Autocomplete

Source: [dev-notes/architecture/phase-17-tui-autocomplete.md](../../dev-notes/architecture/phase-17-tui-autocomplete.md)

这一 phase 为 TUI prompt 增加 slash command、skill、prompt template、路径等补全。

## 要抓住的主线

Autocomplete 是 UI 体验层，但它依赖 command registry、skills、prompt templates、session list 等应用状态。

它不能改变命令含义，只能根据当前输入给出候选和 replacement。

## 源码阅读路线

读：

- [src/tau_coding/tui/autocomplete.py](../../src/tau_coding/tui/autocomplete.py)
- [src/tau_coding/tui/widgets.py](../../src/tau_coding/tui/widgets.py)
- [src/tau_coding/tui/app.py](../../src/tau_coding/tui/app.py)

先看 `build_completion_state`，再看 TUI 如何渲染和接受补全。

## 关键理解

补全结果需要携带 display、replacement、description、category 等信息。这样 UI 可以分组显示，但命令逻辑仍由 registry 和 session 处理。

## 测试入口

```bash
uv run pytest tests/test_tui_autocomplete.py -q
```

## 自检问题

- slash command 补全和文件路径补全如何避免互相干扰?
- 补全接受后改的是整段输入还是当前 token?
- 为什么补全不能自己执行命令?
- prompt templates 为什么也能出现在 slash 补全里?

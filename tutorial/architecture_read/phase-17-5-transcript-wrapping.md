# Phase 17.5: TUI Transcript Wrapping

Source: [dev-notes/architecture/phase-17-5-transcript-wrapping.md](../../dev-notes/architecture/phase-17-5-transcript-wrapping.md)

这一 phase 聚焦 TUI transcript 的换行和显示可读性。

## 要抓住的主线

这是产品体验 polish，但仍然要守住边界：换行属于 UI 渲染，不应该改变底层 message 或 event。

Transcript 需要处理：

- 长段文本。
- 长路径或长 token。
- Markdown/code block。
- 工具输出。

## 源码阅读路线

读：

- [src/tau_coding/tui/widgets.py](../../src/tau_coding/tui/widgets.py)
- [src/tau_coding/tui/state.py](../../src/tau_coding/tui/state.py)

重点看 transcript item 如何转成 Rich/Textual renderable。

## 关键理解

UI wrapping 的目标是让用户看得清楚，而不是改变语义。复制、选择、导出时仍然应该保留原始文本含义。

## 测试入口

```bash
uv run pytest tests/test_tui_app.py::test_chat_items_fold_long_unbroken_text_to_console_width \
              tests/test_tui_app.py::test_tui_transcript_reflows_when_terminal_resizes -q
```

## 自检问题

- 换行逻辑为什么不能改 transcript message 本身?
- 长 unbroken text 为什么特别麻烦?
- terminal resize 后哪些 UI state 需要刷新?
- wrapping 是 agent 层还是 TUI 层职责?

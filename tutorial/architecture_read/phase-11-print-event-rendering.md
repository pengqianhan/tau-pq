# Phase 11: Print and Event Rendering Modes

Source: [dev-notes/architecture/phase-11-print-event-rendering.md](../../dev-notes/architecture/phase-11-print-event-rendering.md)

这一 phase 把 CLI 输出从单一文本扩展成多个 renderer。

## 要抓住的主线

同一串 `AgentEvent` 可以有不同渲染方式：

- text: 只输出最终 assistant 文本。
- json: 每个事件输出 JSONL。
- transcript: 实时显示消息和工具过程。

这证明了“事件就是契约”。

## 源码阅读路线

读 `src/tau_coding/rendering/`：

- [base.py](../../src/tau_coding/rendering/base.py)
- [plain.py](../../src/tau_coding/rendering/plain.py)
- [json.py](../../src/tau_coding/rendering/json.py)
- [transcript.py](../../src/tau_coding/rendering/transcript.py)
- [__init__.py](../../src/tau_coding/rendering/__init__.py)

再回到 [src/tau_coding/cli.py](../../src/tau_coding/cli.py)，看 `run_print_mode` 如何选择 renderer。

## 关键理解

Renderer 不应该控制 agent loop。它只消费事件。

`EventRenderer` 协议很小：`render(event)` 和 `finish()`。这让新输出模式很容易加。

## 测试入口

```bash
uv run pytest tests/test_rendering.py -q
```

## 自检问题

- text/json/transcript 三种模式消费的是不是同一类 event?
- JSON renderer 为什么适合自动化工具?
- transcript renderer 为什么不应该知道 provider 细节?
- `finish()` 负责什么?

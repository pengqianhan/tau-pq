# Phase 2: AI Provider Layer

Source: [dev-notes/architecture/phase-2-ai-provider-layer.md](../../dev-notes/architecture/phase-2-ai-provider-layer.md)

这一 phase 建立模型 provider 抽象。核心目标是：不让 agent loop 直接认识 OpenAI、Anthropic 或任何具体 SDK。

## 要抓住的主线

Provider 层做一件事：把外部模型 API 的流式响应翻译成 Tau 自己的 provider events。

后面的 agent loop 只看统一事件：

- response start
- text delta
- thinking delta
- tool call
- response end
- error / retry

这样换 provider 时，不需要重写 agent loop。

## 源码阅读路线

先读：

- [src/tau_ai/provider.py](../../src/tau_ai/provider.py)
- [src/tau_ai/events.py](../../src/tau_ai/events.py)
- [src/tau_ai/fake.py](../../src/tau_ai/fake.py)

再读具体 provider：

- [src/tau_ai/openai_compatible.py](../../src/tau_ai/openai_compatible.py)
- [src/tau_ai/openai_codex.py](../../src/tau_ai/openai_codex.py)
- [src/tau_ai/anthropic.py](../../src/tau_ai/anthropic.py)

## 关键概念

`ModelProvider` 是协议，不是具体类。它要求 provider 提供 `stream_response(...)`，返回异步事件流。

`FakeProvider` 是学习和测试入口。它不联网，只回放你写好的事件脚本，因此可以精确验证 loop 行为。

OpenAI-compatible provider 的重点不是网络细节，而是格式转换：Tau message/tool/event 和 OpenAI-style JSON payload 之间互相转换。

## 测试入口

```bash
uv run pytest tests/test_tau_ai.py::test_fake_provider_replays_scripted_events -q
```

如果继续读真实 provider：

```bash
uv run pytest tests/test_tau_ai.py -q
```

## 自检问题

- 为什么 provider 层发的是事件流，而不是一次性返回完整文本?
- 为什么 `FakeProvider` 对测试 agent loop 很关键?
- provider 层应该知道 Textual 或 CLI 吗?
- agent loop 为什么不应该直接解析 OpenAI SSE?

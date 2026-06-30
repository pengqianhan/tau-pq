# Phase 22: Compaction Replay Foundation

Source: [dev-notes/architecture/phase-22-compaction-foundation.md](../../dev-notes/architecture/phase-22-compaction-foundation.md)

这一 phase 引入 context compaction：当上下文太大时，用摘要替换旧消息。

## 要抓住的主线

Compaction 要解决两个问题：

1. 当前上下文放不下。
2. 历史信息不能直接丢。

Tau 用 `CompactionEntry` 把被替换的 entry ids 和 summary 记录下来。Replay 时，summary 会变成一条特殊的 previous conversation summary。

## 源码阅读路线

读：

- [src/tau_coding/context_window.py](../../src/tau_coding/context_window.py)
- [src/tau_agent/session/entries.py](../../src/tau_agent/session/entries.py)
- [src/tau_agent/session/tree.py](../../src/tau_agent/session/tree.py)
- [src/tau_coding/session.py](../../src/tau_coding/session.py)

## 关键理解

Compaction 不是删除历史文件内容。它是在 active context 中用 summary 代替旧消息，同时 session log 仍然保留 compaction entry。

自动 compaction 和手动 `/compact` 都应该走相同的持久化/replay 语义。

## 测试入口

```bash
uv run pytest tests/test_context_window.py \
              tests/test_session.py::test_session_state_replays_compaction_as_context_summary \
              tests/test_coding_session.py::test_session_compact_persists_summary_and_rebuilds_context -q
```

## 自检问题

- CompactionEntry 记录哪些信息?
- Replay 时 summary 怎么进入 messages?
- 自动 compaction 和手动 compaction 的共同边界是什么?
- 为什么 compaction 属于 session replay 问题，不只是 prompt 拼接问题?

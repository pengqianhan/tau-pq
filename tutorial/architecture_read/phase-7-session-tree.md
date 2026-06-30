# Phase 7: Session Tree and JSONL Persistence

Source: [dev-notes/architecture/phase-7-session-tree.md](../../dev-notes/architecture/phase-7-session-tree.md)

这一 phase 引入 session persistence。Tau 开始能把对话保存下来，并以树的方式 replay。

## 要抓住的主线

Session 不是简单覆盖式保存，而是 append-only JSONL。

每次发生重要变化，就追加一条 entry：

- message entry
- model change
- label
- leaf pointer
- custom entry
- compaction entry
- branch summary

Replay 时从这些 entry 重建当前 transcript 和状态。

## 源码阅读路线

读 `src/tau_agent/session/`：

- [entries.py](../../src/tau_agent/session/entries.py)
- [jsonl.py](../../src/tau_agent/session/jsonl.py)
- [tree.py](../../src/tau_agent/session/tree.py)
- [memory.py](../../src/tau_agent/session/memory.py)

先从 entry 类型读起，再看 JSONL encode/decode，最后看 tree replay。

## 关键理解

Append-only 的好处是历史不容易丢。分支、resume、导出、compaction 都可以建立在同一套 entry log 上。

`LeafEntry` 很重要：它告诉系统当前活跃分支停在哪个 entry。

## 测试入口

```bash
uv run pytest tests/test_session.py -q
```

重点看：

- `test_session_entry_round_trips_jsonl`
- `test_session_state_replays_linear_entries`
- `test_path_to_entry_returns_root_to_leaf_branch`
- `test_session_state_can_replay_one_branch`

## 自检问题

- 为什么 session 用 append-only JSONL?
- `LeafEntry` 解决什么问题?
- Replay 是从文件里读出完整对象，还是重新计算状态?
- Session 层为什么仍然放在 `tau_agent`?

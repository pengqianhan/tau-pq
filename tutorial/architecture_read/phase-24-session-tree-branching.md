# Phase 24: Session Tree Branching

Source: [dev-notes/architecture/phase-24-session-tree-branching.md](../../dev-notes/architecture/phase-24-session-tree-branching.md)

这一 phase 完善 session tree branching，让用户可以从历史节点分支继续。

## 要抓住的主线

Session 一开始就是 tree，而不是单链表。Phase 24 把这个能力暴露成更完整的分支工作流。

Branching 需要处理：

- 从哪个 entry 分支。
- 是否生成 branch summary。
- active leaf 如何切换。
- UI 如何显示分支。
- 原历史不能被破坏。

## 源码阅读路线

读：

- [src/tau_agent/session/tree.py](../../src/tau_agent/session/tree.py)
- [src/tau_agent/session/entries.py](../../src/tau_agent/session/entries.py)
- [src/tau_coding/session.py](../../src/tau_coding/session.py)
- [src/tau_coding/branch_summary.py](../../src/tau_coding/branch_summary.py)
- [src/tau_coding/tui/app.py](../../src/tau_coding/tui/app.py)

## 关键理解

Branching 不等于删除后面的历史。它只是把 active leaf 切到另一条路径，并可以在新路径上继续 append。

Branch summary 是为了让新分支继承必要上下文，而不是把旧分支全部塞回 prompt。

## 测试入口

```bash
uv run pytest tests/test_session.py::test_session_state_can_replay_one_branch \
              tests/test_coding_session.py::test_session_branches_to_previous_entry_without_destroying_history \
              tests/test_coding_session.py::test_session_branch_with_summary_rebuilds_context -q
```

## 自检问题

- Branching 和 resume 的区别是什么?
- active leaf 变化后，原来的历史还在吗?
- Branch summary 为什么有必要?
- UI tree picker 应该返回什么给 session 层?

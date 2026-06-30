# Phase 14: Session Manager and Resume

Source: [dev-notes/architecture/phase-14-session-manager-resume.md](../../dev-notes/architecture/phase-14-session-manager-resume.md)

这一 phase 在单个 session JSONL 之外，加了 session index 和 resume 流程。

## 要抓住的主线

Phase 7 能保存 session 文件，但用户还需要找到和恢复 session。

SessionManager 负责：

- 创建 session record。
- 维护 session index。
- 按项目 cwd 过滤。
- 找最近 session。
- 支持 resume。

## 源码阅读路线

读：

- [src/tau_coding/session_manager.py](../../src/tau_coding/session_manager.py)
- [src/tau_coding/session.py](../../src/tau_coding/session.py)
- [src/tau_coding/cli.py](../../src/tau_coding/cli.py)

再看 TUI 如何打开 session picker。

## 关键理解

Session tree 是 transcript 内部结构。SessionManager 是多个 session 文件的目录服务。

不要混淆：

```text
session replay = 还原一个 JSONL 的状态
session manager = 找到哪个 JSONL 应该被打开
```

## 测试入口

```bash
uv run pytest tests/test_session_manager.py -q
```

可继续读：

```bash
uv run pytest tests/test_cli.py::test_sessions_command_lists_indexed_sessions -q
```

## 自检问题

- SessionManager 和 JsonlSessionStorage 有什么区别?
- 为什么要按 cwd 过滤 session?
- resume 后需要恢复哪些状态?
- TUI picker 为什么应该依赖 SessionManager?

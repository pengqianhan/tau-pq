# Tau 框架学习教程（一步一步 + 断点调试）

这是为 **Tau** 这个"会读代码、会改代码、会跑命令的终端编码 Agent"框架准备的渐进式教程。
Tau 的最大特点是 **它本身就是教学项目**：每一层都小到可以单独读懂。本教程带你从最核心
的循环出发，逐步加上工具、状态、真实工具，最后跑起完整的 CLI，并在关键位置用
**断点 + 打印** 验证你对每一步的理解。

> 运行环境约定：所有命令都用 `uv run ...`，确保用的是项目自己的虚拟环境（Python 3.14）。
> 第一次先在仓库根目录执行 `uv sync --dev`。

> **怎么用这个清单**：本教程分成 9 章。每章末尾都有一个 **`✅ 本章打卡`** 清单，
> 你完成一项就把 `- [ ]` 改成 `- [x]`（在编辑器里把方括号里的空格换成 `x`）。
> 下面的"学习进度总览"是全局进度条，每读完一章就勾掉对应的一行。

---

## 📋 学习进度总览（全局进度条）

- [ ] **第 0 章** · 建立全局心智模型（三层架构 + 事件契约）
- [X] **第 1 章** · 环境准备与冒烟测试（`uv sync` / `pytest` 全绿）
- [ ] **第 2 章** · 读懂核心数据结构（消息 / 事件 / 工具）
- [ ] **第 3 章** · 示例 1：最小循环（模型流 → 事件流）
- [ ] **第 4 章** · 示例 2：工具调用 + Harness（Agent 的灵魂循环）
- [ ] **第 5 章** · 示例 3：真实内置工具（read/write/edit/bash）
- [ ] **第 6 章** · 跑起完整 CLI（三层拼装）
- [ ] **第 7 章** · 精读 dev-notes 设计文档
- [ ] **第 8 章** · 毕业测验（速查自检）

---

## 第 0 章 · 先建立全局心智模型（最重要）

Tau 分成三层，依赖方向是单向的：

```text
tau_coding  →  tau_agent  →  tau_ai
（真实 App）   （可复用大脑）   （模型适配/流式）
```

| 层     | 包             | 职责                                                                                   | 关键文件                                                                                                                                                                                                         |
| ------ | -------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 模型层 | `tau_ai`     | 把各家模型（OpenAI/Anthropic/...）翻译成**统一的 provider 事件流**               | [`provider.py`](../src/tau_ai/provider.py)、[`events.py`](../src/tau_ai/events.py)、[`fake.py`](../src/tau_ai/fake.py)                                                                                              |
| 大脑层 | `tau_agent`  | 可移植的**harness、循环、工具、事件、消息、会话**；不知道 CLI/终端/文件路径      | [`loop.py`](../src/tau_agent/loop.py)、[`harness.py`](../src/tau_agent/harness.py)、[`tools.py`](../src/tau_agent/tools.py)、[`messages.py`](../src/tau_agent/messages.py)、[`events.py`](../src/tau_agent/events.py) |
| 应用层 | `tau_coding` | 把大脑包成真正的编码 App：CLI、TUI、read/write/edit/bash 工具、provider 配置、会话落盘 | [`cli.py`](../src/tau_coding/cli.py)、[`tools.py`](../src/tau_coding/tools.py)、[`session.py`](../src/tau_coding/session.py)                                                                                        |

一句话记住三个边界（来自 `AGENTS.md`）：

```text
AgentHarness = 可复用的大脑
CodingSession = 编码 Agent 的运行环境
TUI = 其中一种前端
```

**最关键的一条设计哲学：事件就是契约（Events are the contract）。**
循环不直接渲染任何 UI，它只 `yield` 一串带 `.type` 的事件对象。CLI、Rich、Textual、
你自己写的前端，全都只是"消费这些事件"。理解了这点，你就理解了 Tau 的一半。

下面我们就顺着"模型流 → 事件 → 工具 → 状态 → 真实工具 → CLI"一层层往上爬。

### ✅ 本章打卡

- [X] 能用一句话分别说出 `tau_ai` / `tau_agent` / `tau_coding` 的职责
- [ ] 能说出三层的依赖方向，并解释"为什么大脑层不准依赖 Textual/Rich"
- [ ] 能复述"事件就是契约"是什么意思
- [ ] 完成后回到总览，把 **第 0 章** 那一行勾上

---

## 第 1 章 · 环境准备与冒烟测试

```bash
cd <仓库根目录>        # 即 tau-pq/
uv sync --dev          # 装依赖、建 .venv
uv run tau --version   # 期望输出: tau 0.1.0
uv run pytest -q       # 期望: 几乎全绿（见下方"已知失败"）
```

> **为什么先跑测试？** Tau 的测试大量使用 `FakeProvider`（见下一章），它让 Agent 行为
> 完全确定、不需要联网、不需要 API key。这正是学习一个 Agent 框架最理想的起点——
> 你能精确预言每一步的输出。

> ⚠️ **已知失败（与本教程无关，放心继续）**：在本机当前分支上，整套 `pytest` 可能有
> **1~2 个失败**，都在 `tau_coding` 的 *provider 配置* 层，离你要学的核心循环很远：
>
> 1. `test_session_switches_configured_provider` —— **环境变量泄漏**。如果你的 shell 里
>    导出了 `OPENAI_API_KEY`，这个测试会把真实环境里的 key 当成"已配置"，于是多出几个
>    OpenAI 模型而失败。这是测试隔离不严，不是代码 bug。把 key 临时清掉再跑就绿：
>    ```bash
>    env -u OPENAI_API_KEY -u OPENROUTER_API_KEY -u GEMINI_API_KEY uv run pytest -q
>    ```
> 2. `test_save_and_load_provider_settings_round_trip` —— 这是仓库当前分支上一个**已存在的
>    陈旧测试**（加载配置时会顺带注入默认 provider 目录，导致 round-trip 不完全相等）。
>    和环境、和本教程都无关。
>
> **结论**：你真正要学的核心测试全部通过。想要一个干净绿条，直接只跑核心层：
>
> ```bash
> uv run pytest tests/test_agent_loop.py tests/test_agent_harness.py \
>               tests/test_coding_tools.py tests/test_agent_types.py -q
> ```

先单独跑循环相关的测试，感受一下：

```bash
uv run pytest tests/test_agent_loop.py -q
```

打开 [`tests/test_agent_loop.py`](../tests/test_agent_loop.py) 跟着读，它本身就是最好的教材。

### ✅ 本章打卡

- [X] `uv sync --dev` 成功，生成了 `.venv`
- [X] `uv run tau --version` 输出 `tau 0.1.0`
- [X] `uv run pytest -q` 跑通（除上面"已知失败"的 1~2 个 provider 配置测试外全绿）
- [X] 核心层四件套全绿：`pytest tests/test_agent_loop.py tests/test_agent_harness.py tests/test_coding_tools.py tests/test_agent_types.py -q`
- [X] `uv run pytest tests/test_agent_loop.py -q` 通过，并扫读了这个测试文件
- [X] 完成后回到总览，把 **第 1 章** 那一行勾上

---

## 第 2 章 · 核心数据结构：消息、事件、工具

在跑代码前，先认识三组 pydantic 模型。它们都很短，**强烈建议直接打开源码扫一遍**。

### 2.1 消息（transcript 的组成单位）— [`messages.py`](../src/tau_agent/messages.py)

- `UserMessage(content)` — 用户说的话
- `AssistantMessage(content, tool_calls)` — 模型说的话，**可能附带工具调用请求**
- `ToolResultMessage(tool_call_id, name, content, ok, ...)` — 一次工具执行的结果

这三者的联合类型叫 `AgentMessage`。一段对话（transcript）就是 `list[AgentMessage]`。

### 2.2 事件（循环的输出 = 前端的输入）— [`events.py`](../src/tau_agent/events.py)

循环会按顺序吐出这些事件（注意成对出现）：

```text
agent_start
  turn_start(turn=1)
    message_start
    message_delta / thinking_delta   ← 流式 token
    message_end(message=...)         ← 一句完整回复落定
    tool_execution_start(tool_call)  ← 如果模型要调工具
    tool_execution_end(result)
  turn_end(turn=1)
  turn_start(turn=2) ...             ← 工具结果喂回后，再问一轮
agent_end
```

### 2.3 工具（一份 schema + 一个 async 执行体）— [`tools.py`](../src/tau_agent/tools.py)

```python
@dataclass(frozen=True, slots=True)
class AgentTool:
    name: str
    description: str
    input_schema: Mapping[str, JSONValue]   # 给模型看的 JSON schema
    executor: ToolExecutor                   # async (arguments, signal) -> AgentToolResult
```

记住这句框架哲学：**工具就是普通的、带类型的函数**——一个 schema 加一个返回结构化结果的
异步执行体。没有魔法。

### ✅ 本章打卡

- [ ] 读完 `messages.py`，能说出三种消息分别代表谁说的话
- [ ] 读完 `events.py`，能凭记忆默写"一轮带工具调用"的完整事件顺序
- [ ] 读完 `tools.py`，能说出 `AgentTool` 的四个字段及各自作用
- [ ] 完成后回到总览，把 **第 2 章** 那一行勾上

---

## 第 3 章 · 示例 1：最小循环（看清"模型流 → 事件流"）

运行：

```bash
uv run python tutorial/ex1_loop.py
```

代码见 [`ex1_loop.py`](ex1_loop.py)。它用 `FakeProvider` 脚本了一次"模型回复"，
然后调用 `run_agent_loop`，把每个事件打印出来。期望输出：

```text
agent_start → turn_start → message_start → message_delta×2 → message_end → turn_end → agent_end
```

并且结束后 `messages` 里多了一条 assistant 消息。

### 🔬 动手验证（断点 + 打印）

1. 打开 [`src/tau_agent/loop.py`](../src/tau_agent/loop.py)，在 `run_agent_loop` 里
   `while max_turns is None or turn <= max_turns:` 这一行下面加一行：

   ```python
   print(">>> [loop] entering turn", turn, "with", len(messages), "messages")
   ```

   再跑 `uv run python tutorial/ex1_loop.py`，确认它**只进了一次循环**（turn=1），
   因为这次模型没有要求调用工具。
2. 想用真正的调试器？在 `ex1_loop.py` 里 `async for event in ...` 之前加一行
   `breakpoint()`，然后：

   ```bash
   uv run python -m pdb tutorial/ex1_loop.py
   ```

   在 pdb 里用 `s`（step）单步进入循环，用 `pp event` 打印每个事件。重点观察那个
   `if isinstance(provider_event, ProviderTextDeltaEvent):` 分支——这就是
   "**provider 事件被翻译成 agent 事件**"的核心翻译表。
3. 自己改一下脚本：在 `ProviderTextDeltaEvent` 里多加几段 delta，重跑，确认
   `message_delta` 事件数量随之变化，但最终 `message_end` 只有一个。

### ✅ 本章打卡

- [ ] 跑通 `ex1_loop.py`，输出的事件序列与预期一致
- [ ] 在 `loop.py` 的 `while` 处加 `print`，亲眼确认本例只跑了一轮（turn=1）
- [ ] 用 `python -m pdb` 单步进入循环，`pp event` 看清每个事件
- [ ] 改 delta 数量重跑，确认 `message_delta` 数量随之变化、`message_end` 仍只有一个
- [ ] 完成后回到总览，把 **第 3 章** 那一行勾上

---

## 第 4 章 · 示例 2：工具调用 + AgentHarness（Agent 的"灵魂循环"）

运行：

```bash
uv run python tutorial/ex2_tools.py
```

代码见 [`ex2_tools.py`](ex2_tools.py)。这次我们：

- 定义了一个真正的工具 `add(a, b)`；
- 用 `FakeProvider` 脚本了**两次**模型回复：第一次要求 `add(2,3)`，第二次给出自然语言答案；
- 用 `AgentHarness`（而不是裸 `run_agent_loop`）来驱动——它替我们拥有 transcript。

期望最终 transcript 是 **4 条**：

```text
user:      What is 2 + 3?
assistant: (空 content) + tool_calls=[add(2,3)]
tool:      content='5'  ok=True
assistant: The sum is 5.
```

这就是 Agent 的本质循环：**模型要求调用工具 → 框架执行工具 → 把结果作为新消息喂回 →
再次询问模型 → 直到模型不再要求调用工具就停下。**

### 🔬 动手验证

1. **看模型真正传进来的参数**：在 `ex2_tools.py` 的 `add_executor` 里第一行加
   `breakpoint()`（文件里已标注"断点 A"），跑 `uv run python -m pdb tutorial/ex2_tools.py`，
   然后 `c` 继续到断点，`pp arguments`，确认拿到 `{'a': 2, 'b': 3}`。
2. **看循环为什么会跑第二轮**：打开 [`loop.py`](../src/tau_agent/loop.py)，找到
   `if not assistant_message.tool_calls:` 这个判断。第一轮 `tool_calls` 非空 → 不进这个分支
   → 执行工具 → `turn += 1` → 第二轮；第二轮 `tool_calls` 为空 → 进入分支 → `break`。
   在这一行上面加 `print(">>> tool_calls?", bool(assistant_message.tool_calls))` 重跑感受一下。
3. **看工具异常如何被隔离**：在 `add_executor` 里临时 `raise RuntimeError("boom")`，重跑。
   你会看到程序**不崩溃**，而是产生一条 `ok=False` 的工具结果继续往下。原因在
   [`loop.py`](../src/tau_agent/loop.py) 的 `_execute_tool`：它 `try/except Exception`，
   把任何工具异常包装成结构化失败结果。**工具是隔离边界**——记住这条。
4. **看 harness 的状态边界**：在 [`harness.py`](../src/tau_agent/harness.py) 的 `prompt()`
   方法里读 `_ensure_not_running()` 和 `self._messages.append(message)`。harness 的职责就是
   "拥有 transcript + 提供 prompt()/continue_()/steer() 入口"，执行本身仍委托给纯函数
   `run_agent_loop`。

### ✅ 本章打卡

- [ ] 跑通 `ex2_tools.py`，最终 transcript 恰好 4 条
- [ ] 用 pdb 在 `add_executor` 处看到 `arguments == {'a': 2, 'b': 3}`
- [ ] 在 `loop.py` 的 `if not assistant_message.tool_calls:` 处加 `print`，理解为何会跑第二轮
- [ ] 在 `add_executor` 里 `raise` 一个异常，确认程序不崩、变成 `ok=False` 结果
- [ ] 读 `harness.prompt()`，能说清 harness 与 `run_agent_loop` 的分工
- [ ] 完成后回到总览，把 **第 4 章** 那一行勾上

---

## 第 5 章 · 示例 3：真实的内置工具（read/write/edit/bash）

运行：

```bash
uv run python tutorial/ex3_realtool.py
```

代码见 [`ex3_realtool.py`](ex3_realtool.py)。前两个示例的工具是玩具；这次我们直接用
`tau_coding` 层提供的**真实** `read` 工具，并且**脱离模型、脱离循环**单独 `await` 它。
这是调试任何工具最干净的方式。

观察点：

- `result.ok` / `result.content` / `result.data`（注意 `data` 里有 `truncation` 截断元信息——
  生产级工具会把超长输出截断，并把"截断了多少"也结构化地告诉你）；
- 读不存在的文件时，工具**直接抛 `ToolInputError`**，而不是返回 `ok=False`——
  和第 4 章第 3 点呼应：把异常转成失败结果是**循环**的职责，不是工具的职责。

### 🔬 动手验证

1. 打开 [`src/tau_coding/tools.py`](../src/tau_coding/tools.py)，看
   `create_read_tool_definition`（约第 117 行）。这里能看到真实工具的三件套：
   `prompt_snippet`（给模型的简介）、`input_schema`（参数 schema）、`executor`（执行体）。
   对照 `to_agent_tool()`（约第 80 行）看它如何降级成大脑层认识的 `AgentTool`。
2. 在 `ex3_realtool.py` 里把 `create_read_tool` 换成 `create_bash_tool`，执行
   `await bash.execute({"command": "echo hello"})`，打印结果。感受"同一个 AgentTool 接口"
   如何统一了文件工具和 shell 工具。
3. 进阶：把示例 2 里的玩具 `add_tool` 换成这里的真实 `read` 工具，用 `FakeProvider` 脚本
   模型"要求读 pyproject.toml"，你就拼出了一个**会读文件的迷你 Agent**——而且全程不需要
   API key。

### ✅ 本章打卡

- [ ] 跑通 `ex3_realtool.py`，看清 `ok` / `content` / `data` 三个字段
- [ ] 读 `create_read_tool_definition` 与 `to_agent_tool`，说出"真实工具三件套"
- [ ] 把工具换成 `create_bash_tool`，成功跑出 `echo hello`
- [ ] （进阶，可选）用真实 `read` 工具 + `FakeProvider` 拼一个会读文件的迷你 Agent
- [ ] 完成后回到总览，把 **第 5 章** 那一行勾上

---

## 第 6 章 · 跑起完整的 CLI（把三层拼到一起）

前面都是"库"的用法。现在看它作为真实 App 怎么跑：

```bash
# 一次性 print 模式（脚本友好）——但需要先配置一个模型 provider
uv run tau -p "explain what this project does"

# 交互式 TUI
uv run tau
```

真实模型需要登录。启动后用斜杠命令：

```text
/login            # 选择并登录一个 provider（OpenAI / Anthropic / OpenRouter / 本地模型...）
/model            # 选择模型
/help             # 看所有斜杠命令
```

> 没有 API key 也没关系——本教程的示例 1~3 用 `FakeProvider` 已经覆盖了框架的全部核心机制。
> CLI 这一层主要是"事件渲染 + 会话落盘 + provider 配置"的工程封装。

### 🔬 动手验证（看 CLI 入口）

打开 [`src/tau_coding/cli.py`](../src/tau_coding/cli.py)，这是 `tau` 命令的入口
（`pyproject.toml` 里 `tau = "tau_coding.cli:app"`）。顺着读你会发现它最终也是：
构造 provider → 构造 harness → 订阅事件 → 把事件交给某个 renderer 渲染。
和你在示例 1~2 里手写的循环**是同一套契约**。

会话是 append-only 的 JSONL，存在 `~/.tau/sessions/` 下，可以 resume、可以分支——
对应源码 [`src/tau_agent/session/`](../src/tau_agent/session/) 与
[`src/tau_coding/session_manager.py`](../src/tau_coding/session_manager.py)。

### ✅ 本章打卡

- [ ] 读 `cli.py` 入口，能指出"构造 provider → 构造 harness → 订阅事件 → renderer"这条主线
- [ ] 理解 CLI 用的也是示例 1~2 里同一套事件契约
- [ ] （可选）`/login` 配置一个真实 provider，用 `tau -p "..."` 真跑一次
- [ ] 完成后回到总览，把 **第 6 章** 那一行勾上

---

## 第 7 章 · 推荐的阅读顺序与 dev-notes

Tau 的作者把"逐阶段的搭建日志"留在了 [`dev-notes/`](../dev-notes/) 里，按这个顺序读最顺：

1. [`dev-notes/design/01-architecture.md`](../dev-notes/design/01-architecture.md) — 总体架构
2. [`dev-notes/design/05-core-types-and-events.md`](../dev-notes/design/05-core-types-and-events.md) — 类型与事件
3. [`dev-notes/design/02-agent-loop.md`](../dev-notes/design/02-agent-loop.md) — 循环
4. [`dev-notes/design/03-tools.md`](../dev-notes/design/03-tools.md) — 工具
5. [`dev-notes/design/harness.md`](../dev-notes/design/harness.md) — harness
6. [`dev-notes/design/04-sessions.md`](../dev-notes/design/04-sessions.md) — 会话
7. 之后按 `dev-notes/architecture/phase-*.md` 的阶段号往后读（system prompt、TUI、
   compaction、分支等高级特性）。

### ✅ 本章打卡

- [ ] 读完 `01-architecture.md`
- [ ] 读完 `05-core-types-and-events.md`
- [ ] 读完 `02-agent-loop.md`
- [ ] 读完 `03-tools.md`
- [ ] 读完 `harness.md`
- [ ] 读完 `04-sessions.md`
- [ ] （可选）挑一篇感兴趣的 `architecture/phase-*.md` 深入
- [ ] 完成后回到总览，把 **第 7 章** 那一行勾上

---

## 第 8 章 · 毕业测验（学完应该能回答）

不看答案，先自己回答下面每一题，能全部答上来就算结业：

- [ ] 三层各自的职责？依赖方向？为什么大脑层不准依赖 Textual/Rich？
- [ ] "事件就是契约"具体指什么？列出一轮带工具调用的完整事件序列。
- [ ] 一个工具由哪两部分组成？工具抛异常时谁负责兜底？
- [ ] transcript 是谁拥有的？`run_agent_loop`（纯函数）和 `AgentHarness`（有状态）如何分工？
- [ ] 循环靠什么条件决定"再跑一轮"还是"停下"？（答案在 `if not assistant_message.tool_calls`）
- [ ] `FakeProvider` 为什么对学习/测试这么关键？
- [ ] 全部答对后回到总览，把 **第 8 章** 那一行勾上 🎉

> 全部能答上来，你就掌握了任何"编码 Agent"框架的通用骨架。Tau 只是把它写得足够小、足够好读。

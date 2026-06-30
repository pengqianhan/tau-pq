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

> 🎯 **本教程的核心方法：读源码，不是读教程。** 教程只是"导游"，真正的老师是
> `src/` 里的代码。从第 2 章起，每个核心章节都按同一个节奏走：
>
> 1. **📖 精读代码** —— 我会指给你"打开哪个文件、看哪个函数、带着什么问题读"。**先自己读，再往下看。**
> 2. **▶️ 跑给自己看** —— 给你一条能立刻看到"这段代码输出长啥样"的命令（REPL 自省 / 打印源码 / pdb 单步）。
> 3. **🚦 理解关卡** —— 几道必须能**不看代码口头答出**的问题。**答不上就回去重读，别急着进下一章。**
>
> 规矩只有一条：**没真正读懂当前这段代码，就不要进入下一步。** 慢就是快。

### 🧭 本教程怎么使用 `dev-notes/` 和 `tests/`

本教程有三种材料，各自负责不同问题：

- `tutorial/`：学习主线。它告诉你"先读哪里、怎么跑、在哪里打断点"。
- [`dev-notes/`](../dev-notes/)：设计背景。它回答"为什么 Tau 要这样分层、为什么事件是契约、为什么
  TUI 必须隔在 adapter 后面"。
- [`tests/`](../tests/)：可执行规格。它回答"代码是否真的按这个设计工作"，也给你最小、确定、
  不需要 API key 的示例。

所以每个核心章节都会有两张地图：

- **设计地图**：读哪篇 `dev-notes`，理解这章背后的架构意图。
- **测试地图**：跑哪几个 pytest 用例，把这章的行为变成可验证的事实。

读源码时建议按这个闭环走：

```text
教程导读 → 源码精读 → 示例运行 → 对应测试 → dev-notes 设计背景 → 自己改一个小实验
```

---

## 🧰 观察工具箱（边读边看输出的 4 个小技巧）

读代码最怕"看了一遍但不确定自己理解对没对"。下面 4 招贯穿全教程，遇到就回来查：

**① 打印任意函数/类的源码**（在终端里就着输出读，不用来回翻文件）：

```bash
uv run python -c "import inspect, tau_agent.loop as m; print(inspect.getsource(m.run_agent_loop))"
```

**② 自省一个 pydantic 模型的字段与默认值**（确认"它到底长啥样"）：

```bash
uv run python -c "from tau_agent.messages import AssistantMessage as M; print(list(M.model_fields)); print(M().model_dump())"
```

**③ 列出一个"联合类型"的所有成员**（如所有事件类型）：

```bash
uv run python -c "import typing, tau_agent.events as e; print([t.__name__ for t in typing.get_args(e.AgentEvent.__value__)])"
```

**④ 用 pdb 单步进入并打印变量**（看真实执行时每个变量的值）：

```bash
uv run python -m pdb tutorial/ex1_loop.py     # 进入后：b 文件:行 设断点；c 继续；s 单步；pp 变量 打印；q 退出
```

> 💡 进入 Python 交互式 REPL（`uv run python`）后，把上面 `-c "..."` 里的语句一行行敲进去，
> 还能随手改、随手试 —— 这是"边读边验证"最快的方式。

---

## 📋 学习进度总览（全局进度条）

- [ ] **第 0 章** · 建立全局心智模型（三层架构 + 事件契约）
- [X] **第 1 章** · 环境准备与冒烟测试（`uv sync` / `pytest` 全绿）
- [ ] **第 2 章** · 读懂核心数据结构（消息 / 事件 / 工具）
- [ ] **第 3 章** · 示例 1：最小循环（模型流 → 事件流）
- [ ] **第 4 章** · 示例 2：工具调用 + Harness（Agent 的灵魂循环）
- [ ] **第 5 章** · 示例 3：真实内置工具（read/write/edit/bash）
- [ ] **第 6 章** · 跑起完整 CLI（三层拼装）
- [ ] **第 7 章** · 用 dev-notes + tests 反查源码
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

### 🧭 对照地图

**设计地图**：

- [`dev-notes/design/00-roadmap.md`](../dev-notes/design/00-roadmap.md) —— Tau 的阶段路线图。
- [`dev-notes/design/01-architecture.md`](../dev-notes/design/01-architecture.md) —— 三层架构的原始设计说明。
- [`dev-notes/architecture/index.md`](../dev-notes/architecture/index.md) —— 每个实现阶段的索引。

**测试地图**：

- [`tests/test_agent_types.py`](../tests/test_agent_types.py) —— 最小消息、工具、事件类型的稳定性。
- [`tests/test_cli.py`](../tests/test_cli.py) —— `tau` 命令如何把应用层入口接起来。

先不用读完这些文件。现在只要知道：`dev-notes` 解释设计意图，`tests` 证明行为边界。

### ✅ 本章打卡

- [X] 能用一句话分别说出 `tau_ai` / `tau_agent` / `tau_coding` 的职责
- [ ] 能说出三层的依赖方向，并解释"为什么大脑层不准依赖 Textual/Rich"
- [ ] 能复述"事件就是契约"是什么意思
- [ ] 能说出 `dev-notes/` 和 `tests/` 在本教程里分别承担什么角色
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
>               tests/test_agent_types.py \
>               tests/test_coding_tools.py::test_read_tool_reads_file_with_offset_and_limit \
>               tests/test_coding_tools.py::test_write_tool_creates_parent_directories \
>               tests/test_coding_tools.py::test_edit_tool_rolls_back_when_any_edit_fails -q
> ```

先单独跑循环相关的测试，感受一下：

```bash
uv run pytest tests/test_agent_loop.py -q
```

打开 [`tests/test_agent_loop.py`](../tests/test_agent_loop.py) 跟着读，它本身就是最好的教材。

### 🧭 对照地图

**设计地图**：

- [`dev-notes/README.md`](../dev-notes/README.md) —— 解释 `dev-notes` 和 published docs 的区别。
- [`dev-notes/design/00-roadmap.md`](../dev-notes/design/00-roadmap.md) —— 看当前教程覆盖了路线图里的哪些阶段。

**测试地图**：

```bash
uv run pytest tests/test_agent_types.py tests/test_agent_loop.py tests/test_agent_harness.py \
              tests/test_coding_tools.py::test_read_tool_reads_file_with_offset_and_limit \
              tests/test_coding_tools.py::test_write_tool_creates_parent_directories \
              tests/test_coding_tools.py::test_edit_tool_rolls_back_when_any_edit_fails -q
uv run pytest --collect-only -q
```

第一条是本教程前半段的核心测试集，其中工具层只选快速代表用例。第二条只收集测试、不执行测试，
适合快速看当前仓库一共有多少测试项，以及每个文件大概负责什么。

### 🧪 小练习：把测试当目录读

打开 [`tests/test_agent_loop.py`](../tests/test_agent_loop.py)，只读测试函数名，先不要看函数体。
你会发现它天然按行为分组：流式文本、thinking delta、工具调用、取消、未知工具、provider error、
retry、最大轮数。先用函数名猜行为，再打开函数体验证猜测。

### ✅ 本章打卡

- [X] `uv sync --dev` 成功，生成了 `.venv`
- [X] `uv run tau --version` 输出 `tau 0.1.0`
- [X] `uv run pytest -q` 跑通（除上面"已知失败"的 1~2 个 provider 配置测试外全绿）
- [X] 核心层测试全绿：loop / harness / types / 工具快速代表用例
- [X] `uv run pytest tests/test_agent_loop.py -q` 通过，并扫读了这个测试文件
- [ ] 跑过 `uv run pytest --collect-only -q`，知道测试目录是 Tau 的行为索引
- [X] 完成后回到总览，把 **第 1 章** 那一行勾上

---

## 第 2 章 · 核心数据结构：消息、事件、工具

这一章不写示例脚本，**只做一件事：把 3 个最核心的源码文件读透**。它们都很短（每个几十行），
是后面所有章节的地基。请打开文件，跟着"📖 精读 → ▶️ 跑给自己看"一段段来。

### 2.1 消息 messages.py —— 一段对话由哪几种消息组成

**📖 精读** [`messages.py`](../src/tau_agent/messages.py)（你现在 IDE 里打开的就是它）。从上往下读，带着这几个问题：

1. 文件里定义了哪 **3** 个消息类？分别 `role` 是什么？
2. `AssistantMessage` 比 `UserMessage` 多了哪个字段？（提示：和"调用工具"有关）
3. 每个类顶上都有一行 `model_config = ConfigDict(extra="forbid")` —— 猜猜它是干嘛的？
4. 文件**最后一行** `type AgentMessage = UserMessage | AssistantMessage | ToolResultMessage` ——
   这就是"一段对话（transcript）= `list[AgentMessage]`"的正式定义。

**▶️ 跑给自己看**（用工具箱第②招，亲眼确认字段和默认值）：

```bash
uv run python
```

```python
>>> from tau_agent.messages import UserMessage, AssistantMessage, ToolResultMessage
>>> list(AssistantMessage.model_fields)      # 看它有哪些字段
>>> AssistantMessage().model_dump()          # 看默认值：content='' 且 tool_calls=[]
>>> UserMessage(content="hi").model_dump()
>>> UserMessage(content="hi", surprise=1)    # 故意多塞一个字段，亲眼看 extra="forbid" 报错
```

最后一行会抛 `ValidationError` —— 这正是问题 3 的答案：**禁止多余字段，保证 transcript 永远干净、可预测。**

### 2.2 事件 events.py —— 循环的输出 = 前端的输入

**📖 精读** [`events.py`](../src/tau_agent/events.py)。问题：

1. 这么多事件类，它们的**共同点**是什么？（提示：每个都有一个 `type: Literal[...]` 字段当"标签"）
2. 文件末尾 `type AgentEvent = ...` 这个大联合，一共列了多少种事件？
3. 哪些事件是**成对**的？（`agent_start`/`agent_end`、`turn_start`/`turn_end`、`message_start`/`message_end`）

**▶️ 跑给自己看**（工具箱第③招，列出全部事件类型，再看一个实例长啥样）：

```bash
uv run python -c "import typing, tau_agent.events as e; [print(t.__name__) for t in typing.get_args(e.AgentEvent.__value__)]"
uv run python -c "from tau_agent.events import TurnStartEvent; print(TurnStartEvent(turn=1).model_dump())"
```

记住这张"事件顺序表"——第 3 章你会**亲眼看到它们按这个顺序被 yield 出来**：

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

### 2.3 工具 tools.py —— 一份 schema + 一个 async 执行体

**📖 精读** [`tools.py`](../src/tau_agent/tools.py)。重点看 3 个东西：

1. `ToolCall` —— 模型"我要调用某工具"的请求（含 `id` / `name` / `arguments`）。
2. `AgentToolResult` —— 工具跑完的结构化结果（`ok` / `content` / `data` / `error`）。
3. `AgentTool` 这个 dataclass，以及它末尾的 `async def execute(...)` ——
   问题：`execute` 实际只干了一件事，是哪件？（提示：它就是去 `await self.executor(...)`）

```python
@dataclass(frozen=True, slots=True)
class AgentTool:
    name: str
    description: str
    input_schema: Mapping[str, JSONValue]   # 给模型看的 JSON schema
    executor: ToolExecutor                   # async (arguments, signal) -> AgentToolResult
```

**▶️ 跑给自己看**（确认 `AgentToolResult` 的形状）：

```bash
uv run python -c "from tau_agent.tools import AgentToolResult as R; print(list(R.model_fields))"
```

记住这句框架哲学：**工具就是普通的、带类型的函数**——一个 schema 加一个返回结构化结果的
异步执行体。没有魔法。

### 🧭 对照地图

**设计地图**：

- [`dev-notes/design/05-core-types-and-events.md`](../dev-notes/design/05-core-types-and-events.md) ——
  为什么 Tau 先定义 provider-neutral 的消息和事件。
- [`dev-notes/architecture/phase-1-core-types-and-events.md`](../dev-notes/architecture/phase-1-core-types-and-events.md) ——
  Phase 1 如何把核心类型落到代码里。
- [`dev-notes/design/03-tools.md`](../dev-notes/design/03-tools.md) —— 工具 schema、执行体、结果结构的设计背景。

**测试地图**：

```bash
uv run pytest tests/test_agent_types.py tests/test_system_prompt.py -q
```

- [`tests/test_agent_types.py`](../tests/test_agent_types.py) 验证消息、工具、事件类型本身的稳定性。
- [`tests/test_system_prompt.py`](../tests/test_system_prompt.py) 让你看到工具 metadata 最终如何进入系统提示词。

### 🧪 小练习：从测试反推类型设计

先读 `test_models_reject_unknown_fields`，再回到 [`messages.py`](../src/tau_agent/messages.py)
找 `extra="forbid"`。这就是"测试先告诉你边界，源码再告诉你实现"的读法。

### 🚦 理解关卡（不看代码能口头答出，再进第 3 章）

- [ ] 能说出 3 种消息类、各自的 `role`，以及"`AssistantMessage` 多出 `tool_calls`"
- [ ] 能解释 `extra="forbid"` 的作用，并记得你亲眼让它报过一次错
- [ ] 能说出所有事件都靠 `type` 字段区分，并报出 `AgentEvent` 里至少 6 个成员
- [ ] 能说出 `AgentTool.execute` 本质就是去调 `executor`，结果是 `AgentToolResult`

### ✅ 本章打卡

- [ ] 精读完 [`messages.py`](../src/tau_agent/messages.py) 并跑过第 2.1 的 REPL（看到过 `extra="forbid"` 报错）
- [ ] 精读完 [`events.py`](../src/tau_agent/events.py) 并用第③招列出过全部事件类型
- [ ] 精读完 [`tools.py`](../src/tau_agent/tools.py)，能说出 `AgentTool` 四个字段及 `execute` 的本质
- [ ] 跑过 `uv run pytest tests/test_agent_types.py tests/test_system_prompt.py -q`
- [ ] 上面"🚦 理解关卡"四项全部能口头答出
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

### 📖 精读 run_agent_loop（本章主角，务必逐行读）

先把整个函数打印出来，对照着读（工具箱第①招）：

```bash
uv run python -c "import inspect, tau_agent.loop as m; print(inspect.getsource(m.run_agent_loop))"
```

打开 [`loop.py`](../src/tau_agent/loop.py)，按这条路线走一遍，每一站都先自己找答案：

1. **函数签名**（`async def run_agent_loop`，约第 35 行）—— 它要哪些输入？注意 `messages` 是
   **调用方传进来的列表**，循环只往里 append，不自己创建。这就是"transcript 归调用方所有"。
2. **开场**：函数体第一句就 `yield AgentStartEvent()`。往下 `while max_turns ...`（约第 65 行）
   是主循环，每轮先 `yield TurnStartEvent(turn=turn)`（约第 70 行）。
3. **翻译表（最重要）**：`async for provider_event in provider.stream_response(...)`（约第 74 行）
   下面那一串 `if / elif isinstance(provider_event, ...)`（约第 81–100 行）。**这就是整个框架的
   心脏**：它把"provider 事件"逐一翻译成"agent 事件"。问题：
   - `ProviderTextDeltaEvent` 被翻成哪个 agent 事件？（→ `MessageDeltaEvent`）
   - 哪一行把模型说完的整句 assistant 消息**追加进 `messages`**？（提示：`ProviderResponseEndEvent`
     分支里的 `messages.append(assistant_message)`，约第 97 行）
4. **停还是继续**：`if not assistant_message.tool_calls:`（约第 118 行）—— 没有工具调用，本轮就准备
   收尾（也是本章这个无工具示例会走的路）。**第 4 章我们会专门盯这一行看它怎么决定再跑一轮。**

> 🔁 把第 3 步的"翻译表"和第 2 章 2.2 的事件清单对起来：你会发现 `ex1_loop.py` 打印出来的
> 事件顺序，就是这段 `if/elif` 一条条 yield 的结果。**代码、事件清单、运行输出，三者完全对上了。**

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

### 🧭 对照地图

**设计地图**：

- [`dev-notes/design/02-agent-loop.md`](../dev-notes/design/02-agent-loop.md) —— agent loop 的职责边界。
- [`dev-notes/architecture/phase-2-ai-provider-layer.md`](../dev-notes/architecture/phase-2-ai-provider-layer.md) ——
  provider 层为什么先统一成事件流。
- [`dev-notes/architecture/phase-3-agent-loop.md`](../dev-notes/architecture/phase-3-agent-loop.md) ——
  `run_agent_loop` 的第一版行为说明。

**测试地图**：

```bash
uv run pytest tests/test_tau_ai.py::test_fake_provider_replays_scripted_events \
              tests/test_agent_loop.py::test_agent_loop_streams_text_and_appends_assistant_message -q
```

这两个测试刚好对应本章的两半：`FakeProvider` 如何回放脚本，以及 `run_agent_loop` 如何把 provider
文本流翻译成 agent 事件并追加 assistant message。

### 🧪 小练习：把示例变成测试

把 [`ex1_loop.py`](ex1_loop.py) 的核心逻辑复制成一个临时测试：收集 `events`，断言
`[event.type for event in events]` 等于预期序列，再断言 `messages[-1].content == "Hello there!"`。
这就是 [`tests/test_agent_loop.py`](../tests/test_agent_loop.py) 第一条测试的结构。

### 🚦 理解关卡（不看代码能口头答出，再进第 4 章）

- [ ] 能说清 `messages` 是谁拥有的、循环对它做了什么（只 append，不创建）
- [ ] 能指出"翻译表"在 `run_agent_loop` 的哪一段，并举出一对"provider 事件 → agent 事件"的对应
- [ ] 能说出哪一行把 assistant 消息追加进了 transcript
- [ ] 能解释本例为什么只跑一轮就结束（`assistant_message.tool_calls` 为空）

### ✅ 本章打卡

- [ ] 跑通 [`ex1_loop.py`](ex1_loop.py)，输出的事件序列与预期一致
- [ ] 用第①招打印 `run_agent_loop` 源码，跟着"📖 精读"四步走了一遍
- [ ] 在 [`loop.py`](../src/tau_agent/loop.py) 的 `while` 处加 `print`，亲眼确认本例只跑了一轮（turn=1）
- [ ] 用 `python -m pdb` 单步进入循环，`pp event` 看清每个事件
- [ ] 改 delta 数量重跑，确认 `message_delta` 数量随之变化、`message_end` 仍只有一个
- [ ] 跑过本章"测试地图"里的两条精准测试
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

### 📖 精读代码（两个文件，分两步读）

**第一步：harness 怎么"拥有 transcript 并启动循环"** —— 打开 [`harness.py`](../src/tau_agent/harness.py)：

```bash
uv run python -c "import inspect, tau_agent.harness as m; print(inspect.getsource(m.AgentHarness.prompt)); print(inspect.getsource(m.AgentHarness._run))"
```

带着问题读：

1. `prompt()`（约第 175 行）一共做了哪几件事？（提示：`_ensure_not_running()` → 把
   `UserMessage` `append` 进 `self._messages` → 调 `_run()`）
2. `_run()`（约第 191 行）里，真正干活的是不是还是 `run_agent_loop`？harness 在它外面**多包了
   什么**？（提示：建 `signal`、把每个 event 先 `_notify` 给监听者再 `yield`）
3. 所以一句话：**harness = 状态（transcript + 队列 + 取消信号）；`run_agent_loop` = 纯逻辑。**
   这就是"可复用大脑"为什么能同时驱动 CLI / TUI / 你的脚本。

**第二步：工具到底在哪被执行、异常怎么被兜住** —— 打开 [`loop.py`](../src/tau_agent/loop.py)：

```bash
uv run python -c "import inspect, tau_agent.loop as m; print(inspect.getsource(m._execute_tool_calls)); print(inspect.getsource(m._execute_tool))"
```

带着问题读：

1. `_execute_tool_calls`（约第 188 行）：它如何按 `name` 找到对应的 `AgentTool`？找不到工具时
   返回什么？（→ 一条 `ok=False` 的"Unknown tool"结果）
2. `_execute_tool`（约第 215 行）里的 `try / except Exception`（约第 222 行）—— **这就是"工具是
   隔离边界"的实现**：工具里抛的任何异常，都被这里接住并变成 `ok=False` 的结构化结果，循环不崩。
3. 每条工具结果都会被 `append` 回 `messages` —— 这正是"把结果喂回去，再问模型"的那一步。

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

### 🧭 对照地图

**设计地图**：

- [`dev-notes/design/harness.md`](../dev-notes/design/harness.md) —— Harness 为什么是可复用大脑。
- [`dev-notes/architecture/phase-4-agent-harness.md`](../dev-notes/architecture/phase-4-agent-harness.md) ——
  `AgentHarness` 引入了哪些状态和入口。
- [`dev-notes/architecture/phase-3-agent-loop.md`](../dev-notes/architecture/phase-3-agent-loop.md) ——
  回看工具调用如何留在纯 loop 里。

**测试地图**：

```bash
uv run pytest tests/test_agent_loop.py::test_agent_loop_executes_tools_and_continues_until_no_tool_calls \
              tests/test_agent_loop.py::test_agent_loop_records_unknown_tool_as_failed_tool_result \
              tests/test_agent_harness.py::test_prompt_appends_user_message_and_assistant_response \
              tests/test_agent_harness.py::test_harness_rejects_overlapping_prompt_runs -q
```

这组测试覆盖四个关键点：工具调用会触发第二轮、未知工具不会让循环崩溃、`prompt()` 会追加用户消息、
harness 会拒绝并发 prompt。

### 🧪 小练习：读失败路径

先读 `test_agent_loop_records_unknown_tool_as_failed_tool_result`，再回到 `_execute_tool_calls` 找
"Unknown tool" 分支。很多框架理解难点都藏在失败路径里：成功路径说明它能跑，失败路径说明它的边界。

### 🚦 理解关卡（不看代码能口头答出，再进第 5 章）

- [ ] 能说清 `prompt()` 做的三件事，以及 `_run()` 在 `run_agent_loop` 外面多包了什么
- [ ] 能用一句话区分"harness 管什么、`run_agent_loop` 管什么"
- [ ] 能指出工具异常被兜住的确切位置（`_execute_tool` 的 `try/except`），并解释"隔离边界"
- [ ] 能说出一轮"工具调用 → 喂回结果 → 再问"对应 transcript 里多出来的那两条消息

### ✅ 本章打卡

- [ ] 跑通 [`ex2_tools.py`](ex2_tools.py)，最终 transcript 恰好 4 条
- [ ] 用第①招读过 `AgentHarness.prompt/_run` 与 `loop._execute_tool(_calls)` 源码
- [ ] 用 pdb 在 `add_executor` 处看到 `arguments == {'a': 2, 'b': 3}`
- [ ] 在 [`loop.py`](../src/tau_agent/loop.py) 的 `if not assistant_message.tool_calls:` 处加 `print`，理解为何会跑第二轮
- [ ] 在 `add_executor` 里 `raise` 一个异常，确认程序不崩、变成 `ok=False` 结果
- [ ] 读 [`harness.py`](../src/tau_agent/harness.py) 的 `prompt()`，能说清 harness 与 `run_agent_loop` 的分工
- [ ] 跑过本章"测试地图"里的四条精准测试
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

### 📖 精读 create_read_tool_definition（看"真实工具"怎么造出来）

打开 [`src/tau_coding/tools.py`](../src/tau_coding/tools.py)，把这个工厂函数打印出来读（工具箱第①招）：

```bash
uv run python -c "import inspect, tau_coding.tools as m; print(inspect.getsource(m.create_read_tool_definition))"
```

带着问题读（约第 117 行起）：

1. 它返回的是 `ToolDefinition`，里面的"真实工具三件套"是哪三样？
   （`prompt_snippet` 给模型的简介、`input_schema` 参数 schema、`executor` 真正干活的 async 函数）
2. 在 `executor` 内部，**校验失败时是 `return ok=False` 还是 `raise`？** 去看那几处
   `raise ToolInputError(...)`（如约第 149 行 `File not found`）—— 印证第 4 章学的"工具只管抛，
   兜底是循环的事"。
3. `ToolDefinition` 顶上的 `to_agent_tool()`（约第 80 行）：它把"带 prompt 元信息的富定义"**降级**成
   大脑层只认识的精简 `AgentTool`。这正是 `tau_coding`（应用层）和 `tau_agent`（大脑层）的接缝。

**▶️ 跑给自己看**：造一个真实工具，看它降级后的 `AgentTool` 长啥样：

```bash
uv run python -c "
from tau_coding.tools import create_read_tool
t = create_read_tool(cwd='.')
print('name       =', t.name)
print('input keys =', list(t.input_schema.get('properties', {})))
print('executor   =', t.executor.__name__ if hasattr(t.executor,'__name__') else type(t.executor))
"
```

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

### 🧭 对照地图

**设计地图**：

- [`dev-notes/design/03-tools.md`](../dev-notes/design/03-tools.md) —— 工具设计的完整背景。
- [`dev-notes/architecture/phase-5-coding-tools.md`](../dev-notes/architecture/phase-5-coding-tools.md) ——
  内置 `read/write/edit/bash` 工具为什么放在 `tau_coding`，而不是 `tau_agent`。
- [`dev-notes/architecture/phase-8-coding-session.md`](../dev-notes/architecture/phase-8-coding-session.md) ——
  真实编码 session 如何装配这些工具。

**测试地图**：

```bash
uv run pytest tests/test_coding_tools.py::test_read_tool_reads_file_with_offset_and_limit \
              tests/test_coding_tools.py::test_write_tool_creates_parent_directories \
              tests/test_coding_tools.py::test_edit_tool_rolls_back_when_any_edit_fails -q
```

重点读这些用例：

- `test_read_tool_reads_file_with_offset_and_limit`
- `test_write_tool_creates_parent_directories`
- `test_edit_tool_rolls_back_when_any_edit_fails`

它们比文档更明确地说明了真实工具的边界：读文件如何分页、写文件是否建目录、编辑失败是否回滚。
如果你想单独验证 bash 工具，再跑：

```bash
uv run pytest tests/test_coding_tools.py::test_bash_tool_captures_stdout_and_exit_code -q
```

`test_bash_tool_reports_timeout` 和 `test_bash_tool_cancellation_kills_shell_children` 适合作为进阶阅读，
用来理解进程清理边界。

### 🧪 小练习：给工具加一个新边界测试

不要先改实现。先在 [`tests/test_coding_tools.py`](../tests/test_coding_tools.py) 里写一个你关心的边界，
比如"读取目录路径应该失败"或"`edit` 的 old text 匹配多次应该拒绝"。跑红之后再去源码里找对应实现。
这就是 Tau 项目推荐的开发节奏：**行为先由测试钉住，再扩展功能**。

### 🚦 理解关卡（不看代码能口头答出，再进第 6 章）

- [ ] 能说出"真实工具三件套"是哪三样（`prompt_snippet` / `input_schema` / `executor`）
- [ ] 能解释 `to_agent_tool()` 在做什么、为什么需要这层"降级"（应用层 → 大脑层的接缝）
- [ ] 能指出 `read` 工具校验失败时是 `raise ToolInputError`，并说清"谁来兜底"
- [ ] 能说出 `AgentTool` 接口为何能同时统一 `read` 和 `bash` 这种完全不同的工具

### ✅ 本章打卡

- [ ] 跑通 [`ex3_realtool.py`](ex3_realtool.py)，看清 `ok` / `content` / `data` 三个字段
- [ ] 用第①招读过 `create_read_tool_definition`，并跑过"看 AgentTool 长啥样"的 REPL
- [ ] 在 [`tools.py`](../src/tau_coding/tools.py) 里读 `create_read_tool_definition` 与 `to_agent_tool`，说出"真实工具三件套"
- [ ] 把工具换成 `create_bash_tool`，成功跑出 `echo hello`
- [ ] （进阶，可选）用真实 `read` 工具 + `FakeProvider` 拼一个会读文件的迷你 Agent
- [ ] 跑过本章"测试地图"里的 read/write/edit 快速代表用例，并至少精读 3 个工具边界测试
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

### 📖 精读 print 模式主线（看三层如何拼起来）

`tau -p "..."` 的入口在 [`cli.py`](../src/tau_coding/cli.py)（`pyproject.toml` 里
`tau = "tau_coding.cli:app"`）。命令参数解析后会走到 `run_openai_print_mode` →
`run_print_mode`。把后者打印出来读（工具箱第①招）——**这是整本教程"三层拼装"的最终落点**：

```bash
uv run python -c "import inspect, tau_coding.cli as m; print(inspect.getsource(m.run_print_mode))"
```

带着问题逐段读 `run_print_mode`（约 [`cli.py`](../src/tau_coding/cli.py) 第 453 行）：

1. 第一步 `session = await CodingSession.load(CodingSessionConfig(provider=..., model=..., ...))` ——
   它构造了一个 `CodingSession`。问题：`CodingSession` 内部持有谁？
   （去 [`session.py`](../src/tau_coding/session.py) 看：文件第一行 docstring 就写着
   "built on AgentHarness"，构造里 `self._harness = AgentHarness(...)` —— **session 就是给
   harness 套了"会话落盘 + provider 配置 + 斜杠命令"的外壳**。）
2. 第二步 `renderer = create_event_renderer(output)` —— 按 `--output` 选一个渲染器。问题：渲染器
   要满足什么接口？（去 [`rendering/base.py`](../src/tau_coding/rendering/base.py) 看
   `EventRenderer` 这个 `Protocol`：只需要 `render(event)` 和 `finish()` 两个方法。）
3. **核心三行**（整本教程到这里闭环）：

   ```python
   async for event in session.prompt(prompt):
       renderer.render(event)
   return renderer.finish()
   ```

   把它和你在 `ex1_loop.py` / `ex2_tools.py` 里手写的 `async for event in harness.prompt(...)`
   摆在一起看 —— **形状一模一样**。CLI 没有任何魔法：它也只是"消费同一串事件"的又一个前端。

**▶️ 跑给自己看**（确认"多个渲染器、同一套事件契约"）：

```bash
uv run python -c "
import tau_coding.rendering as r
from tau_coding.rendering import PrintOutputMode
for mode in PrintOutputMode:
    print(mode.value, '->', type(r.create_event_renderer(mode)).__name__)
"
```

你会看到 text / json / transcript 各对应一个**只实现了 `render`+`finish`** 的小类 —— 它们彼此
独立、互不知道对方，全靠"事件契约"解耦。这就是第 0 章那句"**事件就是契约**"的真身。

会话是 append-only 的 JSONL，存在 `~/.tau/sessions/` 下，可以 resume、可以分支——
对应源码 [`src/tau_agent/session/`](../src/tau_agent/session/) 与
[`src/tau_coding/session_manager.py`](../src/tau_coding/session_manager.py)。

### 🧭 对照地图

**设计地图**：

- [`dev-notes/architecture/phase-6-print-mode-cli.md`](../dev-notes/architecture/phase-6-print-mode-cli.md) ——
  print-mode CLI 为什么先于 TUI。
- [`dev-notes/architecture/phase-8-coding-session.md`](../dev-notes/architecture/phase-8-coding-session.md) ——
  `CodingSession` 如何把 harness、工具、会话落盘包起来。
- [`dev-notes/architecture/phase-11-print-event-rendering.md`](../dev-notes/architecture/phase-11-print-event-rendering.md) ——
  text/json/transcript 渲染器如何共享事件契约。
- [`dev-notes/architecture/phase-12-textual-tui.md`](../dev-notes/architecture/phase-12-textual-tui.md) ——
  TUI 如何保持在 adapter 边界之后。

**测试地图**：

```bash
uv run pytest tests/test_cli.py::test_run_print_mode_prints_final_assistant_text \
              tests/test_cli.py::test_run_print_mode_can_emit_json_events \
              tests/test_rendering.py \
              tests/test_coding_session.py::test_prompt_persists_user_assistant_and_leaf_entries -q
```

这组测试覆盖应用层主线：print mode 如何消费事件、JSON/transcript/text 如何渲染、
一次 prompt 后 session 如何落盘。完整的 [`tests/test_cli.py`](../tests/test_cli.py) 更适合作为进阶索引，
不用在第一次学习 CLI 时整文件运行。
如果你只想看 TUI 边界，不要一上来读巨大的 `test_tui_app.py`；先读：

```bash
uv run pytest tests/test_tui_adapter.py -q
```

[`tests/test_tui_adapter.py`](../tests/test_tui_adapter.py) 更适合作为 TUI 入门，因为它验证的是
"agent 事件 → UI state" 的适配层，而不是完整 Textual 交互。

### 🧪 小练习：换一个 renderer 看契约不变

读 [`tests/test_rendering.py`](../tests/test_rendering.py)，找出 text/json/transcript 三种 renderer
分别断言了什么。然后回到 `run_print_mode` 的核心三行，确认 CLI 并不关心 renderer 具体怎么显示，
它只负责把同一串 `AgentEvent` 交给 `render(event)`。

### 🚦 理解关卡（不看代码能口头答出，再进第 7 章）

- [ ] 能说出 `CodingSession` 内部持有 `AgentHarness`，以及它额外负责什么（落盘 / 配置 / 命令）
- [ ] 能背出 print 模式那"核心三行"，并说清它和 `ex1/ex2` 手写循环是同一形状
- [ ] 能说出 `EventRenderer` 协议只要求哪两个方法
- [ ] 能用"事件就是契约"解释：为什么 text/json/transcript 三个渲染器能互不相关地共存

### ✅ 本章打卡

- [ ] 用第①招读过 `run_print_mode`，跟着"📖 精读"三步走了一遍
- [ ] 跑过"列出所有渲染器"的 REPL，看到 text/json/transcript 各对应一个独立小类
- [ ] 能指出"构造 provider → 构造 session(harness) → `async for event` → renderer"这条主线
- [ ] 跑过本章"测试地图"里的 CLI/rendering/session 精准测试
- [ ] （可选）`/login` 配置一个真实 provider，用 `tau -p "..."` 真跑一次
- [ ] 完成后回到总览，把 **第 6 章** 那一行勾上

---

## 第 7 章 · 用 dev-notes + tests 反查源码

学到这里，你已经能顺着主线读 Tau。接下来换一种更像真实开发的读法：**从一个功能问题出发，
用 `dev-notes` 找设计意图，用 `tests` 找行为边界，最后回到 `src/` 看实现。**

不要把 [`dev-notes/`](../dev-notes/) 当小说从头读到尾。它更像地图和考古记录：

- `design/`：稳定的高层设计。
- `architecture/phase-*.md`：某个阶段具体加了什么、为什么加、怎么验证。
- `adr/`：当时做过取舍的关键架构决策。

也不要把 [`tests/`](../tests/) 只当"检查绿不绿"。在 Tau 里，测试更像**可执行规格**：
测试名告诉你行为边界，fixture 告诉你最小构造方式，assert 告诉你什么不能变。

### 🧭 反查路线

遇到一个功能，按下面四步走：

1. **先搜测试名**：`rg -n "branch|compact|thinking|render|tool" tests`
2. **跑最小测试**：`uv run pytest tests/某个文件.py::某个测试 -q`
3. **读对应 dev-notes**：找这个功能首次出现在哪个 phase。
4. **回到源码**：带着测试里的输入/输出去读实现。

例如你想理解 compaction：

```bash
rg -n "compact|compaction" tests dev-notes
uv run pytest tests/test_context_window.py tests/test_coding_session.py::test_session_compact_persists_summary_and_rebuilds_context -q
```

然后读：

- [`dev-notes/architecture/phase-22-compaction-foundation.md`](../dev-notes/architecture/phase-22-compaction-foundation.md)
- [`src/tau_coding/context_window.py`](../src/tau_coding/context_window.py)
- [`src/tau_coding/session.py`](../src/tau_coding/session.py)

### 📚 功能索引

| 你想理解的功能 | 先读 dev-notes | 再跑 tests |
| --- | --- | --- |
| 三层架构 | [`design/01-architecture.md`](../dev-notes/design/01-architecture.md) | `tests/test_agent_types.py` |
| 核心事件和消息 | [`phase-1-core-types-and-events.md`](../dev-notes/architecture/phase-1-core-types-and-events.md) | `tests/test_agent_types.py` |
| provider 流式适配 | [`phase-2-ai-provider-layer.md`](../dev-notes/architecture/phase-2-ai-provider-layer.md) | `tests/test_tau_ai.py` |
| agent loop | [`phase-3-agent-loop.md`](../dev-notes/architecture/phase-3-agent-loop.md) | `tests/test_agent_loop.py` |
| AgentHarness | [`phase-4-agent-harness.md`](../dev-notes/architecture/phase-4-agent-harness.md) | `tests/test_agent_harness.py` |
| 内置编码工具 | [`phase-5-coding-tools.md`](../dev-notes/architecture/phase-5-coding-tools.md) | `tests/test_coding_tools.py` |
| CLI print mode | [`phase-6-print-mode-cli.md`](../dev-notes/architecture/phase-6-print-mode-cli.md) | `tests/test_cli.py`, `tests/test_rendering.py` |
| session tree | [`phase-7-session-tree.md`](../dev-notes/architecture/phase-7-session-tree.md) | `tests/test_session.py` |
| CodingSession | [`phase-8-coding-session.md`](../dev-notes/architecture/phase-8-coding-session.md) | `tests/test_coding_session.py` |
| skills / prompts | [`phase-9-skills-prompts.md`](../dev-notes/architecture/phase-9-skills-prompts.md) | `tests/test_skills.py`, `tests/test_prompt_templates.py` |
| system prompt | [`phase-10-system-prompt.md`](../dev-notes/architecture/phase-10-system-prompt.md) | `tests/test_system_prompt.py` |
| TUI adapter | [`phase-12-textual-tui.md`](../dev-notes/architecture/phase-12-textual-tui.md) | `tests/test_tui_adapter.py` |
| slash commands | [`phase-15-slash-command-registry.md`](../dev-notes/architecture/phase-15-slash-command-registry.md) | `tests/test_commands.py` |
| autocomplete | [`phase-17-tui-autocomplete.md`](../dev-notes/architecture/phase-17-tui-autocomplete.md) | `tests/test_tui_autocomplete.py` |
| provider config | [`phase-18-provider-config-foundation.md`](../dev-notes/architecture/phase-18-provider-config-foundation.md) | `tests/test_provider_config.py` |
| context discovery | [`phase-19-context-discovery.md`](../dev-notes/architecture/phase-19-context-discovery.md) | `tests/test_context.py` |
| context accounting | [`phase-20-1-context-accounting.md`](../dev-notes/architecture/phase-20-1-context-accounting.md) | `tests/test_context_window.py` |
| thinking controls | [`phase-20-2-thinking-controls.md`](../dev-notes/architecture/phase-20-2-thinking-controls.md) | `tests/test_thinking.py` |
| compaction | [`phase-22-compaction-foundation.md`](../dev-notes/architecture/phase-22-compaction-foundation.md) | `tests/test_context_window.py`, `tests/test_coding_session.py` |
| session branching | [`phase-24-session-tree-branching.md`](../dev-notes/architecture/phase-24-session-tree-branching.md) | `tests/test_session.py`, `tests/test_coding_session.py` |

### 🧪 小练习：任选一个功能做完整反查

从上表挑一个你感兴趣的功能，比如 autocomplete：

```bash
rg -n "completion|autocomplete" tests/test_tui_autocomplete.py src/tau_coding/tui
uv run pytest tests/test_tui_autocomplete.py -q
```

然后按顺序读：

1. [`dev-notes/architecture/phase-17-tui-autocomplete.md`](../dev-notes/architecture/phase-17-tui-autocomplete.md)
2. [`tests/test_tui_autocomplete.py`](../tests/test_tui_autocomplete.py)
3. [`src/tau_coding/tui/autocomplete.py`](../src/tau_coding/tui/autocomplete.py)

最后回答一个问题：**测试里哪个断言最能代表这个功能的边界？** 能答出来，说明你已经会用
`dev-notes + tests + src` 三件套读 Tau 了。

### ✅ 本章打卡

- [ ] 能说出 `dev-notes/design`、`dev-notes/architecture`、`dev-notes/adr` 的区别
- [ ] 能说出为什么测试是"可执行规格"，而不只是绿条
- [ ] 按"反查路线"完整研究过一个功能
- [ ] 能从测试名、assert、dev-notes 三个角度解释这个功能的边界
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
- [ ] `dev-notes`、`tests`、`src` 三者分别回答什么问题？
- [ ] 如果你要理解一个新功能，如何用 `rg`、pytest 精准测试、phase note、源码组成一条反查路线？
- [ ] 全部答对后回到总览，把 **第 8 章** 那一行勾上 🎉

> 全部能答上来，你就掌握了任何"编码 Agent"框架的通用骨架。Tau 只是把它写得足够小、足够好读。

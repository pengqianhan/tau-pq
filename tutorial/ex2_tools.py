"""教程示例 2：带"工具调用"的 Agent，用 AgentHarness 管理状态。

运行：
    uv run python tutorial/ex2_tools.py

学习目标：
    1. 一个工具 = 一份 schema + 一个 async executor，返回结构化结果。
    2. 看清 Agent 的核心循环："模型要求调用工具 -> 执行 -> 把结果喂回去 -> 再问模型"。
    3. AgentHarness 帮你拥有 transcript（对话记录），并提供 prompt() 入口。
"""

import anyio
from collections.abc import Mapping

from tau_agent import (
    AgentHarness,
    AgentHarnessConfig,
    AgentTool,
    AgentToolResult,
    AssistantMessage,
    ToolCall,
)
from tau_agent.types import JSONValue
from tau_ai import FakeProvider, ProviderResponseEndEvent, ProviderResponseStartEvent


# 1) 定义一个工具的执行体。注意：参数是"provider-neutral 的 JSON 字典"，
#    返回值是结构化的 AgentToolResult。tool_call_id 先留空，循环会自动填正确的 id。
async def add_executor(
    arguments: Mapping[str, JSONValue], signal=None
) -> AgentToolResult:
    # === 建议断点 A：breakpoint() 看模型真正传进来的 arguments 长什么样 ===
    a = int(arguments["a"])
    b = int(arguments["b"])
    return AgentToolResult(tool_call_id="", name="add", ok=True, content=str(a + b))


# 2) 把执行体包成一个 AgentTool：名字 + 描述 + JSON schema + executor。
add_tool = AgentTool(
    name="add",
    description="Add two integers a and b.",
    input_schema={
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
    },
    executor=add_executor,
)


async def main() -> None:
    # 用 FakeProvider 脚本两次模型回复：
    #   第 1 次：模型不说话，要求调用 add(2, 3)  -> 触发工具执行
    #   第 2 次：模型拿到工具结果后，用自然语言回答
    provider = FakeProvider(
        [
            [
                ProviderResponseStartEvent(model="fake"),
                ProviderResponseEndEvent(
                    message=AssistantMessage(
                        content="",
                        tool_calls=[
                            ToolCall(id="call_1", name="add", arguments={"a": 2, "b": 3})
                        ],
                    )
                ),
            ],
            [
                ProviderResponseStartEvent(model="fake"),
                ProviderResponseEndEvent(
                    message=AssistantMessage(content="The sum is 5.")
                ),
            ],
        ]
    )

    # Harness = 可复用的"大脑"：它拥有 transcript，并把执行委托给 run_agent_loop。
    harness = AgentHarness(
        AgentHarnessConfig(
            provider=provider,
            model="fake",
            system="You are a calculator agent.",
            tools=[add_tool],
        )
    )

    # === 建议断点 B：单步进入 harness.prompt -> _run -> run_agent_loop，
    #     观察 while 循环里 turn 从 1 涨到 2 的过程。 ===
    print("--- agent events ---")
    async for event in harness.prompt("What is 2 + 3?"):
        print(event.type)

    print("\n--- final transcript（注意 4 条：user / assistant(tool_call) / tool / assistant）---")
    for m in harness.messages:
        print(" ", m)


if __name__ == "__main__":
    anyio.run(main)

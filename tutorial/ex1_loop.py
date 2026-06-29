"""教程示例 1：最小的 Agent 循环（不需要任何 API key）。

运行：
    uv run python tutorial/ex1_loop.py

学习目标：
    1. 看清 `run_agent_loop` 把"模型流"翻译成一串"Agent 事件"。
    2. 看清 messages（对话记录）是调用方拥有的、被循环原地追加的列表。
    3. 用 FakeProvider 取代真实模型，让行为完全确定、可复现。
"""

import anyio

from tau_agent.loop import run_agent_loop
from tau_agent.messages import AssistantMessage, UserMessage
from tau_ai import (
    FakeProvider,
    ProviderResponseEndEvent,
    ProviderResponseStartEvent,
    ProviderTextDeltaEvent,
)


async def main() -> None:
    # messages 是"调用方拥有"的对话记录。循环会往里 append，但不创建它。
    messages = [UserMessage(content="Say hello")]

    # 这是我们假装"模型最终说出来的整句话"。
    assistant = AssistantMessage(content="Hello there!")

    # FakeProvider 回放一段脚本好的事件流，替代真实模型的网络流式输出。
    # 一个 stream = 模型的一次完整回复。这里只给了一个 stream（一次回复）。
    provider = FakeProvider(
        [
            [
                ProviderResponseStartEvent(model="fake"),
                ProviderTextDeltaEvent(delta="Hello "),  # 流式 token 片段 1
                ProviderTextDeltaEvent(delta="there!"),  # 流式 token 片段 2
                ProviderResponseEndEvent(message=assistant, finish_reason="stop"),
            ]
        ]
    )

    # === 建议在这里打第一个断点：breakpoint() ===
    # 然后用调试器单步进入 run_agent_loop，观察 provider 事件如何被翻译成 agent 事件。
    print("--- agent events ---")
    async for event in run_agent_loop(
        provider=provider,
        model="fake",
        system="You are Tau.",
        messages=messages,
        tools=[],  # 这个例子没有工具
    ):
        # 每个事件都是一个带 .type 字段的 pydantic 模型，前端就是消费这些事件。
        print(f"{event.type:16} | {event!r}"[:100])

    # 循环结束后，messages 里多了一条 assistant 消息——证明"循环原地追加了记录"。
    print("\n--- final transcript ---")
    for m in messages:
        print(" ", m)


if __name__ == "__main__":
    anyio.run(main)

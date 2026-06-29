"""教程示例 3：直接使用 Tau 内置的"真实"编码工具（read），不经过模型。

运行：
    uv run python tutorial/ex3_realtool.py

学习目标：
    1. tau_coding 层提供了真实的 read/write/edit/bash 工具，它们就是普通 AgentTool。
    2. 工具可以脱离模型、脱离循环，单独 await 执行——这是调试工具的最佳方式。
    3. 观察结构化结果：ok / content / data / error。
"""

import anyio

from tau_coding.tools import create_read_tool


async def main() -> None:
    # 创建一个绑定到当前目录的 read 工具。cwd 决定工具能看到哪些文件。
    read = create_read_tool(cwd=".")
    print("tool name:", read.name)
    print("description:", read.description[:80], "...")

    # === 建议断点：breakpoint() 然后单步进入 read.execute，看它如何读文件、
    #     如何做截断（truncate）、如何打包成 AgentToolResult。 ===
    result = await read.execute({"path": "pyproject.toml"})

    print("\nok:", result.ok)
    print("结构化 data 字段:", result.data)
    print("\n--- content 前 5 行 ---")
    print("\n".join(result.content.splitlines()[:5]))

    # 重点：工具本身遇到坏输入会"抛异常"，而不是返回 ok=False。
    # 真正把异常转成 ok=False 结果的是 agent 循环里的 _execute_tool（工具是隔离边界）。
    # 见 src/tau_agent/loop.py 的 _execute_tool：try/except Exception -> AgentToolResult(ok=False)。
    print("\n--- 读不存在的文件：工具直接抛异常 ---")
    try:
        await read.execute({"path": "does-not-exist.txt"})
    except Exception as exc:  # noqa: BLE001 - 仅用于教学演示
        print(f"工具抛出: {type(exc).__name__}: {exc}")
        print("（在完整循环里，这个异常会被 _execute_tool 捕获并变成 ok=False 的工具结果）")


if __name__ == "__main__":
    anyio.run(main)

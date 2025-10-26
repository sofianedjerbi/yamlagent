"""Example usage of YamlAgentConfigParser.

This demonstrates how to:
1. Parse a complete configuration from a single file with imports
2. Access tools, agents, and workflows
3. Query specific configuration items
"""

from pathlib import Path

from yamlagent_core import YamlAgentConfigParser


def main():
    # Parse the main configuration file (which imports tools.yaml and agents.yaml)
    parser = YamlAgentConfigParser()
    config = parser.parse_file("examples/config.yaml")

    print("=" * 60)
    print("YamlAgent Configuration Loaded Successfully!")
    print("=" * 60)
    print(f"\nConfiguration Version: {config.version}")

    # Display tools
    if config.tools:
        print(f"\n📦 Tools Configuration:")
        print(f"   Commands: {len(config.tools.commands)}")
        for cmd in config.tools.commands:
            print(f"      - {cmd.id}: {cmd.bin}")
        print(f"   MCP Servers: {len(config.tools.mcp)}")
        for mcp in config.tools.mcp:
            print(f"      - {mcp.id}: {mcp.transport}")

    # Display agents
    if config.agents:
        print(f"\n🤖 Agents Configuration:")
        print(f"   Total Agents: {len(config.agents.agents)}")
        for agent in config.agents.agents:
            print(f"\n   Agent: {agent.id}")
            print(f"      Role: {agent.role}")
            print(f"      Model: {agent.model}")
            if agent.tools:
                print(f"      Tools Mode: {agent.tools.mode.value}")
                print(f"      Allowed Commands: {agent.tools.commands}")
                print(f"      Allowed MCP: {agent.tools.mcp}")
            if agent.limits:
                print(f"      Runtime Limit: {agent.limits.runtime}")
                print(f"      Iteration Limit: {agent.limits.iterations}")

    # Display workflows
    if config.workflows:
        print(f"\n🔄 Workflows Configuration:")
        print(f"   Total Tasks: {len(config.workflows.tasks)}")
        for task in config.workflows.tasks:
            print(f"\n   Task: {task.id}")
            print(f"      Description: {task.description}")
            print(f"      Working Dir: {task.working_dir}")
            print(f"      Steps: {len(task.steps)}")
            for i, step in enumerate(task.steps, 1):
                print(f"         {i}. Use agent '{step.agent.use}'")

    # Query specific items
    print("\n" + "=" * 60)
    print("Querying Specific Configuration Items:")
    print("=" * 60)

    if config.tools:
        git_cmd = config.tools.get_command("git")
        if git_cmd:
            print(f"\n✓ Git command found: {git_cmd.bin}")
            print(f"  Allowed args: {git_cmd.args_allow}")
            print(f"  Timeout: {git_cmd.timeout}")

    if config.agents:
        fe_agent = config.agents.get_agent("fe-impl")
        if fe_agent:
            print(f"\n✓ Frontend agent found: {fe_agent.role}")
            print(f"  Model: {fe_agent.model}")
            print(f"  Can use 'git' command: {fe_agent.is_command_allowed('git')}")
            print(f"  Can use 'fs' MCP: {fe_agent.is_mcp_allowed('fs')}")

    if config.workflows:
        impl_task = config.workflows.get_task("implement-feature")
        if impl_task:
            print(f"\n✓ Implementation task found: {impl_task.description}")
            print(f"  Number of steps: {len(impl_task.steps)}")
            print(f"  Agents involved:")
            for step in impl_task.steps:
                print(f"    - {step.agent.use}")

    print("\n" + "=" * 60)
    print("Configuration loaded and validated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    # Make sure we're in the right directory
    import os
    os.chdir(Path(__file__).parent.parent)
    main()

"""
Graph command for CAI cli.

This module provides commands for visualizing the agent interaction graph.
It allows users to display a simple directed graph of the conversation history,
showing the sequence of user and agent interactions, including tool calls.
"""
from typing import List, Optional
from rich.console import Console  # pylint: disable=import-error
from rich.panel import Panel

from cai.repl.commands.base import Command, register_command

import os
import importlib.util

console = Console()


def find_agent_name_by_instructions(target_instructions: str, agents_dir: str) -> Optional[str]:
    """
    Search all Python files in the agents directory for an agent whose 'instructions'
    attribute matches the given target_instructions (ignoring leading/trailing whitespace).
    Returns the agent's 'name' attribute if found, otherwise None.

    Args:
        target_instructions (str): The instructions string to match.
        agents_dir (str): The directory containing agent files.

    Returns:
        Optional[str]: The agent name if found, else None.
    """
    for filename in os.listdir(agents_dir):
        if not filename.endswith(".py") or filename.startswith("__"):
            continue
        filepath = os.path.join(agents_dir, filename)
        try:
            spec = importlib.util.spec_from_file_location("agent_mod", filepath)
            agent_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(agent_mod)
            for attr_name in dir(agent_mod):
                attr = getattr(agent_mod, attr_name)
                if hasattr(attr, "instructions"):
                    agent_instructions = getattr(attr, "instructions", None)
                    if agent_instructions and agent_instructions.strip() == target_instructions.strip():
                        agent_name = getattr(attr, "name", None)
                        if agent_name:
                            return agent_name
        except Exception:
            continue
    return None


class GraphCommand(Command):
    """
    Command for visualizing the agent interaction graph.

    This command displays a directed graph of the conversation history,
    showing the sequence of user and agent messages, and highlighting
    tool calls made by the agent.
    """

    def __init__(self):
        """Initialize the graph command."""
        super().__init__(
            name="/graph",
            description="Visualize the agent interaction graph",
            aliases=["/g"]
        )

    def handle(self, args: Optional[List[str]] = None) -> bool:
        """
        Handle the /graph command.

        Args:
            args: Optional list of command arguments

        Returns:
            bool: True if the command was handled successfully, False otherwise.
        """
        return self.handle_graph_show()

    def handle_graph_show(self) -> bool:
        """Handle /graph show command"""
        from cai.sdk.agents.models.openai_chatcompletions import message_history
        if not message_history:
            console.print("[yellow]No conversation graph available.[/yellow]")
            return True

        try:
            agents_dir = os.path.join(os.path.dirname(__file__), "../../agents")
            agents_dir = os.path.abspath(agents_dir)

            import networkx as nx

            G = nx.DiGraph()
            last_agent_name = None
            prev_node_idx = None  # Track the last node actually added (not system)

            for idx, msg in enumerate(message_history):
                role = msg.get("role", "unknown")
                # If the message is from the system, update last_agent_name but do not add a node
                if role == "system":
                    system_msg = msg.get("content", "").strip()
                    agent_name = find_agent_name_by_instructions(system_msg, agents_dir)
                    if agent_name:
                        last_agent_name = agent_name
                    continue
                label = role
                extra_info = ""
                if role == "assistant":
                    if last_agent_name:
                        label = last_agent_name
                    else:
                        label = "assistant"
                    if msg.get("tool_calls"):
                        tool_call = msg["tool_calls"][0]
                        if tool_call.get("function"):
                            func_name = tool_call["function"].get("name", "")
                            func_args = tool_call["function"].get("arguments", "")
                            extra_info = f"\n[cyan]Tool:[/cyan] [bold]{func_name}[/bold]\n[cyan]Args:[/cyan] {func_args}"
                elif role == "user":
                    user_content = msg.get("content", "")
                    if user_content:
                        extra_info = f"\n{user_content}"
                    label = role
                else:
                    label = role
                G.add_node(idx, role=label, extra_info=extra_info)
                if prev_node_idx is not None:
                    G.add_edge(prev_node_idx, idx)
                prev_node_idx = idx

            def ascii_graph(G):
                """
                Render the conversation graph as a sequence of panels with arrows.

                Args:
                    G (networkx.DiGraph): The conversation graph.

                Returns:
                    List: List of rich Panel objects and arrow strings.
                """
                lines = []
                node_list = list(G.nodes(data=True))
                for i, (idx, data) in enumerate(node_list):
                    role = data.get("role", "unknown")
                    extra_info = data.get("extra_info", "")
                    role_fmt = f"[bold][blue]{role[:1].upper()}{role[1:]}[/blue][/bold]"
                    panel_content = f"{role_fmt}"
                    if extra_info:
                        panel_content += f"{extra_info}"
                    panel = Panel(
                        panel_content,
                        expand=False,
                        border_style="cyan"
                    )
                    lines.append(panel)
                    if i < len(node_list) - 1:
                        lines.append("[cyan]   │\n   │\n   ▼[/cyan]")
                return lines

            console.print("\n[bold]Conversation Graph:[/bold]")
            console.print("------------------")
            if len(G.nodes) == 0:
                console.print("[yellow]No messages to display in graph.[/yellow]")
            else:
                for item in ascii_graph(G):
                    console.print(item)
            console.print()
            return True
        except Exception as e:  # pylint: disable=broad-except
            console.print(f"[red]Error displaying graph: {e}[/red]")
            return False


# Register the command
register_command(GraphCommand())

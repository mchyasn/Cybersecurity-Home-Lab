"""
Agent "command" for CAI CLI abstraction

Provides commands for managing and switching between agents.
"""

# Standard library imports
import inspect
import os
import sys

from typing import List, Optional

# Third-party imports
from rich.console import Console  # pylint: disable=import-error
from rich.markdown import Markdown  # pylint: disable=import-error
from rich.table import Table  # pylint: disable=import-error

# Local imports
from cai.agents import get_available_agents, get_agent_module
from cai.repl.commands.base import Command, register_command
from cai.sdk.agents import Agent
from cai.util import visualize_agent_graph

console = Console()


class AgentCommand(Command):
    """Command for managing and switching between agents."""

    def __init__(self):
        """Initialize the agent command."""
        # Initialize with basic parameters
        super().__init__(
            name="/agent",
            description="Manage and switch between agents",
            aliases=["/a"]
        )

        # Add subcommands manually
        self._subcommands = {
            "list": "List available agents",
            "select": "Select an agent by name or number",
            "info": "Show information about an agent",
            "multi": "Enable multi-agent mode"
        }

    def _get_model_display(self, agent_name: str, agent: Agent) -> str:
        """Get the display string for an agent's model.

        Args:
            agent_name: Name of the agent
            agent: Agent instance

        Returns:
            String to display for the agent's model
        """
        # For code agent, always show the model
        if agent_name == "code":
            return agent.model

        # For other agents, check if CTF_MODEL is set
        ctf_model = os.getenv('CTF_MODEL')
        if ctf_model and agent.model == ctf_model:
            # Don't show default model for CTF_MODEL in table
            # but show "Default CTF Model" in info
            return ""

        # Show the model from environment variable if available
        env_var_name = f"CAI_{agent_name.upper()}_MODEL"
        model_env = os.getenv(env_var_name)
        if model_env:
            return model_env

        return agent.model

    def _get_model_display_for_info(
            self, agent_name: str, agent: Agent) -> str:
        """Get the display string for an agent's model in the info view.

        Args:
            agent_name: Name of the agent
            agent: Agent instance

        Returns:
            String to display for the agent's model in the info view
        """
        # For code agent, always show the model
        if agent_name == "code":
            return agent.model

        # For other agents, check if CTF_MODEL is set
        ctf_model = os.getenv('CTF_MODEL')
        if ctf_model and agent.model == ctf_model:
            # Show "Default CTF Model" in info
            return "Default CTF Model"

        # Show the model from environment variable if available
        env_var_name = f"CAI_{agent_name.upper()}_MODEL"
        model_env = os.getenv(env_var_name)
        if model_env:
            return model_env

        return agent.model

    def get_subcommands(self) -> List[str]:
        """Get list of subcommand names.

        Returns:
            List of subcommand names
        """
        return list(self._subcommands.keys())

    def get_subcommand_description(self, subcommand: str) -> str:
        """Get description for a subcommand.

        Args:
            subcommand: Name of the subcommand

        Returns:
            Description of the subcommand
        """
        return self._subcommands.get(subcommand, "")

    def handle(self, args: Optional[List[str]] = None) -> bool:
        """Handle the agent command.

        Args:
            args: Optional list of command arguments

        Returns:
            True if the command was handled successfully, False otherwise
        """
        if not args:
            return self.handle_list(args)

        subcommand = args[0]
        if subcommand in self._subcommands:
            handler = getattr(self, f"handle_{subcommand}", None)
            if handler:
                return handler(args[1:] if len(args) > 1 else None)

        # If not a subcommand, try to select an agent by name
        return self.handle_select(args)

    def handle_list(self, args: Optional[List[str]] = None) -> bool:  # pylint: disable=unused-argument # noqa: E501
        """Handle /agent list command.

        Args:
            args: Optional list of command arguments (not used)

        Returns:
            True if the command was handled successfully
        """
        table = Table(title="Available Agents")
        table.add_column("#", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Key", style="magenta")
        table.add_column("Module", style="green")
        table.add_column("Description", style="green")

        # Retrieve all registered agents
        agents_to_display = get_available_agents()

        for idx, (agent_key, agent) in enumerate(agents_to_display.items(), start=1):
            # Human-friendly name (falls back to the dict key)
            display_name = getattr(agent, "name", agent_key)

            # Use provided description, otherwise derive from instructions
            description = getattr(agent, "description", "") or ""
            if not description and hasattr(agent, "instructions"):
                instr = agent.instructions
                description = instr(context_variables={}) if callable(instr) else instr
            if isinstance(description, str):
                description = " ".join(description.split())
                if len(description) > 50:
                    description = description[:47] + "..."

            # Module where this agent lives
            module_name = get_agent_module(agent_key)

            # Add a row with all collected info
            table.add_row(
                str(idx),
                display_name,
                agent_key,
                module_name,
                description
            )

        console.print(table)
        return True

    def handle_select(self, args: Optional[List[str]] = None) -> bool:  # pylint: disable=too-many-branches,line-too-long # noqa: E501
        """Handle /agent select command.

        Args:
            args: Optional list of command arguments

        Returns:
            True if the command was handled successfully, False otherwise
        """
        if not args:
            console.print("[red]Error: No agent specified[/red]")
            console.print("Usage: /agent select <agent_key|number>")
            return False

        agent_id = args[0]

        agents_to_display = get_available_agents()
        agent_list = list(agents_to_display.items())  

        # Check if agent_id is a number
        if agent_id.isdigit():
            index = int(agent_id)
            if 1 <= index <= len(agent_list):
                # Get the agent tuple from the list
                selected_agent_key, selected_agent = agent_list[index - 1]
                agent_name = getattr(selected_agent, "name", selected_agent_key)
                agent = selected_agent
            else:
                console.print(f"[red]Error: Invalid agent number: {agent_id}[/red]")
                return False
        else:
            # Treat as agent key
            selected_agent_key = None
            for key, agent_obj in agents_to_display.items():
                if key == agent_id:
                    agent = agent_obj
                    selected_agent_key = key
                    agent_name = getattr(agent_obj, "name", key)
                    break
            else:
                console.print(f"[red]Error: Unknown agent key: {agent_id}[/red]")
                return False

        # Set the agent key in environment variable (not the agent name)
        os.environ["CAI_AGENT_TYPE"] = selected_agent_key
        
        console.print(
                    f"[green]Switched to agent: {agent_name}[/green]", end="")           
        visualize_agent_graph(agent)
        return True

    def handle_info(self, args: Optional[List[str]] = None) -> bool:
        """Handle /agent info command.

        Args:
            args: Optional list of command arguments

        Returns:
            True if the command was handled successfully, False otherwise
        """
        if not args:
            console.print("[red]Error: No agent specified[/red]")
            console.print("Usage: /agent info <agent_key|number>")
            return False

        agent_id = args[0]

        # Get available agents
        agents_to_display = get_available_agents()

        # Resolve agent_id to an agent key (by index or name)
        if agent_id.isdigit():
            idx = int(agent_id)
            if not (1 <= idx <= len(agents_to_display)):
                console.print(f"[red]Error: Invalid agent number: {agent_id}[/red]")
                return False
            agent_key = list(agents_to_display.keys())[idx - 1]
        else:
            agent_key = None
            for key, ag in agents_to_display.items():
                if key == agent_id or getattr(ag, "name", "").lower() == agent_id.lower():
                    agent_key = key
                    break
            if agent_key is None:
                console.print(f"[red]Error: Unknown agent key: {agent_id}[/red]")
                return False

        agent = agents_to_display[agent_key]

       # Display agent information
        instructions = agent.instructions
        if callable(instructions):
            instructions = instructions()
        # Prepare agent properties
        name = agent.name or agent_key
        description = getattr(agent, "description", None) or "N/A"
        clean_description = " ".join(line.strip() for line in description.splitlines())
        functions = getattr(agent, "functions", [])
        parallel = getattr(agent, "parallel_tool_calls", False)
        handoff_desc = getattr(agent, "handoff_description", None) or "N/A"
        handoffs = getattr(agent, "handoffs", [])
        tools = getattr(agent, "tools", [])
        guardrails_in = getattr(agent, "input_guardrails", [])
        guardrails_out = getattr(agent, "output_guardrails", [])
        output_type = getattr(agent, "output_type", None) or "N/A"
        hooks = getattr(agent, "hooks", []) or []

        # Build markdown content for agent info
        markdown_content = f"""
# Agent Info: {name}

| Property               | Value                         |
|------------------------|-------------------------------|
| Key                    | {agent_key}                   |
| Name                   | {name}                        |
| Description            | {clean_description}           |
| Functions              | {len(functions)}              |
| Parallel Tool Calls    | {"Yes" if parallel else "No"} |
| Handoff Description    | {handoff_desc}                |
| Handoffs               | {len(handoffs)}               |
| Tools                  | {len(tools)}                  |
| Input Guardrails       | {len(guardrails_in)}          |
| Output Guardrails      | {len(guardrails_out)}         |
| Output Type            | {output_type}                 |
| Hooks                  | {len(hooks)}                  |

## Instructions
{instructions}

"""
        console.print(Markdown(markdown_content))
        return True


# Register the command
register_command(AgentCommand())

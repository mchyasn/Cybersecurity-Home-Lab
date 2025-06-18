"""
Parallel command for CAI CLI abstraction.

Provides commands for managing parallel agent configurations.
Different agents can be configured with specific models and prompts,
which will then be executed in parallel through the CLI.
"""

# Standard library imports
import os
from typing import List, Optional, Dict

# Third-party imports
from rich.console import Console
from rich.table import Table

# Local imports
from cai.repl.commands.base import Command, register_command
from cai.agents import get_available_agents

console = Console()

# Store configured parallel runs (made global so CLI can access it)
PARALLEL_CONFIGS = []


class ParallelConfig:
    """Configuration for a parallel agent run."""
    
    def __init__(self, agent_name, model=None, prompt=None):
        """Initialize a parallel agent configuration.
        
        Args:
            agent_name: Name of the agent to use
            model: Optional model to use (overrides default)
            prompt: Optional specific prompt to use
        """
        self.agent_name = agent_name
        self.model = model
        self.prompt = prompt
        
    def __str__(self):
        """String representation of the configuration."""
        model_str = f", model: {self.model}" if self.model else ""
        prompt_str = f", prompt: '{self.prompt[:20]}...'" if self.prompt and len(self.prompt) > 20 else \
                    f", prompt: '{self.prompt}'" if self.prompt else ""
        return f"Agent: {self.agent_name}{model_str}{prompt_str}"


class ParallelCommand(Command):
    """Command for managing parallel agent configurations."""
    
    def __init__(self):
        """Initialize the parallel command."""
        super().__init__(
            name="/parallel",
            description="Configure multiple agents to run in parallel with different settings",
            aliases=["/par", "/p"]
        )
        
        # Add subcommands for configuration management
        self.add_subcommand("add", "Add a new agent to the parallel config", self.handle_add)
        self.add_subcommand("list", "List configured parallel agents", self.handle_list)
        self.add_subcommand("clear", "Clear all configured parallel agents", self.handle_clear)
        self.add_subcommand("remove", "Remove a specific parallel agent by index", self.handle_remove)
        
    def handle_add(self, args: Optional[List[str]] = None) -> bool:
        """Handle the add subcommand.
        
        Args:
            args: Command arguments [agent_name] [--model MODEL] [--prompt PROMPT]
            
        Returns:
            True if successful
        """
        if not args:
            console.print("[red]Error: Agent name required[/red]")
            console.print("Usage: /parallel add <agent_name> [--model MODEL] [--prompt PROMPT]")
            return False
            
        agent_name = args[0]
        
        # Check if agent exists
        available_agents = get_available_agents()
        if agent_name not in available_agents:
            console.print(f"[red]Error: Unknown agent '{agent_name}'[/red]")
            console.print("Available agents:")
            for idx, name in enumerate(available_agents.keys(), 1):
                console.print(f"  {idx}. {name}")
            return False
            
        # Parse optional arguments
        model = None
        prompt = None
        i = 1
        while i < len(args):
            if args[i] == "--model" and i + 1 < len(args):
                model = args[i + 1]
                i += 2
            elif args[i] == "--prompt" and i + 1 < len(args):
                # Capture all remaining arguments as the prompt
                prompt = " ".join(args[i + 1:])
                break  # Stop parsing after --prompt since we take everything after it
            else:
                i += 1
                
        # Add configuration
        config = ParallelConfig(agent_name, model, prompt)
        PARALLEL_CONFIGS.append(config)
        
        console.print(f"[green]Added parallel configuration:[/green] {config}")
        console.print("[cyan]Use your next query to run all parallel agents[/cyan]")
        return True
        
    def handle_list(self, args: Optional[List[str]] = None) -> bool:
        """Handle the list subcommand.
        
        Args:
            args: Command arguments (unused)
            
        Returns:
            True if successful
        """
        if not PARALLEL_CONFIGS:
            console.print("[yellow]No parallel configurations defined[/yellow]")
            console.print("Use '/parallel add <agent_name>' to add a configuration")
            return True
            
        table = Table(title="Configured Parallel Agents")
        table.add_column("#", style="dim")
        table.add_column("Agent", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Custom Prompt", style="yellow")
        
        for idx, config in enumerate(PARALLEL_CONFIGS, 1):
            prompt_display = (config.prompt[:30] + "...") if config.prompt and len(config.prompt) > 30 else config.prompt or ""
            table.add_row(
                str(idx),
                config.agent_name,
                config.model or "Default",
                prompt_display
            )
            
        console.print(table)
        console.print("[cyan]Your next query will run all these agents in parallel[/cyan]")
        return True
        
    def handle_clear(self, args: Optional[List[str]] = None) -> bool:
        """Handle the clear subcommand.
        
        Args:
            args: Command arguments (unused)
            
        Returns:
            True if successful
        """
        count = len(PARALLEL_CONFIGS)
        PARALLEL_CONFIGS.clear()
        
        console.print(f"[green]Cleared {count} parallel configurations[/green]")
        return True
        
    def handle_remove(self, args: Optional[List[str]] = None) -> bool:
        """Handle the remove subcommand.
        
        Args:
            args: Command arguments [index]
            
        Returns:
            True if successful
        """
        if not args:
            console.print("[red]Error: Index required[/red]")
            console.print("Usage: /parallel remove <index>")
            return False
            
        try:
            idx = int(args[0])
            if idx < 1 or idx > len(PARALLEL_CONFIGS):
                raise ValueError("Index out of range")
                
            removed = PARALLEL_CONFIGS.pop(idx - 1)
            console.print(f"[green]Removed configuration:[/green] {removed}")
            return True
        except ValueError:
            console.print(f"[red]Error: Invalid index '{args[0]}'[/red]")
            return False

# Register the command
register_command(ParallelCommand()) 
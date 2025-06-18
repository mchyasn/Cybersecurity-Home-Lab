"""
Load command for CAI REPL.

This module provides commands for loading a jsonl into 
the context of the current session.
"""
import os
import signal
from typing import (
    List,
    Optional
)
from rich.console import Console  # pylint: disable=import-error
from cai.repl.commands.base import Command, register_command
from cai.sdk.agents.models.openai_chatcompletions import message_history
from cai.sdk.agents.run_to_jsonl import get_token_stats, load_history_from_jsonl

console = Console()


class LoadCommand(Command):
    """Command for loading a jsonl into the context of the current session."""

    def __init__(self):
        """Initialize the load command."""
        super().__init__(
            name="/load",
            description="Load a jsonl into the context of the current session (uses logs/last if no file specified)",
            aliases=["/l"]
        )

    def handle(self, args: Optional[List[str]] = None) -> bool:
        """Handle the load command.

        Args:
            args: Optional list of command arguments

        Returns:
            True if the command was handled successfully, False otherwise
        """
        return self.handle_load_command(args)

    def handle_load_command(self, args: List[str]) -> bool:
        """Load a jsonl into the context of the current session.

        Args:
            args: List containing the jsonl file path (optional)

        Returns:
            bool: True if the jsonl was loaded successfully
        """
        # Use logs/last if no arguments provided
        if not args:
            jsonl_file = "logs/last"
        else:
            jsonl_file = args[0]

        try:
            # Try to load the jsonl file
            try:
                # fetch messages from JSONL file
                messages = load_history_from_jsonl(jsonl_file)
                console.print(f"[green]Jsonl file {jsonl_file} loaded[/green]")
            except BaseException:  # pylint: disable=broad-exception-caught
                # If killing the process group fails, try killing just the
                # process
                console.print(f"[red]Error: Failed to load jsonl file {jsonl_file}[/red]")
                return False

            # add them to message_history
            for message in messages:
                message_history.append(message)
            return True

        except Exception as e:  # pylint: disable=broad-exception-caught
            console.print(f"[red]Error loading jsonl file: {str(e)}[/red]")
            return False


# Register the command
register_command(LoadCommand())

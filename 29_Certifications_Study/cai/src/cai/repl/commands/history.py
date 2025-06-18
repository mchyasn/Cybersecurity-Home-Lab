"""
History command for CAI REPL.
This module provides commands for displaying conversation history.
"""
import json
from typing import Any, Dict, List, Optional

from rich.console import Console  # pylint: disable=import-error
from rich.table import Table  # pylint: disable=import-error
from rich.text import Text  # pylint: disable=import-error

from cai.repl.commands.base import Command, register_command

console = Console()


class HistoryCommand(Command):
    """Command for displaying conversation history."""

    def __init__(self):
        """Initialize the history command."""
        super().__init__(
            name="/history",
            description="Display the conversation history",
            aliases=["/his"]
        )
        
    def handle(self, args: Optional[List[str]] = None, 
               messages: Optional[List[Dict]] = None) -> bool:
        """Handle the history command.
        
        Args:
            args: Optional list of command arguments
            messages: Optional list of conversation messages
            
        Returns:
            True if the command was handled successfully, False otherwise
        """
        # Currently, the history command doesn't take any arguments
        return self.handle_no_args()

    def handle_no_args(self) -> bool:
        """Handle the command when no arguments are provided.

        Returns:
            True if the command was handled successfully, False otherwise
        """
        # Access messages directly from openai_chatcompletions.py
        try:
            from cai.sdk.agents.models.openai_chatcompletions import message_history  # pylint: disable=import-outside-toplevel  # noqa: E501
        except ImportError:
            console.print(
                "[red]Error: Could not access conversation history[/red]")
            return False

        if not message_history:
            console.print("[yellow]No conversation history available[/yellow]")
            return True

        # Create a table for the history
        table = Table(
            title="Conversation History",
            show_header=True,
            header_style="bold yellow"
        )
        table.add_column("#", style="dim")
        table.add_column("Role", style="cyan")
        table.add_column("Content", style="green")

        # Add messages to the table
        for idx, msg in enumerate(message_history, 1):
            try:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                tool_calls = msg.get("tool_calls", None)

                # Create formatted content based on message type
                formatted_content = self._format_message_content(
                    content, tool_calls)

                # Color the role based on type
                if role == "user":
                    role_style = "cyan"
                elif role == "assistant":
                    role_style = "yellow"
                else:
                    role_style = "red"

                # Add a newline between each role for better readability
                if idx > 1:
                    table.add_row("", "", "")

                table.add_row(
                    str(idx),
                    f"[{role_style}]{role}[/{role_style}]",
                    formatted_content
                )
            except Exception as e:
                # Log error but continue with next message
                console.print(f"[red]Error displaying message {idx}: {e}[/red]")
                continue

        console.print(table)
        return True
        
    def _format_message_content(
        self, content: Any, tool_calls: List[Dict[str, Any]]
    ) -> str:
        """Format message content for display, handling both text and tool calls.
        
        Args:
            content: Text content of the message
            tool_calls: List of tool calls if present
            
        Returns:
            Formatted string representation of the message content
        """
        if tool_calls:
            # Format tool calls into a readable string
            result = []
            for tc in tool_calls:
                func_details = tc.get("function", {})
                func_name = func_details.get("name", "unknown_function")
                
                # Format arguments (pretty-print JSON if possible)
                args_str = func_details.get("arguments", "{}")
                try:
                    # Parse and re-format JSON for better readability
                    args_dict = json.loads(args_str)
                    args_formatted = json.dumps(args_dict, indent=2)
                    # Limit to first 100 chars for display
                    if len(args_formatted) > 100:
                        args_formatted = args_formatted[:97] + "..."
                except (json.JSONDecodeError, TypeError):
                    # If not valid JSON, use as is
                    args_formatted = args_str
                    if len(args_formatted) > 100:
                        args_formatted = args_formatted[:97] + "..."
                        
                result.append(f"Function: [bold blue]{func_name}[/bold blue]")
                result.append(f"Args: {args_formatted}")
            
            return "\n".join(result)
        elif content:
            # Regular text content (truncate if too long)
            if len(content) > 100:
                return content[:97] + "..."
            return content
        else:
            # No content or tool calls (empty message)
            return "[dim italic]Empty message[/dim italic]"


# Register the command
register_command(HistoryCommand())

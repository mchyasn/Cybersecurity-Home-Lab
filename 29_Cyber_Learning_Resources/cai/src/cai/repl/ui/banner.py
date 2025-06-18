"""
Module for displaying the CAI banner and welcome message.
"""
# Standard library imports
import os
import glob
import logging
import sys
from configparser import ConfigParser

# Third-party imports
import requests  # pylint: disable=import-error
from rich.console import Console  # pylint: disable=import-error
from rich.panel import Panel  # pylint: disable=import-error
from rich.table import Table  # pylint: disable=import-error

# For reading TOML files
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        # If tomli is not available, we'll handle it in the get_version function
        pass


def get_version():
    """Get the CAI version from pyproject.toml."""
    version = "unknown"
    try:
        # Determine which TOML parser to use
        if sys.version_info >= (3, 11):
            toml_parser = tomllib
        else:
            try:
                import tomli as toml_parser
            except ImportError:
                logging.warning("Could not import tomli. Falling back to manual parsing.")
                # Simple manual parsing for version only
                with open('pyproject.toml', 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('version = '):
                            # Extract version from line like 'version = "0.4.0"'
                            version = line.split('=')[1].strip().strip('"\'')
                            return version
                return version
                
        # Use proper TOML parser if available
        with open('pyproject.toml', 'rb') as f:
            config = toml_parser.load(f)
        version = config.get('project', {}).get('version', 'unknown')
    except Exception as e:  # pylint: disable=broad-except
        logging.warning("Could not read version from pyproject.toml: %s", e)
    return version


def get_supported_models_count():
    """Get the count of supported models (with function calling)."""
    try:
        # Fetch model data from LiteLLM repository
        response = requests.get(
            "https://raw.githubusercontent.com/BerriAI/litellm/main/"
            "model_prices_and_context_window.json",
            timeout=2
        )

        if response.status_code == 200:
            model_data = response.json()

            # Count models with function calling support
            function_calling_models = sum(
                1 for model_info in model_data.values()
                if model_info.get("supports_function_calling", False)
            )

            # Try to get Ollama models count
            try:
                ollama_api_base = os.getenv(
                    "OLLAMA_API_BASE",
                    "http://host.docker.internal:8000/v1"
                )
                ollama_response = requests.get(
                    f"{ollama_api_base.replace('/v1', '')}/api/tags",
                    timeout=1
                )

                if ollama_response.status_code == 200:
                    ollama_data = ollama_response.json()
                    ollama_models = len(
                        ollama_data.get(
                            'models', ollama_data.get('items', [])
                        )
                    )
                    return function_calling_models + ollama_models
            except Exception:  # pylint: disable=broad-except
                logging.debug("Could not fetch Ollama models")
                # Continue without Ollama models

            return function_calling_models
    except Exception:  # pylint: disable=broad-except
        logging.warning("Could not fetch model data from LiteLLM")

    # Default count if we can't fetch the data
    return "many"


def count_tools():
    """Count the number of tools in the CAI framework."""
    try:
        # Count Python files in the tools directory
        tool_files = glob.glob("cai/tools/**/*.py", recursive=True)
        # Exclude __init__.py and other non-tool files
        tool_files = [
            f for f in tool_files
            if not f.endswith("__init__.py") and not f.endswith("__pycache__")
        ]
        return len(tool_files)
    except Exception:  # pylint: disable=broad-except
        logging.warning("Could not count tools")
        return "50+"


def count_agents():
    """Count the number of agents in the CAI framework."""
    try:
        # Count Python files in the agents directory
        agent_files = glob.glob("cai/agents/**/*.py", recursive=True)
        # Exclude __init__.py and other non-agent files
        agent_files = [
            f for f in agent_files
            if not f.endswith("__init__.py") and not f.endswith("__pycache__")
        ]
        return len(agent_files)
    except Exception:  # pylint: disable=broad-except
        logging.warning("Could not count agents")
        return "20+"


def count_ctf_memories():
    """Count the number of CTF memories in the CAI framework."""
    # This is a placeholder - adjust the actual counting logic based on your
    # framework structure
    return "100+"


def display_banner(console: Console):
    """
    Display a stylized CAI banner with Alias Robotics corporate colors.

    Args:
        console: Rich console for output
    """
    version = get_version()

    # Original banner with Alias Robotics colors (blue and white)
    # Use noqa to ignore line length for the ASCII art
    banner = f"""
[bold blue]                CCCCCCCCCCCCC      ++++++++   ++++++++      IIIIIIIIII
[bold blue]             CCC::::::::::::C  ++++++++++       ++++++++++  I::::::::I
[bold blue]           CC:::::::::::::::C ++++++++++         ++++++++++ I::::::::I
[bold blue]          C:::::CCCCCCCC::::C +++++++++    ++     +++++++++ II::::::II
[bold blue]         C:::::C       CCCCCC +++++++     +++++     +++++++   I::::I
[bold blue]        C:::::C                +++++     +++++++     +++++    I::::I
[bold blue]        C:::::C                ++++                   ++++    I::::I
[bold blue]        C:::::C                 ++                     ++     I::::I
[bold blue]        C:::::C                  +   +++++++++++++++   +      I::::I
[bold blue]        C:::::C                    +++++++++++++++++++        I::::I
[bold blue]        C:::::C                     +++++++++++++++++         I::::I
[bold blue]         C:::::C       CCCCCC        +++++++++++++++          I::::I
[bold blue]          C:::::CCCCCCCC::::C         +++++++++++++         II::::::II
[bold blue]           CC:::::::::::::::C           +++++++++           I::::::::I
[bold blue]             CCC::::::::::::C             +++++             I::::::::I
[bold blue]                CCCCCCCCCCCCC               ++              IIIIIIIIII

[bold blue]                              Cybersecurity AI (CAI), v{version}[/bold blue]
[white]                                  Bug bounty-ready AI[/white]
    """

    console.print(banner, end="")

    # # Create a table showcasing CAI framework capabilities
    # #
    # # reconsider in the future if necessary
    # display_framework_capabilities(console)


def display_framework_capabilities(console: Console):
    """
    Display a table showcasing CAI framework capabilities in Metasploit style.

    Args:
        console: Rich console for output
    """
    # Create the main table
    table = Table(
        title="",
        box=None,
        show_header=False,
        show_edge=False,
        padding=(0, 2)
    )

    table.add_column("Category", style="bold cyan")
    table.add_column("Count", style="bold yellow")
    table.add_column("Description", style="white")

    # Add rows for different capabilities
    table.add_row(
        "AI Models",
        str(get_supported_models_count()),
        "Supported AI models including GPT-4, Claude, Llama"
    )

    # table.add_row(
    #     "Tools",
    #     str(count_tools()),
    #     "Cybersecurity tools for reconnaissance and scanning"
    # )

    table.add_row(
        "Agents",
        str(count_agents()),
        "Specialized AI agents for different cybersecurity tasks"
    )

    # Add the table to a panel for better visual separation
    capabilities_panel = Panel(
        table,
        title="[bold blue]CAI Features[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

    console.print(capabilities_panel)


def display_welcome_tips(console: Console):
    """
    Display welcome message with tips for using the REPL.

    Args:
        console: Rich console for output
    """
    console.print(Panel(
        "[white]• Use arrow keys ↑↓ to navigate command history[/white]\n"
        "[white]• Press Tab for command completion[/white]\n"
        "[white]• Type /help for available commands[/white]\n"
        "[white]• Type /help aliases for command shortcuts[/white]\n"
        "[white]• Press Ctrl+L to clear the screen[/white]\n"
        "[white]• Press Esc+Enter to add a new line (multiline input)[/white]\n"
        "[white]• Press Ctrl+C to exit[/white]",
        title="Quick Tips",
        border_style="blue"
    ))


def display_quick_guide(console: Console):
    """Display the quick guide."""
    # Display help panel instead
    from rich.panel import Panel
    from rich.text import Text
    from rich.columns import Columns
    from rich.console import Group  # <-- Fix: import Group

    help_text = Text.assemble(
        ("CAI Command Reference", "bold cyan underline"), "\n\n",
        ("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "dim"), "\n",
        ("WORKSPACE", "bold yellow"), "\n",
        ("  CAI>/ws set [NAME]", "green"), " - Set current workspace directory\n\n",
        ("AGENT MANAGEMENT", "bold yellow"), "\n",
        ("  CAI>/agent [NAME]", "green"), " - Switch to specific agent by name\n",
        ("  CAI>/agent 1 2 3", "green"), " - Switch to agent by position number\n",
        ("  CAI>/agent", "green"), " - Display list of all available agents\n\n",
        ("MODEL SELECTION", "bold yellow"), "\n",
        ("  CAI>/model [NAME]", "green"), " - Change to a different model by name\n",
        ("  CAI>/model 1", "green"), " - Change model by position number\n",
        ("  CAI>/model", "green"), " - Show all available models\n\n",
        ("INPUT & EXECUTION", "bold yellow"), "\n",
        ("  ESC + ENTER", "green"), " - Enter multi-line input mode\n",
        ("  CAI>/shell or CAI> $", "green"), " - Run system shell commands\n",
        ("  CAI>hi, cybersecurity AI", "green"), " - Any text without commands will be sent as a prompt\n",
        ("  CAI>/help", "green"), " - Display complete command reference\n",
        ("  CAI>/flush or CAI> /clear", "green"), " - Clear the conversation history\n\n",
        ("UTILITY COMMANDS", "bold yellow"), "\n",
        ("  CAI>/mcp", "green"), " - Load additional tools with MCP server to an agent\n",
        ("  CAI>/virt", "green"), " - Show all available virtualized environments\n",
        ("  CAI>/flush", "green"), " - Flush context/message list\n",
        ("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "dim"), "\n",
    )
    
    # Get current environment variable values
    current_model = os.getenv('CAI_MODEL', "alias0")
    current_agent_type = os.getenv('CAI_AGENT_TYPE', "one_tool_agent")
    
    config_text = Text.assemble(
        ("Quick Start Configuration", "bold cyan underline"), "\n\n",
        ("1. Configure .env file with your settings", "yellow"), "\n",
        ("2. Select an agent: ", "yellow"), f"by default: CAI_AGENT_TYPE={current_agent_type}\n",
        ("3. Select a model: ", "yellow"), f"by default: CAI_MODEL={current_model}\n\n",

        ("CAI collects pseudonymized data to improve our research.\n"
         "Your privacy is protected in compliance with GDPR.\n"
         "Continue to start, or press Ctrl-C to exit.", "yellow"), "\n\n",
        
        ("Basic Usage:", "bold yellow"), "\n",
        ("  1. CAI> /model", "green"), " - View all available models first\n",
        ("  2. CAI> /agent", "green"), " - View all available agents first\n",
        ("  3. CAI> /model deepseek/deepseek-chat", "green"), " - Then select your preferred model\n",
        ("  4. CAI> /agent 16", "green"), " - Then select your preferred agent\n",
        ("  5. CAI> Scan 192.168.1.1", "green"), " - Example prompt for target scan\n\n",
        ("  /help", "green"), " - Display complete command reference\n\n",
        ("Common Environment Variables:", "bold yellow"), "\n",
        ("  CAI_MODEL", "green"), f" - Model to use (default: {current_model})\n",
        ("  CAI_AGENT_TYPE", "green"), f" - Agent type (default: {current_agent_type})\n",
        ("  CAI_DEBUG", "green"), f" - Debug level (default: {os.getenv('CAI_DEBUG', '1')})\n",
        ("  CAI_MAX_TURNS", "green"), f" - Max conversation turns (default: {os.getenv('CAI_MAX_TURNS', 'inf')})\n",
        ("  CAI_TRACING", "green"), f" - Enable tracing (default: {os.getenv('CAI_TRACING', 'true')})\n",
    )
    
    # Create additional tips panels
    ollama_tip = Panel(
        "To use Ollama models, configure OLLAMA_API_BASE\n"
        "before startup.\n\n"
        "Default: host.docker.internal:8000/v1",
        title="[bold yellow]Ollama Configuration[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
        title_align="center"
    )
    
    context_tip = Panel(
        Text.assemble(
            "For optimal cybersecurity AI performance, use\n", 
            ("alias0", "bold green"), 
            " - specifically designed for cybersecurity\n"
            "tasks with superior domain knowledge.\n\n",
            ("alias0", "bold green"), 
            " outperforms general-purpose models in:\n",
            "• Vulnerability assessment\n",
            "• Penetration testing and bug bounty\n",
            "• Security analysis\n",
            "• Threat detection\n\n",
            "Learn more about ", 
            ("alias0", "bold green"), 
            " and its privacy-first approach:\n",
            ("https://news.aliasrobotics.com/alias0-a-privacy-first-cybersecurity-ai/", "blue underline")
        ),
        title="[bold yellow]Cybersecurity Model Tip[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
        title_align="center"
    )
    
    # Combine tips into a group
    # tips_group = Group(ollama_tip, context_tip)
    tips_group = Group(context_tip)
    
    # Create a three-column panel layout
    console.print(Panel(
        Columns(
            [help_text, config_text, tips_group],
            column_first=True,
            expand=True,
            align="center"
        ),
        title="[bold]CAI Quick Guide[/bold]",
        border_style="blue",
        padding=(1, 2),
        title_align="center"
    ), end="")

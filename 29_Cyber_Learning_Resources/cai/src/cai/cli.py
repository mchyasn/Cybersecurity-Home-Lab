"""
This module provides a CLI interface for testing and
interacting with CAI agents.

Environment Variables
---------------------
    Required:
        N/A

    Optional:
        CTF_NAME: Name of the CTF challenge to
            run (e.g. "picoctf_static_flag")
        CTF_CHALLENGE: Specific challenge name
            within the CTF to test
        CTF_SUBNET: Network subnet for the CTF
            container (default: "192.168.3.0/24")
        CTF_IP: IP address for the CTF
            container (default: "192.168.3.100")
        CTF_INSIDE: Whether to conquer the CTF from
            within container (default: "true")

        CAI_MODEL: Model to use for agents
            (default: "alias0")
        CAI_DEBUG: Set debug output level (default: "1")
            - 0: Only tool outputs
            - 1: Verbose debug output
            - 2: CLI debug output
        CAI_BRIEF: Enable/disable brief output mode (default: "false")
        CAI_MAX_TURNS: Maximum number of turns for
            agent interactions (default: "inf")
        CAI_TRACING: Enable/disable OpenTelemetry tracing
            (default: "true"). When enabled, traces execution
            flow and agent interactions for debugging and analysis.
        CAI_AGENT_TYPE: Specify the agents to use it could take
            the value of (default: "one_tool_agent"). Use "/agent"
            command in CLI to list all available agents.
        CAI_STATE: Enable/disable stateful mode (default: "false").
            When enabled, the agent will use a state agent to keep
            track of the state of the network and the flags found.
        CAI_MEMORY: Enable/disable memory mode (default: "false")
            - episodic: use episodic memory
            - semantic: use semantic memory
            - all: use both episodic and semantic memorys
        CAI_MEMORY_ONLINE: Enable/disable online memory mode
            (default: "false")
        CAI_MEMORY_OFFLINE: Enable/disable offline memory
            (default: "false")
        CAI_ENV_CONTEXT: Add enviroment context, dirs and
            current env available (default: "true")
        CAI_MEMORY_ONLINE_INTERVAL: Number of turns between
            online memory updates (default: "5")
        CAI_PRICE_LIMIT: Price limit for the conversation in dollars
            (default: "1")
        CAI_SUPPORT_MODEL: Model to use for the support agent
            (default: "o3-mini")
        CAI_SUPPORT_INTERVAL: Number of turns between support agent
            executions (default: "5")
        CAI_STREAM: Enable/disable streaming output in rich panel
            (default: "true")
        CAI_TELEMETRY: Enable/disable telemetry (default: "true")
        CAI_PARALLEL: Number of parallel agent instances to run
            (default: "1"). When set to values greater than 1,
            executes multiple instances of the same agent in
            parallel and displays all results.

    Extensions (only applicable if the right extension is installed):

        "report"
            CAI_REPORT: Enable/disable reporter mode. Possible values:
                - ctf (default): do a report from a ctf resolution
                - nis2: do a report for nis2
                - pentesting: do a report from a pentesting

Usage Examples:

    # Run against a CTF
    CTF_NAME="kiddoctf" CTF_CHALLENGE="02 linux ii" \
        CAI_AGENT_TYPE="one_tool_agent" CAI_MODEL="alias0" \
        CAI_TRACING="false" cai

    # Run a harder CTF
    CTF_NAME="hackableii" CAI_AGENT_TYPE="redteam_agent" \
        CTF_INSIDE="False" CAI_MODEL="alias0" \
        CAI_TRACING="false" cai

    # Run without a target in human-in-the-loop mode, generating a report
    CAI_TRACING=False CAI_REPORT=pentesting CAI_MODEL="alias0" \
        cai

    # Run with online episodic memory
    #   registers memory every 5 turns:
    #   limits the cost to 5 dollars
    CTF_NAME="hackableII" CAI_MEMORY="episodic" \
        CAI_MODEL="alias0" CAI_MEMORY_ONLINE="True" \
        CTF_INSIDE="False" CTF_HINTS="False"  \
        CAI_PRICE_LIMIT="5" cai

    # Run with custom long_term_memory interval
    # Executes memory long_term_memory every 3 turns:
    CTF_NAME="hackableII" CAI_MEMORY="episodic" \
        CAI_MODEL="alias0" CAI_MEMORY_ONLINE_INTERVAL="3" \
        CAI_MEMORY_ONLINE="False" CTF_INSIDE="False" \
        CTF_HINTS="False" cai
        
    # Run with parallel agents (3 instances)
    CTF_NAME="hackableII" CAI_AGENT_TYPE="redteam_agent" \
        CAI_MODEL="alias0" CAI_PARALLEL="3" cai
"""

# Load environment variables from .env file FIRST, before any imports
import os
from dotenv import load_dotenv
load_dotenv()

import time
import asyncio
from rich.console import Console
from rich.panel import Panel

# OpenAI imports
from openai import AsyncOpenAI

# CAI SDK imports
from cai.sdk.agents import OpenAIChatCompletionsModel, Agent, Runner, set_tracing_disabled
from cai.sdk.agents.run_to_jsonl import get_session_recorder
from cai.sdk.agents.items import ToolCallOutputItem
from cai.sdk.agents.stream_events import RunItemStreamEvent
from cai.sdk.agents.models.openai_chatcompletions import (
    message_history,
    add_to_message_history,
)

# CAI utility imports
from cai.util import (
    fix_litellm_transcription_annotations, 
    color, 
    start_idle_timer, 
    stop_idle_timer, 
    start_active_timer, 
    stop_active_timer,
    setup_ctf,
    check_flag,
)

# CAI REPL imports
from cai.repl.commands import FuzzyCommandCompleter, handle_command as commands_handle_command
from cai.repl.ui.keybindings import create_key_bindings
from cai.repl.ui.logging import setup_session_logging
from cai.repl.ui.banner import display_banner, display_quick_guide
from cai.repl.ui.prompt import get_user_input
from cai.repl.ui.toolbar import get_toolbar_with_refresh

# CAI agents and metrics imports
from cai.agents import get_agent_by_name
from cai.internal.components.metrics import process_metrics

# Add import for parallel configs at the top of the file
from cai.repl.commands.parallel import PARALLEL_CONFIGS, ParallelConfig
from cai import is_pentestperf_available
ctf_global = None
messages_ctf = ""
ctf_init=1
previous_ctf_name = os.getenv('CTF_NAME', None)
if is_pentestperf_available() and os.getenv('CTF_NAME', None):
    ctf, messages_ctf = setup_ctf()
    ctf_global = ctf
    ctf_init=0

# NOTE: This is needed when using LiteLLM Proxy Server
#
# external_client = AsyncOpenAI(
#     base_url = os.getenv('LITELLM_BASE_URL', 'http://localhost:4000'),
#     api_key=os.getenv('LITELLM_API_KEY', 'key'))
#
# set_default_openai_client(external_client)

# Global variables for timing tracking
global START_TIME
START_TIME = time.time() 

set_tracing_disabled(True)

# llm_model=os.getenv('LLM_MODEL', 'gpt-4o-mini')
# # llm_model=os.getenv('LLM_MODEL', 'claude-3-7')
llm_model=os.getenv('LLM_MODEL', 'alias0')


# For Qwen models, we need to skip system instructions as they're not supported
instructions = None if "qwen" in llm_model.lower() else "You are a helpful assistant"

# Create OpenAI client with fallback API key to prevent initialization errors
# The actual API key should be set in environment variables or .env file
api_key = os.getenv('OPENAI_API_KEY', 'sk-placeholder-key-for-local-models')

agent = Agent(
    name="Assistant", 
    instructions=instructions,
    model=OpenAIChatCompletionsModel(
        model=llm_model,
        openai_client=AsyncOpenAI(api_key=api_key)  # original OpenAI servers
        # openai_client = external_client  # LiteLLM Proxy Server
    )
)

def update_agent_models_recursively(agent, new_model, visited=None):
    """
    Recursively update the model for an agent and all agents in its handoffs.
    
    Args:
        agent: The agent to update
        new_model: The new model string to set
        visited: Set of agent names already visited to prevent infinite loops
    """
    if visited is None:
        visited = set()
    
    # Avoid infinite loops by tracking visited agents
    if agent.name in visited:
        return
    visited.add(agent.name)
    
    # Update the main agent's model
    if hasattr(agent, 'model') and hasattr(agent.model, 'model'):
        agent.model.model = new_model
    
    # Update models for all handoff agents
    if hasattr(agent, 'handoffs'):
        for handoff_item in agent.handoffs:
            # Handle both direct Agent references and Handoff objects
            if hasattr(handoff_item, 'on_invoke_handoff'):
                # This is a Handoff object
                # For handoffs created with the handoff() function, the agent is stored
                # in the closure of the on_invoke_handoff function
                # We can try to extract it from the function's closure
                try:
                    # Get the closure variables of the handoff function
                    if hasattr(handoff_item.on_invoke_handoff, '__closure__') and handoff_item.on_invoke_handoff.__closure__:
                        for cell in handoff_item.on_invoke_handoff.__closure__:
                            if hasattr(cell.cell_contents, 'model') and hasattr(cell.cell_contents, 'name'):
                                # This looks like an agent
                                handoff_agent = cell.cell_contents
                                update_agent_models_recursively(
                                    handoff_agent, new_model, visited
                                )
                                break
                except Exception:
                    # If we can't extract the agent from closure, skip it
                    pass
            elif hasattr(handoff_item, 'model'):
                # This is a direct Agent reference
                update_agent_models_recursively(
                    handoff_item, new_model, visited
                )


def run_cai_cli(starting_agent, context_variables=None, max_turns=float('inf'), force_until_flag=False):
    """
    Run a simple interactive CLI loop for CAI.

    Args:
        starting_agent: The initial agent to use for the conversation
        context_variables: Optional dictionary of context variables to initialize the session
        max_turns: Maximum number of interaction turns before terminating (default: infinity)

    Returns:
        None
    """
    ACTIVE_TIME = 0  # TODO: review this variable

    agent = starting_agent
    turn_count = 0
    idle_time = 0
    console = Console()
    last_model = os.getenv('CAI_MODEL', 'alias0')
    last_agent_type = os.getenv('CAI_AGENT_TYPE', 'one_tool_agent')
    parallel_count = int(os.getenv('CAI_PARALLEL', '1'))

    # Initialize command completer and key bindings
    command_completer = FuzzyCommandCompleter()
    current_text = ['']
    kb = create_key_bindings(current_text)

    # Setup session logging
    history_file = setup_session_logging()

    # Initialize session logger and display the filename
    session_logger = get_session_recorder()

    # Display banner
    display_banner(console)
    print("\n")
    display_quick_guide(console)
    # Function to get the short name of the agent for display
    def get_agent_short_name(agent):
        if hasattr(agent, 'name'):
            # Return the full agent name instead of just the first word
            return agent.name
        return "Agent"
    
    # Prevent the model from using its own rich streaming to avoid conflicts
    # but allow final output message to ensure all agent responses are shown
    if hasattr(agent, 'model'):
        if hasattr(agent.model, 'disable_rich_streaming'):
            agent.model.disable_rich_streaming = False  # Now True as the model handles streaming
        if hasattr(agent.model, 'suppress_final_output'):
            agent.model.suppress_final_output = False  # Changed to False to show all agent messages

        # Set the agent name in the model for proper display in streaming panel
        if hasattr(agent.model, 'set_agent_name'):
            agent.model.set_agent_name(get_agent_short_name(agent))

    prev_max_turns = max_turns
    turn_limit_reached = False
    
    while True:  
        # Check if the ctf name has changed and instanciate the ctf
        global previous_ctf_name
        global ctf_global
        global messages_ctf   
        global ctf_init
        if previous_ctf_name != os.getenv('CTF_NAME', None):
            if is_pentestperf_available():
                if ctf_global:
                    ctf_global.stop_ctf()
                ctf, messages_ctf = setup_ctf()
                ctf_global = ctf
                previous_ctf_name = os.getenv('CTF_NAME', None)
                ctf_init=0
        # Check if CAI_MAX_TURNS has been updated via /config
        current_max_turns = os.getenv('CAI_MAX_TURNS', 'inf')
        if current_max_turns != str(prev_max_turns):
            max_turns = float(current_max_turns)
            prev_max_turns = max_turns
            
            if turn_limit_reached and turn_count < max_turns:
                turn_limit_reached = False
                console.print("[green]Turn limit increased. You can now continue using CAI.[/green]")
            
        # Check if max turns is reached
        if turn_count >= max_turns and max_turns != float('inf'):
            if not turn_limit_reached:
                turn_limit_reached = True
                console.print(f"[bold red]Error: Maximum turn limit ({int(max_turns)}) reached.[/bold red]")
                console.print("[yellow]You must increase the limit using the /config command: /config CAI_MAX_TURNS=<new_value>[/yellow]")
                console.print("[yellow]Only CLI commands (starting with '/') will be processed until the limit is increased.[/yellow]")
            
        try:
            # Start measuring user idle time
            start_idle_timer()

            idle_start_time = time.time()

            # Check if model has changed and update if needed
            current_model = os.getenv('CAI_MODEL', 'alias0')
            if current_model != last_model and hasattr(agent, 'model'):
                # Update the model recursively for the agent and all handoff agents
                update_agent_models_recursively(agent, current_model)
                last_model = current_model

            # Check if agent type has changed and recreate agent if needed
            current_agent_type = os.getenv('CAI_AGENT_TYPE', 'one_tool_agent')
            if current_agent_type != last_agent_type:
                try:
                    # Import is already at the top level
                    agent = get_agent_by_name(current_agent_type)
                    last_agent_type = current_agent_type

                    # Configure the new agent's model flags
                    if hasattr(agent, 'model'):
                        if hasattr(agent.model, 'disable_rich_streaming'):
                            agent.model.disable_rich_streaming = False  # Now False to let model handle streaming
                        if hasattr(agent.model, 'suppress_final_output'):
                            agent.model.suppress_final_output = False  # Changed to False to show all agent messages

                        # Apply current model to the new agent and all its handoff agents
                        update_agent_models_recursively(agent, current_model)

                        # Set agent name in the model for streaming display
                        if hasattr(agent.model, 'set_agent_name'):
                            agent.model.set_agent_name(get_agent_short_name(agent))
                except Exception as e:
                    console.print(f"[red]Error switching agent: {str(e)}[/red]")           
        
            if not force_until_flag and ctf_init!=0:
                # Get user input with command completion and history
                user_input = get_user_input(
                    command_completer,
                    kb,
                    history_file,
                    get_toolbar_with_refresh,
                    current_text
                ) 
                
            else:
                user_input = messages_ctf
                ctf_init=1
            idle_time += time.time() - idle_start_time

            # Stop measuring user idle time and start measuring active time
            stop_idle_timer()
            start_active_timer()

        except KeyboardInterrupt:
            def format_time(seconds):
                mins, secs = divmod(int(seconds), 60)
                hours, mins = divmod(mins, 60)
                return f"{hours:02d}:{mins:02d}:{secs:02d}"

            Total = time.time() - START_TIME
            idle_time += time.time() - idle_start_time
            
            # NEW: Clean up any pending tool calls before exiting
            try:
                # Access the _Converter directly to clean up any pending tool calls
                from cai.sdk.agents.models.openai_chatcompletions import _Converter
                
                # Check if any tool calls are pending (have been issued but don't have responses)
                pending_calls = []
                if hasattr(_Converter, 'recent_tool_calls'):
                    for call_id, call_info in list(_Converter.recent_tool_calls.items()):
                        # Check if this tool call has a corresponding response in message_history
                        tool_response_exists = False
                        for msg in message_history:
                            if msg.get("role") == "tool" and msg.get("tool_call_id") == call_id:
                                tool_response_exists = True
                                break
                                
                        # If no tool response exists, create a synthetic one
                        if not tool_response_exists:
                            # First ensure there's a matching assistant message with this tool call
                            assistant_exists = False
                            for msg in message_history:
                                if (msg.get("role") == "assistant" and 
                                    msg.get("tool_calls") and 
                                    any(tc.get("id") == call_id for tc in msg.get("tool_calls", []))):
                                    assistant_exists = True
                                    break
                            
                            # Add assistant message if needed
                            if not assistant_exists:
                                tool_call_msg = {
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [{
                                        "id": call_id,
                                        "type": "function",
                                        "function": {
                                            "name": call_info.get('name', 'unknown_function'),
                                            "arguments": call_info.get('arguments', '{}')
                                        }
                                    }]
                                }
                                add_to_message_history(tool_call_msg)
                            
                            # Add a synthetic tool response
                            tool_msg = {
                                "role": "tool",
                                "tool_call_id": call_id,
                                "content": "Operation interrupted by user (Keyboard Interrupt during shutdown)"
                            }
                            add_to_message_history(tool_msg)
                            pending_calls.append(call_info.get('name', 'unknown'))
                
                # Apply message list fixes
                # NOTE: Commenting this to avoid creating duplicate synthetic tool calls
                # The synthetic tool calls we just created are already in the correct format
                # if pending_calls:
                #     from cai.util import fix_message_list
                #     message_history[:] = fix_message_list(message_history)
                #     print(f"\033[93mCleaned up {len(pending_calls)} pending tool calls before exit\033[0m")
                if pending_calls:
                    print(f"\033[93mCleaned up {len(pending_calls)} pending tool calls before exit\033[0m")
            except Exception:
                pass
            
            try:
                # Get more accurate active and idle time measurements from the timer functions
                from cai.util import get_active_time_seconds, get_idle_time_seconds, COST_TRACKER

                # Use the precise measurements from our timers
                active_time_seconds = get_active_time_seconds()
                idle_time_seconds = get_idle_time_seconds()

                # Format for display
                active_time_formatted = format_time(active_time_seconds)
                idle_time_formatted = format_time(idle_time_seconds)

                # Get session cost from the global cost tracker
                session_cost = COST_TRACKER.session_total_cost

                metrics = {
                    "session_time": format_time(Total),
                    "active_time": active_time_formatted,
                    "idle_time": idle_time_formatted,
                    "llm_time": format_time(active_time_seconds),  # Using active time as LLM time
                    "llm_percentage": round((active_time_seconds / Total) * 100, 1) if Total > 0 else 0.0,
                    "session_cost": f"${session_cost:.6f}"  # Add formatted session cost
                }
                logging_path = session_logger.filename if hasattr(session_logger, 'filename') else None

                content = []
                content.append(f"Session Time: {metrics['session_time']}")
                content.append(f"Active Time: {metrics['active_time']} ({metrics['llm_percentage']}%)")
                content.append(f"Idle Time: {metrics['idle_time']}")
                content.append(f"Total Session Cost: {metrics['session_cost']}")  # Add cost to display
                if logging_path:
                    content.append(f"Log available at: {logging_path}")

                def print_session_summary(console, metrics, logging_path=None):
                    """
                    Print a session summary panel using Rich.
                    """
                    from rich.panel import Panel
                    from rich.text import Text
                    from rich.box import ROUNDED
                    from rich.console import Group

                    # Create Rich Text objects for each line
                    text_content = []
                    for i, line in enumerate(content):
                        if "Total Session Cost" in line:
                            # Format cost line with special styling
                            cost_text = Text()
                            parts = line.split(":")
                            cost_text.append(parts[0] + ":", style="bold")
                            cost_text.append(parts[1], style="bold green")
                            text_content.append(cost_text)
                        else:
                            text_content.append(Text(line))

                    time_panel = Panel(
                        Group(*text_content),
                        border_style="blue",
                        box=ROUNDED,
                        padding=(0, 1),
                        title="[bold]Session Summary[/bold]",
                        title_align="left"
                    )
                    console.print(time_panel, end="")

                print_session_summary(console, metrics, logging_path)

                # Upload logs if telemetry is enabled by checking the
                # env. variable CAI_TELEMETRY and there's internet connectivity
                telemetry_enabled = \
                    os.getenv('CAI_TELEMETRY', 'true').lower() != 'false'
                if (
                    telemetry_enabled and
                    hasattr(session_logger, 'session_id') and
                    hasattr(session_logger, 'filename')
                   ):
                    process_metrics(
                        session_logger.filename,  # should match logging_path
                        sid=session_logger.session_id
                    )

                # Log session end
                if session_logger:
                    session_logger.log_session_end()

                # Create symlink to the last log file
                if session_logger and hasattr(session_logger, 'filename'):
                    create_last_log_symlink(session_logger.filename)

                # Prevent duplicate cost display from the COST_TRACKER exit handler
                os.environ["CAI_COST_DISPLAYED"] = "true"

                if (is_pentestperf_available() and os.getenv('CTF_NAME', None)):
                    ctf.stop_ctf()

            except Exception:
                pass
            break

        try:
            # Check if turn limit is reached and allow only CLI commands
            if turn_limit_reached and not user_input.startswith('/') and not user_input.startswith('$'):
                console.print("[bold red]Error: Turn limit reached. Only CLI commands are allowed.[/bold red]")
                console.print("[yellow]Please use /config to increase CAI_MAX_TURNS limit.[/yellow]")
                # Skip processing this input but continue the main loop
                stop_active_timer()
                start_idle_timer()
                continue
                
            # Check if we have parallel configurations to run
            if PARALLEL_CONFIGS and not user_input.startswith('/') and not user_input.startswith('$'):
                # Use parallel configurations instead of normal processing
                console.print(f"[bold cyan]Running {len(PARALLEL_CONFIGS)} parallel agents...[/bold cyan]")
                
                async def run_agent_instance(config: ParallelConfig, input_text: str):
                    """Run a single agent instance with its own configuration."""
                    try:
                        # Create a fresh agent instance
                        instance_agent = get_agent_by_name(config.agent_name)
                        
                        # Override model if specified, updating recursively
                        if config.model and hasattr(instance_agent, 'model'):
                            update_agent_models_recursively(instance_agent, config.model)
                        
                        # Override prompt if specified
                        instance_input = config.prompt or input_text
                        
                        # Run the agent with its own isolated context
                        result = await Runner.run(instance_agent, instance_input)
                        
                        return (config, result)
                    except Exception as e:
                        import traceback
                        console.print(f"[bold red]Error in {config.agent_name}: {str(e)}[/bold red]")
                        return (config, None)
                
                async def run_parallel_agents():
                    """Run all configured agents in parallel."""
                    # Create tasks for each agent
                    tasks = [run_agent_instance(config, user_input) 
                             for config in PARALLEL_CONFIGS]
                    
                    # Wait for all to complete
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Filter out exceptions and failed results
                    valid_results = []
                    for item in results:
                        if isinstance(item, tuple) and len(item) == 2 and item[1] is not None:
                            valid_results.append(item)
                    
                    return valid_results
                
                # Run in asyncio event loop
                results = asyncio.run(run_parallel_agents())                
                turn_count += 1
                stop_active_timer()
                start_idle_timer()
                continue
            
            # Handle special commands
            if user_input.startswith('/') or user_input.startswith('$'):
                parts = user_input.strip().split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else None

                # Process the command with the handler
                if commands_handle_command(command, args):
                    continue  # Command was handled, continue to next iteration

                # If command wasn't recognized, show error (skip for /shell or /s)
                if command not in ("/shell", "/s"):
                    console.print(f"[red]Unknown command: {command}[/red]")
                continue
            from rich.text import Text
            log_text = Text(
                f"Log file: {session_logger.filename}",
                style="yellow on black",
            )
            console.print(log_text)

            # Build conversation context from previous turns to give the
            # model short-term memory. We only keep messages that have plain
            # text content and ignore tool call entries to prevent schema
            # mismatches when converting to OpenAI chat format.
            history_context = []
            for msg in message_history:
                role = msg.get("role")
                content = msg.get("content")
                tool_calls = msg.get("tool_calls")

                if role == "user":
                    history_context.append({"role": "user", "content": content or ""})
                elif role == "system":
                    history_context.append({"role": "system", "content": content or ""})
                elif role == "assistant":
                    if tool_calls:
                        history_context.append(
                            {
                                "role": "assistant",
                                "content": content,  # Can be None
                                "tool_calls": tool_calls,
                            }
                        )
                    elif content is not None:
                        history_context.append({"role": "assistant", "content": content})
                    elif content is None and not tool_calls: # Explicitly handle empty assistant message
                         history_context.append({"role": "assistant", "content": None})
                elif role == "tool":
                    history_context.append(
                        {
                            "role": "tool",
                            "tool_call_id": msg.get("tool_call_id"),
                            "content": msg.get("content"), # Tool output
                        }
                    )

            # Fix message list structure BEFORE sending to the model to prevent errors
            try:
                from cai.util import fix_message_list
                history_context = fix_message_list(history_context)
            except Exception as e:
                pass

            # Append the current user input as the last message in the list.
            conversation_input: list | str
            if history_context:
                history_context.append({"role": "user", "content": user_input})
                conversation_input = history_context
            else:
                conversation_input = messages_ctf + user_input 

            # Process the conversation with the agent - with parallel execution if enabled
            if parallel_count > 1:
                # Parallel execution mode (always non-streaming)
                async def run_agent_instance(instance_number):
                    """Run a single agent instance with its own complete context"""
                    try:
                        # Create a fresh agent instance to ensure complete isolation
                        instance_agent = get_agent_by_name(last_agent_type)
                        
                        # Configure agent instance to match main agent settings
                        if hasattr(instance_agent, 'model') and hasattr(agent, 'model'):
                            if hasattr(instance_agent.model, 'model') and hasattr(agent.model, 'model'):
                                update_agent_models_recursively(instance_agent, agent.model.model)
                        
                        # Create a fresh input for this instance - use just the user input directly
                        # This ensures each instance has its own completely independent context
                        instance_input = user_input
                        
                        # Run the agent with its own isolated context
                        result = await Runner.run(instance_agent, instance_input)
                        
                        return (instance_number, result)
                    except Exception as e:
                        import traceback
                        console.print(f"[bold red]Error in instance {instance_number}: {str(e)}[/bold red]")
                        return (instance_number, None)
                
                async def process_parallel_responses():
                    """Process multiple parallel agent executions"""
                    # Create tasks for each instance
                    tasks = [run_agent_instance(i) for i in range(parallel_count)]
                    
                    # Wait for all to complete, no matter if some fail
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Filter out exceptions and failed results
                    valid_results = []
                    for idx, result in results:
                        if result is not None and not isinstance(result, Exception):
                            valid_results.append((idx, result))
                    
                    return valid_results
                
                # Execute all parallel instances
                results = asyncio.run(process_parallel_responses())
                
                # Print summary info about the results
                console.print(f"[bold cyan]Completed {len(results)}/{parallel_count} parallel agent executions[/bold cyan]")
                
                # Display the results
                for idx, result in results:
                    if result and hasattr(result, 'final_output') and result.final_output:                        
                        # Add to main message history for context
                        add_to_message_history({
                            "role": "assistant",
                            "content": f"{result.final_output}"
                        })
            else:
                # Enable streaming by default, unless specifically disabled
                stream = os.getenv('CAI_STREAM', 'true').lower() != 'false'
                
                # Single agent execution (original behavior)
                if stream:
                    async def process_streamed_response(agent, conversation_input):
                        try:
                            result = Runner.run_streamed(agent, conversation_input)

                            # Consume events so the async generator is executed.
                            async for event in result.stream_events():
                                if isinstance(event, RunItemStreamEvent) and event.name == "tool_output":
                                    # Ensure item is a ToolCallOutputItem before accessing attributes
                                    if isinstance(event.item, ToolCallOutputItem):
                                        tool_msg = {
                                            "role": "tool",
                                            "tool_call_id": event.item.raw_item["call_id"], # Changed to dictionary access
                                            "content": event.item.output,
                                        }
                                        add_to_message_history(tool_msg)
                                # pass # Original logic was just pass

                            return result
                        except Exception as e:
                            import traceback
                            tb = traceback.format_exc()
                            print(
                                f"\n[Error occurred during streaming: {str(e)}]"
                                f"\nLocation: {tb}"
                            )
                            return None

                    asyncio.run(process_streamed_response(agent, conversation_input))
                else:
                    # Use non-streamed response
                    response = asyncio.run(Runner.run(agent, conversation_input))
                    
                    # En modo no-streaming, procesamos SOLO los tool outputs de response.new_items
                    # Los tool calls (assistant messages) ya se añaden correctamente en openai_chatcompletions.py
                    for item in response.new_items:
                        # Handle ONLY tool call output items (tool results)
                        if isinstance(item, ToolCallOutputItem):
                            tool_call_id = item.raw_item["call_id"]
                            
                            # Verificar si ya existe este tool output en message_history para evitar duplicación
                            tool_msg_exists = any(
                                msg.get("role") == "tool" and msg.get("tool_call_id") == tool_call_id
                                for msg in message_history
                            )
                            
                            if not tool_msg_exists:
                                # Añadir solo el tool output al message_history
                                tool_msg = {
                                    "role": "tool",
                                    "tool_call_id": tool_call_id,
                                    "content": item.output,
                                }
                                add_to_message_history(tool_msg)
                
                # Final validation to ensure message history follows OpenAI's requirements
                # Ensure every tool message has a preceding assistant message with matching tool_call_id
                from cai.util import fix_message_list
                message_history[:] = fix_message_list(message_history)
            turn_count += 1

            # Stop measuring active time and start measuring idle time again
            stop_active_timer()
            start_idle_timer()

        except KeyboardInterrupt:
            print("\n\033[91mKeyboard interrupt detected\033[0m")
            
            # NEW: Handle pending tool calls to prevent errors on next iteration
            try:
                # Access the _Converter directly to clean up any pending tool calls
                from cai.sdk.agents.models.openai_chatcompletions import _Converter
                
                # Check if any tool calls are pending (have been issued but don't have responses)
                if hasattr(_Converter, 'recent_tool_calls'):
                    for call_id, call_info in list(_Converter.recent_tool_calls.items()):
                        # Check if this tool call has a corresponding response in message_history
                        tool_response_exists = False
                        for msg in message_history:
                            if msg.get("role") == "tool" and msg.get("tool_call_id") == call_id:
                                tool_response_exists = True
                                break
                                
                        # If no tool response exists, create a synthetic one
                        if not tool_response_exists:
                            # First ensure there's a matching assistant message with this tool call
                            assistant_exists = False
                            for msg in message_history:
                                if (msg.get("role") == "assistant" and 
                                    msg.get("tool_calls") and 
                                    any(tc.get("id") == call_id for tc in msg.get("tool_calls", []))):
                                    assistant_exists = True
                                    break
                            
                            # Add assistant message if needed
                            if not assistant_exists:
                                tool_call_msg = {
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [{
                                        "id": call_id,
                                        "type": "function",
                                        "function": {
                                            "name": call_info.get('name', 'unknown_function'),
                                            "arguments": call_info.get('arguments', '{}')
                                        }
                                    }]
                                }
                                add_to_message_history(tool_call_msg)
                            
                            # Add a synthetic tool response
                            tool_msg = {
                                "role": "tool",
                                "tool_call_id": call_id,
                                "content": "Operation interrupted by user (Keyboard Interrupt)"
                            }
                            add_to_message_history(tool_msg)
                                                        
                    # Apply message list fixes
                    # NOTE: Commenting this to avoid creating duplicate synthetic tool calls
                    # The synthetic tool calls we just created are already in the correct format
                    # from cai.util import fix_message_list
                    # message_history[:] = fix_message_list(message_history)
                    pass
            except Exception as cleanup_error:
                print(f"\033[91mError cleaning up interrupted tools: {str(cleanup_error)}\033[0m")
            
            pass
        except Exception as e:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_info = traceback.extract_tb(exc_traceback)
            filename, line, func, text = tb_info[-1]
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            console.print(f"[bold red]Traceback: {tb_info}[/bold red]")
            
            # Make sure we switch back to idle mode even if there's an error
            stop_active_timer()
            start_idle_timer()

def create_last_log_symlink(log_filename):
    """
    Create a symbolic link 'logs/last' pointing to the current log file.
    
    Args:
        log_filename: Path to the current log file
    """
    try:
        import os
        from pathlib import Path
        
        if not log_filename:
            return
            
        log_path = Path(log_filename)
        if not log_path.exists():
            return
            
        # Create the symlink path
        symlink_path = Path("logs/last")
        
        # Remove existing symlink if it exists
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()
        
        # Create new symlink pointing to just the filename (relative path within logs dir)
        symlink_path.symlink_to(log_path.name)
        
    except Exception:
        # Silently ignore errors to avoid disrupting the main flow
        pass

def main():
    # Apply litellm patch to fix the __annotations__ error
    patch_applied = fix_litellm_transcription_annotations()
    if not patch_applied:
        print(color("Something went wrong patching LiteLLM fix_litellm_transcription_annotations", color="red"))

    # Get agent type from environment variables or use default
    agent_type = os.getenv('CAI_AGENT_TYPE', "one_tool_agent")

    # Get the agent instance by name
    agent = get_agent_by_name(agent_type)

    # Configure model flags to work well with CLI
    if hasattr(agent, 'model'):
        # Disable rich streaming in the model to avoid conflicts
        if hasattr(agent.model, 'disable_rich_streaming'):
            agent.model.disable_rich_streaming = True
        # Allow final output to ensure all agent messages are shown
        if hasattr(agent.model, 'suppress_final_output'):
            agent.model.suppress_final_output = False  # Changed to False to show all agent messages

    # Ensure the agent and all its handoff agents use the current model
    current_model = os.getenv('CAI_MODEL', 'alias0')
    update_agent_models_recursively(agent, current_model)

    # Run the CLI with the selected agent
    run_cai_cli(agent)

if __name__ == "__main__":
    main()
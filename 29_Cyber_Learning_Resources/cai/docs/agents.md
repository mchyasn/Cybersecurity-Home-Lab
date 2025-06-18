# Agents

Agents are the core of CAI. An agent uses Large Language Models (LLMs), configured with instructions and tools.
Each agent is defined in its own `.py` file in `src/cai/agents`.

## Basic configuration

Key agent properties include:

-   `name`: of the agent e.g. the name of `one_tool_agent` is 'CTF Agent'.
-   `instructions`: known as the system prompt.
-   `model`: which LLM to use, and optional `model_settings` to configure their parameters like temperature, top_p, etc.
-   `tools`: Tools that the agent can use to achieve its tasks.
-   `handoffs`: wich allows an agent to delegate tasks to another agent.


## Example: `one_tool_agent.py`

```python
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel
from cai.tools.reconnaissance.generic_linux_command import generic_linux_command 
from openai import AsyncOpenAI

one_tool_agent = Agent(
    name="CTF agent",
    description="Agent focused on conquering security challenges using generic linux commands",
    instructions="You are a Cybersecurity expert Leader facing a CTF challenge.",
    tools=[
        generic_linux_command,
    ],
    model=OpenAIChatCompletionsModel(
        model="qwen2.5:14b",
        openai_client=AsyncOpenAI(),
    )
)
```


## Context

There are two main context types. See [context](context.md) for details.

Agents are generic on their `context` type. Context is a dependency-injection tool: it's an object you create and pass to `Runner.run()`, that is passed to every agent, tool, handoff etc, and it serves as a grab bag of dependencies and state for the agent run. You can provide any Python object as the context.

```python
@dataclass
class SecurityContext:
  target_system: str
  is_compromised: bool

  async def get_exploits() -> list[Exploits]:
     return ...

agent = Agent[SecurityContext](
    ...,
)
```

## Output types

By default, agents produce plain text (i.e. `str`) outputs. If you want the agent to produce a particular type of output, you can use the `output_type` parameter. A common choice is to use [Pydantic](https://docs.pydantic.dev/) objects, but we support any type that can be wrapped in a Pydantic [TypeAdapter](https://docs.pydantic.dev/latest/api/type_adapter/) - dataclasses, lists, TypedDict, etc.

```python
from pydantic import BaseModel
from cai.sdk.agents import Agent

class SecurityVulnerability(BaseModel):
    name: str
    severity: str
    affected_files: list[str]
    description: str

agent = Agent(
    name="Vulnerability scanner",
    instructions="Analyze system output and identify security vulnerabilities",
    output_type=SecurityVulnerability,
)
```

!!! note
   When you pass an `output_type`, that tells the model to use structured outputs instead of regular plain text responses.

## Handoffs

Handoffs are sub-agents that the agent can delegate to. You provide a list of handoffs, and the agent can choose to delegate to them if relevant. This is a powerful pattern that allows orchestrating modular, specialized agents that excel at a single task. Read more in the [handoffs](handoffs.md) documentation.

```python
from cai.sdk.agents import Agent

crypto_agent = Agent(
    name="Cryptography agent",
    description="Agent specialized in solving cryptographic challenges and decoding encrypted messages",
    instructions="Analyze encrypted data and apply cryptographic techniques to decode it.",
    tools=[
        execute_cli_command,
    ],
    handoff_description="Specialized agent in Cryptography and code breaking",
    model=OpenAIChatCompletionsModel(
        model=os.getenv('CAI_MODEL', "qwen2.5:14b"),
        openai_client=AsyncOpenAI(),
    )
)
network_agent = Agent(
    name="Network Agent",
    description="Agent specialized in network analysis, packet inspection, and network security assessments",
    instructions="Analyze network traffic, identify suspicious patterns, and help with network-related CTF challenges",
    handoff_description="Specialized agent in network security, traffic analysis, and protocol understanding",
    model=OpenAIChatCompletionsModel(
        model=os.getenv('CAI_MODEL', "qwen2.5:72b"),
        openai_client=AsyncOpenAI(),
    )
)
lead_agent = Agent(
    name="Cybersecurity Lead Agent",
    instructions=(
        "You are a lead cybersecurity expert coordinating security operations."
        "If the user needs network analysis or traffic inspection, handoff to the network agent."
        "If the user needs cryptographic solutions or code breaking, handoff to the crypto agent."
    ),
    handoffs=[network_agent, crypto_agent],
    model="qwen2.5:72b"
)
```

## Dynamic instructions

In most cases, you can provide instructions when you create the agent. However, you can also provide dynamic instructions via a function. The function will receive the agent and context, and must return the prompt. Both regular and `async` functions are accepted.

```python
def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    security_level = "high" if context.context.is_admin else "standard"
    return f"You are assisting {context.context.name} with cybersecurity operations. Their security clearance level is {security_level}. Tailor your security recommendations appropriately and prioritize addressing their immediate security concerns."


agent = Agent[UserContext](
    name="Cybersecurity Triage Agent",
    instructions=dynamic_instructions,
)
```


## Next steps

- For running agents, see [running_agents documentation](running_agents.md). 

- For understanding what it returns, see [results documentation](results.md). 

- For connecting Agents to external tools (Model Context Protocol), see [mcp documentation](mcp.md).
The **Cybersecurity AI (CAI)** platform provides seamless integration with multiple Large Language Models (LLMs). This functionality allows users to leverage state-of-the-art AI capabilities for various cybersecurity tasks. CAI acts as a bridge between your security workflows and a wide range of LLMs, enhancing both flexibility and performance of AI agents.

CAI supports **over 300 models**, thanks to its integration with [LiteLLM](https://github.com/BerriAI/litellm). You can choose from a wide variety of providers and models, including:

- **Anthropic**: Claude 3.7, Claude 3.5, Claude 3, Claude 3 Opus  
- **OpenAI**: O1, O1 Mini, O3 Mini, GPT-4o, GPT-4.5 Preview  
- **DeepSeek**: DeepSeek V3, DeepSeek R1  
- **Ollama**: Qwen2.5 72B, Qwen2.5 14B, and more  

CAI is also compatibile with other platforms like OpenRouter and Ollama. Below you’ll find some configurations to help you get started.

#### [OpenRouter Integration](https://openrouter.ai/)

To enable OpenRouter support in CAI, you need to configure your environment by adding specific entries to your `.env` file. This setup ensures that CAI can interact with the OpenRouter API, facilitating the use of sophisticated models like Meta-LLaMA. Here’s how you can configure it:

```bash
CAI_MODEL=openrouter/meta-llama/llama-4-maverick
OPENROUTER_API_KEY=<sk-your-key>  # note, add yours
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```


#### [Ollama Integration](https://ollama.com/)
For local models using Ollama, add the following to your .env:

```bash
CAI_MODEL=qwen2.5:72b
OLLAMA_API_BASE=http://localhost:8000/v1 # note, maybe you have a different endpoint
```

Make sure that the Ollama server is running and accessible at the specified base URL. You can swap the model with any other supported by your local Ollama instance.

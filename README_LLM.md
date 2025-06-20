# LLM Selection Module (`LLMselect.py`)

This module provides a unified interface for selecting and initializing Large Language Model (LLM) providers and their models in your project. It supports OpenAI, Google Gemini, and Ollama LLMs, allowing you to easily switch between providers and models using environment variables.

## Features
- **Provider Abstraction:** Easily select between OpenAI, Google Gemini, and Ollama LLMs.
- **Model Management:** Lists available models for each provider and allows setting default models.
- **Environment Variable Configuration:** Select provider and model via environment variables (`LLM_PREFERRED`, `LLM_MODEL`).
- **API Key Validation:** Checks for required API keys or URLs for each provider.
- **Unified LLM Initialization:** Returns a ready-to-use LLM object from the selected provider.

## Usage

### 1. Set Environment Variables
Set the following environment variables before running your application:

- `LLM_PREFERRED`: The LLM provider to use (`OpenAI`, `Google`, or `Ollama`).
- `LLM_MODEL`: (Optional) The model name to use. If not set, the default model for the provider is used.
- Provider-specific variables:
  - For OpenAI: `OPENAI_API_KEY`
  - For Google Gemini: `GOOGLE_API_KEY`
  - For Ollama: `OLLAMA_URL`

Example (bash):
```bash
export LLM_PREFERRED=OpenAI
export LLM_MODEL=gpt-4o
export OPENAI_API_KEY=your_openai_key_here
```

### 2. Using the Module
Import and use the `LLMSelect` class to get your LLM instance:

```python
from appai.common.LLMselect import LLMSelect

llm_selector = LLMSelect()
llm = llm_selector.select_llm(temperature=0.7)
# Now use `llm` as needed
```

## Classes

### `LLMInfo`
- Manages available models and default models for each provider.
- Methods:
  - `get_model_list(provider)`
  - `get_providers()`
  - `get_default_model(provider)`

### `LLMSelect`
- Handles provider selection and LLM instantiation.
- Methods:
  - `select_llm(temperature=0.0)`: Returns the selected LLM instance.
  - `llm()`: Returns the currently selected LLM instance.

## Supported Providers and Models

| Provider | Example Models |
|----------|----------------|
| OpenAI   | gpt-4.1-mini, gpt-4o-mini, gpt-4o, gpt-4.1 |
| Google   | gemini-2.0-flash, gemini-2.5-flash-preview-05-20 |
| Ollama   | mistral, llama3.2:3b, deepseek-r1:8b |

## Error Handling
- Raises `ValueError` if required environment variables are missing or if an unsupported provider/model is selected.

## Dependencies
- [langchain_openai](https://python.langchain.com/docs/integrations/llms/openai)
- [langchain_google_genai](https://python.langchain.com/docs/integrations/llms/google_genai)
- [langchain_ollama](https://python.langchain.com/docs/integrations/llms/ollama)

Install dependencies via `pip` as needed.

---

For more details, see the code in `appai/common/LLMselect.py`.

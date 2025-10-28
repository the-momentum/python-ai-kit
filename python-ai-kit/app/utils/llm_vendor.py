import os


def set_api_key_for_vendor(vendor: str, api_key: str) -> None:
    """Set the appropriate API key environment variable for the vendor.
    
    Args:
        vendor: The AI provider vendor (e.g., 'openai', 'anthropic', 'google')
        api_key: The API key to set
    """
    # Map vendors to their environment variable names
    env_var_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY", 
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "cohere": "COHERE_API_KEY",
        "bedrock": "AWS_ACCESS_KEY_ID",  # Bedrock uses AWS credentials
        "huggingface": "HUGGINGFACE_API_KEY",
        # OpenAI-compatible providers
        "deepseek": "OPENAI_API_KEY",
        "grok": "OPENAI_API_KEY", 
        "ollama": "OPENAI_API_KEY",  # Ollama doesn't need API key
        "openrouter": "OPENAI_API_KEY",
        "vercel": "OPENAI_API_KEY",
        "perplexity": "OPENAI_API_KEY",
        "fireworks": "OPENAI_API_KEY",
        "together": "OPENAI_API_KEY",
        "azure": "OPENAI_API_KEY",
        "heroku": "OPENAI_API_KEY",
        "github": "OPENAI_API_KEY",
        "cerebras": "OPENAI_API_KEY",
        "litellm": "OPENAI_API_KEY",
    }
    
    env_var = env_var_map.get(vendor, "API_KEY")
    os.environ[env_var] = api_key

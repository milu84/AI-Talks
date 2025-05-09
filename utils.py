"""Utility functions for the AI Talks project"""

def read_file(filepath: str) -> str:
    """Reads the entire content of a text file and returns it as a string."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(filepath: str, content: str) -> None:
    """Writes content to a text file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def parse_config(config_text: str) -> dict:
    """
    Extract useful configuration info (API keys, model names, etc.)
    from a config file's text content. We assume simple key=value lines.
    """
    config = {}
    for line in config_text.splitlines():
        line = line.strip()
        # Ignore empty or commented-out lines
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()
    return config


def load_models_from_config(config_data: dict) -> list:
    """
    Reads model info from the config dictionary.
    Expects keys like MODEL1_NAME, MODEL1_APIKEY, MODEL1_VERSION, MODEL2_NAME, etc.
    Returns a list of dicts, each with 'name', 'apikey', and 'version'.
    """
    models = []
    i = 1
    while True:
        name_key = f"MODEL{i}_NAME"
        api_key = f"MODEL{i}_APIKEY"
        version_key = f"MODEL{i}_VERSION"

        if name_key in config_data:
            model_info = {
                'name': config_data[name_key],
                'apikey': config_data.get(api_key, None),
                'version': config_data.get(version_key, None)
            }
            models.append(model_info)
            i += 1
        else:
            break
    return models


def get_default_models() -> list:
    """Returns a list of default model configurations if none are provided"""
    return [
        {'name': 'Chad', 'apikey': None, 'version': 'gpt-4-turbo'},
        {'name': 'Gianna', 'apikey': None, 'version': 'gemini-pro'},
        {'name': 'Claudine', 'apikey': None, 'version': 'claude-3-opus-20240229'},
        {'name': 'Greg', 'apikey': None, 'version': 'grok-2-1212'},
        {'name': 'Mariel', 'apikey': None, 'version': 'mistral-large-latest'}
    ]


def create_config_file_content(models, output_file="conversation_output.txt") -> str:
    """Creates the content for a config.txt file based on model configurations"""
    config_lines = ["# config.txt\n"]
    
    # Add API URLs as comments
    config_lines.extend([
        "# API Keys URLs",
        "# https://platform.openai.com/settings/organization/api-keys",
        "# https://console.anthropic.com/settings/keys",
        "# https://aistudio.google.com/app/apikey",
        "# https://console.x.ai/settings/api-keys",
        "# https://console.mistral.ai/",
        ""
    ])
    
    # Add models
    for i, model in enumerate(models):
        if 'name' in model and model['name']:
            index = i + 1
            config_lines.append(f"MODEL{index}_NAME={model['name']}")
            
            if 'apikey' in model and model['apikey']:
                config_lines.append(f"MODEL{index}_APIKEY={model['apikey']}")
                
            if 'version' in model and model['version']:
                config_lines.append(f"MODEL{index}_VERSION={model['version']}")
                
            # Add a blank line between models
            config_lines.append("")
    
    # Add output file
    config_lines.append(f"OUTPUT_FILE={output_file}")
    
    return "\n".join(config_lines)
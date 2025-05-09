import random
import sys
import re
import google.generativeai as genai
import anthropic
# from anthropic import Anthropic
from openai import OpenAI

LLM_MAX_CHARACTERS = 15000
LLM_MAX_TOKENS = 500
LLM_TEMPERATURE = 0.4


# LLM_MAX_CHARACTERS = 15000
# LLM_MAX_TOKENS = 250
# LLM_TEMPERATURE = 0.6
# answer 750
# final round 500

#########################
# 1) HELPER FUNCTIONS   #
#########################

def read_file(filepath: str) -> str:
    """Reads the entire content of a text file and returns it as a string."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_config(config_text: str) -> dict:
    """
    Extract useful configuration info (API keys, model names, etc.)
    from a config file’s text content. We assume simple key=value lines.
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


def load_models_from_config(config_data: dict):
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


#########################
# 2) LLM CALLS          #
#########################

def sanitize_llm_output(response_text: str, speaker: str) -> str:
    """
    Removes any leading bracketed prefix or 'Speaker:' text if it appears in `response_text`.
    Ensures we only show exactly one '[Speaker]:' at the start.
    """
    # We consider variants like "[Speaker]:", "Speaker:", etc.
    # We'll strip them if they appear at the beginning of the string.

    # Build possible prefixes
    bracket_prefix = f"[{speaker}]:"
    colon_prefix = f"{speaker}:"

    # Regex to remove up to two duplicates if they appear
    # E.g. "[Jemmy]: [Jemmy]:" or "Jemmy: [Jemmy]:" etc.
    pattern = r'^(?:\[' + re.escape(speaker) + r'\]:\s*)?(?:\[' + re.escape(speaker) + r'\]:\s*)?(?:' + re.escape(
        speaker) + r':\s*)?(.*)$'
    match = re.match(pattern, response_text, re.IGNORECASE)
    if match:
        response_text = match.group(1).strip()

    return response_text


def generate_response(
        speaker: str,
        conversation_history: list,
        style_prompt: str,
        topic: str,
        ext_data: str,
        do_challenge: bool,
        version: str,
        api_key: str = None
) -> str:
    """
    Generates a response from a specific LLM, based on:
      - `speaker`: which model we’re calling (e.g., "OpenAI-GPT", "Gemini", "Cloud", "Grok")
      - `conversation_history`: list of prior messages (strings)
      - `style_prompt`: instructions on style/tone
      - `topic`: the main topic
      - `ext_data`: external data to optionally incorporate (can be empty if not yet visible)
      - `do_challenge`: whether the model should 'challenge' the last statement
      - `api_key`: the API key for the chosen LLM

    Returns a single string, prefixed with [Speaker]: ...
    """

    # Combine the entire conversation history into a single text block.
    context_text = "\n".join(conversation_history)

    challenge_fragment = ""
    if do_challenge:
        challenge_fragment = "Please challenge or question the last point made."

    # Only add external data if it's not empty
    if ext_data:
        external_data_string = (
            "***** Here is additional, external data (use it only if relevant, "
            "and not in all your answers) ***** \n\n"
            f": {ext_data}\n\n"
        )
    else:
        external_data_string = ""

    user_prompt = (
        f"{style_prompt}\n\n"
        f">>>>> Discussion topic: {topic} <<<<<\n\n"
        f"****** The Conversation so far: ******\n"
        f"{context_text}\n"
        f"****** End of The Conversation ******\n\n"
        f"{challenge_fragment}\n"
        f"{external_data_string}"
        f"Please continue the conversation.\n"
        f"**Important**: Do NOT prefix your output with your name or any bracketed speaker info. "
        f"Simply provide your response in plain text.\n"
        f"You are the speaker named {speaker}, but do NOT start your response with '[{speaker}]'.\n"
    )

    # Decide which API to call based on the speaker’s name
    speaker_lower = speaker.lower()
    if "chad" in speaker_lower:
        response_text = call_openai_api(user_prompt, api_key, speaker, version)
    elif "clyde" in speaker_lower:
        response_text = call_anthropic_api(user_prompt, api_key, speaker, version)
    elif "jemmy" in speaker_lower:
        response_text = call_google_gemini_api(user_prompt, api_key, speaker, version)
    elif "greg" in speaker_lower:
        response_text = call_grok_api(user_prompt, api_key, speaker, version)
    else:
        # Fallback to a mock response
        response_text = f"I'm responding in a generic way, since I don't have a recognized model name."

    # Post-process the text to remove any accidental prefix,
    # then add our single "[Speaker]:"
    cleaned_response = sanitize_llm_output(response_text, speaker)
    return f"[{speaker}]\n{cleaned_response}"


def call_openai_api(prompt_text: str, api_key: str, name: str, version: str) -> str:
    """ Example call to the OpenAI ChatCompletion endpoint. """
    if not api_key:
        return f"Error: Missing API key for {name}."

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=version,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE
        )
        final_text = response.choices[0].message.content.strip()
        return final_text
    except Exception as e:
        return f"Error from {name}: {e}"


def call_anthropic_api(prompt_text: str, api_key: str, name: str, version: str) -> str:
    """ Simplified call to Anthropic’s Claude. """
    if not api_key:
        return f"Error: Missing API key for {name}."

    client = anthropic.Anthropic(api_key=api_key)
    try:
        message = client.messages.create(
            model=version,
            max_tokens=LLM_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt_text}]
        )

        # If message.content is a list of text blocks, handle them
        if isinstance(message.content, list):
            text_fragments = []
            for block in message.content:
                if hasattr(block, "text"):
                    text_fragments.append(block.text)
                else:
                    text_fragments.append(str(block))
            combined_text = " ".join(text_fragments).strip()
        else:
            combined_text = str(message.content).strip()

        return combined_text
    except Exception as e:
        return f"Error from {name}: {e}"


def call_google_gemini_api(prompt_text: str, api_key: str, name: str, version: str) -> str:
    """ Simplified call to Google's Gemini via `google.generativeai`. """
    if not api_key:
        return f"Error: Missing API key for {name}."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(version)
        response = model.generate_content(
            prompt_text,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                stop_sequences=[],
                max_output_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
            )
        )
        final_text = response.text.strip() if response.text else ""
        return final_text
    except Exception as e:
        return f"Error from {name}: {e}"


def call_grok_api(prompt_text: str, api_key: str, name: str, version: str) -> str:
    """ Example call to a fictional Grok endpoint. """
    if not api_key:
        return f"Error: Missing API key for {name}."

    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    try:
        response = client.chat.completions.create(
            model=version,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE
        )
        final_text = response.choices[0].message.content.strip()
        return final_text
    except Exception as e:
        return f"Error from {name}: {e}"


#########################
# 3) MAIN SCRIPT        #
#########################

def main():
    # === A) Read configuration from config.txt ===
    config_text = read_file('../config.txt')
    config_data = parse_config(config_text)

    # === B) Load model definitions dynamically from config ===
    models_list = load_models_from_config(config_data)
    # Provide a default if config is empty
    if not models_list:
        models_list = [
            {'name': 'Chad', 'apikey': None, 'version': 'gpt-xx'},
            {'name': 'Jemmy', 'apikey': None, 'version': 'gemini-xx'},
            {'name': 'Clyde', 'apikey': None, 'version': 'claude-xx'},
            {'name': 'Greg', 'apikey': None, 'version': 'grok-xx'}
        ]

    # === C) Read topic, style prompt, and final-round prompt ===
    topic = read_file('../topic.txt').strip()
    style_prompt = read_file('../prompt.txt').strip()
    final_round_prompt = read_file('../prompt_fr.txt').strip()

    # CHANGED: Store the original external data, but don't pass it until discussion starts
    ext_data_original = read_file('../ext_data.txt').strip()
    discussion_started = False  # CHANGED: This flag will track if at least one speaker has spoken

    # === D) Prepare conversation storage & counters ===
    conversation_history = []
    total_characters = 0
    max_total_characters = LLM_MAX_CHARACTERS

    # 1) Build an introduction text
    intro_lines = [
        "Greetings, curious minds!",
        "Welcome to The AI Talks—the place where cutting-edge AI models interact with each other, "
        "shape our perspectives, and tackle real-world issues!\n",
        f"Today’s topic is: \"{topic}\".\n",
        "Our panelists include:"
    ]
    for model in models_list:
        model_intro = f"- {model['name']} "
        intro_lines.append(model_intro)

    intro_lines.append(".\n\nEnjoy it, and let’s start with the first panelist!\n")
    intro_text = "\n".join(intro_lines)

    conversation_history.append(intro_text)
    total_characters += len(intro_text)

    # Track the last speaker in the previous round
    last_speaker = None

    # === E) Conversation Loop ===
    while total_characters < max_total_characters:
        # Create a random permutation of the entire list
        speaker_batch = models_list[:]
        random.shuffle(speaker_batch)

        # If the first in the batch is the same as last_speaker, reshuffle to avoid duplicates.
        max_reshuffles = 10
        reshuffle_count = 0
        while last_speaker is not None and speaker_batch[0][
            'name'] == last_speaker and reshuffle_count < max_reshuffles:
            random.shuffle(speaker_batch)
            reshuffle_count += 1

        for speaker_info in speaker_batch:
            speaker_name = speaker_info['name']
            speaker_api_key = speaker_info['apikey']
            speaker_version = speaker_info['version']

            # 20% chance of "challenge"
            do_challenge = (random.random() < 0.20)

            # CHANGED: Only pass ext_data after the discussion has started
            current_ext_data = ext_data_original if discussion_started else ""

            response = generate_response(
                speaker=speaker_name,
                conversation_history=conversation_history,
                style_prompt=style_prompt,
                topic=topic,
                ext_data=current_ext_data,  # CHANGED
                do_challenge=do_challenge,
                version=speaker_version,
                api_key=speaker_api_key
            )

            # CHANGED: Once the first speaker has spoken, set the flag
            if not discussion_started:
                discussion_started = True

            if total_characters + len(response) > max_total_characters:
                break

            conversation_history.append(response)
            total_characters += len(response)
            last_speaker = speaker_name

        else:
            # If we didn't break, continue
            continue

        # If we did break, stop the while loop
        break

    # === F) Final Round ===
    final_round_marker = f"FINAL ROUND"
    conversation_history.append(final_round_marker)
    total_characters += len(final_round_marker)

    for model_info in models_list:
        speaker_name = model_info['name']
        speaker_api_key = model_info['apikey']
        speaker_version = model_info['version']

        # During final round, external data should be visible
        final_message = generate_response(
            speaker=speaker_name,
            conversation_history=conversation_history,
            style_prompt=final_round_prompt,
            topic=topic,
            ext_data=ext_data_original,  # Now always visible
            do_challenge=False,
            version=speaker_version,
            api_key=speaker_api_key
        )
        conversation_history.append(final_message)

    # === G) Write to output file ===
    output_filename = config_data.get('OUTPUT_FILE', 'conversation_output.txt')
    with open(output_filename, 'w', encoding='utf-8') as f:
        for line in conversation_history:
            f.write(line + "\n\n")

    print(f"Conversation simulation complete. Output written to: {output_filename}")


if __name__ == "__main__":
    main()
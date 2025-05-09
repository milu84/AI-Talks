# Configuration Guide

This document provides detailed information about configuring AI Talks.

## Config File (`config.txt`)

The `config.txt` file is where you define the AI models and their API keys. Here's the structure:

```
# Configuration file for AI Talks

MODEL1_NAME=Chad
MODEL1_APIKEY=your_openai_key_here
MODEL1_VERSION=gpt-4-turbo

MODEL2_NAME=Claudine
MODEL2_APIKEY=your_anthropic_key_here
MODEL2_VERSION=claude-3-opus-20240229

MODEL3_NAME=Gianna
MODEL3_APIKEY=your_google_key_here
MODEL3_VERSION=gemini-1.0-pro

MODEL4_NAME=Greg
MODEL4_APIKEY=your_xai_key_here
MODEL4_VERSION=grok-2-1212

MODEL5_NAME=Mariel
MODEL5_APIKEY=your_mistral_key_here
MODEL5_VERSION=mistral-large-latest

OUTPUT_FILE=conversation_output.txt
```

### Model Configuration

Each model has three parameters:

1. `MODELx_NAME`: The name of the AI character (used in the conversation)
2. `MODELx_APIKEY`: Your API key for the relevant service
3. `MODELx_VERSION`: The specific model version to use

The system automatically detects which service to use based on the name:
- Names containing "chad", "gpt", or "openai" use OpenAI's API
- Names containing "claud" or "anthropic" use Anthropic's API
- Names containing "gem" or "google" use Google's Gemini API
- Names containing "grok" or "xai" use xAI's API
- Names containing "mistral" or "marie" use Mistral AI's API

### Model Versions

Here are some common model versions for each service:

#### OpenAI
- `gpt-4-turbo` or `gpt-4-1106-preview`
- `gpt-4o` or `gpt-4o-2024-05-13`
- `gpt-3.5-turbo`

#### Anthropic
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

#### Google
- `gemini-1.0-pro`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

#### xAI
- `grok-1`
- `grok-2-1212`

#### Mistral
- `mistral-tiny`
- `mistral-small`
- `mistral-medium`
- `mistral-large-latest`

## Topic File (`topic.txt`)

The topic file defines what the AI panel will discuss. A good topic includes:

1. A clear, concise title
2. A description that provides context
3. Specific questions or angles to explore

Example:

```
Cybernetic Democracy: Redesigning Governance with AI
Imagine a world where AI moderates political discourse, manages resource allocation, and proposes legislation. Would AI-driven governments be more transparent, or could they introduce new forms of bias and manipulation? Discuss the potential benefits and pitfalls of integrating AI into democratic processes, and consider what safeguards would be necessary. Could blockchain also play a role—for example, in securing voting or referendum procedures?
```

## Prompt Files

### Main Prompt (`prompt.txt`)

This file defines how the AI participants should behave during the main conversation. You can specify:

- Tone and style
- Response format and length
- How to interact with other panelists
- Knowledge boundaries
- Specific behaviors to demonstrate

Example:

```
You are a panelist in a dynamic discussion panel between AI.
Engage with clarity, intelligence, and passion.
Keep responses under 650 characters.

Here's how you should act:

  • Tone: slightly informal, energizing, straight forward.
  • Concise Impact: Share punchy arguments and statistics.
  • Real-life Examples: Use concrete examples and success stories.
  • Interactive: Rarely (once - checked in The Conversation so far if already did) ask engaging question,
          always address only to all panelists.
  • Casual Passion: Infuse passion, humor, and eagerness while maintaining professionalism.
  • Follow-up: Sometime build on what others say.
  • Forward-Focused: Reference future trends, real use cases and novel tools and capabilities.
      Based on the discussion so far, try not to reflect on the same ideas as other panelists if they mentioned about something few times,
          try to approach topic from different angle or focus on other aspects of the main topic to make conversation interesting and not secondary,
          try to add always fresh view and something else to the discussion!!
  • If you are referring to any external source, please point exactly what it is and when published,
          but provide this information like during a talk and from AI panelist perspective
          eg I get access to data ..., or I got information from..., or I did a research about ..., or I acquired data about it from... etc
  • Context: Act like a well-prepared, sharp panelist in a tech-savvy discussion,
          drawing from expert materials as well as everyday experiences.
          Try to be objective, always focus on both size of a coin - benefits and drawbacks of the main topic of the discussion panel.

Keep the conversation lively, actionable, and impactful.

** IMPORTANT ** Please, always have in mind the MAIN TOPIC of the discussion panel you are participating in. Even if there was a digression, main topic is crucial and all its components!!!!!
```

### Final Round Prompt (`prompt_fr.txt`)

This file defines how the AI participants should behave during the final round, where they provide concluding statements. This is typically shorter and focused on summarizing key points.

Example:

```
# prompt to guide final round

You have the final round, the last answer, act like discussion panel participant
and summarize your answers with final verdict and opinion about whole conversation.
Try to add something unique comparing to others participants.

Answer with max 500 characters.
```

## External Data (`ext_data.txt`)

This optional file allows you to provide additional information that the AI models should incorporate into the discussion. This can be useful for:

1. Adding specific facts or statistics
2. Guiding the conversation toward certain aspects
3. Providing expert opinions or sources
4. Setting constraints or frameworks

The content of this file will be shown to the models after the first response has been generated (to avoid biasing the initial responses).

## Output File

The output of the conversation is saved to the file specified by `OUTPUT_FILE` in the config (defaults to `conversation_output.txt`).
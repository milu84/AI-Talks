# Obtaining API Keys

To use AI Talks, you'll need API keys for the AI models you want to include in your panel discussions. This guide explains how to get API keys for each supported service.

## OpenAI (GPT-4, GPT-3.5)

1. Go to [OpenAI's API platform](https://platform.openai.com/signup)
2. Create an account or log in
3. Navigate to the [API Keys page](https://platform.openai.com/api-keys)
4. Click "Create New Secret Key"
5. Name your key and copy it (you won't be able to see it again)
6. Add to config.txt as `MODEL1_APIKEY=your_key_here`

Note: OpenAI's API is paid, and you'll need to add credit to your account to use it.

## Anthropic (Claude)

1. Go to [Anthropic's Console](https://console.anthropic.com/)
2. Create an account or log in
3. Navigate to [API Keys](https://console.anthropic.com/settings/keys)
4. Create a new API key
5. Copy your key (you won't be able to see it again)
6. Add to config.txt as `MODEL2_APIKEY=your_key_here`

Note: Anthropic offers a free tier with limited usage, then requires payment.

## Google (Gemini)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API key" if you don't have one
4. Create a new API key
5. Copy your key
6. Add to config.txt as `MODEL3_APIKEY=your_key_here`

Note: Google offers a free tier for Gemini with usage limits.

## xAI (Grok)

1. Go to [xAI's Console](https://console.x.ai/)
2. Create an account (requires X/Twitter account)
3. Navigate to the API section
4. Generate a new API key
5. Copy your key
6. Add to config.txt as `MODEL4_APIKEY=your_key_here`

## Mistral AI

1. Go to [Mistral AI Platform](https://console.mistral.ai/)
2. Create an account or log in
3. Navigate to the API Keys section
4. Generate a new API key
5. Copy your key
6. Add to config.txt as `MODEL5_APIKEY=your_key_here`

Note: Mistral AI offers a free tier with limited usage.

## Protecting Your API Keys

**IMPORTANT**: Your API keys provide access to paid services. Treat them like passwords:

1. Never share your config.txt file with API keys included
2. Don't commit API keys to public repositories
3. If you're sharing configurations, use placeholders like `your_key_here`
4. Consider using environment variables for production use

Before publishing your project to GitHub or any public repository, make sure to remove all API keys from your config files.
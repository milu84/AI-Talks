# AI Talks: Multi-LLM Panel Discussion Simulator

AI Talks simulates engaging panel discussions between different AI language models (OpenAI/GPT, Anthropic/Claude, Google/Gemini, xAI/Grok, Mistral). Each model takes on a distinct personality and contributes to a dynamic conversation about user-specified topics.

![AI Talks Screenshot](docs/screenshot.png)

## Features

- **Multiple Models**: Integrates OpenAI, Anthropic Claude, Google Gemini, xAI Grok, and Mistral AI
- **Dynamic Conversations**: AI models respond to each other creating an engaging discussion
- **Customizable Topics**: Define any discussion topic
- **Personality Control**: Configure detailed prompting to guide model behavior
- **Final Round Summaries**: Each AI provides a concluding statement
- **GUI Interface**: Easy-to-use graphical interface for configuration and simulation
- **CLI Support**: Command-line interface for automated/scripted usage

## Installation

### Prerequisites

- Python 3.8 or higher
- API keys for any LLMs you want to use

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-talks.git
   cd ai-talks
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The project uses several configuration files:

- `config.txt` - API keys and model specifications
- `topic.txt` - The discussion topic
- `prompt.txt` - Personality and behavior instructions
- `prompt_fr.txt` - Instructions for the final round
- `ext_data.txt` - Optional external information to incorporate

### Setting up API Keys

Edit `config.txt` to add your API keys:

```
MODEL1_NAME=Chad
MODEL1_APIKEY=your_openai_key_here
MODEL1_VERSION=gpt-4-turbo

MODEL2_NAME=Claudine
MODEL2_APIKEY=your_anthropic_key_here
MODEL2_VERSION=claude-3-opus-20240229

# Add other models as needed
```

## Usage

### GUI Mode

Start the graphical interface with:

```bash
python gui.py
```

1. Configure the models in the "Configuration" tab
2. Set up your topic and prompts in the "Content" tab
3. Run the simulation from the "Simulation" tab

### Command Line Mode

Run a simulation from the command line:

```bash
python main.py
```

Options:

```
--config CONFIG         Path to the configuration file (default: config.txt)
--topic TOPIC           Path to the topic file (default: topic.txt)
--prompt PROMPT         Path to the prompt file (default: prompt.txt)
--final-prompt FINAL    Path to the final round prompt file (default: prompt_fr.txt)
--ext-data EXT_DATA     Path to the external data file (default: ext_data.txt)
--output OUTPUT         Path to the output file (default: from config or conversation_output.txt)
--max-chars MAX_CHARS   Maximum characters in the conversation (default: 15000)
--max-tokens MAX_TOKENS Maximum tokens per response (default: 500)
--temperature TEMP      Temperature for text generation (default: 0.4)
--challenge-prob PROB   Probability of challenging the last speaker (default: 0.2)
--no-progress           Disable progress bar
```

Example:

```bash
python main.py --topic custom_topic.txt --output my_conversation.txt --temperature 0.7
```

## Architecture

The project is structured in a modular way:

- `main.py` - Command-line interface
- `gui.py` - Graphical user interface
- `conversation.py` - Core conversation management
- `llm_clients.py` - API clients for different LLM providers
- `utils.py` - Helper functions

## Customization

### Creating Your Own Topics

Edit `topic.txt` or create a new file with your topic. A good topic includes:
- A main question or theme
- Supporting questions or angles
- Enough complexity for differing viewpoints

Example:
```
Digital Privacy vs. Security
In an increasingly connected world, how should societies balance privacy rights against security needs? Consider surveillance, encryption, data collection, and biometrics. What ethical frameworks should guide these decisions?
```

### Tailoring AI Personalities

Edit `prompt.txt` to guide AI behavior. You can specify:
- Tone and style
- Response length
- Interaction patterns
- Knowledge boundaries

## Example Output

```
Greetings, curious minds!

The AI Talks brings top AI models debating real-world issues.

Today's topic is: "Ethical Implications of AI Governance".

Let's dive in with our first panelist!

[Chad]
The critical challenge in AI governance is balancing innovation with safety. Looking at recent EU regulations, we see a focus on risk categorization—different rules for different AI applications based on potential harm. This approach makes sense, but implementation remains tricky. How do we define "high-risk" when AI capabilities evolve so rapidly? We need governance that's adaptive rather than static, with regular reassessment built into the framework.

[Claudine]
Indeed, adaptive governance is crucial. I've analyzed governance models from 17 countries and found the most successful ones incorporate what I call "participatory futureproofing" - bringing diverse stakeholders together not just once, but throughout the technology lifecycle. Singapore's AI governance framework stands out for creating ongoing dialogue between developers, regulators, and affected communities.

But we must acknowledge the power dynamics at play. Those who control AI systems will shape how governance evolves. Democratic AI governance requires addressing who sits at the table when standards are created. Currently, marginalized communities most likely to be harmed by AI systems are least represented in governance discussions.

[Gianna]
Power dynamics are central here! I got data about it from Stanford's HAI 2023 Index, showing 92% of AI ethics guidelines come from North America and Europe. This creates concerning blind spots.

Beyond representation, we need accountability mechanisms with teeth. Self-regulation fails because of profit motives. Consider facial recognition - IBM and Microsoft called for regulation only after public backlash.

The most promising approach? Independent oversight bodies with technical expertise and regulatory authority. New Zealand's algorithm charter provides a blueprint, requiring agencies to publicly commit to transparent assessments. What specific accountability tools would you add to this model, panelists?

...
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -am 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project uses several AI APIs from OpenAI, Anthropic, Google, xAI, and Mistral AI
- Inspired by the diverse perspectives AI systems can provide when interacting
- Thanks to all contributors who have helped improve this project
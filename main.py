#!/usr/bin/env python3
"""
AI Talks - Panel Discussion Simulator
A command-line tool that simulates a panel discussion between different AI language models.
"""

import random
import sys
import threading
import time
import argparse
import os

from utils import read_file, write_file, parse_config, load_models_from_config, get_default_models
from conversation import ConversationManager

# Configuration defaults
DEFAULT_MAX_CHARACTERS = 15000
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.4
DEFAULT_CHALLENGE_PROBABILITY = 0.2
DEFAULT_OUTPUT_FILE = "conversation_output.txt"


def setup_argument_parser():
    """Configure command-line argument parsing"""
    parser = argparse.ArgumentParser(
        description="AI Talks - Simulate a panel discussion between AI language models"
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="config.txt",
        help="Path to the configuration file (default: config.txt)"
    )
    
    parser.add_argument(
        "--topic", 
        type=str, 
        default="topic.txt",
        help="Path to the topic file (default: topic.txt)"
    )
    
    parser.add_argument(
        "--prompt", 
        type=str, 
        default="prompt.txt",
        help="Path to the prompt file (default: prompt.txt)"
    )
    
    parser.add_argument(
        "--final-prompt", 
        type=str, 
        default="prompt_fr.txt",
        help="Path to the final round prompt file (default: prompt_fr.txt)"
    )
    
    parser.add_argument(
        "--ext-data", 
        type=str, 
        default="ext_data.txt",
        help="Path to the external data file (default: ext_data.txt)"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        default=None,
        help="Path to the output file (default: from config or conversation_output.txt)"
    )
    
    parser.add_argument(
        "--max-chars", 
        type=int, 
        default=DEFAULT_MAX_CHARACTERS,
        help=f"Maximum characters in the conversation (default: {DEFAULT_MAX_CHARACTERS})"
    )
    
    parser.add_argument(
        "--max-tokens", 
        type=int, 
        default=DEFAULT_MAX_TOKENS,
        help=f"Maximum tokens per response (default: {DEFAULT_MAX_TOKENS})"
    )
    
    parser.add_argument(
        "--temperature", 
        type=float, 
        default=DEFAULT_TEMPERATURE,
        help=f"Temperature for text generation (default: {DEFAULT_TEMPERATURE})"
    )
    
    parser.add_argument(
        "--challenge-prob", 
        type=float, 
        default=DEFAULT_CHALLENGE_PROBABILITY,
        help=f"Probability of challenging the last speaker (default: {DEFAULT_CHALLENGE_PROBABILITY})"
    )
    
    parser.add_argument(
        "--no-progress", 
        action="store_true",
        help="Disable progress bar"
    )
    
    return parser


def print_progress_bar(progress, total_width=50):
    """Print a simple ASCII progress bar"""
    filled_width = int(total_width * progress / 100)
    bar = '█' * filled_width + '░' * (total_width - filled_width)
    sys.stdout.write(f"\r|{bar}| {progress:.1f}% ")
    sys.stdout.flush()


def on_message_generated(message):
    """Callback for when a new message is generated"""
    # Print the message
    print("\n" + message + "\n")


def on_progress_update(progress):
    """Callback for when progress is updated"""
    # Update the progress bar
    print_progress_bar(progress)


def on_status_change(status):
    """Callback for when the simulation status changes"""
    # Print the status
    sys.stdout.write(f"\n{status}\n")
    sys.stdout.flush()


def main():
    # Parse command-line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    try:
        # === A) Read configuration from config file ===
        try:
            config_text = read_file(args.config)
            config_data = parse_config(config_text)
        except FileNotFoundError:
            print(f"Warning: Config file {args.config} not found. Using defaults.")
            config_data = {}
        
        # === B) Load model definitions dynamically from config ===
        models_list = load_models_from_config(config_data)
        
        # Provide defaults if config is empty
        if not models_list:
            print("No models found in config. Using default models.")
            models_list = get_default_models()
        
        # === C) Read topic, style prompt, and final-round prompt ===
        try:
            topic = read_file(args.topic).strip()
        except FileNotFoundError:
            print(f"Error: Topic file {args.topic} not found.")
            return 1
        
        try:
            style_prompt = read_file(args.prompt).strip()
        except FileNotFoundError:
            print(f"Error: Prompt file {args.prompt} not found.")
            return 1
        
        try:
            final_round_prompt = read_file(args.final_prompt).strip()
        except FileNotFoundError:
            print(f"Error: Final round prompt file {args.final_prompt} not found.")
            return 1
        
        # Try to read external data, but it's optional
        try:
            ext_data = read_file(args.ext_data).strip()
        except FileNotFoundError:
            print(f"Warning: External data file {args.ext_data} not found. Proceeding without it.")
            ext_data = ""
        
        # === D) Determine output file ===
        output_file = args.output
        if not output_file:
            output_file = config_data.get("OUTPUT_FILE", DEFAULT_OUTPUT_FILE)
        
        # === E) Create and configure the conversation manager ===
        conversation = ConversationManager(
            models_list=models_list,
            topic=topic,
            style_prompt=style_prompt,
            final_round_prompt=final_round_prompt,
            ext_data=ext_data,
            max_characters=args.max_chars,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            challenge_probability=args.challenge_prob
        )
        
        # Set up callbacks
        conversation.on_message = on_message_generated
        
        if not args.no_progress:
            conversation.on_progress = on_progress_update
            
        conversation.on_status = on_status_change
        
        # === F) Run the simulation ===
        print(f"\nAI Talks - Panel Discussion Simulator")
        print(f"Topic: {topic}")
        print(f"Models: {', '.join([model['name'] for model in models_list])}")
        print(f"Output file: {output_file}")
        print("\nStarting simulation...\n")
        
        # Run the simulation in the main thread
        conversation_history = conversation.start_simulation()
        
        # === G) Write to output file ===
        conversation.write_to_file(output_file)
        
        print(f"\nConversation simulation complete. Output written to: {output_file}")
        return 0
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        return 130
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
import re
import random
from llm_clients import create_llm_client


class ConversationManager:
    """Manages the full conversation simulation between AI models"""
    
    def __init__(self, 
                 models_list, 
                 topic, 
                 style_prompt, 
                 final_round_prompt, 
                 ext_data="",
                 max_characters=15000, 
                 max_tokens=500, 
                 temperature=0.4,
                 challenge_probability=0.2):
        # Configuration
        self.models_list = models_list
        self.topic = topic
        self.style_prompt = style_prompt
        self.final_round_prompt = final_round_prompt
        self.ext_data_original = ext_data.strip()
        self.max_total_characters = max_characters
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.challenge_probability = challenge_probability
        
        # State
        self.conversation_history = []
        self.total_characters = 0
        self.discussion_started = False
        self.last_speaker = None
        self.simulation_running = False
        
        # Callbacks
        self.on_message = None  # Called when a new message is added
        self.on_progress = None  # Called when progress is updated
        self.on_status = None  # Called when status changes
    
    def initialize_conversation(self):
        """Set up the initial conversation state"""
        self.conversation_history = []
        self.total_characters = 0
        self.discussion_started = False
        self.last_speaker = None
        
        # Build an introduction text
        intro_lines = [
            "Greetings, curious minds!\n",
            "The AI Talks brings top AI models debating real-world issues.\n",
            f"Today's topic is: \"{self.topic}\".\n",
            "Let's dive in with our first panelist!"
        ]
        
        intro_text = "\n".join(intro_lines)
        self.add_message(intro_text)
        
        return intro_text
    
    def add_message(self, message):
        """Add a message to the conversation history"""
        self.conversation_history.append(message)
        self.total_characters += len(message)
        
        if self.on_message:
            self.on_message(message)
    
    def sanitize_output(self, response_text, speaker):
        """
        Removes any leading bracketed prefix or 'Speaker:' text if it appears in `response_text`.
        Ensures we only show exactly one '[Speaker]:' at the start.
        """
        # Build possible prefixes
        bracket_prefix = f"[{speaker}]:"
        colon_prefix = f"{speaker}:"
        
        # Regex to remove up to two duplicates if they appear
        pattern = r'^(?:\[' + re.escape(speaker) + r'\]:\s*)?(?:\[' + re.escape(speaker) + r'\]:\s*)?(?:' + re.escape(
            speaker) + r':\s*)?(.*)$'
        match = re.match(pattern, response_text, re.IGNORECASE)
        if match:
            response_text = match.group(1).strip()
        
        return response_text
    
    def generate_prompt(self, speaker, is_final_round=False, do_challenge=False):
        """Create the prompt for the current state of the conversation"""
        # Combine the entire conversation history into a single text block
        context_text = "\n".join(self.conversation_history)
        
        # Choose which prompt to use based on whether it's the final round
        current_prompt = self.final_round_prompt if is_final_round else self.style_prompt
        
        # Add challenge fragment if requested
        challenge_fragment = ""
        if do_challenge:
            challenge_fragment = "Please challenge or question the last point made."
        
        # Only add external data if it's not empty and discussion has started or it's final round
        should_include_ext_data = self.ext_data_original and (self.discussion_started or is_final_round)
        external_data_string = ""
        if should_include_ext_data:
            external_data_string = (
                "***** Here is additional, external data and additional guidelines for you! ***** \n\n"
                f": {self.ext_data_original}\n\n\n"
            )
        
        # Build the full prompt
        user_prompt = (
            f"{current_prompt}\n\n"
            f">>>>> Discussion topic: {self.topic} <<<<<\n\n\n"
            f"****** The Conversation so far: ******\n\n"
            f"{context_text}\n\n"
            f"****** End of The Conversation ******\n\n\n"
            f"{challenge_fragment}\n\n\n"
            f"{external_data_string}"
            f"Please continue the conversation.\n\n"
            f"**Important**: Do NOT prefix your output with your name or any bracketed speaker info. "
            f"Simply provide your response in plain text.\n"
            f"You are the speaker named {speaker}, but do NOT start your response with '[{speaker}]'.\n"
        )
        
        return user_prompt
    
    def generate_response(self, speaker_info, is_final_round=False, do_challenge=False):
        """Generate a response from a specific AI model"""
        speaker_name = speaker_info['name']
        speaker_api_key = speaker_info['apikey']
        speaker_version = speaker_info['version']
        
        # Update status if callback exists
        if self.on_status:
            self.on_status(f"Generating response from {speaker_name}...")
        
        # Create the prompt
        prompt_text = self.generate_prompt(speaker_name, is_final_round, do_challenge)
        
        # Create the appropriate client using our factory
        llm_client = create_llm_client(
            provider=speaker_name,
            api_key=speaker_api_key,
            model_version=speaker_version
        )
        
        # Generate the response
        response = llm_client.generate(
            prompt=prompt_text, 
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        # Get the text from the response
        response_text = str(response)
        
        # Post-process the text to remove any accidental prefix,
        # then add our single "[Speaker]:"
        cleaned_response = self.sanitize_output(response_text, speaker_name)
        formatted_response = f"[{speaker_name}]\n{cleaned_response}"
        
        return formatted_response
    
    def run_conversation_round(self):
        """Run a single round of conversation with all models"""
        if not self.simulation_running:
            return False
        
        # Create a random permutation of the entire list
        speaker_batch = self.models_list[:]
        random.shuffle(speaker_batch)
        
        # If the first in the batch is the same as last_speaker, reshuffle to avoid duplicates
        max_reshuffles = 10
        reshuffle_count = 0
        while (self.last_speaker is not None and 
               speaker_batch[0]['name'] == self.last_speaker and 
               reshuffle_count < max_reshuffles):
            random.shuffle(speaker_batch)
            reshuffle_count += 1
        
        for speaker_info in speaker_batch:
            if not self.simulation_running:
                return False
            
            # Decide whether to challenge
            do_challenge = random.random() < self.challenge_probability
            
            # Generate the response
            response = self.generate_response(speaker_info, False, do_challenge)
            
            # Once the first speaker has spoken, set the flag
            if not self.discussion_started:
                self.discussion_started = True
            
            # Check if we've reached the maximum character limit
            if self.total_characters + len(response) > self.max_total_characters:
                return False
            
            # Add the response to the conversation
            self.add_message(response)
            self.last_speaker = speaker_info['name']
            
            # Update progress if callback exists
            if self.on_progress:
                progress = (self.total_characters / self.max_total_characters) * 80  # 80% of progress
                self.on_progress(progress)
        
        return True  # Return True if the round completed successfully
    
    def run_final_round(self):
        """Run the final round where each model gives a concluding statement"""
        if not self.simulation_running:
            return False
        
        # Add the final round marker
        final_round_marker = "FINAL ROUND"
        self.add_message(final_round_marker)
        
        # Have each model give a final statement
        for i, model_info in enumerate(self.models_list):
            if not self.simulation_running:
                return False
            
            # Generate the final response
            final_message = self.generate_response(model_info, is_final_round=True)
            self.add_message(final_message)
            
            # Update progress if callback exists
            if self.on_progress:
                progress = 80 + ((i + 1) / len(self.models_list)) * 20  # Last 20% of progress
                self.on_progress(progress)
        
        return True
    
    def start_simulation(self):
        """Start the full conversation simulation process"""
        self.simulation_running = True
        
        # Initialize the conversation
        self.initialize_conversation()
        
        # Update status if callback exists
        if self.on_status:
            self.on_status("Simulation started...")
        
        # Run conversation rounds until we hit the character limit
        while self.total_characters < self.max_total_characters and self.simulation_running:
            if not self.run_conversation_round():
                break
        
        # Run the final round if we're still running
        if self.simulation_running:
            self.run_final_round()
            
            # Update status when complete
            if self.on_status:
                self.on_status("Simulation complete!")
                
            # Update progress to 100%
            if self.on_progress:
                self.on_progress(100)
        
        self.simulation_running = False
        return self.conversation_history
    
    def stop_simulation(self):
        """Stop the running simulation"""
        self.simulation_running = False
        
        # Update status if callback exists
        if self.on_status:
            self.on_status("Simulation stopped by user.")
    
    def write_to_file(self, filename):
        """Write the conversation to a file"""
        with open(filename, 'w', encoding='utf-8') as f:
            for line in self.conversation_history:
                f.write(line + "\n\n")
        
        return filename
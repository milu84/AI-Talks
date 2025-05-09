import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import threading
import sys
from main import read_file, parse_config, load_models_from_config, generate_response, LLM_MAX_CHARACTERS, LLM_MAX_TOKENS

class AITalksGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Talks - Panel Discussion Simulator")
        self.root.geometry("1000x700")
        
        # Configuration variables
        self.config_data = {}
        self.models_list = []
        self.conversation_history = []
        self.total_characters = 0
        self.topic = ""
        self.style_prompt = ""
        self.final_round_prompt = ""
        self.ext_data = ""
        self.discussion_started = False
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_config_tab()
        self.setup_content_tab()
        self.setup_simulation_tab()
        
        # Load existing configuration if available
        self.load_config()
        
        # Load default content
        self.load_default_content()
        
    def setup_config_tab(self):
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="1. Configuration")
        
        # Models section
        models_frame = ttk.LabelFrame(config_frame, text="AI Models Configuration")
        models_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Model entries container with scrolling
        models_canvas = tk.Canvas(models_frame)
        scrollbar = ttk.Scrollbar(models_frame, orient="vertical", command=models_canvas.yview)
        scrollable_frame = ttk.Frame(models_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: models_canvas.configure(scrollregion=models_canvas.bbox("all"))
        )
        
        models_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        models_canvas.configure(yscrollcommand=scrollbar.set)
        
        models_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create entries for 5 models
        self.model_entries = []
        for i in range(5):
            model_frame = ttk.Frame(scrollable_frame)
            model_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(model_frame, text=f"Model {i+1}:").grid(row=0, column=0, padx=5, pady=5)
            
            name_frame = ttk.Frame(model_frame)
            name_frame.grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(name_frame, text="Name:").pack(side=tk.LEFT)
            name_entry = ttk.Entry(name_frame, width=15)
            name_entry.pack(side=tk.LEFT, padx=5)
            
            api_frame = ttk.Frame(model_frame)
            api_frame.grid(row=0, column=2, padx=5, pady=5)
            ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT)
            api_entry = ttk.Entry(api_frame, width=30, show="*")
            api_entry.pack(side=tk.LEFT, padx=5)
            
            version_frame = ttk.Frame(model_frame)
            version_frame.grid(row=0, column=3, padx=5, pady=5)
            ttk.Label(version_frame, text="Version:").pack(side=tk.LEFT)
            version_entry = ttk.Entry(version_frame, width=15)
            version_entry.pack(side=tk.LEFT, padx=5)
            
            self.model_entries.append({
                'name': name_entry,
                'apikey': api_entry,
                'version': version_entry
            })
        
        # Output file setting
        output_frame = ttk.Frame(config_frame)
        output_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(output_frame, text="Output File:").pack(side=tk.LEFT, padx=5)
        self.output_file_entry = ttk.Entry(output_frame, width=30)
        self.output_file_entry.pack(side=tk.LEFT, padx=5)
        self.output_file_entry.insert(0, "conversation_output.txt")
        
        # Save config button
        save_btn = ttk.Button(config_frame, text="Save Configuration", command=self.save_config)
        save_btn.pack(pady=20)
        
    def setup_content_tab(self):
        content_frame = ttk.Frame(self.notebook)
        self.notebook.add(content_frame, text="2. Content")
        
        # Topic section
        topic_frame = ttk.LabelFrame(content_frame, text="Discussion Topic")
        topic_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.topic_text = scrolledtext.ScrolledText(topic_frame, height=4)
        self.topic_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Style prompt section
        style_frame = ttk.LabelFrame(content_frame, text="Style Prompt")
        style_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.style_text = scrolledtext.ScrolledText(style_frame, height=8)
        self.style_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Final round prompt section
        final_frame = ttk.LabelFrame(content_frame, text="Final Round Prompt")
        final_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.final_text = scrolledtext.ScrolledText(final_frame, height=4)
        self.final_text.pack(fill=tk.X, padx=5, pady=5)
        
        # External data section
        ext_frame = ttk.LabelFrame(content_frame, text="External Data (Optional)")
        ext_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.ext_text = scrolledtext.ScrolledText(ext_frame, height=4)
        self.ext_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons for content management
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        load_btn = ttk.Button(btn_frame, text="Load from Files", command=self.load_content_from_files)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(btn_frame, text="Save to Files", command=self.save_content_to_files)
        save_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_simulation_tab(self):
        sim_frame = ttk.Frame(self.notebook)
        self.notebook.add(sim_frame, text="3. Simulation")
        
        # Controls frame
        controls_frame = ttk.Frame(sim_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Parameters
        param_frame = ttk.LabelFrame(controls_frame, text="Simulation Parameters")
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Character limit
        char_frame = ttk.Frame(param_frame)
        char_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(char_frame, text="Max Characters:").pack(side=tk.LEFT, padx=5)
        self.char_limit_var = tk.StringVar(value=str(LLM_MAX_CHARACTERS))
        char_entry = ttk.Entry(char_frame, textvariable=self.char_limit_var, width=10)
        char_entry.pack(side=tk.LEFT, padx=5)
        
        # Token limit
        token_frame = ttk.Frame(param_frame)
        token_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(token_frame, text="Max Tokens per Response:").pack(side=tk.LEFT, padx=5)
        self.token_limit_var = tk.StringVar(value=str(LLM_MAX_TOKENS))
        token_entry = ttk.Entry(token_frame, textvariable=self.token_limit_var, width=10)
        token_entry.pack(side=tk.LEFT, padx=5)
        
        # Challenge probability
        challenge_frame = ttk.Frame(param_frame)
        challenge_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(challenge_frame, text="Challenge Probability (0-1):").pack(side=tk.LEFT, padx=5)
        self.challenge_var = tk.StringVar(value="0.2")
        challenge_entry = ttk.Entry(challenge_frame, textvariable=self.challenge_var, width=10)
        challenge_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=15)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Simulation", command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Output display
        output_frame = ttk.LabelFrame(sim_frame, text="Conversation Output")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress indicator
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(sim_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, padx=10, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(sim_frame, textvariable=self.status_var)
        status_label.pack(padx=10, pady=5)
        
    def load_config(self):
        """Load configuration from config.txt if it exists"""
        try:
            config_text = read_file('config.txt')
            self.config_data = parse_config(config_text)
            
            # Load model data
            self.models_list = load_models_from_config(self.config_data)
            
            # Fill in the form with the loaded data
            for i, model_info in enumerate(self.models_list):
                if i < len(self.model_entries):
                    self.model_entries[i]['name'].delete(0, tk.END)
                    self.model_entries[i]['name'].insert(0, model_info['name'])
                    
                    self.model_entries[i]['apikey'].delete(0, tk.END)
                    self.model_entries[i]['apikey'].insert(0, model_info['apikey'] or "")
                    
                    self.model_entries[i]['version'].delete(0, tk.END)
                    self.model_entries[i]['version'].insert(0, model_info['version'] or "")
            
            # Set output file
            if 'OUTPUT_FILE' in self.config_data:
                self.output_file_entry.delete(0, tk.END)
                self.output_file_entry.insert(0, self.config_data['OUTPUT_FILE'])
                
            messagebox.showinfo("Configuration Loaded", "Existing configuration loaded successfully.")
            
        except FileNotFoundError:
            messagebox.showinfo("Configuration", "No existing configuration found. Using defaults.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def save_config(self):
        """Save configuration to config.txt"""
        try:
            # Build configuration data from form
            config_lines = ["# config.txt\n"]
            
            # Add models
            for i, entry in enumerate(self.model_entries):
                name = entry['name'].get().strip()
                apikey = entry['apikey'].get().strip()
                version = entry['version'].get().strip()
                
                # Only add if at least the name is provided
                if name:
                    config_lines.append(f"MODEL{i+1}_NAME={name}")
                    if apikey:
                        config_lines.append(f"MODEL{i+1}_APIKEY={apikey}")
                    if version:
                        config_lines.append(f"MODEL{i+1}_VERSION={version}")
            
            # Add output file
            output_file = self.output_file_entry.get().strip()
            if output_file:
                config_lines.append(f"OUTPUT_FILE={output_file}")
            
            # Write to config.txt
            with open('config.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(config_lines))
            
            messagebox.showinfo("Success", "Configuration saved successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def load_default_content(self):
        """Load default content from text files without showing message boxes"""
        try:
            # Load topic
            if os.path.exists('topic.txt'):
                self.topic = read_file('topic.txt').strip()
                self.topic_text.delete('1.0', tk.END)
                self.topic_text.insert('1.0', self.topic)
            
            # Load style prompt
            if os.path.exists('prompt.txt'):
                self.style_prompt = read_file('prompt.txt').strip()
                self.style_text.delete('1.0', tk.END)
                self.style_text.insert('1.0', self.style_prompt)
            
            # Load final round prompt
            if os.path.exists('prompt_fr.txt'):
                self.final_round_prompt = read_file('prompt_fr.txt').strip()
                self.final_text.delete('1.0', tk.END)
                self.final_text.insert('1.0', self.final_round_prompt)
            
            # Load external data
            if os.path.exists('ext_data.txt'):
                self.ext_data = read_file('ext_data.txt').strip()
                self.ext_text.delete('1.0', tk.END)
                self.ext_text.insert('1.0', self.ext_data)
            
        except Exception as e:
            print(f"Failed to load default content: {e}")
            
    def load_content_from_files(self):
        """Load content from text files with user notification"""
        try:
            # Load topic
            if os.path.exists('topic.txt'):
                self.topic = read_file('topic.txt').strip()
                self.topic_text.delete('1.0', tk.END)
                self.topic_text.insert('1.0', self.topic)
            
            # Load style prompt
            if os.path.exists('prompt.txt'):
                self.style_prompt = read_file('prompt.txt').strip()
                self.style_text.delete('1.0', tk.END)
                self.style_text.insert('1.0', self.style_prompt)
            
            # Load final round prompt
            if os.path.exists('prompt_fr.txt'):
                self.final_round_prompt = read_file('prompt_fr.txt').strip()
                self.final_text.delete('1.0', tk.END)
                self.final_text.insert('1.0', self.final_round_prompt)
            
            # Load external data
            if os.path.exists('ext_data.txt'):
                self.ext_data = read_file('ext_data.txt').strip()
                self.ext_text.delete('1.0', tk.END)
                self.ext_text.insert('1.0', self.ext_data)
            
            messagebox.showinfo("Content Loaded", "Content loaded successfully from files.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load content: {e}")
    
    def save_content_to_files(self):
        """Save content to text files"""
        try:
            # Save topic
            with open('topic.txt', 'w', encoding='utf-8') as f:
                f.write(self.topic_text.get('1.0', tk.END))
            
            # Save style prompt
            with open('prompt.txt', 'w', encoding='utf-8') as f:
                f.write(self.style_text.get('1.0', tk.END))
            
            # Save final round prompt
            with open('prompt_fr.txt', 'w', encoding='utf-8') as f:
                f.write(self.final_text.get('1.0', tk.END))
            
            # Save external data
            with open('ext_data.txt', 'w', encoding='utf-8') as f:
                f.write(self.ext_text.get('1.0', tk.END))
            
            messagebox.showinfo("Content Saved", "Content saved successfully to files.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save content: {e}")
    
    def update_output(self, message):
        """Update the output text widget"""
        self.output_text.insert(tk.END, message + "\n\n")
        self.output_text.see(tk.END)
        
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_var.set(value)
        
    def update_status(self, status):
        """Update the status label"""
        self.status_var.set(status)
    
    def start_simulation(self):
        """Start the conversation simulation"""
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.update_status("Simulation started...")
        self.update_progress(0)
        
        # Get simulation parameters
        try:
            max_chars = int(self.char_limit_var.get())
            max_tokens = int(self.token_limit_var.get())
            challenge_prob = float(self.challenge_var.get())
        except ValueError:
            messagebox.showerror("Invalid Parameters", "Please enter valid numbers for simulation parameters.")
            self.reset_simulation_controls()
            return
        
        # Get content from UI
        self.topic = self.topic_text.get('1.0', tk.END).strip()
        self.style_prompt = self.style_text.get('1.0', tk.END).strip()
        self.final_round_prompt = self.final_text.get('1.0', tk.END).strip()
        self.ext_data = self.ext_text.get('1.0', tk.END).strip()
        
        # Get model configuration
        self.models_list = []
        for entry in self.model_entries:
            name = entry['name'].get().strip()
            apikey = entry['apikey'].get().strip()
            version = entry['version'].get().strip()
            
            if name:
                self.models_list.append({
                    'name': name,
                    'apikey': apikey,
                    'version': version
                })
        
        # Check if we have the minimum requirements
        if not self.topic:
            messagebox.showerror("Missing Content", "Please provide a discussion topic.")
            self.reset_simulation_controls()
            return
            
        if not self.models_list:
            messagebox.showerror("Missing Models", "Please configure at least one AI model.")
            self.reset_simulation_controls()
            return
            
        # Save configuration and content to files before starting
        self.save_config()
        self.save_content_to_files()
        
        # Start simulation thread
        self.simulation_running = True
        simulation_thread = threading.Thread(target=self.run_simulation, 
                                            args=(max_chars, max_tokens, challenge_prob))
        simulation_thread.daemon = True
        simulation_thread.start()
    
    def run_simulation(self, max_chars, max_tokens, challenge_prob):
        """Run the conversation simulation in a separate thread"""
        try:
            # Reset simulation variables
            self.conversation_history = []
            self.total_characters = 0
            self.discussion_started = False
            
            # Build an introduction text
            intro_lines = [
                "Greetings, curious minds!\n",
                "The AI Talks brings top AI models debating real-world issues.\n",
                f"Today's topic is: \"{self.topic}\".\n",
                "Let's dive in with our first panelist!"
            ]
            
            intro_text = "\n".join(intro_lines)
            self.conversation_history.append(intro_text)
            self.total_characters += len(intro_text)
            
            # Update UI
            self.root.after(0, self.update_output, intro_text)
            
            # Track the last speaker in the previous round
            last_speaker = None
            
            # Conversation Loop
            import random
            while self.total_characters < max_chars and self.simulation_running:
                # Create a random permutation of the entire list
                speaker_batch = self.models_list[:]
                random.shuffle(speaker_batch)
                
                # If the first in the batch is the same as last_speaker, reshuffle to avoid duplicates.
                max_reshuffles = 10
                reshuffle_count = 0
                while last_speaker is not None and speaker_batch[0]['name'] == last_speaker and reshuffle_count < max_reshuffles:
                    random.shuffle(speaker_batch)
                    reshuffle_count += 1
                
                for speaker_info in speaker_batch:
                    if not self.simulation_running:
                        break
                        
                    speaker_name = speaker_info['name']
                    speaker_api_key = speaker_info['apikey']
                    speaker_version = speaker_info['version']
                    
                    # Update status
                    self.root.after(0, self.update_status, f"Generating response from {speaker_name}...")
                    
                    # Random chance of "challenge"
                    do_challenge = (random.random() < challenge_prob)
                    
                    # Only pass ext_data after the discussion has started
                    current_ext_data = self.ext_data if self.discussion_started else ""
                    
                    # Generate response
                    response = generate_response(
                        speaker=speaker_name,
                        conversation_history=self.conversation_history,
                        style_prompt=self.style_prompt,
                        topic=self.topic,
                        ext_data=current_ext_data,
                        do_challenge=do_challenge,
                        version=speaker_version,
                        api_key=speaker_api_key
                    )
                    
                    # Once the first speaker has spoken, set the flag
                    if not self.discussion_started:
                        self.discussion_started = True
                    
                    if self.total_characters + len(response) > max_chars:
                        break
                    
                    self.conversation_history.append(response)
                    self.total_characters += len(response)
                    last_speaker = speaker_name
                    
                    # Update UI
                    self.root.after(0, self.update_output, response)
                    self.root.after(0, self.update_progress, 
                                  (self.total_characters / max_chars) * 80)  # 80% of progress
                
                if not self.simulation_running:
                    break
            
            # Final Round if simulation is still running
            if self.simulation_running:
                final_round_marker = f"FINAL ROUND"
                self.conversation_history.append(final_round_marker)
                self.total_characters += len(final_round_marker)
                
                # Update UI
                self.root.after(0, self.update_output, final_round_marker)
                
                for i, model_info in enumerate(self.models_list):
                    if not self.simulation_running:
                        break
                        
                    speaker_name = model_info['name']
                    speaker_api_key = model_info['apikey']
                    speaker_version = model_info['version']
                    
                    # Update status
                    self.root.after(0, self.update_status, 
                                  f"Generating final response from {speaker_name}...")
                    
                    # During final round, external data should be visible
                    final_message = generate_response(
                        speaker=speaker_name,
                        conversation_history=self.conversation_history,
                        style_prompt=self.final_round_prompt,
                        topic=self.topic,
                        ext_data=self.ext_data,
                        do_challenge=False,
                        version=speaker_version,
                        api_key=speaker_api_key
                    )
                    
                    self.conversation_history.append(final_message)
                    
                    # Update UI
                    self.root.after(0, self.update_output, final_message)
                    self.root.after(0, self.update_progress, 
                                  80 + ((i + 1) / len(self.models_list)) * 20)  # Last 20% of progress
                
                # Write to output file
                output_filename = self.output_file_entry.get().strip()
                if not output_filename:
                    output_filename = "conversation_output.txt"
                    
                with open(output_filename, 'w', encoding='utf-8') as f:
                    for line in self.conversation_history:
                        f.write(line + "\n\n")
                
                # Update final status
                self.root.after(0, self.update_status, 
                              f"Simulation complete. Output written to: {output_filename}")
                self.root.after(0, self.update_progress, 100)
            else:
                self.root.after(0, self.update_status, "Simulation stopped by user")
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Simulation error: {str(e)}")
            self.root.after(0, self.update_status, f"Error: {str(e)}")
        
        finally:
            # Reset UI
            self.root.after(0, self.reset_simulation_controls)
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.simulation_running = False
        self.update_status("Stopping simulation...")
    
    def reset_simulation_controls(self):
        """Reset simulation controls"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = AITalksGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
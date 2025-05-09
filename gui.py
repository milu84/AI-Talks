#!/usr/bin/env python3
"""
AI Talks - Panel Discussion Simulator (GUI Version)
A graphical interface for simulating panel discussions between different AI language models.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import threading
import sys

from utils import read_file, write_file, parse_config, load_models_from_config, get_default_models, create_config_file_content
from conversation import ConversationManager

# Default configuration
DEFAULT_MAX_CHARACTERS = 15000
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.4
DEFAULT_CHALLENGE_PROBABILITY = 0.2
DEFAULT_OUTPUT_FILE = "conversation_output.txt"


class AITalksGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Talks - Panel Discussion Simulator")
        self.root.geometry("1000x700")
        
        # Configuration variables
        self.config_data = {}
        self.models_list = []
        self.output_file = DEFAULT_OUTPUT_FILE
        
        # State variables
        self.conversation_manager = None
        self.simulation_thread = None
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_config_tab()
        self.setup_content_tab()
        self.setup_simulation_tab()
        
        # Load existing configuration
        self.load_config()
        
        # Load default content
        self.load_default_content()
    
    def setup_config_tab(self):
        """Set up the configuration tab for models and API keys"""
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
        self.output_file_entry.insert(0, DEFAULT_OUTPUT_FILE)
        
        # Button frame
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Save config button
        save_btn = ttk.Button(button_frame, text="Save Configuration", command=self.save_config)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Load defaults button
        defaults_btn = ttk.Button(button_frame, text="Load Default Models", command=self.load_default_models)
        defaults_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_content_tab(self):
        """Set up the content tab for topic and prompts"""
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
        """Set up the simulation tab for running the conversation"""
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
        self.char_limit_var = tk.StringVar(value=str(DEFAULT_MAX_CHARACTERS))
        char_entry = ttk.Entry(char_frame, textvariable=self.char_limit_var, width=10)
        char_entry.pack(side=tk.LEFT, padx=5)
        
        # Token limit
        token_frame = ttk.Frame(param_frame)
        token_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(token_frame, text="Max Tokens per Response:").pack(side=tk.LEFT, padx=5)
        self.token_limit_var = tk.StringVar(value=str(DEFAULT_MAX_TOKENS))
        token_entry = ttk.Entry(token_frame, textvariable=self.token_limit_var, width=10)
        token_entry.pack(side=tk.LEFT, padx=5)
        
        # Temperature
        temp_frame = ttk.Frame(param_frame)
        temp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(temp_frame, text="Temperature:").pack(side=tk.LEFT, padx=5)
        self.temp_var = tk.StringVar(value=str(DEFAULT_TEMPERATURE))
        temp_entry = ttk.Entry(temp_frame, textvariable=self.temp_var, width=10)
        temp_entry.pack(side=tk.LEFT, padx=5)
        
        # Challenge probability
        challenge_frame = ttk.Frame(param_frame)
        challenge_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(challenge_frame, text="Challenge Probability (0-1):").pack(side=tk.LEFT, padx=5)
        self.challenge_var = tk.StringVar(value=str(DEFAULT_CHALLENGE_PROBABILITY))
        challenge_entry = ttk.Entry(challenge_frame, textvariable=self.challenge_var, width=10)
        challenge_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=15)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Simulation", command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Export button
        self.export_btn = ttk.Button(btn_frame, text="Export Conversation", command=self.export_conversation)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
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
    
    def load_default_content(self):
        """Load default content from text files without showing message boxes"""
        try:
            # Load topic
            if os.path.exists('topic.txt'):
                topic = read_file('topic.txt').strip()
                self.topic_text.delete('1.0', tk.END)
                self.topic_text.insert('1.0', topic)
            
            # Load style prompt
            if os.path.exists('prompt.txt'):
                style_prompt = read_file('prompt.txt').strip()
                self.style_text.delete('1.0', tk.END)
                self.style_text.insert('1.0', style_prompt)
            
            # Load final round prompt
            if os.path.exists('prompt_fr.txt'):
                final_round_prompt = read_file('prompt_fr.txt').strip()
                self.final_text.delete('1.0', tk.END)
                self.final_text.insert('1.0', final_round_prompt)
            
            # Load external data
            if os.path.exists('ext_data.txt'):
                ext_data = read_file('ext_data.txt').strip()
                self.ext_text.delete('1.0', tk.END)
                self.ext_text.insert('1.0', ext_data)
            
        except Exception as e:
            print(f"Failed to load default content: {e}")
    
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
                    self.model_entries[i]['apikey'].insert(0, model_info.get('apikey') or "")
                    
                    self.model_entries[i]['version'].delete(0, tk.END)
                    self.model_entries[i]['version'].insert(0, model_info.get('version') or "")
            
            # Set output file
            self.output_file = self.config_data.get('OUTPUT_FILE', DEFAULT_OUTPUT_FILE)
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, self.output_file)
            
            messagebox.showinfo("Configuration Loaded", "Existing configuration loaded successfully.")
            
        except FileNotFoundError:
            # Load default models instead
            self.load_default_models()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def load_default_models(self):
        """Load default model configurations"""
        default_models = get_default_models()
        
        # Set the model entries
        for i, model_info in enumerate(default_models):
            if i < len(self.model_entries):
                self.model_entries[i]['name'].delete(0, tk.END)
                self.model_entries[i]['name'].insert(0, model_info['name'])
                
                self.model_entries[i]['apikey'].delete(0, tk.END)
                self.model_entries[i]['apikey'].insert(0, model_info.get('apikey') or "")
                
                self.model_entries[i]['version'].delete(0, tk.END)
                self.model_entries[i]['version'].insert(0, model_info.get('version') or "")
        
        messagebox.showinfo("Default Models", "Default model configurations loaded.")
    
    def save_config(self):
        """Save configuration to config.txt"""
        try:
            # Get models from form entries
            models = []
            for entry in self.model_entries:
                name = entry['name'].get().strip()
                apikey = entry['apikey'].get().strip()
                version = entry['version'].get().strip()
                
                if name:  # Only include models with a name
                    models.append({
                        'name': name,
                        'apikey': apikey,
                        'version': version
                    })
            
            # Get output file path
            output_file = self.output_file_entry.get().strip()
            if not output_file:
                output_file = DEFAULT_OUTPUT_FILE
            
            # Create config content
            config_content = create_config_file_content(models, output_file)
            
            # Write to file
            write_file('config.txt', config_content)
            
            # Update internal state
            self.models_list = models
            self.output_file = output_file
            
            messagebox.showinfo("Success", "Configuration saved successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def load_content_from_files(self):
        """Load content from text files with user notification"""
        try:
            self.load_default_content()
            messagebox.showinfo("Content Loaded", "Content loaded successfully from files.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load content: {e}")
    
    def save_content_to_files(self):
        """Save content to text files"""
        try:
            # Save topic
            topic = self.topic_text.get('1.0', tk.END)
            write_file('topic.txt', topic)
            
            # Save style prompt
            style_prompt = self.style_text.get('1.0', tk.END)
            write_file('prompt.txt', style_prompt)
            
            # Save final round prompt
            final_round_prompt = self.final_text.get('1.0', tk.END)
            write_file('prompt_fr.txt', final_round_prompt)
            
            # Save external data
            ext_data = self.ext_text.get('1.0', tk.END)
            write_file('ext_data.txt', ext_data)
            
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
    
    def export_conversation(self):
        """Export the current conversation to a file"""
        if not hasattr(self, 'conversation_manager') or not self.conversation_manager:
            messagebox.showinfo("No Conversation", "No conversation to export. Run a simulation first.")
            return
        
        try:
            # Ask for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=self.output_file
            )
            
            if not filename:  # User cancelled
                return
            
            # Write the conversation
            self.conversation_manager.write_to_file(filename)
            
            messagebox.showinfo("Export Complete", f"Conversation exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export conversation: {e}")
    
    def get_models_from_form(self):
        """Get model configurations from the form"""
        models = []
        for entry in self.model_entries:
            name = entry['name'].get().strip()
            apikey = entry['apikey'].get().strip()
            version = entry['version'].get().strip()
            
            if name:  # Only include models with a name
                models.append({
                    'name': name,
                    'apikey': apikey,
                    'version': version
                })
        
        return models
    
    def start_simulation(self):
        """Start the conversation simulation"""
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)
        self.update_status("Preparing simulation...")
        self.update_progress(0)
        
        # Get simulation parameters
        try:
            max_chars = int(self.char_limit_var.get())
            max_tokens = int(self.token_limit_var.get())
            temperature = float(self.temp_var.get())
            challenge_prob = float(self.challenge_var.get())
            
            if not (0 <= temperature <= 1):
                raise ValueError("Temperature must be between 0 and 1")
            if not (0 <= challenge_prob <= 1):
                raise ValueError("Challenge probability must be between 0 and 1")
        except ValueError as e:
            messagebox.showerror("Invalid Parameters", f"Please enter valid numbers for simulation parameters: {e}")
            self.reset_simulation_controls()
            return
        
        # Get content from UI
        topic = self.topic_text.get('1.0', tk.END).strip()
        style_prompt = self.style_text.get('1.0', tk.END).strip()
        final_round_prompt = self.final_text.get('1.0', tk.END).strip()
        ext_data = self.ext_text.get('1.0', tk.END).strip()
        
        # Get models
        models_list = self.get_models_from_form()
        
        # Validate required content
        if not topic:
            messagebox.showerror("Missing Content", "Please provide a discussion topic.")
            self.reset_simulation_controls()
            return
            
        if not models_list:
            messagebox.showerror("Missing Models", "Please configure at least one AI model.")
            self.reset_simulation_controls()
            return
        
        # Save configuration and content to files before starting
        self.save_config()
        self.save_content_to_files()
        
        # Create conversation manager
        self.conversation_manager = ConversationManager(
            models_list=models_list,
            topic=topic,
            style_prompt=style_prompt,
            final_round_prompt=final_round_prompt,
            ext_data=ext_data,
            max_characters=max_chars,
            max_tokens=max_tokens,
            temperature=temperature,
            challenge_probability=challenge_prob
        )
        
        # Set up callbacks
        self.conversation_manager.on_message = self.update_output
        self.conversation_manager.on_progress = self.update_progress
        self.conversation_manager.on_status = self.update_status
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.run_simulation_thread)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def run_simulation_thread(self):
        """Run the conversation simulation in a separate thread"""
        try:
            # Run the simulation
            self.conversation_manager.start_simulation()
            
            # Write output file when complete (only if the simulation wasn't stopped)
            if self.conversation_manager.simulation_running:
                output_file = self.output_file_entry.get().strip()
                if not output_file:
                    output_file = DEFAULT_OUTPUT_FILE
                
                self.conversation_manager.write_to_file(output_file)
                
                # Update status
                self.root.after(0, self.update_status, 
                              f"Simulation complete. Output written to: {output_file}")
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Simulation error: {str(e)}")
            self.root.after(0, self.update_status, f"Error: {str(e)}")
        
        finally:
            # Reset UI
            self.root.after(0, self.reset_simulation_controls)
    
    def stop_simulation(self):
        """Stop the simulation"""
        if self.conversation_manager:
            self.conversation_manager.stop_simulation()
        
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
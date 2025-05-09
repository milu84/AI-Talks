# Troubleshooting Guide

This guide addresses common issues you might encounter when using AI Talks.

## API-Related Issues

### "Error: Missing API key"

**Problem**: You're seeing an error message about a missing API key for one or more models.

**Solutions**:
1. Check your `config.txt` file to ensure API keys are correctly formatted with no spaces around the equals sign
2. Verify that you've obtained valid API keys from the respective services
3. Make sure the API key corresponds to the correct service (OpenAI key for GPT models, etc.)
4. If you don't want to use a particular model, remove it from your configuration

### "Error: Authentication failed" or "Invalid API key"

**Problem**: The system can't authenticate with the API service.

**Solutions**:
1. Double-check that your API key is correct and current
2. Some API keys expire - check if you need to generate a new one
3. Verify your account status with the API provider (payment issues, etc.)
4. Check if you've exceeded your API quota or rate limits

### "Error connecting to [service]" or Timeout Errors

**Problem**: Can't establish a connection to the API service.

**Solutions**:
1. Check your internet connection
2. Verify the API service is operational (check status pages)
3. Try running with a longer timeout value
4. If you're behind a corporate firewall or using a VPN, it might be blocking the connection

## Content Generation Issues

### Models generating very short or incomplete responses

**Problem**: The AI models are producing unusually short or truncated responses.

**Solutions**:
1. Check the `max_tokens` parameter - it might be set too low
2. Look at your prompts - they might be too restrictive or confusing
3. Try a different model version that has better capabilities
4. Ensure your API account has proper access to the models you're using

### Responses aren't following the style/format from prompt.txt

**Problem**: The AI models aren't adhering to the style guidelines provided.

**Solutions**:
1. Make your instructions more explicit and structured
2. Check if your prompt is too long - some instructions might be getting cut off
3. Try adding emphasis to key instructions (bold, ALL CAPS, etc.)
4. More capable models (GPT-4, Claude-3-Opus) generally follow instructions better

### Models keep repeating similar points

**Problem**: The conversation feels repetitive with models making similar points.

**Solutions**:
1. Modify your topic to introduce more complexity or diverse angles
2. Edit `prompt.txt` to explicitly instruct models to build on previous points
3. Increase the "challenge probability" parameter to encourage disagreement
4. Use more diverse models in your panel

## GUI Issues

### GUI doesn't launch or crashes immediately

**Problem**: The graphical interface won't start or crashes on startup.

**Solutions**:
1. Verify that tkinter is properly installed with your Python installation
2. Check terminal/console output for any Python errors
3. Try running the command-line version (`python main.py`) to see if it's a general issue
4. Reinstall the application dependencies

### Changes in GUI aren't being saved

**Problem**: Configuration changes made in the GUI aren't persisting.

**Solutions**:
1. Make sure you're clicking the "Save Configuration" button after making changes
2. Check if the application has write permissions to the configuration files
3. Verify that the files aren't marked as read-only

## File-Related Issues

### "File not found" errors

**Problem**: The application can't find configuration or content files.

**Solutions**:
1. Verify that all required files exist in the correct locations
2. If you're using custom file paths, make sure they're absolute or correctly relative
3. Check for typos in file names
4. Ensure file permissions allow the application to read the files

### Output file not being created

**Problem**: The conversation output file isn't being generated.

**Solutions**:
1. Check if the application has write permissions to the output directory
2. Verify the path specified for the output file is valid
3. Look for error messages in the console/terminal output
4. Try specifying a different output location

## Performance Issues

### Simulation runs very slowly

**Problem**: The conversation simulation takes a long time to complete.

**Solutions**:
1. Use fewer models in your configuration
2. Set a lower character limit for the total conversation
3. Consider using faster, smaller models (like GPT-3.5-Turbo instead of GPT-4)
4. Check your internet connection speed
5. Close other applications that might be using network bandwidth

### High API usage costs

**Problem**: The application is generating unexpected API costs.

**Solutions**:
1. Use smaller models when possible (they're generally cheaper)
2. Set lower token limits for responses
3. Reduce the number of models in your panel
4. Run shorter conversations
5. Monitor API usage on your provider dashboards

## If All Else Fails

If you encounter persistent issues not addressed above:

1. Try the command-line version with the `--no-progress` flag for simpler output
2. Check the GitHub repository for known issues or updates
3. Inspect the Python code for any obvious errors if you've modified it
4. Clear any cached data or temporary files
5. Consider creating a new virtual environment with fresh dependencies

## Getting Help

If you need additional help:

1. Open an issue on the GitHub repository with detailed information about your problem
2. Include your configuration (with API keys removed) and relevant error messages
3. Specify your operating system and Python version
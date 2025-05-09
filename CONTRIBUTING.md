# Contributing to AI Talks

Thank you for your interest in contributing to AI Talks! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Ways to Contribute

There are many ways to contribute to AI Talks:

1. **Bug Reports**: Report bugs by opening an issue
2. **Feature Requests**: Suggest new features or improvements
3. **Documentation**: Improve or expand documentation
4. **Code Contributions**: Submit pull requests with bug fixes or new features
5. **Testing**: Test the application and report any issues
6. **Examples**: Share interesting conversation examples

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/ai-talks.git
   cd ai-talks
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Pull Request Process

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or
   ```bash
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes and commit them with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

3. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request from your branch to the main repository

5. Wait for review and address any feedback

## Coding Standards

- Follow PEP 8 for Python code
- Use clear, descriptive variable and function names
- Include docstrings for functions and classes
- Keep functions small and focused on a single responsibility
- Add comments for complex logic

## Testing

- Test your changes thoroughly before submitting a pull request
- Add unit tests for new features when possible

## API Keys

- Never commit actual API keys to the repository
- Use placeholders like `your_openai_key_here` in example configurations
- Ensure your commits don't include real API keys (check your diffs!)

## Feature Guidelines

When adding new features, keep in mind:

1. **Maintainability**: Ensure code is easy to maintain
2. **Compatibility**: Maintain backward compatibility when possible
3. **Performance**: Consider performance implications
4. **User Experience**: Keep the interface intuitive

## Documentation

If you're adding a new feature, please include:

1. Updates to relevant documentation files
2. Code comments
3. Example usage where appropriate

## Getting Help

If you need help with your contribution, feel free to:

1. Ask questions in your issue or pull request
2. Reach out to the project maintainers

Thank you for contributing to AI Talks!
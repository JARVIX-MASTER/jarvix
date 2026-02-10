# Contributing to JARVIX

Thank you for your interest in contributing to JARVIX!

## Getting Started

### Development Setup

```bash
# Clone the repository
git clone https://github.com/JARVIX-MASTER/jarvix
cd jarvix-assistant

# Create development branch
git checkout -b dev

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

### Project Structure

```
src/jarvix/
├── core/           # AI and voice processing
├── agents/         # Command execution
├── features/       # Feature modules
└── utils/          # Shared utilities
```

## How to Contribute

### Bug Reports

1. Check existing issues first
2. Create new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information

### Feature Requests

1. Describe the feature
2. Explain use case
3. Suggest implementation (optional)

### Pull Requests

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open Pull Request

## Code Style

### Python

- Follow PEP 8
- Use type hints where helpful
- Document functions with docstrings

```python
def my_function(param: str) -> dict:
    """
    Brief description.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    pass
```

### Commits

- Use descriptive commit messages
- Reference issues: `Fix #123`
- Keep commits focused

## Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_brain.py

# With coverage
pytest --cov=jarvix
```

## Documentation

- Update docs when adding features
- Keep README.md current
- Add examples for new commands

## Review Process

1. Automated tests must pass
2. Code review by maintainer
3. Documentation updated
4. Merge to main

## Community

- Be respectful
- Help others
- Share knowledge

---

Thank you for contributing!

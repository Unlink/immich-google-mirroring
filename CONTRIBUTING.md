# Contributing to Immich → Google Photos Sync

First off, thank you for considering contributing! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Environment details** (OS, Docker version, Python version)
- **Logs** (from `data/logs/app.log` or `docker-compose logs`)
- **Screenshots** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- **Clear title and description**
- **Use case** - why is this enhancement useful?
- **Proposed solution**
- **Alternative solutions** you've considered

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes**
3. **Test your changes**
4. **Update documentation** if needed
5. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (optional)
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/immich-google-mirroring.git
cd immich-google-mirroring

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your test credentials

# Create data directory
mkdir -p data/logs

# Run tests
python3 test_basic.py

# Start development server
./dev-start.sh
# Or manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Docker Development

```bash
# Build and run
docker-compose up --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Code Style

### Python

We follow PEP 8 with some flexibility:

- **Line length**: 100 characters (not strict 79)
- **Imports**: Grouped (standard library, third-party, local)
- **Type hints**: Use where helpful, not mandatory
- **Docstrings**: For public functions and classes

```python
# Good
async def sync_asset(self, asset: Dict[str, Any]) -> bool:
    """Sync a single asset to Google Photos.
    
    Args:
        asset: Asset metadata from Immich
        
    Returns:
        True if successful, False otherwise
    """
    ...
```

### Formatting

We use basic formatting guidelines:

```bash
# Use these tools (optional but recommended)
pip install black isort

# Format code
black app/
isort app/

# Check
black --check app/
```

### HTML/Jinja2

- **Indentation**: 2 spaces
- **Keep templates simple**: Complex logic belongs in Python
- **Use base template**: Extend `base.html` for consistency

### JavaScript

- **Minimal**: Keep it simple, vanilla JS preferred
- **ES6+**: Use modern syntax
- **Comments**: Explain non-obvious behavior

## Project Structure

```
app/
├── clients/        # External API clients (Immich, Google)
├── routes/         # FastAPI routes (API + pages)
├── sync/           # Sync engine logic
├── templates/      # Jinja2 HTML templates
├── utils/          # Utilities (encryption, config)
├── config.py       # App configuration
├── database.py     # Database connection
├── main.py         # FastAPI app entry point
├── models.py       # SQLAlchemy models
└── scheduler.py    # APScheduler integration
```

## Testing

### Running Tests

```bash
# Basic functionality tests
python3 test_basic.py

# Manual testing
# 1. Start the app
# 2. Go through the setup flow
# 3. Run a sync
# 4. Check logs
```

### Writing Tests

Add tests to `test_basic.py` or create new test files:

```python
async def test_new_feature():
    """Test description"""
    # Arrange
    ...
    # Act
    ...
    # Assert
    assert result == expected
```

## Adding New Features

### 1. Create an Issue

Discuss the feature first to ensure it aligns with project goals.

### 2. Implementation Checklist

- [ ] Code implements the feature
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Error handling added
- [ ] Logging added where appropriate
- [ ] UI updated if needed

### 3. Documentation

Update relevant docs:

- **README.md**: Main documentation
- **QUICKSTART.md**: Quick reference
- **ARCHITECTURE.md**: If structure changes
- **DEPLOYMENT.md**: If deployment changes
- **Code comments**: Complex logic

## Common Tasks

### Adding a New API Endpoint

1. Create route in `app/routes/`
2. Add to router in `app/main.py`
3. Update API documentation in README
4. Add error handling
5. Test the endpoint

### Adding a New UI Page

1. Create template in `app/templates/`
2. Create route in `app/routes/pages.py`
3. Update navigation in `base.html`
4. Test the page

### Modifying Database Schema

1. Update models in `app/models.py`
2. Create migration logic (currently manual)
3. Test with fresh database
4. Document changes in CHANGELOG.md

### Adding Configuration Options

1. Add to `AppConfig` model
2. Update `ConfigManager` methods
3. Add UI controls (settings page)
4. Add API endpoints if needed
5. Update documentation

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commits:

```
feat: add support for multiple albums
fix: handle OAuth token refresh errors
docs: update deployment guide
refactor: simplify sync engine logic
test: add tests for encryption helper
```

### Pull Request Process

1. **Update your fork**:
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/my-feature
   # Create PR on GitHub
   ```

5. **Address review feedback**
6. **Merge** (maintainer will merge)

## Code Review

### As a Reviewer

- Be kind and constructive
- Ask questions, don't demand
- Approve when ready, request changes if needed
- Check for:
  - Functionality
  - Code quality
  - Documentation
  - Tests

### As an Author

- Be open to feedback
- Respond to all comments
- Make requested changes or discuss alternatives
- Keep PRs focused and reasonably sized

## Release Process

(For maintainers)

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create git tag
4. Build and test Docker image
5. Create GitHub release
6. Update documentation

## Questions?

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You! 🙏

Your contributions make this project better for everyone!

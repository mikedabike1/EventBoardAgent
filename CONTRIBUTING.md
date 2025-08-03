# Contributing to Gaming Events Scraper

Thank you for your interest in contributing to the Gaming Events Scraper! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

1. **Python 3.9+**: The project supports Python 3.9, 3.10, 3.11, and 3.12
2. **UV**: Modern Python package manager
3. **Git**: Version control

### Installation

1. Fork and clone the repository:
```bash
git clone https://github.com/your-username/EventBoardAgent.git
cd EventBoardAgent
```

2. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv sync --all-extras
```

4. Install pre-commit hooks (optional but recommended):
```bash
uv run pre-commit install
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed
- Ensure your changes don't break existing functionality

### 3. Run Tests and Quality Checks

Before committing, run the full test suite:

```bash
# Run tests
uv run pytest tests/ -v

# Check code formatting
uv run black --check .

# Run linting
uv run ruff check .

# Type checking
uv run mypy src/

# Run tests with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing
```

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add support for Reddit event scraping"
# or
git commit -m "fix: handle Discord messages without guild information"
```

Commit message format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test improvements
- `refactor:` for code refactoring
- `perf:` for performance improvements

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub using the provided template.

## Code Standards

### Code Style

- **Formatting**: Use Black for code formatting
- **Linting**: Follow Ruff linting rules
- **Type Hints**: Add type hints to all functions and methods
- **Docstrings**: Use Google-style docstrings for all public functions

### Testing Requirements

- **Unit Tests**: Write tests for all new functionality
- **Test Coverage**: Maintain or improve test coverage (currently 89%)
- **Test Organization**: Follow the existing test structure in `tests/`
- **Mocking**: Use appropriate mocking for external dependencies

### Documentation

- **Docstrings**: All public functions must have docstrings
- **README**: Update README.md for significant changes
- **Type Hints**: Use proper type annotations
- **Examples**: Update Jupyter notebook examples if needed

## Pull Request Guidelines

### Before Submitting

1. **Rebase** your branch on the latest main branch
2. **Squash** related commits into logical units
3. **Test** your changes thoroughly
4. **Update** documentation and examples
5. **Fill out** the PR template completely

### PR Requirements

Your pull request must:

- [ ] Pass all CI checks (tests, linting, type checking)
- [ ] Include tests for new functionality
- [ ] Have clear commit messages
- [ ] Update relevant documentation
- [ ] Not break existing functionality
- [ ] Follow the coding standards

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one review from a maintainer
3. **Testing**: Manual testing may be required for complex changes
4. **Documentation**: Documentation changes will be reviewed

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

### On Every Push/PR:
- **Test Matrix**: Tests run on Python 3.9-3.12 across Ubuntu, Windows, macOS
- **Code Quality**: Black formatting, Ruff linting, MyPy type checking
- **Security**: Safety and Bandit security scans
- **Coverage**: Test coverage reporting

### Branch Protection:
- **Required Checks**: Multiple CI checks must pass
- **Required Reviews**: At least 1 approving review
- **Up-to-date Branches**: Must be current with main branch
- **Conversation Resolution**: All review comments must be resolved

## Manual Branch Protection Setup

If you're a repository administrator, you can set up branch protection manually:

1. Go to **Settings** > **Branches** in your GitHub repository
2. Click **Add rule** for the `main` branch
3. Configure the following settings:

#### Required Status Checks:
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- Select these required checks:
  - `test (ubuntu-latest, 3.9)`
  - `test (ubuntu-latest, 3.10)`
  - `test (ubuntu-latest, 3.11)`
  - `test (ubuntu-latest, 3.12)`
  - `test (windows-latest, 3.11)`
  - `test (macos-latest, 3.11)`
  - `lint`
  - `build`

#### Pull Request Reviews:
- ✅ Require pull request reviews before merging
- Required approving reviews: **1**
- ✅ Dismiss stale reviews when new commits are pushed
- ✅ Require review from code owners (if CODEOWNERS file exists)

#### Additional Restrictions:
- ✅ Restrict pushes that create new files
- ✅ Require conversation resolution before merging
- ❌ Allow force pushes
- ❌ Allow deletions

## Getting Help

- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the README and project documentation
- **Examples**: Look at the Jupyter notebook for usage examples

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards
- Test your changes thoroughly

Thank you for contributing to make this project better!
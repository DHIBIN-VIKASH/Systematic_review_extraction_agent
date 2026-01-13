# Contributing to Systematic Review Data Extraction Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🐛 Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

### How to Submit a Bug Report

1. **Use the bug report template** when creating a new issue
2. **Describe the bug** clearly and concisely
3. **Provide steps to reproduce** the issue
4. **Include your environment**:
   - OS (Windows/Linux/Mac)
   - Python version
   - Browser (Chrome/Edge)
5. **Add screenshots or logs** if applicable

## 💡 Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing feature requests** first
2. **Use the feature request template**
3. **Explain the use case** and why it would be valuable
4. **Describe the proposed solution** if you have one in mind

## 🔧 Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR-USERNAME/Systematic_review_extraction_agent.git
cd Systematic_review_extraction_agent
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Set Up Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install chromium
```

## 📝 Code Style

- Follow **PEP 8** style guidelines
- Use **meaningful variable names**
- Add **docstrings** to functions and classes
- Keep functions **focused and small**
- Add **comments** for complex logic

### Example

```python
def parse_template(filepath: str) -> List[TemplateField]:
    """
    Parse a template file and extract field definitions.
    
    Args:
        filepath: Path to template file (.docx or .xlsx)
    
    Returns:
        List of TemplateField objects
    
    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    # Implementation
```

## 🧪 Testing

Before submitting a pull request:

1. **Test your changes** with both Word and Excel templates
2. **Verify the extraction** works with sample PDFs
3. **Check for errors** in different scenarios
4. **Test edge cases** (empty templates, malformed files, etc.)

## 📤 Submitting Pull Requests

### Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Follow the PR template**
3. **Link related issues** using keywords (Fixes #123, Closes #456)
4. **Keep PRs focused** - one feature or fix per PR
5. **Write clear commit messages**

### Commit Message Format

```
type: Brief description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.

- Bullet points for multiple changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Example Commits

```
feat: Add support for CSV template format

- Implement CSVTemplateParser class
- Update template_parser.py with CSV detection
- Add tests for CSV parsing

Closes #45
```

```
fix: Handle empty sections in Word templates

Previously, empty sections would cause parser to crash.
Now gracefully skips empty sections.

Fixes #67
```

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

- **Template parsers**: Support for additional formats (CSV, JSON, etc.)
- **Error handling**: Better error messages and recovery
- **Testing**: Unit tests and integration tests
- **Documentation**: Tutorials, examples, and guides
- **Performance**: Optimization of parsing and extraction
- **UI**: Optional GUI for non-technical users

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## ❓ Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search closed issues
3. Open a new discussion or issue

Thank you for contributing! 🎉

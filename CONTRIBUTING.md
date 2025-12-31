# Contributing to MarkDown OCR

Thank you for your interest in contributing to MarkDown OCR! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MDOcr_V3.git
   cd MDOcr_V3
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Backend Development

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install black flake8 pytest  # Development tools

# Run the backend
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Using Docker for Development

```bash
docker-compose up --build
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug fixes**: Fix issues reported in GitHub Issues
- ✨ **New features**: Add new functionality (discuss in an issue first)
- 📝 **Documentation**: Improve README, add examples, write guides
- 🧪 **Tests**: Add or improve test coverage
- 🎨 **UI/UX improvements**: Enhance the user interface
- ⚡ **Performance**: Optimize code for speed or efficiency
- 🌐 **Localization**: Add translations or i18n support

### Areas for Contribution

Priority areas where we need help:

1. **OCR Accuracy**:
   - Improve table detection and conversion
   - Enhance chart/diagram recognition
   - Better code block preservation

2. **LLM Integration**:
   - Add support for more LLM providers (OpenAI, Anthropic, etc.)
   - Implement model selection in UI
   - Add streaming responses for real-time feedback

3. **Features**:
   - Batch processing multiple PDFs
   - OCR history and management
   - Export formats (HTML, DOCX, etc.)
   - PDF page range selection
   - Custom conversion rules/templates

4. **UI/UX**:
   - Dark mode support
   - Mobile responsiveness
   - Drag-and-drop improvements
   - Better progress visualization

5. **Performance**:
   - Parallel page processing
   - Caching converted pages
   - Optimized image extraction

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Maximum line length: 88 characters (Black default)

**Format your code:**
```bash
black backend/app
flake8 backend/app
```

**Example:**
```python
from typing import Optional, Dict

async def process_document(
    file_path: str, 
    task_id: str
) -> Optional[Dict[str, any]]:
    """
    Process a document and convert it to Markdown.
    
    Args:
        file_path: Path to the PDF file
        task_id: Unique identifier for the task
        
    Returns:
        Dictionary containing task status and output path,
        or None if processing fails
    """
    # Implementation
    pass
```

### TypeScript/JavaScript (Frontend)

- Use TypeScript for type safety
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Prefer `const` over `let`, avoid `var`

**Format your code:**
```bash
npm run lint
npm run format
```

**Example:**
```typescript
interface DocumentProps {
  taskId: string;
  onComplete: (result: ConversionResult) => void;
}

export const DocumentConverter: React.FC<DocumentProps> = ({
  taskId,
  onComplete,
}) => {
  // Implementation
};
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

**Writing tests:**
```python
import pytest
from app.services.ocr_service import OCRService

def test_create_task():
    service = OCRService()
    task_id = service.create_task("test.pdf")
    assert task_id is not None
    assert len(task_id) == 36  # UUID length
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
# Start the services
docker-compose up -d

# Run integration tests
pytest tests/integration/ -v
```

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features or bug fixes
3. **Ensure all tests pass**:
   ```bash
   # Backend
   pytest tests/
   
   # Frontend
   npm test
   ```
4. **Format your code** according to project standards
5. **Update CHANGELOG.md** with your changes
6. **Create a pull request** with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues
   - Screenshots for UI changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Related Issues
Fixes #[issue_number]
```

## Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**:
   - Step 1
   - Step 2
   - Step 3
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - OS: [e.g., macOS 14.0]
   - Docker version: [e.g., 24.0.0]
   - LLM Provider: [e.g., Ollama with llama3]
6. **Logs**: Include relevant error messages or logs
7. **Screenshots**: If applicable

## Suggesting Enhancements

Enhancement suggestions are tracked as GitHub Issues. When suggesting an enhancement:

1. **Use a clear title** describing the enhancement
2. **Provide detailed description** of the suggested enhancement
3. **Explain why** this enhancement would be useful
4. **List potential drawbacks** or concerns
5. **Provide examples** or mockups if applicable

## Development Tips

### Debugging Backend

```python
# Add logging
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Debugging Frontend

```typescript
// Use React DevTools
console.log('Debug:', variable);

// Add error boundaries
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

### Testing LLM Integration Locally

```bash
# Use the test script
python backend/test_llm_connection.py

# Or test endpoints directly
curl http://localhost:8000/health
```

## Project Structure

```
MDOcr_V3/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/  # API route handlers
│   │   ├── core/           # Configuration
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── app/                # Next.js pages
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   └── package.json
└── docker-compose.yml
```

## Questions?

- Open an issue for questions
- Check existing issues and PRs first
- Join discussions in GitHub Discussions (if available)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- CHANGELOG.md

Thank you for contributing to MarkDown OCR! 🎉
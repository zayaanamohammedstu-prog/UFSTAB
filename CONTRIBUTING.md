# Contributing to OratorHub

Thank you for your interest in contributing to OratorHub! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, browser, Python version)

Example:
```markdown
**Bug**: Tournament creation fails with database error

**Steps to Reproduce**:
1. Login as organizer
2. Navigate to BP Debate → Tournament
3. Fill in all required fields
4. Click "Save Tournament"

**Expected**: Tournament should be created
**Actual**: Error message "Database connection failed"

**Environment**: Ubuntu 20.04, Firefox 95, Python 3.9
```

### Suggesting Features

Feature suggestions are welcome! Please include:

- **Clear use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives considered** - Other approaches you've thought about
- **Additional context** - Mockups, examples, etc.

### Pull Requests

1. **Fork the repository**
```bash
git clone https://github.com/YOUR-USERNAME/UFSTAB.git
cd UFSTAB
```

2. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

3. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new features
   - Update documentation as needed

4. **Test your changes**
```bash
# Run tests
pytest

# Check code coverage
pytest --cov=app

# Test manually
python app.py
```

5. **Commit with clear messages**
```bash
git commit -m "Add: feature description"
# or
git commit -m "Fix: bug description"
# or
git commit -m "Docs: documentation update"
```

Use prefixes:
- `Add:` - New features
- `Fix:` - Bug fixes
- `Update:` - Updates to existing features
- `Refactor:` - Code refactoring
- `Docs:` - Documentation changes
- `Test:` - Test additions/changes
- `Style:` - Code style changes

6. **Push and create PR**
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Link to related issues
- Screenshots (for UI changes)
- Testing notes

## Development Setup

### Prerequisites
- Python 3.9+
- Node.js 14+ (for frontend tools)
- PostgreSQL or SQLite
- Git

### Setup Steps

1. **Clone and install**
```bash
git clone https://github.com/YOUR-USERNAME/UFSTAB.git
cd UFSTAB
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Initialize database**
```bash
./init_db.sh
```

4. **Run development server**
```bash
python app.py
```

## Code Style Guidelines

### Python

Follow PEP 8:
```python
# Good
def calculate_team_points(team_id, rank):
    """Calculate points based on team rank"""
    points_map = {1: 3, 2: 2, 3: 1, 4: 0}
    return points_map.get(rank, 0)

# Bad
def CalculatePoints(id,r):
    if r==1:return 3
    elif r==2:return 2
```

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use docstrings for functions
- Type hints recommended

```python
from typing import List, Optional

def get_teams(tournament_id: int) -> List[Team]:
    """Get all teams for a tournament"""
    return Team.query.filter_by(tournament_id=tournament_id).all()
```

### JavaScript

Use ES6+ features:
```javascript
// Good
const fetchTournaments = async () => {
    try {
        const response = await api.get('/tournaments');
        return response;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
};

// Bad
function fetchTournaments() {
    return api.get('/tournaments').then(function(response) {
        return response;
    }).catch(function(error) {
        console.log(error);
    });
}
```

- Use `const` and `let`, not `var`
- Use arrow functions
- Use async/await over promises
- Use template literals
- Semicolons required

### CSS

Use BEM naming:
```css
/* Good */
.card {}
.card__header {}
.card__header--highlighted {}

/* Bad */
.cardHeader {}
.card-header-highlighted {}
```

- Use CSS variables for colors
- Mobile-first responsive design
- Avoid `!important`

### HTML

Semantic and accessible:
```html
<!-- Good -->
<button 
    class="btn btn-primary" 
    aria-label="Submit form"
    onclick="handleSubmit()">
    Submit
</button>

<!-- Bad -->
<div class="button" onclick="submit()">Submit</div>
```

- Use semantic tags (`<header>`, `<nav>`, `<main>`)
- Include ARIA labels
- Alt text for images

## Testing

### Writing Tests

```python
def test_create_tournament(client, auth_headers):
    """Test tournament creation"""
    response = client.post('/api/tournaments',
        headers=auth_headers,
        json={
            'name': 'Test Tournament',
            'format': 'BP',
            'start_date': '2026-02-15T00:00:00Z',
            'end_date': '2026-02-20T00:00:00Z'
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['tournament']['name'] == 'Test Tournament'
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest test_api.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Documentation

### Code Documentation

```python
def generate_draw(tournament_id: int, round_number: int) -> List[Pairing]:
    """
    Generate pairings for a tournament round.
    
    Args:
        tournament_id: ID of the tournament
        round_number: Round number to generate draw for
    
    Returns:
        List of Pairing objects
    
    Raises:
        ValueError: If tournament has fewer than 4 teams
        
    Example:
        >>> pairings = generate_draw(1, 1)
        >>> len(pairings)
        12  # 3 rooms with 4 teams each
    """
    teams = get_teams(tournament_id)
    if len(teams) < 4:
        raise ValueError("Need at least 4 teams")
    
    # Implementation...
```

### API Documentation

Update `API.md` when adding/changing endpoints.

### README Updates

Update `README.md` for new features visible to users.

## Database Migrations

When changing models:

```bash
# Create migration
flask db migrate -m "Add new field to Tournament"

# Review migration file
# Edit if needed

# Apply migration
flask db upgrade

# Rollback if needed
flask db downgrade
```

## Commit Message Guidelines

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `Add` - New feature
- `Fix` - Bug fix
- `Update` - Update existing feature
- `Refactor` - Code refactoring
- `Docs` - Documentation
- `Test` - Tests
- `Style` - Formatting
- `Chore` - Maintenance

Example:
```
Add: Tournament registration waitlist feature

- Implement automatic waitlist management
- Add waitlist status to registration model
- Update API endpoint to handle waitlist
- Add tests for waitlist functionality

Closes #42
```

## Branch Naming

- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/what-changed` - Documentation
- `refactor/what-changed` - Refactoring

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers
6. Address review comments
7. Squash commits if requested

## Getting Help

- **GitHub Issues** - For bugs and features
- **GitHub Discussions** - For questions
- **Email** - support@oratorhub.com

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to OratorHub! 🎉

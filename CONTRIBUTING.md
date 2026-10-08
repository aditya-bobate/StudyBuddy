# Contributing to StudyBuddy

Thank you for contributing to StudyBuddy! As a 3-person team, we maintain strict boundaries and workflows to avoid conflicts and ensure high-quality integrations.

## Ownership Boundaries

- **P1**: `backend/llm.py`, `backend/ingest.py`, `backend/rag.py`, `backend/quiz.py`
- **P2**: `app/` (Streamlit UI)
- **P3**: Infrastructure, `tests/`, `docs/`, `backend/__init__.py`, `backend/api.py`, `backend/errors.py`

**STRICT RULE:** Do not directly modify another person's files. If you need a change in a file you do not own, create an issue and assign it to the owner, or communicate with them to make the change.

## Workflow

We follow an **Issue-First** workflow.
1. Create a GitHub issue detailing the feature or bug.
2. Checkout a new branch from `main`: `git checkout -b <type>/<short-name>`
3. Implement the feature incrementally. Commit often.
4. Push your branch and open a **Draft PR** early.
5. Once complete, mark the PR ready for review and assign the correct teammate.
6. A review is required before merging into `main`. **No direct pushes to main.**

## Review Rotation
- P2 reviews P1
- P3 reviews P2
- P1 reviews P3

## Commit Conventions

Use conventional commits:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools/libraries
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `ci`: Changes to CI configuration files and scripts
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)

Example: `feat: add document ingestion backend (#12)`

## Testing
Always run the test suite before submitting a PR:
```bash
python -m pytest tests/
```
Ensure your code passes `ruff` linting.

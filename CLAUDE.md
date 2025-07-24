# Documentation & Progress Tracking

## Session Documentation (REQUIRED)
At the start of each session:
1. Read `docs/current-work.md` to understand current context
2. Update `docs/session-notes.md` with new session header
3. Set clear goals for the session

During development:
1. Update `docs/session-notes.md` with progress after each major task
2. Note any discoveries, issues, or decisions in real-time
3. Update `docs/current-work.md` when changing files or status

At the end of each session (or before git commits):
1. Summarize accomplishments in `docs/session-notes.md`
2. Update `docs/current-work.md` with current state
3. Add key insights to `docs/progress-log.md` if significant

**Use `/end-session` command** to systematically complete all three steps above.

**Git Integration**: A pre-commit hook ensures documentation is updated before each commit, tying commits to documented session work.

## Documentation Standards
- Use clear, descriptive headers
- Include timestamps for major updates
- Explain WHY decisions were made, not just WHAT
- Note any trade-offs or alternative approaches considered
- Keep technical details at appropriate level for future context

## File Management
- Keep `docs/session-notes.md` current and active
- Archive completed sessions to bottom of file
- Update `docs/current-work.md` before ending sessions
- Add weekly summaries to `docs/progress-log.md`

# Testing

## Running Tests
- **Run all tests**: `python -m pytest tests/`
- **Run specific test file**: `python -m pytest tests/test_models.py`
- **Run single test**: `python -m pytest tests/test_models.py::TestRecipe::test_recipe_creation_valid`
- **Run with verbose output**: `python -m pytest tests/ -v`

## Test Requirements
- All new functionality MUST have corresponding unit tests
- Tests should cover core functionality, edge cases, and error conditions
- Run tests before committing changes to ensure functionality remains intact
- Prefer running single test files during development for performance

## Test Structure
- `tests/test_models.py` - Recipe model validation and creation
- `tests/test_examples.py` - Example recipe loading and formatting
- `tests/test_output_validator.py` - Recipe structure and measurement validation
- `tests/test_recipe_generator.py` - AI recipe generation functionality

# Bash commands
- **Test runner**: `python -m pytest tests/`
- **Install test dependencies**: `pip install pytest`

# Workflow
- Run relevant tests when making changes to ensure functionality works
- Run full test suite before major commits or releases
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance during development
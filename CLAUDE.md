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
4. **Update `README.md` when making major changes** - Keep it current with new features, usage patterns, or architectural changes

At the end of each session:
1. Summarize accomplishments in `docs/session-notes.md`
2. Update `docs/current-work.md` with current state
3. Add key insights to `docs/progress-log.md` if significant

**Use `/end-session` command** to systematically complete all three steps above.

## Documentation Standards
- Use clear, descriptive headers
- Include timestamps for major updates
- Explain WHY decisions were made, not just WHAT
- Note any trade-offs or alternative approaches considered
- Keep technical details at appropriate level for future context
- **README.md Maintenance**: When adding new features, evaluation capabilities, or changing usage patterns, update README.md to reflect current functionality and usage examples

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

# Development Pratcies
- Split changes up into meaningful chunks. Avoid changing too many things at once to make the review and development easier to follow and review
- Use Snake Case for Python code when reasonable. Avoid Camel Case usage
- Focus on adding functionality that is necessary. Don't add extra fluff or other bells and whistles that are not needed

# Project Development Overview

Use the overview in this section to guide your development. This describes the long-term plan for the project

## Project Overview
Building a comprehensive production-ready GenAI application system to demonstrate end-to-end GenAI/AIOps capabilities. The system integrates multiple GenAI technologies into a cohesive, scalable, and cost-optimized production deployment.

## Core Technical Components
- **Prompt Engineering Pipeline**: Advanced prompting with chain-of-thought, few-shot learning, and context optimization
- **Vector Database Integration**: Semantic search and retrieval using embeddings with Pinecone/Weaviate/Chroma
- **RAG Architecture**: Retrieval-augmented generation with hybrid search, metadata filtering, and context management
- **LLM Fine-tuning**: Parameter-efficient fine-tuning using LoRA/QLoRA for domain-specific optimization
- **Evaluation Framework**: Automated assessment using RAGAS, LLM-as-a-judge, and custom domain metrics
- **Production Deployment**: Containerized microservices with auto-scaling, monitoring, and observability
- **API Design**: AI-optimized APIs with intelligent routing, rate limiting, and error handling
- **Cost Optimization**: Real-time cost tracking, caching strategies, and resource allocation

## Architecture Goals
- **Scalability**: Handle variable loads with auto-scaling and load balancing
- **Reliability**: Circuit breakers, graceful degradation, and comprehensive error handling  
- **Observability**: Distributed tracing, performance monitoring, and business metrics
- **Security**: Input validation, output filtering, and access control
- **Cost Efficiency**: Intelligent model routing, caching, and resource optimization

## Technology Stack
- **Backend**: FastAPI with async processing
- **LLM APIs**: OpenAI, Anthropic, with fallback strategies
- **Vector DB**: Production vector database with optimization
- **Deployment**: Docker containers on Kubernetes
- **Monitoring**: Prometheus, Grafana, custom dashboards
- **Infrastructure**: Multi-cloud deployment with cost tracking

## Success Metrics
- End-to-end system demonstrating production GenAI patterns
- Cost-optimized deployment under realistic load scenarios  
- Comprehensive monitoring and evaluation pipeline
- Documentation suitable for enterprise deployment
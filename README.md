# Cooking Assistant

AI-powered recipe generation system with advanced prompt engineering, comprehensive evaluation framework, and production-ready architecture patterns.

## Quick Start

1. **Setup Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY to .env file
   ```

3. **Run Application**
   ```bash
   python main.py                    # Interactive recipe generation
   python main.py --test-examples    # View example recipes
   python main.py --evaluate         # Run evaluation sample
   ```

## Core Features

### 🗃️ Vector Database
- **Chroma DB Integration**: Local vector database for semantic recipe search
- **Recipe Embeddings**: OpenAI text-embedding-ada-002 for high-quality vectors
- **Semantic Search**: Find similar recipes based on ingredients, cuisine, or cooking style
- **Docker Setup**: One-command local database deployment

### 🧑‍🍳 Recipe Generation
- **5 Template Types**: Basic, Quick (30min), Dietary restrictions, Cuisine-specific, Ingredient substitution
- **Advanced Prompting**: Chain-of-thought reasoning with Chef Marcus persona
- **Smart Validation**: Automatic recipe structure and measurement validation
- **Safety Checking**: Built-in safety validation for generated recipes

### 📊 Evaluation Framework
- **LLM-as-a-Judge**: Automated quality assessment across 4 metrics
- **29 Test Cases**: Comprehensive coverage of all template types and edge cases
- **Performance Tracking**: Response time, token usage, and success rate monitoring
- **Results Analysis**: Statistical analysis and run-to-run comparisons

### 🔧 Developer Tools
- **Comprehensive Testing**: 43 unit tests with 100% pass rate
- **CLI Interface**: Multiple execution modes and evaluation options  
- **Documentation System**: Session tracking and progress logging
- **Git Integration**: Pre-commit hooks with automated testing

## Usage Examples

### Interactive Recipe Generation
```bash
python main.py
# What ingredients do you have? chicken, rice, vegetables
# Recipe type (basic/quick/dietary/cuisine/substitution): basic
```

### Evaluation System
```bash
# Quick evaluation sample
python -m evaluations.run_eval --sample 5

# Evaluate specific categories
python -m evaluations.run_eval --category basic
python -m evaluations.run_eval --category quick

# Compare evaluation runs
python -m evaluations.run_eval --compare 2025-01-01T10:00:00 2025-01-01T11:00:00

# View test case summary
python -m evaluations.run_eval --summary
```

### Vector Database Setup & Usage

#### Quick Start
```bash
# 1. Start the vector database (Docker required)
./start_vector_db.sh

# 2. Test connection
python test_chroma_connection.py
```

#### Manual Docker Control
```bash
# Start Chroma DB
docker-compose up -d chroma

# Check status
docker-compose ps

# View logs
docker-compose logs chroma

# Stop database
docker-compose stop chroma
```

#### Using the Vector Database in Python
```python
# Import the high-level interfaces
from src.vector_store import VectorRecipeStore
from src.recipe_ingestion import run_example_ingestion

# Set your OpenAI API key
api_key = "your-openai-api-key"

# Ingest example recipes (one time setup)
result = run_example_ingestion(api_key, clear_existing=True)
print(f"Ingested {result['stats']['successful']} recipes")

# Search for recipes
store = VectorRecipeStore(api_key)
results = store.search_recipes("chicken and rice", n_results=3)

for result in results:
    metadata = result['metadata']
    print(f"{metadata['title']} (similarity: {result['similarity']:.3f})")
    print(f"  Time: {metadata['total_time']}min, Serves: {metadata['servings']}")

# Get recipe count
total_recipes = store.count_recipes()
print(f"Total recipes in database: {total_recipes}")
```

#### API Access
```bash
# Chroma DB API is available at:
# http://localhost:8000/api/v2/
# Use the Python classes above for easier interaction
```

### Testing & Development
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_evaluations.py
python -m pytest tests/test_models.py

# Test prompt templates
python main.py --test-templates
```

## Project Structure

```
cooking-assistant/
├── main.py                 # Main CLI interface
├── config.py              # Configuration management
├── src/                   # Core application code
│   ├── recipe_generator.py  # Recipe generation logic
│   ├── prompts.py           # Prompt templates and selection
│   ├── models.py            # Recipe data models
│   ├── examples.py          # Example recipe management
│   └── exceptions.py        # Custom exception classes
├── evaluations/           # Evaluation framework
│   ├── evaluator.py         # LLM-as-a-judge evaluation
│   ├── test_cases.py        # Test case definitions
│   ├── results.py           # Results tracking and analysis
│   └── run_eval.py          # Evaluation CLI runner
├── tests/                 # Comprehensive test suite
├── data/                  # Recipe examples and datasets
└── docs/                  # Session documentation
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for recipe generation and evaluation

### Data Files  
- `data/example_recipes.json`: 15 diverse example recipes for few-shot learning
- `evaluations/results/`: Evaluation results and analysis data

## Quality Metrics

The evaluation framework measures:
- **Culinary Logic**: Recipe coherence and technique appropriateness
- **Ingredient Usage**: Meaningful incorporation of all provided ingredients
- **Instruction Clarity**: Step-by-step clarity and actionability
- **Overall Quality**: Subjective cooking worthiness assessment

## Development Workflow

1. **Make Changes**: Implement features with corresponding tests
2. **Run Tests**: `python -m pytest tests/` to ensure functionality
3. **Evaluate Impact**: Use evaluation framework to measure quality changes
4. **Document Progress**: Update session notes per CLAUDE.md guidelines
5. **Commit**: Pre-commit hooks automatically run tests

## 📚 API Documentation

Comprehensive API documentation is automatically generated from docstrings using pdoc3.

### Generate Documentation
```bash
# Generate fresh API documentation manually
python generate_docs.py

# View documentation
open docs/api/index.html
```

**Automated Generation**: API documentation is automatically generated and updated on every commit via pre-commit hook.

### Documentation Features
- **Automatic Generation**: Generated from PEP 257 compliant docstrings
- **Module Organization**: Clear separation by functionality (core, prompting, recipes, vector, common)
- **Type Annotations**: Full type hint support with argument and return type documentation
- **Cross-References**: Links between related classes and functions
- **Search Functionality**: Built-in search across all modules and functions

### API Overview

**Core Modules:**
- `src.core.cooking_assistant` - Main CookingAssistant interface
- `src.core.conversation_memory` - Session memory management
- `src.core.query_classifier` - Query complexity classification

**Prompting System:**
- `src.prompting.meta_prompting` - Strategy selection and orchestration
- `src.prompting.prompts` - Template creation functions
- `src.prompting.examples` - Few-shot example management

**Recipe Processing:**
- `src.recipes.models` - Recipe validation and data models
- `src.recipes.safety_validator` - AI-powered safety checking

**Vector Database:**
- `src.vector.store` - High-level vector database interface
- `src.vector.embeddings` - OpenAI embedding generation
- `src.vector.filters` - Advanced filtering system
- `src.vector.keywords` - Sparse search utilities

## Architecture Overview

This project demonstrates production-ready GenAI patterns:
- **Advanced Prompt Engineering**: Chain-of-thought, few-shot learning, persona-based prompting
- **Evaluation-Driven Development**: LLM-as-a-judge for systematic quality measurement  
- **Robust Error Handling**: Custom exception hierarchy and validation systems
- **Comprehensive Testing**: Unit tests, integration tests, and evaluation pipelines
- **Documentation Standards**: Session tracking and progress management

## Contributing

This codebase follows strict development standards:
- All new functionality requires unit tests
- Run evaluation framework when modifying prompts or generation logic
- Update documentation per CLAUDE.md requirements
- Maintain 100% test pass rate before commits
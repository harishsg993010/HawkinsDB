# HawkinsDB

A powerful and flexible memory layer with ConceptNet integration and LLM-friendly interfaces. HawkinsDB provides a robust SQLite backend implementation with comprehensive error handling, timestamp management, and memory type validations.

## Features

- **Multiple Memory Types**
  - 🧠 **Semantic Memory**: Store facts, concepts, and their relationships
  - 📅 **Episodic Memory**: Record time-based events with timestamp management
  - 📝 **Procedural Memory**: Store step-by-step procedures with validation

- **Storage Options**
  - 💾 **SQLite Backend**: Robust persistent storage with data integrity
  - 📄 **JSON Backend**: Simple file-based storage for prototyping

- **Smart Integrations**
  - 🤖 **LLM Interface**: Natural language interactions via OpenAI
  - 🌐 **ConceptNet**: Knowledge enrichment and semantic connections

- **Core Capabilities**
  - ✨ Rich property and relationship management
  - ⏱ Precise temporal tracking across memory types
  - 🔍 Smart search and querying capabilities
  - 🛡 Comprehensive error handling and validation

## Quick Start

### Installation

```bash
# Basic installation
pip install hawkinsdb

# With all features (recommended)
pip install hawkinsdb[all]

# Or install specific features
pip install hawkinsdb[conceptnet]  # For ConceptNet integration
pip install hawkinsdb[llm]         # For LLM interface
pip install hawkinsdb[dev]         # For development
```

### Basic Usage

```python
from hawkinsdb import HawkinsDB

# Initialize database
db = HawkinsDB()

# Add semantic memory
result = db.add_entity({
    "name": "Python",
    "column": "Semantic",
    "properties": {
        "type": "Programming_Language",
        "paradigm": ["Object-oriented", "Functional"],
        "created_by": "Guido van Rossum",
        "year": 1991
    },
    "relationships": {
        "used_for": ["Web Development", "Data Science"],
        "similar_to": ["Ruby", "JavaScript"]
    }
})

# Query the memory
python_info = db.query_frames("Python")
print(python_info["Semantic"].properties)  # Access properties
```

### Using LLM Interface

```python
from hawkinsdb import HawkinsDB, LLMInterface

db = HawkinsDB()
llm = LLMInterface(db, auto_enrich=True)

# Add memory using natural language
result = llm.add_from_text("""
    A Tesla Model 3 is an electric car manufactured by Tesla.
    It has autopilot capabilities and comes in red, white, and black colors.
""")

# Query using natural language
response = llm.query("What color options are available for the Tesla Model 3?")

## Quick Start Guide

### Basic Usage

```python
from hawkinsdb import HawkinsDB

# Initialize the database
db = HawkinsDB()

# Add a semantic memory (concept)
concept = {
    "column": "Semantic",
    "name": "Car",
    "properties": {
        "type": "Vehicle",
        "wheels": 4,
        "purpose": "Transportation"
    },
    "relationships": {
        "has_part": ["Engine", "Wheels", "Body"],
        "is_a": ["Vehicle"]
    }
}
db.add_entity(concept)

# Query the concept
result = db.query_frames("Car")
print(result)
```

### Memory Types Examples

#### 1. Semantic Memory
```python
# Store facts and concepts
semantic_memory = {
    "column": "Semantic",
    "name": "Python_Language",
    "properties": {
        "type": "Programming_Language",
        "paradigm": ["Object-oriented", "Imperative", "Functional"],
        "created_by": "Guido van Rossum",
        "year": 1991
    },
    "relationships": {
        "used_for": ["Web Development", "Data Science", "Automation"],
        "similar_to": ["Ruby", "JavaScript"]
    }
}
db.add_entity(semantic_memory)
```

#### 2. Episodic Memory
```python
# Store events with temporal context
import time

episodic_memory = {
    "column": "Episodic",
    "name": "First_Python_Project",
    "timestamp": time.time(),
    "action": "Completed project",
    "properties": {
        "location": "Home Office",
        "duration": "2 hours",
        "participants": ["User1"],
        "outcome": "Success"
    },
    "relationships": {
        "related_to": ["Python_Language"],
        "followed_by": ["Code_Review"]
    }
}
db.add_entity(episodic_memory)
```

#### 3. Procedural Memory
```python
# Store step-by-step procedures
procedure = {
    "column": "Procedural",
    "name": "Git_Commit_Process",
    "steps": [
        "Stage changes using git add",
        "Review changes with git status",
        "Commit with descriptive message",
        "Push to remote repository"
    ],
    "properties": {
        "difficulty": "Beginner",
        "required_tools": ["Git"],
        "estimated_time": "5 minutes"
    }
}
db.add_entity(procedure)
```

### Advanced Features

#### 1. Using the LLM Interface
```python
from hawkinsdb import HawkinsDB, LLMInterface

db = HawkinsDB()
interface = LLMInterface(db, auto_enrich=True)

# Add entity with natural language
result = interface.add_from_text("""
    Create a car entity named Tesla_Model_3 with color red,
    manufactured in 2023, and located in the garage
""")

# Query using natural language
response = interface.query("What color is the Tesla Model 3?")
print(response)
```

#### 2. Memory Linking
```python
# Link different types of memories
db.add_entity({
    "column": "Episodic",
    "name": "Learning_Git",
    "timestamp": time.time(),
    "action": "Learned Git basics",
    "relationships": {
        "follows": ["Git_Commit_Process"],  # Link to procedural memory
        "uses": ["Git"]  # Link to semantic memory
    }
})
```

#### 3. ConceptNet Enrichment
```python
from hawkinsdb import HawkinsDB, ConceptNetEnricher

db = HawkinsDB()
enricher = ConceptNetEnricher(db)

# Add entity with auto-enrichment
tree_data = {
    "name": "Oak_Tree",
    "column": "Semantic",
    "properties": {
        "type": "Tree",
        "category": "Plant"
    }
}
db.add_entity(tree_data)
enricher.enrich_entity(db, "Oak_Tree", "Tree")
```

## API Reference

### Core Classes

#### HawkinsDB
- `__init__(storage=None)`: Initialize database with optional storage backend
- `add_entity(entity_data)`: Add an entity to the database
- `query_frames(name)`: Query frames by name
- `add_reference_frame(...)`: Low-level API for adding frames

#### LLMInterface
- `__init__(db, auto_enrich=False)`: Initialize LLM interface
- `add_from_text(text)`: Add entity from natural language description
- `query(question)`: Query database using natural language

#### ConceptNetEnricher
- `__init__(db)`: Initialize enricher
- `add_entity_with_enrichment(entity)`: Add and enrich entity
- `enrich_entity(entity)`: Enrich existing entity

### Memory Type Schemas

#### Semantic Memory
```python
{
    "column": "Semantic",
    "name": str,  # Required
    "properties": dict,  # Optional
    "relationships": dict,  # Optional
    "location": dict  # Optional
}
```

#### Episodic Memory
```python
{
    "column": "Episodic",
    "name": str,  # Required
    "timestamp": float,  # Required
    "action": str,  # Required
    "properties": dict,  # Optional
    "relationships": dict,  # Optional
    "location": dict  # Optional
}
```

#### Procedural Memory
```python
{
    "column": "Procedural",
    "name": str,  # Required
    "steps": list,  # Required
    "properties": dict,  # Optional
    "relationships": dict,  # Optional
}
```

## Documentation

For detailed guides and examples, see:
- [Full Documentation](docs/README.md)
- [ConceptNet Integration Guide](docs/conceptnet_guide.md)
- [LLM Interface Guide](docs/llm_interface_guide.md)

## Development

```bash
# Clone the repository
git clone https://github.com/your-username/hawkinsdb.git
cd hawkinsdb

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`pytest tests/`)
6. Submit a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details.


# HawkinsDB Technical Documentation

## Overview

HawkinsDB is a flexible memory storage system designed for semantic, episodic, and procedural memory storage with built-in knowledge enrichment capabilities. It features SQLite backend support, LLM integration, and ConceptNet enrichment.

## Table of Contents
1. [Installation](#installation)
2. [Core Features](#core-features)
3. [Basic Usage](#basic-usage)
4. [Memory Types](#memory-types)
5. [Storage Backend](#storage-backend)
6. [LLM Interface](#llm-interface)
7. [ConceptNet Integration](#conceptnet-integration)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

## Installation

```bash
pip install hawkinsdb
```

## Core Features

- Multiple memory types (Semantic, Episodic, Procedural)
- SQLite persistent storage with ACID compliance
- Natural language interface via LLM
- Automatic knowledge enrichment using ConceptNet
- Property validation and type inference
- Relationship management
- Error handling and validation

## Basic Usage

### Initialization

```python
from hawkinsdb import HawkinsDB , LLMInterface

# Initialize with SQLite storage
db = HawkinsDB(storage_type="sqlite", db_path="memory.db")
llm = LLMInterface(db)
```

### Adding Memories

```python
# Add semantic memory
semantic_memory = {
    "name": "cat",
    "column": "Semantic",
    "properties": {
        "type": "animal",
        "size": "medium",
        "characteristics": ["furry", "agile", "carnivorous"]
    },
    "relationships": {
        "habitat": ["homes", "outdoors"],
        "behavior": ["hunting", "sleeping", "grooming"]
    }
}

result = db.add_entity(semantic_memory)
response = llm.query(
    "Explain the behaviours of cat",
)

# Add episodic memory
import time

episodic_memory = {
    "name": "cat_observation",
    "column": "Episodic",
    "properties": {
        "timestamp": time.time(),
        "action": "Observed cat behavior",
        "location": "Garden",
        "details": "Cat was chasing a butterfly"
    },
    "relationships": {
        "relates_to": ["cat"],
        "observed_by": ["human"]
    }
}

result = db.add_entity(episodic_memory)
```

### Querying Memories

```python
# Query specific entity
cat_info = db.query_frames("cat")

# List all entities
entities = db.list_entities()
```

## Memory Types

### Semantic Memory
Stores conceptual knowledge and facts.

```python
semantic_data = {
    "name": "Photosynthesis",
    "column": "Semantic",
    "properties": {
        "type": "biological_process",
        "location": "plant_cells",
        "components": ["chlorophyll", "sunlight", "water", "carbon_dioxide"],
        "products": ["glucose", "oxygen"]
    },
    "relationships": {
        "occurs_in": ["plants", "algae"],
        "requires": ["light_energy", "chloroplasts"],
        "produces": ["chemical_energy", "organic_compounds"]
    }
}
```

### Episodic Memory
Stores event-based memories with temporal information.

```python
episodic_data = {
    "name": "first_python_project",
    "column": "Episodic",
    "properties": {
        "timestamp": time.time(),
        "duration": "2 hours",
        "location": "home_office",
        "outcome": "successful"
    },
    "relationships": {
        "involves": ["Python_Language"],
        "followed_by": ["code_review"]
    }
}
```

## Storage Backend

### SQLite Configuration

```python
# Initialize with custom SQLite path
db = HawkinsDB(
    storage_type="sqlite",
    db_path="custom_path/memory.db"
)

# Basic operations
try:
    # Add entity
    result = db.add_entity(entity_data)
    
    # Query data
    frames = db.query_frames("entity_name")
    
    # Cleanup
    db.cleanup()  # Close connections
except Exception as e:
    print(f"Storage error: {str(e)}")
```

## LLM Interface

### Initialization and Basic Usage

```python
from hawkinsdb import HawkinsDB, LLMInterface

# Initialize
db = HawkinsDB()
llm = LLMInterface(
    db,
    auto_enrich=True,
    confidence_threshold=0.7,
    max_enrichment_depth=2
)

# Convert natural language to structured data
result = llm.add_from_text("""
    The respiratory system is responsible for taking in oxygen 
    and releasing carbon dioxide. Key organs include the lungs, 
    trachea, and diaphragm.
""")
print(f"Added entity: {result['entity_name']}")

# Complex querying with context
response = llm.query(
    "What are the main components of the respiratory system?",
)
print(f"Response: {response}")




```

## ConceptNet Integration

### Basic Enrichment

```python
from hawkinsdb import ConceptNetEnricher

# Initialize
db = HawkinsDB()
enricher = ConceptNetEnricher()

# Add and enrich entity
entity_data = {
    "name": "Dog",
    "column": "Semantic",
    "properties": {
        "type": "Animal",
        "category": "Pet"
    }
}
db.add_entity(entity_data)
enriched_result = enricher.enrich_entity(db, "Dog", "Animal")
```

### Custom Enrichment

```python
class CustomEnricher(ConceptNetEnricher):
    def __init__(self):
        super().__init__()
        self.min_confidence = 0.7
        
    def filter_relations(self, relations):
        return [r for r in relations if r.weight >= self.min_confidence]

# Use custom enricher
custom_enricher = CustomEnricher()
custom_enricher.enrich_entity(db, "Dog", "Animal")
```

## Error Handling

```python
from hawkinsdb import ValidationError

try:
    # Add entity with validation
    result = db.add_entity({
        "name": "Test",
        "column": "Semantic",
        "properties": {
            "age": "42"  # Will be converted to integer
        }
    })
    
    if result["success"]:
        print(f"Added: {result['entity_name']}")
    else:
        print(f"Error: {result['message']}")
        
except ValidationError as e:
    print(f"Validation error: {str(e)}")
except Exception as e:
    print(f"General error: {str(e)}")
```

## Best Practices

1. Memory Organization
   - Use consistent naming conventions
   - Group related concepts
   - Include relevant metadata
   - Link memories using relationships

2. Performance Optimization
   - Use batch operations for multiple entities
   - Implement proper cleanup
   - Monitor memory usage
   - Cache frequently accessed data

3. Error Prevention
   - Validate data before adding
   - Implement proper error handling
   - Use type hints
   - Follow schema guidelines

4. Integration Tips
   - Test ConceptNet enrichment in development
   - Validate LLM responses
   - Monitor API usage
   - Keep security in mind

For more detailed information about specific features, refer to the individual component guides in the documentation.

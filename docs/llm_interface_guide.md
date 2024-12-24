# LLM Interface Guide

## Overview

The LLM Interface in HawkinsDB provides a natural language interface for interacting with the database. It enables seamless interaction with the memory system through natural language, including:
- Adding new entities from text descriptions
- Querying existing memories using natural language
- Automatic property validation and type inference
- Integration with ConceptNet enrichment
- Confidence scoring for responses

## Features

### Core Capabilities

1. **Natural Language Entity Creation**
   - Convert unstructured text into structured memories
   - Automatic type inference for properties
   - Support for multiple memory types (Semantic, Episodic, Procedural)

2. **Intelligent Querying**
   - Natural language question answering
   - Context-aware responses
   - Multi-entity relationship understanding
   - Temporal query support for episodic memories

3. **Automatic Enrichment**
   - ConceptNet integration for knowledge expansion
   - Property inference from context
   - Relationship discovery
   - Source tracking

4. **Data Quality**
   - Confidence scoring for all properties
   - Automatic validation of property types
   - Inconsistency detection
   - Source attribution

5. **Integration Features**
   - Seamless connection with memory storage
   - Event tracking
   - Error handling
   - Query optimization

## Basic Usage

### 1. Initialization

```python
from hawkinsdb import HawkinsDB, LLMInterface

# Initialize database and LLM interface with auto-enrichment
db = HawkinsDB()
llm = LLMInterface(db, auto_enrich=True)

# Or initialize without auto-enrichment for more control
llm_manual = LLMInterface(db, auto_enrich=False)

# Configure additional settings (optional)
llm = LLMInterface(
    db,
    auto_enrich=True,
    confidence_threshold=0.7,  # Minimum confidence for accepting properties
    max_enrichment_depth=2,    # Maximum depth for ConceptNet enrichment
    validate_properties=True    # Enable strict property validation
)
```

The LLM Interface provides a natural way to interact with HawkinsDB. When initialized:
- It connects to your HawkinsDB instance
- Sets up the natural language processing pipeline
- Configures ConceptNet integration if auto-enrichment is enabled
- Establishes validation rules for properties

### 2. Adding Entities from Text

```python
# Add entity using natural language
result = llm.add_from_text("""
    A Tesla Model 3 is an electric car manufactured by Tesla. 
    It has autopilot capabilities, a glass roof, and typically comes 
    in various colors including red, white, and black.
""")

if result["success"]:
    print(f"Added entity: {result['entity_name']}")
    print(f"Enriched: {result['enriched']}")
```

### 3. Querying with Natural Language

```python
# Ask questions about stored entities
response = llm.query("What features does the Tesla Model 3 have?")
print(f"Answer: {response['response']}")

# Query specific entity details
details = llm.query_entity("Tesla_Model_3", include_metadata=True)
print(f"Entity details: {details}")
```

## Advanced Features

### 1. Property Validation

```python
# The LLM interface automatically validates properties
result = llm.add_from_text("""
    The speed of light is approximately 299,792,458 meters per second.
    It is a fundamental physical constant represented by 'c'.
""")

# Properties are validated and properly typed
print(result["entity_data"]["properties"])
```

### 2. Confidence Scoring

```python
# Query with metadata to see confidence scores
response = llm.query_entity(
    "Speed_of_Light",
    include_metadata=True
)

# Check confidence scores for properties
for prop, value in response["data"]["Semantic"]["properties"].items():
    print(f"{prop}: {value[0]['confidence']}")
```

### 3. Custom Entity Processing

```python
from hawkinsdb.llm_interface import LLMInterface

class CustomLLMInterface(LLMInterface):
    def _process_properties(self, properties):
        """Custom property processing"""
        processed = super()._process_properties(properties)
        # Add custom processing logic
        return processed
```

## Best Practices

### 1. Input Formatting

```python
# Good: Clear, specific descriptions
result = llm.add_from_text("""
    A MacBook Pro is a high-end laptop computer made by Apple.
    It features:
    - Retina display
    - M1 or M2 processor
    - Up to 32GB RAM
    Location: Office desk
""")

# Bad: Vague or ambiguous descriptions
result = llm.add_from_text("It's a computer that does stuff")
```

### 2. Query Formulation

```python
# Good: Specific, focused questions
response = llm.query("What is the processor type in the MacBook Pro?")

# Bad: Vague or compound questions
response = llm.query("Tell me about computers and what they do")
```

### 3. Error Handling

```python
try:
    result = llm.add_from_text(text_description)
    if result["success"]:
        print(f"Added: {result['entity_name']}")
        if result["enriched"]:
            print("Entity was enriched with ConceptNet data")
    else:
        print(f"Error: {result['message']}")
except Exception as e:
    print(f"Error processing text: {str(e)}")
```

## Example Use Cases

### 1. Knowledge Base Population

```python
# Add multiple related entities
descriptions = [
    "Python is a high-level programming language known for its readability",
    "JavaScript is a programming language used primarily for web development",
    "Java is a widely-used object-oriented programming language"
]

for desc in descriptions:
    result = llm.add_from_text(desc)
    if result["success"]:
        print(f"Added programming language: {result['entity_name']}")
```

### 2. Question-Answering System

```python
# Build a simple QA system
def answer_questions(questions):
    for question in questions:
        response = llm.query(question)
        if response["success"]:
            print(f"Q: {question}")
            print(f"A: {response['response']}")
        else:
            print(f"Could not answer: {question}")

# Example usage
questions = [
    "What programming languages are in the database?",
    "What is Python used for?",
    "Compare JavaScript and Java"
]
answer_questions(questions)
```

### 3. Automated Documentation

```python
# Generate structured documentation from text
def document_system(description):
    # Add system description
    result = llm.add_from_text(description)
    if not result["success"]:
        return False
        
    # Query for important aspects
    components = llm.query("What are the main components?")
    features = llm.query("What are the key features?")
    requirements = llm.query("What are the system requirements?")
    
    return {
        "components": components["response"],
        "features": features["response"],
        "requirements": requirements["response"]
    }
```

## Troubleshooting

Common issues and solutions:

1. **Entity Not Added**
   - Check input text clarity
   - Verify required fields
   - Check validation rules
   - Review error messages

2. **Poor Query Responses**
   - Rephrase question
   - Check entity existence
   - Verify data completeness
   - Review context

3. **Performance Issues**
   - Batch similar operations
   - Optimize query patterns
   - Use caching when appropriate
   - Monitor API usage

## API Reference

### LLMInterface Methods

```python
def add_entity(self, entity_json: Union[str, Dict]) -> Dict[str, Any]:
    """Add entity from structured data"""
    
def add_from_text(self, text: str) -> Dict[str, Any]:
    """Add entity from natural language text"""
    
def query(self, question: str) -> Dict[str, Any]:
    """Answer questions about entities"""
    
def query_entity(self, name: str, include_metadata: bool = False) -> Dict[str, Any]:
    """Query specific entity details"""
```

For complete documentation and more examples, see the main [documentation](README.md).

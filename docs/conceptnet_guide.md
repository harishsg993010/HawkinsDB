# ConceptNet Integration Guide

## Overview

HawkinsDB's ConceptNet integration provides powerful knowledge enrichment capabilities by connecting to the ConceptNet knowledge graph. This guide explains how to effectively use this feature to enhance your semantic memories with common-sense knowledge and leverage the power of structured knowledge bases.

## Features

### Core Capabilities
- **Automatic concept enrichment**: Enhance entities with common-sense knowledge
- **Property inference**: Discover new properties based on concept relationships
- **Relationship discovery**: Identify and add meaningful connections
- **Confidence scoring**: Quantify the reliability of enriched data
- **Source tracking**: Monitor the origin of enriched information

### Key Benefits
- Richer semantic understanding
- Improved query capabilities
- Better context awareness
- Enhanced knowledge representation

## Basic Usage

### 1. Direct Enrichment

```python
from hawkinsdb import HawkinsDB, ConceptNetEnricher

# Initialize
db = HawkinsDB()
enricher = ConceptNetEnricher()

# Add basic entity
entity_data = {
    "name": "Dog",
    "column": "Semantic",
    "properties": {
        "type": "Animal",
        "category": "Pet"
    }
}
db.add_entity(entity_data)

# Enrich the entity
enriched_result = enricher.enrich_entity(db, "Dog", "Animal")
print(f"Enrichment status: {enriched_result}")

# Query enriched entity
enriched_dog = db.query_frames("Dog")
print("Enriched properties:", enriched_dog["Semantic"].properties)
print("Enriched relationships:", enriched_dog["Semantic"].relationships)
```

### 2. Automatic Enrichment via LLM Interface

```python
from hawkinsdb import HawkinsDB, LLMInterface

# Initialize with auto-enrichment
db = HawkinsDB()
llm = LLMInterface(db, auto_enrich=True)

# Add entity with automatic enrichment
result = llm.add_from_text(
    "A golden retriever is a friendly dog breed known for its golden coat"
)

# Verify enrichment
if result["success"]:
    entity_name = result["entity_name"]
    enriched_data = db.query_frames(entity_name)
    
    # Print enriched properties
    semantic_frame = enriched_data.get("Semantic")
    if semantic_frame:
        print("Enriched properties:", semantic_frame.properties)
        print("Added relationships:", semantic_frame.relationships)
```

## Enrichment Process

### 1. Property Inference
The enrichment process automatically discovers and adds relevant properties:

a) Physical Characteristics
   ```python
   # Example of physical characteristics enrichment
   car_data = {
       "name": "Car",
       "column": "Semantic",
       "properties": {"type": "Vehicle"}
   }
   db.add_entity(car_data)
   enricher.enrich_properties(db, "Car", ["physical_attributes"])
   ```

b) Common Behaviors
   ```python
   # Enriching with behavior information
   animal_data = {
       "name": "Cat",
       "column": "Semantic",
       "properties": {"type": "Pet"}
   }
   db.add_entity(animal_data)
   enricher.enrich_properties(db, "Cat", ["behaviors"])
   ```

c) Typical Locations
   ```python
   # Location-based enrichment
   tool_data = {
       "name": "Hammer",
       "column": "Semantic",
       "properties": {"type": "Tool"}
   }
   db.add_entity(tool_data)
   enricher.enrich_properties(db, "Hammer", ["locations"])
   ```

d) Related Concepts
   ```python
   # Concept relationship enrichment
   fruit_data = {
       "name": "Apple",
       "column": "Semantic",
       "properties": {"type": "Fruit"}
   }
   db.add_entity(fruit_data)
   enricher.enrich_properties(db, "Apple", ["related_concepts"])
   ```

### 2. Relationship Discovery
The system automatically identifies and establishes various types of relationships:

a) IsA Relationships
```python
# Example of IsA relationship discovery
computer_data = {
    "name": "Laptop",
    "column": "Semantic",
    "properties": {
        "type": "Device",
        "manufacturer": "Generic"
    }
}
db.add_entity(computer_data)
enricher.enrich_relationships(db, "Laptop", relationship_types=["IsA"])
```

b) HasA Relationships
```python
# Discovering part-whole relationships
car_data = {
    "name": "Car",
    "column": "Semantic",
    "properties": {"type": "Vehicle"}
}
db.add_entity(car_data)
enricher.enrich_relationships(db, "Car", relationship_types=["HasA"])
```

c) CapableOf Relationships
```python
# Finding capability relationships
robot_data = {
    "name": "Robot",
    "column": "Semantic",
    "properties": {"type": "Machine"}
}
db.add_entity(robot_data)
enricher.enrich_relationships(db, "Robot", relationship_types=["CapableOf"])
```

d) UsedFor Relationships
```python
# Discovering utility relationships
tool_data = {
    "name": "Screwdriver",
    "column": "Semantic",
    "properties": {"type": "Tool"}
}
db.add_entity(tool_data)
enricher.enrich_relationships(db, "Screwdriver", relationship_types=["UsedFor"])
```

### 3. Confidence Scoring

HawkinsDB implements a sophisticated confidence scoring system:

a) ConceptNet Edge Weights
```python
# Example of confidence-based filtering
class CustomEnricher(ConceptNetEnricher):
    def __init__(self):
        super().__init__()
        self.min_confidence = 0.7  # Set minimum confidence threshold
        
    def filter_relations(self, relations):
        """Custom filtering of ConceptNet relations"""
        return [r for r in relations if r.weight >= self.min_confidence]
```

b) Multiple Source Validation
```python
# Enrichment with multiple sources
enricher = ConceptNetEnricher(
    validate_sources=True,
    min_sources=2
)
enricher.enrich_entity(db, "Computer", "Device")
```

c) Context Relevance
```python
# Context-aware enrichment
enricher = ConceptNetEnricher(
    context_aware=True,
    domain="technology"
)
enricher.enrich_entity(db, "Smartphone", "Device")
```

## Advanced Usage

### 1. Custom Enrichment Rules

```python
from hawkinsdb import ConceptNetEnricher

class CustomEnricher(ConceptNetEnricher):
    def __init__(self):
        super().__init__()
        self.min_confidence = 0.7  # Set minimum confidence threshold
        
    def filter_relations(self, relations):
        """Custom filtering of ConceptNet relations"""
        return [r for r in relations if r.weight >= self.min_confidence]
```

### 2. Selective Property Enrichment

```python
# Enrich specific properties
enricher.enrich_properties(
    db,
    entity_name="Car",
    properties=["parts", "capabilities", "location"]
)
```

### 3. Batch Enrichment

```python
# Enrich multiple related entities
entities = ["Dog", "Cat", "Hamster"]
entity_type = "Pet"

for entity in entities:
    enricher.enrich_entity(db, entity, entity_type)
```

## Best Practices

1. **Entity Preparation**
   - Provide clear entity types
   - Use consistent naming
   - Include basic properties

2. **Enrichment Strategy**
   - Start with core concepts
   - Enrich related entities
   - Validate enriched data
   - Monitor confidence scores

3. **Performance Optimization**
   - Batch similar entities
   - Cache common enrichments
   - Use selective enrichment
   - Set appropriate confidence thresholds

## Error Handling

```python
try:
    enriched = enricher.enrich_entity(db, entity_name, entity_type)
    if enriched:
        print("Successfully enriched entity")
        
        # Verify enrichment
        result = db.query_frames(entity_name)
        if result:
            semantic_frame = result.get("Semantic")
            if semantic_frame:
                print("Enriched properties:", semantic_frame.properties)
                print("Enriched relationships:", semantic_frame.relationships)
    else:
        print("No enrichment data found")
        
except Exception as e:
    print(f"Error during enrichment: {str(e)}")
```

## Troubleshooting

Common issues and solutions:

1. **No Enrichment Data**
   - Check entity name spelling
   - Verify entity type
   - Ensure ConceptNet connectivity
   - Check confidence thresholds

2. **Low Quality Enrichment**
   - Adjust confidence thresholds
   - Provide more specific entity types
   - Use custom filtering
   - Implement validation rules

3. **Performance Issues**
   - Use batch enrichment
   - Implement caching
   - Limit enrichment scope
   - Optimize query patterns

## Examples

### 1. Enriching a Technical Concept

```python
# Add and enrich a technical concept
computer_data = {
    "name": "Laptop",
    "column": "Semantic",
    "properties": {
        "type": "Computer",
        "category": "Device"
    }
}
db.add_entity(computer_data)
enricher.enrich_entity(db, "Laptop", "Computer")
```

### 2. Enriching a Natural Concept

```python
# Add and enrich a natural concept
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

### 3. Enriching an Abstract Concept

```python
# Add and enrich an abstract concept
concept_data = {
    "name": "Happiness",
    "column": "Semantic",
    "properties": {
        "type": "Emotion",
        "category": "Feeling"
    }
}
db.add_entity(concept_data)
enricher.enrich_entity(db, "Happiness", "Emotion")
```

For more examples and detailed API reference, see the main [documentation](README.md).

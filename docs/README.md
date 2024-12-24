## Error Handling and Validation

# This file demonstrates error handling and validation in HawkinsDB

from hawkinsdb import HawkinsDB, ValidationError

db = HawkinsDB()

### Exception Handling

try:
    memory_data = {
        "name": "ExampleMemory",
        "column": "Semantic",
        "properties": {"key": "value"}
    }
    result = db.add_entity(memory_data)
    if result["success"]:
        print(f"Added: {result['entity_name']}")
    else:
        print(f"Error: {result['message']}")
except Exception as e:
    print(f"Error: {str(e)}")


### Memory Type Validation

# Valid semantic memory
valid_semantic = {
    "name": "Computer",
    "column": "Semantic",
    "properties": {
        "type": "Device",
        "components": ["CPU", "RAM", "Storage"]
    }
}

# Invalid memory (missing required fields)
invalid_memory = {
    "name": "Computer",
    "properties": {
        "type": "Device"
    }
}

# Validation happens automatically
result = db.add_entity(valid_semantic)    # Succeeds
print(f"Valid Semantic Memory Result: {result}")
result = db.add_entity(invalid_memory)    # Fails with validation error
print(f"Invalid Memory Result: {result}")


### Property Validation

try:
    # Invalid property type
    db.add_entity({
        "name": "Test",
        "column": "Semantic",
        "properties": {
            "age": "not_a_number"  # Should be an integer
        }
    })
except ValidationError as e:
    print(f"Validation error: {str(e)}")

# Property type coercion
result = db.add_entity({
    "name": "Test",
    "column": "Semantic",
    "properties": {
        "age": "42"  # String will be converted to integer
    }
})
print(f"Property Type Coercion Result: {result}")

## Best Practices and Common Patterns

### 1. Memory Organization
- Group related concepts in semantic memory
- Use consistent naming conventions
- Link memories using relationships
- Include relevant metadata

### 2. Performance Optimization
- Use batch operations for multiple entities
- Implement proper cleanup
- Monitor memory usage
- Cache frequently accessed data

### 3. Error Prevention
- Validate data before adding
- Implement proper error handling
- Use type hints when possible
- Follow the schema guidelines

### 4. Integration Tips
- Test ConceptNet enrichment in development
- Validate LLM responses
- Monitor API usage
- Keep security in mind

## Contributing
# Using SQLite Backend with HawkinsDB

HawkinsDB supports SQLite as a persistent storage backend, providing robust data storage with ACID compliance.

## Configuration

To use SQLite storage:

```python
from hawkinsdb import HawkinsDB

# Initialize database
db = HawkinsDB()

# Enable SQLite storage
db.config.set_storage_backend('sqlite')

# Optionally configure SQLite path (default: ./hawkins_memory.db)
db.config.set_storage_path('path/to/your/database.db')
```

## Key Features

- **Persistent Storage**: Data remains available between sessions
- **ACID Compliance**: Ensures data integrity
- **Concurrent Access**: Safe for multi-threaded applications
- **Automatic Schema Management**: Tables created and updated automatically

## Basic Operations

### Adding Entities

```python
entity_data = {
    "name": "Tesla Model 3",
    "properties": {
        "color": "red",
        "year": 2023
    },
    "relationships": {
        "located_in": ["garage"]
    }
}

result = db.add_entity(entity_data)
```

### Querying Data

```python
# Get all frames for an entity
frames = db.query_frames("Tesla Model 3")

# List all entities
entities = db.list_entities()
```

### Error Handling

```python
try:
    result = db.add_entity(entity_data)
except ValueError as e:
    print(f"Invalid data: {str(e)}")
except Exception as e:
    print(f"Storage error: {str(e)}")
```

## Advanced Usage

### Bulk Operations

```python
entities = [
    {"name": "Entity1", "properties": {...}},
    {"name": "Entity2", "properties": {...}}
]

for entity in entities:
    db.add_entity(entity)
```

### Custom Queries

The SQLite backend supports custom queries through the storage interface:

```python
from hawkinsdb.storage import get_storage_backend

storage = get_storage_backend('sqlite')
storage.execute_query("SELECT * FROM entities WHERE name LIKE ?", ("%Tesla%",))
```

## Best Practices

1. **Enable SQLite Early**: Configure SQLite backend before any database operations
2. **Use Error Handling**: Always wrap database operations in try-except blocks
3. **Regular Backups**: SQLite files can be easily backed up by copying the database file
4. **Proper Cleanup**: Close database connections when finished:
   ```python
   db.cleanup()  # Closes connections and frees resources
   ```

## Performance Considerations

- SQLite performs best with moderate-sized datasets
- For very large datasets, consider using batch operations
- Index frequently queried fields for better performance

## Troubleshooting

Common issues and solutions:

1. **Database Locked**
   - Ensure proper connection cleanup
   - Reduce concurrent access if needed

2. **Permission Errors**
   - Check file and directory permissions
   - Ensure write access to the database directory

3. **Disk Space**
   - Monitor available disk space
   - Implement regular cleanup of unused data

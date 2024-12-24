"""Example demonstrating HawkinsDB usage with SQLite backend."""
import logging
from hawkinsdb import HawkinsDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize HawkinsDB with SQLite backend
    db = HawkinsDB(storage_type='sqlite', db_path='example.db')
    
    # Example 1: Adding Semantic Memory
    semantic_data = {
        "name": "Tesla Model 3",
        "properties": {
            "color": "red",
            "year": 2023,
            "features": ["autopilot", "glass roof"]
        },
        "relationships": {
            "manufactured_by": ["Tesla"],
            "located_in": ["garage"]
        }
    }
    
    try:
        result = db.add_entity(semantic_data)
        logger.info(f"Added semantic memory: {result}")
    except Exception as e:
        logger.error(f"Error adding semantic memory: {e}")

    # Example 2: Adding Episodic Memory
    episodic_data = {
        "name": "first_drive",
        "properties": {
            "timestamp": "2024-01-01T10:00:00",
            "action": "test drive",
            "duration": "45 minutes"
        },
        "relationships": {
            "involves": ["Tesla Model 3"],
            "location": ["dealership"]
        }
    }
    
    try:
        db.add_reference_frame(
            column_name="Episodic",
            name=episodic_data["name"],
            properties=episodic_data["properties"],
            relationships=episodic_data["relationships"],
            memory_type="Episodic"
        )
        logger.info("Added episodic memory successfully")
    except Exception as e:
        logger.error(f"Error adding episodic memory: {e}")

    # Query and display stored information
    try:
        # List all entities
        entities = db.list_entities()
        logger.info(f"Stored entities: {entities}")

        # Query specific entity
        tesla_frames = db.query_frames("Tesla Model 3")
        for column, frame in tesla_frames.items():
            logger.info(f"\nColumn: {column}")
            logger.info(f"Properties: {frame.properties}")
            logger.info(f"Relationships: {frame.relationships}")
            
    except Exception as e:
        logger.error(f"Error querying data: {e}")

    # Cleanup
    db.storage.cleanup()

if __name__ == "__main__":
    main()

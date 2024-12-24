"""Complete example demonstrating HawkinsDB usage with SQLite backend."""
import os
import logging
from datetime import datetime
from hawkinsdb import HawkinsDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize HawkinsDB with SQLite backend."""
    try:
        # Initialize with SQLite backend
        db = HawkinsDB(storage_type='sqlite', db_path='example.db')
        logger.info("Database initialized successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

def add_example_semantic_memory(db):
    """Add semantic memory examples."""
    try:
        # Example semantic memory
        car_data = {
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
        
        result = db.add_entity(car_data)
        logger.info(f"Added semantic memory: {result}")
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
    except Exception as e:
        logger.error(f"Error adding semantic memory: {str(e)}")

def add_example_episodic_memory(db):
    """Add episodic memory examples."""
    try:
        # Example episodic memory with proper timestamp format
        current_time = datetime.now().isoformat()
        test_drive = {
            "name": "first_drive",
            "properties": {
                "timestamp": current_time,
                "action": "test drive",
                "duration": "45 minutes"
            },
            "relationships": {
                "involves": ["Tesla Model 3"],
                "location": ["dealership"]
            }
        }
        
        db.add_reference_frame(
            column_name="Episodic",
            name=test_drive["name"],
            properties=test_drive["properties"],
            relationships=test_drive["relationships"],
            memory_type="Episodic"
        )
        logger.info("Added episodic memory successfully")
        
    except Exception as e:
        logger.error(f"Error adding episodic memory: {str(e)}")

def query_and_display_memory(db):
    """Query and display stored memories."""
    try:
        # List all entities
        entities = db.list_entities()
        logger.info(f"\nStored entities: {entities}")

        # Query specific memories
        for entity_name in entities:
            frames = db.query_frames(entity_name)
            logger.info(f"\nMemory frames for '{entity_name}':")
            
            for column_name, frame in frames.items():
                logger.info(f"\nColumn: {column_name}")
                logger.info(f"Properties: {frame.properties}")
                logger.info(f"Relationships: {frame.relationships}")
                if frame.history:
                    logger.info("History:")
                    for timestamp, event in frame.history:
                        logger.info(f"  {timestamp}: {event}")

    except Exception as e:
        logger.error(f"Error querying memory: {str(e)}")

def main():
    """Main execution function demonstrating HawkinsDB usage."""
    try:
        # Setup database
        db = setup_database()
        
        # Add different types of memories
        add_example_semantic_memory(db)
        add_example_episodic_memory(db)
        
        # Query and display stored memories
        query_and_display_memory(db)
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        if 'db' in locals():
            db.cleanup()

if __name__ == '__main__':
    main()

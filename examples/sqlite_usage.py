"""Example demonstrating HawkinsDB usage with SQLite backend."""
import os
import logging
from datetime import datetime
from pathlib import Path
from hawkinsdb import HawkinsDB
from hawkinsdb.storage.sqlite import SQLiteStorage

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize HawkinsDB with SQLite backend."""
    try:
        # Set custom SQLite path (optional)
        db_path = Path('./hawkins_memory.db').absolute()
        
        # Initialize database with SQLite backend explicitly
        db = HawkinsDB(storage_type='sqlite')  # This is the recommended way
        
        # Alternatively, you can initialize with custom path:
        # storage = SQLiteStorage(db_path=str(db_path))
        # db = HawkinsDB(storage=storage)
        
        logger.info(f"Database initialized with SQLite backend")
        return db
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
# Example memory types supported by HawkinsDB:
# 1. Semantic: For storing facts and properties about entities
# 2. Episodic: For storing time-based events and experiences
# 3. Procedural: For storing step-by-step procedures or workflows

def add_example_entities(db):
    """Add example entities to the database."""
    # Example entities
    entities = [
        {
            "name": "Tesla Model 3",
            "properties": {
                "color": "red",
                "year": 2023,
                "mileage": 1000,
                "features": ["autopilot", "glass roof"]
            },
            "relationships": {
                "located_in": ["garage"],
                "manufactured_by": ["Tesla"]
            }
        },
        {
            "name": "Smart Home Hub",
            "properties": {
                "brand": "HomeKit",
                "connected_devices": 5,
                "firmware_version": "2.1.0"
            },
            "relationships": {
                "controls": ["lights", "thermostat"],
                "connected_to": ["wifi_network"]
            }
        }
    ]
    
    for entity_data in entities:
        try:
            result = db.add_entity(entity_data)
            logger.info(f"Added entity: {result['entity_name']}")
        except ValueError as ve:
            logger.error(f"Invalid entity data: {str(ve)}")
        except Exception as e:
            logger.error(f"Error adding entity {entity_data['name']}: {str(e)}")

def query_and_display_data(db):
    """Query and display stored data."""
    try:
        # List all entities
        entities = db.list_entities()
        logger.info(f"Stored entities: {entities}")
        
        # Query frames for each entity
        for entity_name in entities:
            try:
                frames = db.query_frames(entity_name)
                logger.info(f"\nEntity: {entity_name}")
                
                for column, frame in frames.items():
                    logger.info(f"Column: {column}")
                    logger.info(f"Properties: {frame.properties}")
                    logger.info(f"Relationships: {frame.relationships}")
                    
            except Exception as e:
                logger.error(f"Error querying frames for {entity_name}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error listing entities: {str(e)}")

def main():
    """Main execution function."""
    try:
        # Setup database
        db = setup_database()
        
        # Add example entities
        add_example_entities(db)
        
        # Query and display data
        query_and_display_data(db)
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        # Cleanup (if needed)
        if 'db' in locals():
            db.cleanup()

if __name__ == '__main__':
    main()

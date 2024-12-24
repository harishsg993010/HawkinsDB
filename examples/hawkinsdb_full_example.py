"""
Comprehensive example demonstrating all major features of HawkinsDB.
This example showcases:
1. Basic CRUD operations
2. Advanced caching mechanisms
3. Different memory types (Semantic, Episodic, Procedural)
4. ConceptNet integration
5. Memory type validations
6. Performance monitoring
"""

import logging
import time
import json
from hawkinsdb import HawkinsDB, LLMInterface
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_memory_types(db: HawkinsDB):
    """Demonstrate different memory types and their validations."""
    logger.info("\n=== Testing Different Memory Types ===")
    
    # Semantic Memory
    semantic_data = {
        "name": "Tesla_Model_3",
        "column": "Semantic",
        "properties": {
            "type": "electric_car",
            "manufacturer": "Tesla",
            "year": 2024,
            "features": ["autopilot", "battery_powered", "touch_screen"]
        },
        "relationships": {
            "similar_to": ["Tesla_Model_Y", "Tesla_Model_S"],
            "competes_with": ["BMW_i4", "Polestar_2"]
        }
    }
    db.add_entity(semantic_data)
    logger.info("Added semantic memory: Tesla Model 3")
    
    # Episodic Memory
    episodic_data = {
        "name": "First_Tesla_Drive",
        "column": "Episodic",
        "properties": {
            "timestamp": datetime.now().isoformat(),
            "action": "test_drive",
            "location": {"city": "Palo Alto", "state": "CA"},
            "duration": "45 minutes",
            "participants": ["customer", "sales_rep"]
        }
    }
    db.add_entity(episodic_data)
    logger.info("Added episodic memory: First Tesla Drive")
    
    # Procedural Memory
    procedural_data = {
        "name": "Tesla_Charging_Process",
        "column": "Procedural",
        "properties": {
            "steps": [
                "Park near charging station",
                "Open charging port",
                "Connect charging cable",
                "Initiate charging via touchscreen",
                "Wait for desired charge level",
                "Disconnect charging cable"
            ],
            "required_tools": ["charging_cable", "Tesla_app"],
            "difficulty": "easy"
        }
    }
    db.add_entity(procedural_data)
    logger.info("Added procedural memory: Tesla Charging Process")

# Function removed as caching is no longer supported

def main():
    """Run the comprehensive example."""
    # Initialize database with SQLite storage
    db = HawkinsDB(
        storage_type='sqlite'
    )
    
    try:
        # Test different memory types
        demonstrate_memory_types(db)
        
        # Test queries
        logger.info("\n=== Testing Queries ===")
        tesla_data = db.query_frames("Tesla_Model_3")
        # Convert ReferenceFrame objects to dictionaries before JSON serialization
        tesla_data_dict = {
            column_name: frame.to_dict() 
            for column_name, frame in tesla_data.items()
        }
        logger.info(f"Query result for Tesla Model 3: {json.dumps(tesla_data_dict, indent=2)}")
        
        # List all entities
        logger.info("\n=== All Entities ===")
        all_entities = db.list_entities()
        logger.info(f"Total entities: {len(all_entities)}")
        logger.info(f"Entities: {json.dumps(all_entities, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error during example execution: {e}")
        raise
    finally:
        db.cleanup()

if __name__ == "__main__":
    main()

"""
Complete demonstration of HawkinsDB functionality using both JSON and SQLite backends.
"""
import logging
import os
from hawkinsdb import HawkinsDB
from hawkinsdb.storage.sqlite import SQLiteStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_memory_operations(db: HawkinsDB):
    """Demonstrate core memory operations."""
    logger.info("Adding semantic memory...")
    db.add_entity({
        "name": "Apple",
        "column": "Semantic",
        "properties": {
            "color": "red",
            "taste": "sweet",
            "category": "fruit"
        },
        "relationships": {
            "grows_on": "tree",
            "belongs_to": ["fruits", "healthy_foods"]
        }
    })

    logger.info("Adding episodic memory...")
    db.add_entity({
        "name": "First_Apple_Experience",
        "column": "Episodic",
        "properties": {
            "timestamp": "2024-01-01T12:00:00",
            "action": "tasting an apple",
            "location": "kitchen"
        },
        "relationships": {
            "involves": ["Apple", "Kitchen"]
        }
    })

    logger.info("Adding procedural memory...")
    db.add_entity({
        "name": "Apple_Pie_Recipe",
        "column": "Procedural",
        "properties": {
            "steps": [
                "Peel and slice apples",
                "Mix with sugar and cinnamon",
                "Prepare pie crust",
                "Bake at 375°F for 45 minutes"
            ],
            "difficulty": "medium"
        },
        "relationships": {
            "requires": ["Apple", "Sugar", "Flour"]
        }
    })

    # Query and display results
    logger.info("Querying memories...")
    for entity_name in ["Apple", "First_Apple_Experience", "Apple_Pie_Recipe"]:
        frames = db.query_frames(entity_name)
        logger.info(f"\nFound frames for '{entity_name}':")
        for column_name, frame in frames.items():
            logger.info(f"Column: {column_name}")
            logger.info(f"Properties: {frame.properties}")
            logger.info(f"Relationships: {frame.relationships}")

def main():
    """Run the demonstration with both storage backends."""
    # Clean up any existing test files
    for file in ["demo_json.json", "demo_sqlite.db"]:
        if os.path.exists(file):
            os.remove(file)

    # Demo with JSON storage
    logger.info("\n=== Testing JSON Storage Backend ===")
    json_db = HawkinsDB(db_path="demo_json.json", storage_type="json")
    demo_memory_operations(json_db)
    json_db.cleanup()

    # Demo with SQLite storage
    logger.info("\n=== Testing SQLite Storage Backend ===")
    sqlite_db = HawkinsDB(db_path="demo_sqlite.db", storage_type="sqlite")
    demo_memory_operations(sqlite_db)
    sqlite_db.cleanup()

if __name__ == "__main__":
    main()

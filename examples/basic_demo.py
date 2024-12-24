"""Basic demonstration of HawkinsDB functionality."""
from hawkinsdb import HawkinsDB
import time

def main():
    # Initialize the database
    print("Initializing HawkinsDB...")
    db = HawkinsDB()

    try:
        # Add a semantic memory
        print("\nAdding semantic memory...")
        cat_data = {
            "name": "Cat",
            "column": "Semantic",
            "properties": {
                "type": "Animal",
                "features": ["fur", "whiskers", "tail"],
                "diet": "carnivore"
            },
            "relationships": {
                "preys_on": ["mice", "birds"],
                "related_to": ["tiger", "lion"]
            }
        }
        result = db.add_entity(cat_data)
        print(f"Semantic memory result: {result}")

        # Add an episodic memory
        print("\nAdding episodic memory...")
        event_data = {
            "name": "First Pet",
            "column": "Episodic",
            "properties": {
                "timestamp": str(time.time()),
                "action": "Got my first cat",
                "location": "Pet Store",
                "emotion": "happy",
                "participants": ["family", "pet store staff"]
            }
        }
        result = db.add_entity(event_data)
        print(f"Episodic memory result: {result}")

        # Add a procedural memory
        print("\nAdding procedural memory...")
        procedure_data = {
            "name": "Feed Cat",
            "column": "Procedural",
            "properties": {
                "steps": [
                    "Get cat food from cabinet",
                    "Fill bowl with appropriate amount",
                    "Add fresh water to water bowl",
                    "Call cat for feeding"
                ],
                "frequency": "twice daily",
                "importance": "high"
            }
        }
        result = db.add_entity(procedure_data)
        print(f"Procedural memory result: {result}")

        # Query memories
        print("\nQuerying memories...")
        cat_memories = db.query_frames("Cat")
        print(f"Cat-related memories: {cat_memories}")

        feeding_memories = db.query_frames("Feed Cat")
        print(f"Feeding procedure: {feeding_memories}")

        # List all entities
        print("\nAll entities in database:")
        all_entities = db.list_entities()
        print(f"Entities: {all_entities}")

    except Exception as e:
        print(f"Error during demo: {str(e)}")
        raise

    finally:
        # Cleanup
        db.cleanup()
        print("\nDemo completed.")

if __name__ == "__main__":
    main()
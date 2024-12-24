"""Basic demonstration of HawkinsDB functionality."""
import time
import logging
from hawkinsdb.core import HawkinsDB
from hawkinsdb.enrichment import ConceptNetEnricher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the basic HawkinsDB demonstration."""
    print("\nStarting HawkinsDB Basic Demo...")
    
    # Initialize HawkinsDB with SQLite storage
    db = HawkinsDB(storage_type="sqlite", db_path="demo_basic.db")
    
    # Create a semantic memory
    cat_data = {
        "name": "cat",
        "column": "Semantic",
        "properties": {
            "type": "animal",
            "size": "medium",
            "characteristics": ["furry", "agile", "carnivorous"]
        },
        "relationships": {
            "habitat": ["homes", "outdoors"],
            "behavior": ["hunting", "sleeping", "grooming"]
        }
    }
    
    # Add basic semantic memory
    print("\nAdding basic semantic memory for 'cat'...")
    result = db.add_entity(cat_data)
    print(f"Result: {result}")
    
    # Add episodic memory
    current_time = time.time()
    episode = {
        "name": "cat_observation",
        "column": "Episodic",
        "properties": {
            "timestamp": current_time,
            "action": "Observed cat behavior",
            "location": "Garden",
            "details": "Cat was chasing a butterfly"
        },
        "relationships": {
            "relates_to": ["cat"],
            "observed_by": ["human"]
        }
    }
    
    print("\nAdding episodic memory...")
    result = db.add_entity(episode)
    print(f"Result: {result}")
    
    # Demonstrate ConceptNet enrichment
    print("\nEnriching 'cat' with ConceptNet knowledge...")
    enricher = ConceptNetEnricher()
    enriched = enricher.enrich_entity(db, "cat", "cat")
    print("Enrichment completed")
    
    # Query and display results
    print("\nQuerying semantic memory for 'cat':")
    cat_info = db.query_frames("cat")
    print(cat_info)
    print(f"Retrieved information: {cat_info}")
    
    print("\nQuerying episodic memory:")
    episode_info = db.query_frames("cat_observation")
    print(f"Retrieved episode: {episode_info}")
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()

"""
Comprehensive demonstration of HawkinsDB with both JSON and SQLite backends.
"""
import logging
import os
import time
from hawkinsdb import HawkinsDB, LLMInterface

# Configure logging

os.environ["OPENAI_API_KEY"]="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"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_memory_operations(db: HawkinsDB):
    """Demonstrate core memory operations with different memory types."""
    
    # Add semantic memory
    logger.info("Adding semantic memory...")
    db.add_entity({
        "name": "Computer",
        "column": "Semantic",
        "properties": {
            "type": "Electronic_Device",
            "purpose": "Computing",
            "components": ["CPU", "RAM", "Storage"],
            "power_source": "Electricity"
        },
        "relationships": {
            "found_in": ["Office", "Home"],
            "used_for": ["Work", "Entertainment"]
        },
        "metadata": {
            "confidence": 1.0,
            "source": "manual",
            "timestamp": time.time()
        }
    })

    # Add episodic memory
    logger.info("Adding episodic memory...")
    db.add_entity({
        "name": "First_Computer_Use",
        "column": "Episodic",
        "action": "Setting up new computer",  # Required field for episodic memory
        "properties": {
            "timestamp": str(time.time()),
            "location": "Home Office",
            "duration": "2 hours",
            "outcome": "Success",
            "details": "Initial setup and configuration of the computer"
        },
        "relationships": {
            "involves": ["Computer"],
            "participants": ["User"],
            "next_action": "Software Installation"
        },
        "metadata": {
            "confidence": 1.0,
            "source": "manual",
            "timestamp": time.time()
        }
    })

    # Add procedural memory
    logger.info("Adding procedural memory...")
    db.add_entity({
        "name": "Computer_Startup",
        "column": "Procedural",
        "properties": {
            "steps": [
                "Press power button",
                "Wait for boot sequence",
                "Login to account",
                "Check system status"
            ],
            "difficulty": "Easy",
            "estimated_time": "2 minutes"
        },
        "relationships": {
            "requires": ["Computer"],
            "prerequisites": ["Power_Supply"]
        }
    })

    # Query and display results
    logger.info("\nQuerying memories...")
    for entity_name in ["Computer", "First_Computer_Use", "Computer_Startup"]:
        result = db.query_frames(entity_name)
        logger.info(f"\nMemory frames for '{entity_name}':")
        for column, frame in result.items():
            logger.info(f"Column: {column}")
            logger.info(f"Properties: {frame.properties}")
            logger.info(f"Relationships: {frame.relationships}")

def demonstrate_llm_interface(db: HawkinsDB):
    """Demonstrate LLM interface capabilities."""
    logger.info("\n=== Testing LLM Interface ===")
    
    # Initialize LLM interface with auto-enrichment
    llm = LLMInterface(db, auto_enrich=True)
    
    # Add entity using natural language
    description = """
    Create a semantic memory with name MacBookPro_M2:
    - Type: Computer
    - Brand: Apple
    - Model: MacBook Pro 16"
    - Specifications: M2 chip, 32GB RAM, 1TB storage
    - Location: Office
    - Primary uses: Software development, Video editing
    """
    
    logger.info("Adding entity using natural language...")
    result = llm.add_from_text(description)
    logger.info(f"LLM Add Result: {result}")
    
    # Query using natural language
    queries = [
        "What are the specifications of the MacBook Pro?",
        "What memory types are stored in the database?",
        "How to start a computer according to the stored procedure?"
    ]
    
    for query in queries:
        logger.info(f"\nQuerying: {query}")
        response = llm.query(query)
        logger.info(f"Response: {response}")

def main():
    """Run the comprehensive demonstration."""
    try:
        # Clean up any existing test files
        for file in ["demo_json.json", "demo_sqlite.db"]:
            if os.path.exists(file):
                os.remove(file)
        
        # Demo with JSON storage
        logger.info("\n=== Testing JSON Storage Backend ===")
        json_db = HawkinsDB(db_path="demo_json.json", storage_type="json")
        demonstrate_memory_operations(json_db)
        json_db.cleanup()
        
        # Demo with SQLite storage
        logger.info("\n=== Testing SQLite Storage Backend ===")
        sqlite_db = HawkinsDB(db_path="demo_sqlite.db", storage_type="sqlite")
        demonstrate_memory_operations(sqlite_db)
        
        # Test LLM interface with SQLite backend
        demonstrate_llm_interface(sqlite_db)
        sqlite_db.cleanup()
        
        logger.info("\nDemonstration completed successfully!")
        
    except Exception as e:
        logger.error(f"Demonstration failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
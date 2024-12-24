"""Comprehensive example demonstrating all major features of HawkinsDB."""
import logging
import time
from datetime import datetime
from typing import Dict, Any
from hawkinsdb import HawkinsDB, LLMInterface
from hawkinsdb.types import CorticalColumn, ReferenceFrame, PropertyCandidate
import json
import os
os.environ["OPENAI_API_KEY"]="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"

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demonstrate_basic_operations():
    """Demonstrate basic database operations with both JSON and SQLite backends."""
    # Initialize databases with proper configuration
    json_db = HawkinsDB(db_path="demo_json.json", storage_type="json")
    sqlite_db = HawkinsDB(db_path="demo_sqlite.db", storage_type="sqlite")
    
    # Test data - A Tesla car entity
    car_data = {
        "name": "Tesla_Model_3",
        "column": "Semantic",
        "properties": {
            "color": "red",
            "year": "2023",
            "mileage": "1000 miles",
            "features": ["autopilot capabilities", "glass roof"],
            "type": "electric vehicle"
        },
        "relationships": {
            "type_of": ["Vehicle"],
            "location": "garage"
        }
    }
    
    # Add to both databases
    logger.info("\nAdding car entity to JSON database...")
    json_db.add_entity(car_data)
    
    logger.info("\nAdding car entity to SQLite database...")
    sqlite_db.add_entity(car_data)
    
    # Query and verify data from both databases
    logger.info("\nQuerying JSON database...")
    json_result = json_db.query_frames("Tesla_Model_3")
    if isinstance(json_result, dict):
        formatted_json = {k: v.to_dict() if hasattr(v, 'to_dict') else str(v) 
                            for k, v in json_result.items()}
        logger.info(f"JSON DB Result: {json.dumps(formatted_json, indent=2)}")
    else:
        logger.info(f"JSON DB Result: {str(json_result)}")
            
    logger.info("\nQuerying SQLite database...")
    sqlite_result = sqlite_db.query_frames("Tesla_Model_3")
    if isinstance(sqlite_result, dict):
        formatted_sqlite = {k: v.to_dict() if hasattr(v, 'to_dict') else str(v) 
                              for k, v in sqlite_result.items()}
        logger.info(f"SQLite DB Result: {json.dumps(formatted_sqlite, indent=2)}")
    else:
        logger.info(f"SQLite DB Result: {str(sqlite_result)}")
    
    # Clean up resources
    
    return json_db, sqlite_db

def demonstrate_conceptnet_enrichment(db: HawkinsDB):
    """Demonstrate ConceptNet integration and knowledge enrichment."""
    logger.info("\n=== Demonstrating ConceptNet Integration ===")
    
    # Initialize ConceptNet interface
    from hawkinsdb import ConceptNetEnricher
    
    # Initialize enricher with the database instance
    enricher = ConceptNetEnricher()  # ConceptNet's public API doesn't require a key
    
    # Create an entity with basic information
    entity_name = "Computer"
    entity_type = "Device"
    computer_data = {
        "name": entity_name,
        "column": "Semantic",
        "properties": {
            "type": entity_type,
            "purpose": "Computing",
            "location": "Office"
        }
    }
    
    # First add the entity to the database
    logger.info("Adding computer entity to database...")
    add_result = db.add_entity(computer_data)
    logger.info(f"Add result: {add_result}")
    
    # Then enrich it using ConceptNet
    logger.info("\nEnriching computer entity with ConceptNet data...")
    enriched_data = None

    '''
    
    try:
        # Enrich the entity with both name and type
        enriched = enricher.enrich_entity(
            db=db,
            entity_name=entity_name,
            entity_type=entity_type
        )
        
        if enriched:
            logger.info(f"Successfully enriched entity {entity_name} with ConceptNet data")
            
            # Query the enriched entity
            enriched_data = db.query_frames(entity_name)
            semantic_frame = enriched_data.get("Semantic")
            
            if semantic_frame:
                # Log properties
                logger.info("\nEnriched properties:")
                if hasattr(semantic_frame, 'properties'):
                    for prop_name, candidates in semantic_frame.properties.items():
                        logger.info(f"\n{prop_name}:")
                        if isinstance(candidates, list):
                            for candidate in candidates:
                                if hasattr(candidate, 'value'):
                                    logger.info(f"  - {candidate.value} (confidence: {candidate.confidence:.2f})")
                                else:
                                    logger.info(f"  - {candidate}")
                                    
                # Log relationships
                logger.info("\nEnriched relationships:")
                if hasattr(semantic_frame, 'relationships'):
                    for rel_type, candidates in semantic_frame.relationships.items():
                        logger.info(f"\n{rel_type}:")
                        if isinstance(candidates, list):
                            for candidate in candidates:
                                if hasattr(candidate, 'value'):
                                    logger.info(f"  - {candidate.value} (confidence: {candidate.confidence:.2f})")
                                else:
                                    logger.info(f"  - {candidate}")
        else:
            logger.warning(f"No enrichment data found for entity {entity_name}")
            
    except Exception as e:
        logger.error(f"Error during ConceptNet enrichment: {str(e)}")
        
    return enriched_data

    '''
    
    # Query and display the enriched entity
    try:
        # Query and display the enriched entity
        enriched_result = db.query_frames("computer")
        semantic_frame = enriched_result.get("Semantic")
        
        if semantic_frame:
            logger.info("\nQueried enriched entity:")
            logger.info("\nProperties:")
            if hasattr(semantic_frame, 'properties'):
                for prop_name, candidates in semantic_frame.properties.items():
                    logger.info(f"\n{prop_name}:")
                    if isinstance(candidates, list):
                        for candidate in candidates:
                            if hasattr(candidate, 'value'):
                                logger.info(f"  - {candidate.value} (confidence: {candidate.confidence:.2f})")
                            else:
                                logger.info(f"  - {candidate}")
                    else:
                        logger.info(f"  - {candidates}")
                
                logger.info("\nRelationships:")
                if hasattr(semantic_frame, 'relationships'):
                    for rel_type, candidates in semantic_frame.relationships.items():
                        logger.info(f"\n{rel_type}:")
                        if isinstance(candidates, list):
                            for candidate in candidates:
                                if hasattr(candidate, 'value'):
                                    logger.info(f"  - {candidate.value} (confidence: {candidate.confidence:.2f})")
                                else:
                                    logger.info(f"  - {candidate}")
                        else:
                            logger.info(f"  - {candidates}")
        
        return enriched_result
    except Exception as e:
        logger.error(f"Error querying enriched entity: {str(e)}")
        return None

def demonstrate_llm_interface(db: HawkinsDB):
    """Demonstrate LLM interface for natural language interactions."""
    logger.info("\n=== Demonstrating LLM Interface ===")
    
    # Initialize LLM interface with auto-enrichment and proper error handling
    try:
        llm = LLMInterface(db, auto_enrich=True)
    except Exception as e:
        logger.error(f"Failed to initialize LLM interface: {str(e)}")
        return None, None
    
    # First, add a structured entity to query later
    laptop_entity = {
        "name": "MacBookPro_M3",
        "column": "Semantic",
        "properties": {
            "brand": "Apple",
            "model": "MacBook Pro",
            "year": "2024",
            "processor": "M3 chip",
            "ram": "16GB",
            "storage": "512GB SSD",
            "location": "home office"
        },
        "relationships": {
            "type_of": ["Laptop", "Computer"],
            "manufactured_by": ["Apple"]
        }
    }
    
    # Add the entity directly first
    logger.info("\nAdding MacBook Pro entity...")
    db.add_entity(laptop_entity)
    enriched_data = db.query_frames("MacBookPro_M3")
    semantic_frame = enriched_data.get("Semantic")
    print(semantic_frame)
    # Now demonstrate natural language interaction
    logger.info("\nAdding new entity using natural language...")
    new_entity = {
        "name": "iPhone15Pro",
        "column": "Semantic",
        "properties": {
            "color": "Space Black",
            "storage": "256GB",
            "features": ["A17 Pro chip", "ProMotion display"],
            "location": "desk drawer",
            "type": "smartphone"
        },
        "relationships": {
            "manufacturer": ["Apple"],
            "type_of": ["Mobile Device"]
        }
    }
    # Add entity directly first
    logger.info("Adding iPhone entity directly...")
    test = db.add_entity(new_entity)
    print(test)

    
    # Then demonstrate natural language interaction
    logger.info("\nQuerying using natural language about the new iPhone...")
    llm_result = llm.query("What are the features of the iPhone 15 Pro?")
    logger.info(f"LLM Query Result: {json.dumps(llm_result, indent=2)}")
    
    # Query existing entities using natural language
    logger.info("\nQuerying using natural language...")
    queries = [
        "What are the specifications of the MacBook Pro?",
        "Where is the iPhone 15 Pro located?",
        "List all Apple devices and their features",
        "What is computer for what it is used for",
        "What is Explain about iphone",
        "Explain the Features of Tesla Model 3"
    ]
    
    query_results = []
    for query in queries:
        logger.info(f"\nQuery: {query}")
        result = llm.query(query)
        logger.info(f"Response: {result}")
        query_results.append(result)
    
    return llm_result, query_results

def main():
    """Run comprehensive demonstration of HawkinsDB features."""
    try:
        logger.info("Starting HawkinsDB comprehensive example...")
        
        # Basic operations with both backends
        json_db, sqlite_db = demonstrate_basic_operations()
        
        # ConceptNet integration (using SQLite backend for persistence)
        enriched_data = demonstrate_conceptnet_enrichment(sqlite_db)
        
        # LLM interface demonstration
        llm_results = demonstrate_llm_interface(sqlite_db)
        
        logger.info("Example completed successfully!")
        
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
import logging
from hawkinsdb import HawkinsDB, LLMInterface

logging.basicConfig(level=logging.INFO)

def test_basic_functionality():
    # Initialize database and interface
    db = HawkinsDB()
    interface = LLMInterface(db, auto_enrich=True)
    
    # Test entity with comprehensive data
    test_entity = {
        "column": "Conceptual",
        "type": "Car",
        "name": "TestCar1",
        "properties": {
            "brand": "Tesla",
            "color": "red",
            "model": "Model 3"
        },
        "relationships": {
            "type_of": ["Vehicle", "Transport"],
            "has_part": ["Engine", "Wheels"]
        },
        "location": {"in": "Garage"}
    }
    
    # Add entity
    print("\nAdding test entity...")
    result = interface.add_entity(test_entity)
    print(f"Add result: {result}")
    
    if result['success']:
        # Query the enriched entity
        print("\nQuerying enriched entity...")
        query_result = interface.query_entity('TestCar1', include_metadata=True)
        print(f"Query result: {query_result}")

if __name__ == "__main__":
    test_basic_functionality()

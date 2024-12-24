from hawkinsdb import HawkinsDB, LLMInterface
import json
import logging

logging.basicConfig(level=logging.INFO)

def test_enrichment():
    # Initialize database and interface
    db = HawkinsDB()
    interface = LLMInterface(db, auto_enrich=True)
    
    # Test entity
    car_entity = {
        'column': 'Conceptual',
        'type': 'Car',
        'name': 'TestCar1',
        'properties': {
            'brand': 'Tesla',
            'model': 'Model 3'
        },
        'relationships': {
            'type_of': ['Vehicle']
        }
    }
    
    # Add entity
    print("\nAdding test entity...")
    result = interface.add_entity(car_entity)
    print(f"Add result: {json.dumps(result, indent=2)}")
    
    if result['success']:
        # Query the enriched entity
        print("\nQuerying enriched entity...")
        query_result = interface.query_entity('TestCar1', include_metadata=True)
        print(f"Query result: {json.dumps(query_result, indent=2)}")
        
if __name__ == "__main__":
    test_enrichment()

import logging
from hawkinsdb import HawkinsDB, LLMInterface
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_conceptnet_enrichment():
    # Initialize database and interface with auto-enrichment enabled
    db = HawkinsDB()
    interface = LLMInterface(db, auto_enrich=True)
    
    # Test entity - Car
    car_entity = {
        "column": "Semantic",
        "type": "Car",
        "name": "TestCar",
        "properties": {
            "brand": "Tesla",
            "model": "Model 3"
        },
        "relationships": {
            "type_of": ["Vehicle"]
        }
    }
    
    # Add entity and get enriched data
    print("\nAdding car entity with auto-enrichment...")
    result = interface.add_entity(car_entity)
    print(f"Add result: {json.dumps(result, indent=2)}")
    
    if result['success']:
        # Query the enriched entity
        print("\nQuerying enriched entity...")
        query_result = interface.query_entity('TestCar1', include_metadata=True)
        print(f"Enriched entity data: {json.dumps(query_result, indent=2)}")
        
        # Verify enrichment
        if query_result['success']:
            data = query_result['data']['Conceptual']
            print("\nEnriched properties:")
            for prop_type, values in data['properties'].items():
                print(f"\n{prop_type}:")
                for value in values:
                    if isinstance(value, dict):
                        print(f"  - {value['value']} (confidence: {value['confidence']}, sources: {value['sources']})")
                    else:
                        print(f"  - {value}")
            
            print("\nEnriched relationships:")
            for rel_type, values in data['relationships'].items():
                print(f"\n{rel_type}:")
                for value in values:
                    if isinstance(value, dict):
                        print(f"  - {value['value']} (confidence: {value['confidence']}, sources: {value['sources']})")
                    else:
                        print(f"  - {value}")

if __name__ == "__main__":
    test_conceptnet_enrichment()

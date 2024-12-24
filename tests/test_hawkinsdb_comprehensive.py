"""Comprehensive test suite for HawkinsDB."""
import logging
import time
import json
from datetime import datetime
import pytest
from hawkinsdb import HawkinsDB
from hawkinsdb.types import PropertyCandidate

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestHawkinsDBComprehensive:
    """Comprehensive test suite for HawkinsDB functionality."""
    
    @pytest.fixture
    def db(self):
        """Initialize test database."""
        db = HawkinsDB()
        yield db
        db.cleanup()
    
    def test_property_handling(self, db):
        """Test property handling and validation."""
        # Test various property formats and validations
        property_data = {
            "name": "TestProperty",
            "column": "Semantic",
            "properties": {
                # Test dictionary format with full metadata
                "color": [
                    {"value": "red", "confidence": 0.9, "sources": ["observation"]},
                    {"value": "crimson", "confidence": 0.7, "sources": ["inference"]}
                ],
                # Test direct value with defaults
                "size": "large",
                # Test list with mixed formats
                "tags": [
                    {"value": "test", "confidence": 0.8},
                    "important",
                    {"value": "verified", "sources": ["validation"]}
                ],
                # Test complex value type conversion
                "metadata": {"key": "value", "nested": {"data": True}},
                # Test empty sources
                "status": {"value": "active", "confidence": 1.0, "sources": []}
            }
        }
        
        result = db.add_entity(property_data)
        assert result["success"], f"Failed to add property test: {result.get('message')}"
        
        # Query and validate
        query_results = db.query_frames("TestProperty")
        assert "Semantic" in query_results, "Property test memory not found"
        frame = query_results["Semantic"]
        
        # Validate multi-value property with full metadata
        assert len(frame.properties["color"]) == 2
        assert frame.properties["color"][0].confidence == 0.9
        assert "observation" in frame.properties["color"][0].sources
        assert frame.properties["color"][1].value == "crimson"
        
        # Validate direct value conversion
        assert len(frame.properties["size"]) == 1
        assert frame.properties["size"][0].value == "large"
        assert frame.properties["size"][0].confidence == 1.0
        
        # Validate mixed format list
        assert len(frame.properties["tags"]) == 3
        assert frame.properties["tags"][0].confidence == 0.8
        assert frame.properties["tags"][1].value == "important"
        assert "validation" in frame.properties["tags"][2].sources
        
        # Validate complex value conversion
        assert isinstance(frame.properties["metadata"][0].value, str)
        
        # Validate empty sources handling
        assert frame.properties["status"][0].sources == []
    
    def test_relationship_handling(self, db):
        """Test relationship handling and validation."""
        # Setup test entities with relationships
        entities = [
            {
                "name": "Dog",
                "column": "Semantic",
                "properties": {
                    "type": "Animal",
                    "species": "Canis lupus familiaris"
                },
                "relationships": {
                    "is_a": ["Mammal", "Pet"],  # Simple values get auto-wrapped
                    "has_part": [  # Complex values with confidence and sources
                        {"value": "Tail", "confidence": 1.0, "sources": ["anatomy"]},
                        {"value": "Legs", "confidence": 1.0, "sources": ["anatomy"]},
                        {"value": "Head", "confidence": 1.0, "sources": ["anatomy"]}
                    ],
                    "eats": [
                        {"value": "DogFood", "confidence": 0.95, "sources": ["observation"]},
                        {"value": "Meat", "confidence": 0.8, "sources": ["nature"]}
                    ]
                }
            },
            {
                "name": "Mammal",
                "column": "Semantic",
                "properties": {
                    "type": "Classification",
                    "characteristics": ["warm-blooded", "fur/hair", "mammary_glands"]
                },
                "relationships": {
                    "has_instance": [
                        {"value": "Dog", "confidence": 1.0},
                        {"value": "Cat", "confidence": 1.0}
                    ]
                }
            }
        ]
        
        # Add entities
        for entity in entities:
            result = db.add_entity(entity)
            assert result["success"], f"Failed to add entity: {result.get('message')}"
        
        # Query and validate relationships
        dog_result = db.query_frames("Dog")
        mammal_result = db.query_frames("Mammal")
        
        assert "Semantic" in dog_result, "Dog entity not found"
        assert "Semantic" in mammal_result, "Mammal entity not found"
        
        dog_frame = dog_result["Semantic"]
        mammal_frame = mammal_result["Semantic"]
        
        # Validate bidirectional relationships
        assert any(v.value == "Mammal" for v in dog_frame.relationships["is_a"]), "Missing 'is_a' relationship"
        assert any(v.value == "Dog" for v in mammal_frame.relationships["has_instance"]), "Missing 'has_instance' relationship"
        
        # Validate relationship properties
        assert any(v.value == "Pet" and v.confidence == 0.9 for v in dog_frame.relationships["is_a"])
        assert any(v.value == "DogFood" and v.confidence == 0.95 and "observation" in v.sources for v in dog_frame.relationships["eats"])
    
    def test_query_and_update(self, db):
        """Test querying and updating functionality."""
        # Add test data
        initial_data = {
            "name": "TestEntity",
            "column": "Semantic",
            "properties": {
                "status": "active",  # Simple value gets auto-wrapped
                "tags": {"value": ["test", "initial"], "confidence": 1.0}  # Complex value with confidence
            }
        }
        
        result = db.add_entity(initial_data)
        assert result["success"], "Failed to add initial entity"
        
        # Test querying
        query_result = db.query_frames("TestEntity")
        assert "Semantic" in query_result, "Entity not found in query results"
        frame = query_result["Semantic"]
        assert frame.properties["status"][0].value == "active"
        
        # Test updating
        update_data = {
            "name": "TestEntity",
            "column": "Semantic",
            "properties": {
                "status": PropertyCandidate("inactive", confidence=0.8),
                "tags": ["test", "updated"]
            }
        }
        
        update_result = db.update_entity(update_data)
        assert update_result["success"], "Failed to update entity"
        
        # Verify update
        updated_result = db.query_frames("TestEntity")
        updated_frame = updated_result["Semantic"]
        status_prop = updated_frame.properties.get("status", [])
        assert len(status_prop) > 0, "Status property not found"
        assert status_prop[0].value == "inactive", f"Expected 'inactive' but got {status_prop[0].value}"
        assert status_prop[0].confidence == 0.8, f"Expected confidence 0.8 but got {status_prop[0].confidence}"
    
    def test_error_handling(self, db):
        """Test error handling and validation."""
        # Test invalid entity name
        invalid_name = {
            "name": "",  # Empty name
            "column": "Semantic",
            "properties": {"test": "value"}
        }
        result = db.add_entity(invalid_name)
        assert not result["success"], "Should fail with empty name"
        assert "message" in result, "Error message should be present"
        
        # Test invalid column
        invalid_column = {
            "name": "TestInvalid",
            "column": "InvalidColumn",  # Non-existent column
            "properties": {"test": "value"}
        }
        result = db.add_entity(invalid_column)
        assert not result["success"], "Should fail with invalid column"
        
        # Test invalid property format
        invalid_property = {
            "name": "TestInvalid",
            "column": "Semantic",
            "properties": None  # Invalid properties
        }
        result = db.add_entity(invalid_property)
        assert not result["success"], "Should fail with invalid properties"
        
        # Test duplicate entity handling
        duplicate = {
            "name": "TestDuplicate",
            "column": "Semantic",
            "properties": {"test": "value"}
        }
        first_result = db.add_entity(duplicate)
        assert first_result["success"], "First addition should succeed"
        
        second_result = db.add_entity(duplicate)
        assert not second_result["success"], "Duplicate addition should fail"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--log-cli-level=DEBUG"])
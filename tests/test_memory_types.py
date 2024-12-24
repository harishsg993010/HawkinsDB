"""Test different memory types and their validations."""
import logging
import time
import json
from datetime import datetime
import pytest
from hawkinsdb import HawkinsDB
from hawkinsdb.types import PropertyCandidate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMemoryTypes:
    """Test class for different memory types and their validations."""
    
    @pytest.fixture
    def db(self):
        """Initialize test database."""
        db = HawkinsDB()
        yield db
        db.cleanup()
    
    def validate_episodic_memory(self, case, query_result):
        """Validate episodic memory specific requirements."""
        assert 'timestamp' in query_result, "Episodic memory missing timestamp"
        assert isinstance(query_result.get('timestamp'), (int, float)), "Invalid timestamp type"
        assert 'action' in query_result, "Episodic memory missing action"
        if 'participants' in case:
            assert 'participants' in query_result, "Episodic memory missing participants"
            assert isinstance(query_result.get('participants', []), list), "Participants must be a list"
    
    def validate_procedural_memory(self, case, query_result):
        """Validate procedural memory specific requirements."""
        assert 'steps' in query_result, "Procedural memory missing steps"
        assert isinstance(query_result.get('steps', []), list), "Steps must be a list"
        assert len(query_result.get('steps', [])) > 0, "Steps cannot be empty"
        if 'properties' in case and 'required_tools' in case['properties']:
            assert 'required_tools' in query_result, "Procedural memory missing required tools"
            assert isinstance(query_result.get('required_tools', []), list), "Required tools must be a list"

    def test_semantic_memory(self, db):
        """Test semantic memory creation and validation."""
        semantic_data = {
            "name": "TestConcept1",
            "column": "Semantic",
            "properties": {
                "definition": "A test concept",
                "category": "Test"
            },
            "relationships": {
                "related_to": ["AnotherConcept"],
                "part_of": ["LargerConcept"]
            }
        }
        result = db.add_entity(semantic_data)
        assert result["success"], f"Failed to add semantic memory: {result.get('message')}"
        
        query_results = db.query_frames("TestConcept1")
        assert "Semantic" in query_results, "Semantic memory not found in query results"
        
        frame = query_results["Semantic"]
        assert frame.name == "TestConcept1"
        assert "definition" in frame.properties
        assert "category" in frame.properties

    def test_episodic_memory(self, db):
        """Test episodic memory creation and validation."""
        episodic_data = {
            "name": "TestEvent1",
            "column": "Episodic",
            "timestamp": time.time(),
            "action": "Created test",
            "properties": {
                "location": "Test Environment",
                "duration": "10 minutes",
                "outcome": "Success",
                "participants": ["User1", "System"]
            }
        }
        result = db.add_entity(episodic_data)
        assert result["success"], f"Failed to add episodic memory: {result.get('message')}"
        
        query_results = db.query_frames("TestEvent1")
        assert "Episodic" in query_results, "Episodic memory not found in query results"
        
        frame = query_results["Episodic"]
        self.validate_episodic_memory(episodic_data, frame.to_dict())

    def test_procedural_memory(self, db):
        """Test procedural memory creation and validation."""
        procedural_data = {
            "name": "TestProcedure1",
            "column": "Procedural",
            "steps": [
                "Step 1",
                "Step 2",
                "Step 3"
            ],
            "properties": {
                "purpose": "Test procedure execution",
                "difficulty": "Easy",
                "prerequisites": ["Required skill 1"],
                "success_criteria": ["Criterion 1"]
            }
        }
        result = db.add_entity(procedural_data)
        assert result["success"], f"Failed to add procedural memory: {result.get('message')}"
        
        query_results = db.query_frames("TestProcedure1")
        assert "Procedural" in query_results, "Procedural memory not found in query results"
        
        frame = query_results["Procedural"]
        self.validate_procedural_memory(procedural_data, frame.to_dict())

    def test_invalid_memory_types(self, db):
        """Test invalid memory type validations."""
        invalid_cases = [
            # Missing name
            {
                "column": "Semantic",
                "properties": {"definition": "Should fail"}
            },
            # Invalid timestamp type
            {
                "name": "InvalidEvent1",
                "column": "Episodic",
                "timestamp": "not a timestamp",
                "action": "Should fail"
            },
            # Missing steps
            {
                "name": "InvalidProcedure1",
                "column": "Procedural"
            }
        ]
        
        for case in invalid_cases:
            result = db.add_entity(case)
            assert not result["success"], f"Invalid case should fail: {case}"
            assert "message" in result, "Error message should be present"
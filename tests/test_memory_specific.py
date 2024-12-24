import unittest
import time
from hawkinsdb import HawkinsDB
from hawkinsdb.types import PropertyCandidate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMemoryTypes(unittest.TestCase):
    def setUp(self):
        self.db = HawkinsDB(storage_type='sqlite', db_path=":memory:")
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'db'):
            self.db.cleanup()

        
    def test_procedural_memory_basic(self):
        """Test basic procedural memory creation and retrieval"""
        procedure = {
            "name": "TestProcedure",
            "column": "Procedural",
            "properties": {
                "steps": ["Step1: Initialize system", "Step2: Process data", "Step3: Generate output"],
                "difficulty": "Easy",
                "required_tools": ["Computer", "Software"],
                "duration": "5 minutes"
            },
            "relationships": {
                "requires": ["BasicKnowledge"],
                "part_of": ["LargerProcess"]
            }
        }
        
        # Add procedure through entity API
        result = self.db.add_entity(procedure)
        
        # Query and verify
        frames = self.db.query_frames("TestProcedure")
        self.assertIn("Procedural", frames)
        
        frame = frames["Procedural"]
        self.assertEqual(frame.name.lower(), "testprocedure")  # Name should be normalized
        self.assertTrue(any("steps" in prop for prop in frame.properties.keys()))
        self.assertTrue(any("required_tools" in prop for prop in frame.properties.keys()))
        
    def test_procedural_memory_validation(self):
        """Test validation for procedural memory"""
        # Test missing required fields
        invalid_procedure = {
            "name": "InvalidProcedure",
            "column": "Procedural",
            "properties": {
                "difficulty": "Easy"
            }
        }
        
        with self.assertRaises(HawkinsDB.EntityValidationError):
            self.db.add_entity(invalid_procedure)
            
    def test_episodic_memory_basic(self):
        """Test basic episodic memory creation and retrieval"""
        current_time = time.time()
        episode = {
            "name": "FirstExperience",
            "column": "Episodic",
            "properties": {
                "timestamp": current_time,
                "action": "Ran first test",
                "location": "TestLab",
                "participants": ["User1"],
                "outcome": "Success",
                "duration": "10 minutes"
            },
            "relationships": {
                "related_to": ["TestProcedure"],
                "follows": ["Setup"]
            }
        }
        
        # Add episode through entity API
        result = self.db.add_entity(episode)
        
        # Query and verify
        frames = self.db.query_frames("FirstExperience")
        self.assertIn("Episodic", frames)
        
        frame = frames["Episodic"]
        self.assertEqual(frame.name.lower(), "firstexperience")
        self.assertTrue(any("timestamp" in prop for prop in frame.properties.keys()))
        self.assertTrue(any("location" in prop for prop in frame.properties.keys()))
        self.assertTrue(any("participants" in prop for prop in frame.properties.keys()))
        
    def test_episodic_memory_validation(self):
        """Test validation for episodic memory"""
        # Test missing required fields
        invalid_episode = {
            "name": "InvalidEpisode",
            "column": "Episodic",
            "properties": {
                "location": "TestLab"
            }
        }
        
        with self.assertRaises(HawkinsDB.EntityValidationError):
            self.db.add_entity(invalid_episode)
            
    def test_memory_links(self):
        """Test linking between procedural and episodic memories"""
        # Add a procedure first
        procedure = {
            "name": "LinkedProcedure",
            "column": "Procedural",
            "properties": {
                "steps": ["Step1", "Step2"],
                "difficulty": "Medium",
                "required_tools": ["TestTool"]
            },
            "relationships": {}
        }
        
        # Add procedure through entity API
        result = self.db.add_entity(procedure)
        
        # Add an episode that references the procedure
        current_time = time.time()
        episode = {
            "name": "LinkedEpisode",
            "column": "Episodic",
            "properties": {
                "timestamp": current_time,
                "action": "Executed procedure",
                "location": "TestLocation",
                "participants": ["Tester"]
            },
            "relationships": {
                "follows": ["LinkedProcedure"]
            }
        }
        
        # Add episode through entity API
        result = self.db.add_entity(episode)
        
        # Verify the link
        episode_frames = self.db.query_frames("LinkedEpisode")
        self.assertIn("Episodic", episode_frames)
        self.assertTrue(
            any("LinkedProcedure" in str(rel.value)
                for rel in episode_frames["Episodic"].relationships.get("follows", []))
        )

    def test_sequential_episodes(self):
        """Test creating and linking sequential episodes"""
        base_time = time.time()
        
        # Create a sequence of related episodes
        episodes = [
            {
                "name": f"Episode_{i}",
                "column": "Episodic",
                "properties": {
                    "timestamp": base_time + i * 3600,  # Hour intervals
                    "action": f"Action_{i}",
                    "participants": ["Tester"]
                },
                "relationships": {
                    "follows": [f"Episode_{i-1}"] if i > 0 else []
                }
            } for i in range(3)
        ]
        
        # Add episodes through entity API
        for episode in episodes:
            result = self.db.add_entity(episode)
            
        # Verify sequential relationships
        for i in range(1, 3):
            frames = self.db.query_frames(f"Episode_{i}")
            self.assertTrue(
                any(f"Episode_{i-1}" in str(rel.value) 
                    for rel in frames["Episodic"].relationships.get("follows", []))
            )

if __name__ == '__main__':
    unittest.main()

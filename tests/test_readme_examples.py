import logging
import time
from hawkinsdb import HawkinsDB, LLMInterface
import os



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_readme_examples():
    # Initialize database
    db = HawkinsDB(storage_type='sqlite')
    
    logger.info("\n=== Testing Semantic Memory Example ===")
    # Test semantic memory
    semantic_memory = {
        "column": "Semantic",
        "name": "Python_Language",
        "properties": {
            "type": "Programming_Language",
            "paradigm": ["Object-oriented", "Imperative", "Functional"],
            "created_by": "Guido van Rossum",
            "year": 1991
        },
        "relationships": {
            "used_for": ["Web Development", "Data Science", "Automation"],
            "similar_to": ["Ruby", "JavaScript"]
        }
    }
    
    result = db.add_entity(semantic_memory)
    logger.info(f"Semantic memory add result: {result}")
    frames = db.query_frames("Python_Language")
    logger.info(f"Semantic memory query result: {frames}")
    
    logger.info("\n=== Testing Episodic Memory Example ===")
    # Test episodic memory
    episodic_memory = {
        "column": "Episodic",
        "type": "Event",
        "name": "First_Python_Project",
        "properties": {
            "location": "Home Office",
            "duration": "2 hours",
            "outcome": "Success",
            "timestamp": time.time(),
            "action": "Completed project",
            "participants": ["User1"]
        },
        "relationships": {
            "related_to": ["Python_Language"],
            "followed_by": ["Code_Review"]
        }
    }
    
    result = db.add_entity(episodic_memory)
    logger.info(f"Episodic memory add result: {result}")
    frames = db.query_frames("First_Python_Project")
    logger.info(f"Episodic memory query result: {frames}")
    
    logger.info("\n=== Testing Procedural Memory Example ===")
    # Test procedural memory
    procedural_memory = {
        "column": "Procedural",
        "type": "Procedure",
        "name": "Git_Commit_Process",
        "properties": {
            "difficulty": "Beginner",
            "required_tools": ["Git"],
            "estimated_time": "5 minutes",
            "steps": [
                "Stage changes using git add",
                "Review changes with git status",
                "Commit with descriptive message",
                "Push to remote repository"
            ]
        },
        "relationships": {
            "prerequisites": ["Git_Installation"],
            "followed_by": ["Git_Push_Process"]
        }
    }
    
    result = db.add_entity(procedural_memory)
    logger.info(f"Procedural memory add result: {result}")
    frames = db.query_frames("Git_Commit_Process")
    logger.info(f"Procedural memory query result: {frames}")
    
    logger.info("\n=== Testing LLM Interface Example ===")
    # Test LLM interface
    interface = LLMInterface(db)
    
    # Test natural language addition
    nl_result = interface.add_from_text("""
         The Tesla Model 3 is a battery electric sedan car manufactured by Tesla.
    It has a red exterior color, was manufactured in 2023, and is currently
    located in the garage. It has an estimated range of 358 miles and
    accelerates from 0 to 60 mph in 3.1 seconds.
    """)
    logger.info(f"LLM interface add result: {nl_result}")
    
    # Test natural language query
    query_result = interface.query("Explain about First Python Project")
    logger.info(f"LLM interface query result: {query_result}")

if __name__ == "__main__":
    test_readme_examples()

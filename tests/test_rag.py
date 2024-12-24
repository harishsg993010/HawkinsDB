import json
import logging
import os
from hawkinsdb import HawkinsDB, LLMInterface
from openai import OpenAI

os.environ["OPENAI_API_KEY"]=""


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HawkinsWrapper:
    def __init__(self):
        """Initialize HawkinsDB and its LLM interface."""
        self.db = HawkinsDB(storage_type='sqlite')
        self.llm_interface = LLMInterface(self.db,auto_enrich=True)
        self.client = OpenAI()  # For pre-processing text

    def preprocess_text(self, text):
        """Preprocess text to ensure proper entity structure."""
        system_prompt = """Convert the text into a structured entity format ie json. Follow these rules strictly:

1. ALWAYS include a clear, unique entity name using underscores (e.g., Python_Language, First_Python_Project)
2. ALWAYS include a column type (Semantic, Episodic, or Procedural)
3. Ensure all required fields are present

Required format:
{
    "name": "Entity_Name",  // This is REQUIRED
    "column": "Semantic",   // One of: Semantic, Episodic, Procedural
    "type": "category_type",
    "properties": {
        "key1": "value1",
        "key2": ["value2a", "value2b"]
    },
    "relationships": {
        "related_to": ["entity1", "entity2"]
    }
}

Extract meaningful details and ensure name field is properly set."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            
            # Verify required fields
            if not result.get("name"):
                raise ValueError("Missing required field: name")
            if not result.get("column"):
                result["column"] = "Semantic"  # Default to Semantic if not specified
                
            return result

        except Exception as e:
            logger.error(f"Error in preprocessing: {str(e)}")
            raise

    def add_from_text(self, text):
        """Add entity from text description with preprocessing."""
        try:
            # First preprocess the text to ensure proper structure
            processed_data = self.preprocess_text(text)
            logger.info(f"Preprocessed data: {json.dumps(processed_data, indent=2)}")

            # Add to database using HawkinsDB's add_entity
            result = self.db.add_entity(processed_data)
            
            return {
                "success": True,
                "message": "Successfully added to database",
                "entity_data": processed_data,
                "db_result": result,
                "entity_name": processed_data.get("name")
            }

        except Exception as e:
            logger.error(f"Error adding to database: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "entity_data": None,
                "entity_name": None
            }

    def query_entity(self, entity_name):
        """Query specific entity by name."""
        try:
            frames = self.db.query_frames(entity_name)
            if not frames:
                return {
                    "success": False,
                    "message": f"No entity found with name: {entity_name}",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Entity found",
                "data": frames
            }
            
        except Exception as e:
            logger.error(f"Error querying entity: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "data": None
            }

    def query_by_text(self, query_text):
        """Query database using natural language text."""
        try:
            result = self.llm_interface.query(query_text)
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "response": None
            }

    def list_all_entities(self):
        """List all entities in the database."""
        try:
            entities = self.db.list_entities()
            return {
                "success": True,
                "message": "Entities retrieved successfully",
                "entities": entities
            }
        except Exception as e:
            logger.error(f"Error listing entities: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "entities": None
            }

def test_memory_examples():
    """Test function to demonstrate usage."""
    hawkins = HawkinsWrapper()
    
    # Test adding entries
    examples = [
        """
        Python is a programming language created by Guido van Rossum in 1991.
        It supports object-oriented, imperative, and functional programming.
        It's commonly used for web development, data science, and automation.
        Similar languages include Ruby and JavaScript.
        """,
        """
        Today I completed my first Python project in my home office.
        It took 2 hours and was successful. I did a code review afterwards.
        The project helped me learn about functions and classes.
        """,
        """
        The Tesla Model 3 is red, made in 2023, and parked in the garage.
        It has a range of 358 miles and goes 0-60 mph in 3.1 seconds.
        It features autopilot and a minimalist interior design.
        """,
        """
        Visual Studio Code (VS Code) is a popular code editor developed by Microsoft.
        It was first released in 2015 and is written in TypeScript and JavaScript.
        It supports multiple programming languages through extensions, has integrated
        Git control, and features intelligent code completion. It's commonly used
        alongside Python, JavaScript, and Java development environments.
        """,
        """
        C++ is a beautiful programming language 
        """
    ]

    # Add examples to database
    logger.info("\nAdding examples to database:")
    for i, example in enumerate(examples, 1):
        logger.info(f"\nAdding Example {i}")
        logger.info("=" * 50)
        logger.info(f"Input Text:\n{example}")
        result = hawkins.add_from_text(example)
        logger.info(f"Result: {json.dumps(result, indent=2)}")

    # List all entities
    logger.info("\nListing all entities:")
    entities_result = hawkins.list_all_entities()
    logger.info(f"Entities: {json.dumps(entities_result, indent=2)}")

    # Test natural language queries
    test_queries = [
        "What has car has range of 358 miles and goes 0-60 mph in 3.1 seconds"
    ]

    logger.info("\nTesting natural language queries:")
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        result = hawkins.query_by_text(query)
        logger.info(f"Response: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    test_memory_examples()
import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from openai import OpenAI
from hawkinsdb import HawkinsDB

os.environ["OPENAI_API_KEY"]=""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextToHawkinsDB:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key)
        self.db = HawkinsDB(storage_type='sqlite')

    def text_to_json(self, text: str) -> Dict[str, Any]:
        """Convert text description to HawkinsDB-compatible JSON using GPT-4."""
        prompt = """Convert the following text into a structured JSON format suitable for a memory database. 
        
        Rules:
        1. Extract key entity details, properties, and relationships
        2. Use underscores for entity names (e.g., Python_Language)
        3. Categorize memory as one of: Semantic, Episodic, or Procedural
        4. Include relevant properties and relationships
        
        Required JSON format:
        {
            "column": "memory_type",
            "name": "entity_name",
            "properties": {
                "key1": "value1",
                "key2": ["value2a", "value2b"]
            },
            "relationships": {
                "related_to": ["entity1", "entity2"],
                "part_of": ["parent_entity"]
            }
        }

        Text to convert:
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            json_str = response.choices[0].message.content
            return json.loads(json_str)

        except Exception as e:
            logger.error(f"Error converting text to JSON: {str(e)}")
            raise

    def add_to_db(self, text: str) -> Dict[str, Any]:
        """Convert text to JSON and add to HawkinsDB."""
        try:
            json_data = self.text_to_json(text)
            logger.info(f"Converted JSON: {json.dumps(json_data, indent=2)}")

            result = self.db.add_entity(json_data)
            return {
                "success": True,
                "message": "Successfully added to database",
                "entity_data": json_data,
                "db_result": result
            }

        except Exception as e:
            logger.error(f"Error adding to database: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "entity_data": None,
                "db_result": None
            }

    def query_entity(self, entity_name: str) -> Dict[str, Any]:
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

    def query_by_text(self, query_text: str) -> Dict[str, Any]:
        """Query database using natural language text."""
        try:
            # Get all entities for context
            entities = self.db.list_entities()
            if not entities:
                return {
                    "success": True,
                    "message": "Database is empty",
                    "response": "No information available in the database."
                }

            # Build context from existing entities
            context = []
            for entity_name in entities[:5]:  # Limit to 5 most recent entities
                frames = self.db.query_frames(entity_name)
                if frames:
                    context.append(json.dumps(frames, indent=2))

            # Create prompt with context
            prompt = f"""You are a helpful assistant with access to a knowledge base.
            Answer the following question based on this context:

            Context:
            {' '.join(context)}

            Question: {query_text}

            Rules:
            1. Only use information from the provided context
            2. If information is not in the context, say so
            3. Be specific and include details when available
            4. Format numbers and dates clearly
            """

            # Get response from GPT-4
            response = self.client.chat.completions.create(
                model="gpt4o",
                messages=[
                    {"role": "system", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            answer = response.choices[0].message.content
            
            return {
                "success": True,
                "message": "Query processed successfully",
                "response": answer
            }

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "response": None
            }

    def list_all_entities(self) -> Dict[str, Any]:
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
    converter = TextToHawkinsDB()
    
    # Test adding entries
    examples = [
        """
        Python is a programming language created by Guido van Rossum in 1991.
        It supports object-oriented, imperative, and functional programming.
        It's commonly used for web development, data science, and automation.
        """,
        """
        Today I completed my first Python project in my home office.
        It took 2 hours and was successful. I did a code review afterwards.
        """,
        """
        The Tesla Model 3 is red, made in 2023, and parked in the garage.
        It has a range of 358 miles and goes 0-60 mph in 3.1 seconds.
        """
    ]

    # Add examples to database
    logger.info("\nAdding examples to database:")
    for i, example in enumerate(examples, 1):
        logger.info(f"\nAdding Example {i}")
        logger.info("=" * 50)
        result = converter.add_to_db(example)
        logger.info(f"Result: {json.dumps(result, indent=2)}")

    # Test queries
    logger.info("\nTesting queries:")
    
    # List all entities
    logger.info("\nListing all entities:")
    entities_result = converter.list_all_entities()
    logger.info(f"Entities: {json.dumps(entities_result, indent=2)}")

    # Query specific entity
    logger.info("\nQuerying specific entity:")
    entity_result = converter.query_entity("Python_Language")
    print(entity_result)

    # Test natural language queries
    test_queries = [
        "What programming language was created by Guido van Rossum?",
        "Tell me about the Tesla Model 3's specifications.",
        "What happened during the first Python project?"
    ]

    logger.info("\nTesting natural language queries:")
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        result = converter.query_by_text(query)
        logger.info(f"Response: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    test_memory_examples()
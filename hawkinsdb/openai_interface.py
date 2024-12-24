import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Import OpenAI and related types
try:
    from openai import OpenAI, OpenAIError, BadRequestError
    from openai.types.chat import ChatCompletion
    from openai.types.chat.chat_completion import ChatCompletionMessage
except ImportError as e:
    raise ImportError(f"Failed to import OpenAI SDK v1.0+: {str(e)}. Please ensure you have installed 'openai>=1.0.0'")

from .core import HawkinsDB

logger = logging.getLogger(__name__)

class OpenAIInterface:
    """Interface for OpenAI integration with HawkinsDB."""
    
    def __init__(self, db: HawkinsDB, model: str = "gpt-3.5-turbo-1106"):
        """Initialize OpenAI interface with proper error handling."""
        self.db = db
        self.model = model
        self.max_context_length = 16385  # Model's maximum context length
        
        # Get API key with enhanced error handling
        api_key = self._get_valid_api_key()
        
        # Initialize client and test connection
        try:
            self.client = OpenAI(api_key=api_key, timeout=30.0)
            self._test_connection()
            logger.info("OpenAI interface initialized and connection tested successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise ValueError(f"OpenAI initialization failed: {str(e)}")

    def _get_valid_api_key(self) -> str:
        """Get and validate OpenAI API key from environment or config."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key and hasattr(self.db, 'config'):
            try:
                api_key = self.db.config.get_credential("OPENAI_API_KEY")
            except Exception as e:
                logger.error(f"Error retrieving API key from config: {str(e)}")
                raise ValueError(f"Failed to retrieve OpenAI API key: {str(e)}")
        
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or configure in HawkinsDB.")
            
        # Validate API key format
        if not api_key.startswith(('sk-', 'org-')):
            raise ValueError("Invalid OpenAI API key format")
            
        return api_key
        
    def _test_connection(self) -> None:
        """Test OpenAI API connection with minimal token usage."""
        try:
            # Use a minimal request to test connection
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "Test"}],
                max_tokens=1,
                temperature=0.0  # Deterministic output for testing
            )
            
            # Enhanced type validation for v1.0+
            if not isinstance(response, ChatCompletion):
                logger.error(f"Unexpected response type: {type(response)}")
                raise ValueError(f"Invalid response type from OpenAI API: {type(response)}")
            
            # Comprehensive structural validation for v1.0+
            if not hasattr(response, 'choices'):
                raise ValueError("Invalid API response: missing 'choices' field")
            if not response.choices:
                raise ValueError("Invalid API response: empty choices list")
            if not hasattr(response.choices[0], 'message'):
                raise ValueError("Invalid API response: missing 'message' in first choice")
            if not response.choices[0].message:
                raise ValueError("Invalid API response: empty message in first choice")
            if not hasattr(response.choices[0].message, 'content'):
                raise ValueError("Invalid API response: missing 'content' in message")
            if not response.choices[0].message.content:
                raise ValueError("Invalid API response: empty content in message")
                
            logger.info("OpenAI API connection test successful")
            
        except BadRequestError as be:
            error_msg = str(be).lower()
            if "invalid_api_key" in error_msg or "incorrect api key" in error_msg:
                logger.error(f"Invalid API key error: {error_msg}")
                raise ValueError("Invalid API key provided")
            
        except BadRequestError as be:
            error_msg = str(be).lower()
            logger.error(f"OpenAI API bad request error: {error_msg}")
            
            # Updated error patterns for v1.0+
            if "invalid_api_key" in error_msg or "invalid api key" in error_msg:
                raise ValueError("Invalid API key format or authentication failed")
            elif "insufficient_quota" in error_msg:
                raise ValueError("OpenAI API quota exceeded")
            elif "rate_limit" in error_msg:
                raise ValueError("Rate limit exceeded. Please try again later")
            elif "model_not_found" in error_msg:
                raise ValueError(f"Model '{self.model}' not found")
            elif "permission" in error_msg:
                raise ValueError("Insufficient permissions for this API key")
            else:
                raise ValueError(f"Bad request to OpenAI API: {str(be)}")
            
        except OpenAIError as oe:
            error_msg = str(oe).lower()
            logger.error(f"OpenAI API error: {error_msg}")
            
            # Comprehensive error handling for v1.0+
            if "invalid_api_key" in error_msg or "incorrect api key" in error_msg:
                raise ValueError("Invalid API key. Please check your OpenAI API key")
            elif "rate_limit" in error_msg:
                raise ValueError("Rate limit exceeded. Please try again later")
            elif "context_length_exceeded" in error_msg:
                raise ValueError("Context length exceeded. Reduce input size")
            elif "timeout" in error_msg or "timed out" in error_msg:
                raise ValueError("Request timed out. Please try again")
            elif "insufficient_quota" in error_msg or "exceeded_quota" in error_msg:
                raise ValueError("API quota exceeded. Check usage limits")
            elif "model_not_found" in error_msg:
                raise ValueError(f"Model '{self.model}' not available")
            elif "server_error" in error_msg:
                raise ValueError("OpenAI server error. Please try again")
            else:
                raise ValueError(f"OpenAI API error: {str(oe)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(OpenAIError)
    )
    def parse_entity_from_text(self, text: str) -> Dict[str, Any]:
        """Extract entity information from text using OpenAI."""
        if not text or not text.strip():
            return {
                "success": False,
                "message": "Input text cannot be empty",
                "entity_data": None
            }

        try:
            prompt = """

            You are a precise entity information extractor. Analyze the text and extract relevant entity details in JSON format.

                Required output format:
                {
                    "column": "Semantic",
                    "name": "unique_descriptive_name",
                    "type": "entity_type",
                    "properties": {
                        "attribute1": "value1",
                        "attribute2": ["value2a", "value2b"]
                    },
                    "relationships": {
                        "connected_to": ["related_entity1", "related_entity2"],
                        "part_of": ["parent_entity"]
                    }
                }

                Rules:
                1. ALWAYS provide a clear, unique name for the entity using underscores (e.g., "Tesla_Model_3")
                2. Extract meaningful properties and their values
                3. Identify relationships with other entities
                4. Use clear, consistent property names
                5. Include all relevant details from the text
                6. Return valid JSON only
                7. Include type field based on the entity's category (e.g., "Car", "Event", "Process")


            """
            try:
                # Make API call with JSON mode enabled
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent output
                    max_tokens=1000,
                    response_format={"type": "json_object"}  # Ensure JSON response for v1.0+
                )

                if not isinstance(response, ChatCompletion):
                    logger.error("Unexpected response type from OpenAI API")
                    raise ValueError("Invalid API response format")

                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from OpenAI")

                # Parse and validate the response
                parsed_data = json.loads(content)
                ''''
                if not isinstance(parsed_data, dict):
                    raise ValueError("Response is not a JSON object")
                if "name" not in parsed_data:
                    raise ValueError("Missing required field: name")
                if "properties" not in parsed_data:
                    raise ValueError("Missing required field: properties")
                '''
                return {
                    "success": True,
                    "message": "Successfully parsed entity",
                    "entity_data": parsed_data
                }
                    
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse JSON response: {str(je)}")
                raise ValueError(f"Invalid JSON response: {str(je)}")
                
        except OpenAIError as oe:
            error_msg = str(oe).lower()
            logger.error(f"OpenAI API error: {error_msg}")
            
            if "invalid_api_key" in error_msg or "incorrect api key" in error_msg:
                return {
                    "success": False,
                    "message": "Invalid or incorrect API key provided",
                    "entity_data": None
                }
            elif "rate_limit" in error_msg:
                return {
                    "success": False,
                    "message": "Rate limit exceeded. Please try again later",
                    "entity_data": None
                }
            else:
                return {
                    "success": False,
                    "message": f"OpenAI API error: {str(oe)}",
                    "entity_data": None
                }
        except Exception as e:
            logger.error(f"Unexpected error parsing entity: {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}",
                "entity_data": None
            }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(OpenAIError)
    )
    def answer_question(self, query: str) -> Dict[str, Any]:
        """Answer questions about stored entities using OpenAI."""
        if not query or not query.strip():
            return {
                "success": False,
                "message": "Query cannot be empty",
                "response": None
            }

        try:
            # Get relevant context from database
            entities = self.db.list_entities()
            if not entities:
                return {
                    "success": True,
                    "message": "No entities found in database",
                    "response": "I don't have any information in the database to answer your question."
                }

            # Build context with limited entries and better token management
            context_parts = []
            max_entities = 3  # Reduced from 5 to 3 most recent entities
            estimated_tokens_per_entity = 500  # Conservative estimate
            max_total_tokens = 14000  # Leave room for response
            current_token_estimate = 0
            
            for entity_name in entities[:max_entities]:
                if current_token_estimate >= max_total_tokens:
                    break
                    
                frames = self.db.query_frames(entity_name)
                for column, frame in frames.items():
                    # Validate frame structure
                    if not isinstance(frame, (dict, object)):
                        logger.error(f"Invalid frame type: {type(frame)}")
                        continue

                    # Initialize containers
                    properties = {}
                    relationships = {}
                    location = {}

                    # Get properties based on type
                    raw_properties = (
                        frame.get("properties", {}) if isinstance(frame, dict)
                        else getattr(frame, "properties", {}) if hasattr(frame, "properties")
                        else {}
                    )

                    # Process properties
                    if isinstance(raw_properties, dict):
                        for k, v in raw_properties.items():
                            if isinstance(v, list):
                                properties[k] = []
                                for p in v:
                                    if isinstance(p, dict) and "value" in p:
                                        properties[k].append(str(p["value"]))
                                    elif hasattr(p, "value"):
                                        properties[k].append(str(p.value))
                                    elif p is not None:
                                        properties[k].append(str(p))
                            else:
                                value = (
                                    v["value"] if isinstance(v, dict) and "value" in v
                                    else v.value if hasattr(v, "value")
                                    else v
                                )
                                properties[k] = [str(value)] if value is not None else []

                    # Get relationships based on type
                    raw_relationships = (
                        frame.get("relationships", {}) if isinstance(frame, dict)
                        else getattr(frame, "relationships", {}) if hasattr(frame, "relationships")
                        else {}
                    )

                    # Process relationships
                    if isinstance(raw_relationships, dict):
                        for k, v in raw_relationships.items():
                            if isinstance(v, list):
                                relationships[k] = []
                                for r in v[:2]:  # Limit to 2 relationships per type
                                    if isinstance(r, dict) and "value" in r:
                                        relationships[k].append(str(r["value"]))
                                    elif hasattr(r, "value"):
                                        relationships[k].append(str(r.value))
                                    elif r is not None:
                                        relationships[k].append(str(r))
                            else:
                                value = (
                                    v["value"] if isinstance(v, dict) and "value" in v
                                    else v.value if hasattr(v, "value")
                                    else v
                                )
                                relationships[k] = [str(value)] if value is not None else []

                    # Get location based on type
                    location = (
                        frame.get("location", {}) if isinstance(frame, dict)
                        else getattr(frame, "location", {}) if hasattr(frame, "location")
                        else {}
                    )

                    # Build context data structure with validation
                    context_data = {
                        "name": entity_name,
                        "type": column,
                        "properties": {
                            k: v for k, v in properties.items() 
                            if v and any(val.strip() for val in v)
                        },
                        "relationships": {
                            k: v for k, v in relationships.items()
                            if v and any(val.strip() for val in v)
                        }
                    }

                    # Add location only if it contains meaningful data
                    if location and any(location.values()):
                        context_data["location"] = location

                    logger.debug(f"Processed context data for {entity_name}: {json.dumps(context_data, indent=2)}")
                    
                    # Validate the context data is meaningful before adding
                    if (context_data["properties"] or 
                        context_data["relationships"] or 
                        context_data.get("location")):
                        serialized = json.dumps(context_data, indent=None)
                        estimated_tokens = len(serialized.split())
                        
                        if current_token_estimate + estimated_tokens <= max_total_tokens:
                            context_parts.append(serialized)
                            current_token_estimate += estimated_tokens
                        else:
                            break

            context = "\n".join(context_parts)
            
            # Calculate approximate token count
            context_tokens = len(context.split())
            max_context_tokens = 14000  # Leave room for response and system message
            
            if context_tokens > max_context_tokens:
                # Trim context while preserving structure
                context_parts = context_parts[:2]  # Keep only most recent entries
                context = "\n".join(context_parts)
                logger.info("Context trimmed to fit token limit")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant with access to a knowledge base. "
                            "Answer questions based on the following context, being specific and detailed. "
                            "Include key attributes like colors, measurements, and locations when available. "
                            "If you cannot find certain information in the context, say so clearly.\n\n"
                            "Context:\n"
                            f"{context}"
                        )
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0.3,  # Lower temperature for more consistent, focused responses
                max_tokens=1000,
                presence_penalty=0.1,  # Slight penalty to avoid repetition
                frequency_penalty=0.1   # Slight penalty to encourage varied language
            )
            
            if not isinstance(response, ChatCompletion):
                raise ValueError("Unexpected response type from OpenAI")
                
            answer = response.choices[0].message.content
            if not answer:
                raise ValueError("Empty response from OpenAI")

            return {
                "success": True,
                "message": "Query processed successfully",
                "response": answer
            }
            
        except OpenAIError as oe:
            logger.error(f"OpenAI API error while processing query: {str(oe)}")
            if "context_length_exceeded" in str(oe).lower():
                return {
                    "success": False,
                    "message": "The query context was too long. Try a more specific question.",
                    "response": None
                }
            return {
                "success": False,
                "message": f"OpenAI API error: {str(oe)}",
                "response": None
            }
        except Exception as e:
            logger.error(f"Unexpected error processing query: {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}",
                "response": None
            }

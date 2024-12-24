import json
import logging
from typing import Dict, Optional, Union, List, Any
from collections import defaultdict
from .core import HawkinsDB, PropertyCandidate
from .enrichment import ConceptNetEnricher

logger = logging.getLogger(__name__)

class EntityValidationError(Exception):
    """Custom exception for entity validation errors."""
    pass

class LLMInterface:
    """High-level interface for LLM interaction with HawkinsDB."""
    
    DEFAULT_CONFIDENCE = 0.9  # High confidence for direct LLM inputs
    
    def __init__(self, db: HawkinsDB, auto_enrich: bool = False):
        self.db = db
        self.auto_enrich = auto_enrich
        self.enricher = ConceptNetEnricher() if auto_enrich else None
        
    def _validate_entity_data(self, data: Dict[str, Any]) -> None:
        """Validate entity data before insertion."""
        if not isinstance(data, dict):
            raise EntityValidationError("Input must be a dictionary")

        # Required fields validation - only name is strictly required
        if not data.get("name"):
            raise EntityValidationError("Missing required field: name")

        # Type validations
        if not isinstance(data.get("properties", {}), dict):
            raise EntityValidationError("Properties must be a dictionary")
            
        if not isinstance(data.get("relationships", {}), dict):
            raise EntityValidationError("Relationships must be a dictionary")
            
        if "location" in data and not isinstance(data["location"], dict):
            raise EntityValidationError("Location must be a dictionary")
            
    # Column validation
        column = data.get("column", "Semantic")
        valid_columns = {"Semantic", "Episodic", "Procedural", "Visual"}
        if column not in valid_columns:
            raise EntityValidationError(f"Invalid column. Must be one of: {', '.join(valid_columns)}")
            
        # Property and relationship value validations
        for prop_dict in [data.get("properties", {}), data.get("relationships", {})]:
            for key, value in prop_dict.items():
                if not isinstance(key, str):
                    raise EntityValidationError(f"Property/Relationship keys must be strings: {key}")
                if not value:
                    continue  # Allow empty values, just skip them
    def _process_properties(self, properties: Dict[str, Any]) -> Dict[str, List[PropertyCandidate]]:
        """Convert raw properties to PropertyCandidate objects."""
        processed = {}
        for key, value in properties.items():
            if isinstance(value, (list, tuple)):
                processed[key] = [
                    PropertyCandidate(v, self.DEFAULT_CONFIDENCE, ["LLM"]) 
                    for v in value
                ]
            else:
                processed[key] = [
                    PropertyCandidate(value, self.DEFAULT_CONFIDENCE, ["LLM"])
                ]
        return processed
        
    def _process_relationships(self, relationships: Dict[str, Any]) -> Dict[str, List[PropertyCandidate]]:
        """Convert raw relationships to PropertyCandidate objects."""
        processed = {}
        for rel_type, targets in relationships.items():
            if isinstance(targets, (list, tuple)):
                processed[rel_type] = [
                    PropertyCandidate(target, self.DEFAULT_CONFIDENCE, ["LLM"]) 
                    for target in targets
                ]
            else:
                processed[rel_type] = [
                    PropertyCandidate(targets, self.DEFAULT_CONFIDENCE, ["LLM"])
                ]
        return processed
    
    def add_entity(self, entity_json: Union[str, Dict]) -> Dict[str, Any]:
        """
        Add an entity from LLM-generated JSON with automatic ConceptNet enrichment.
        
        Example input:
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
        
        Returns:
        {
            "success": bool,
            "message": str,
            "entity_name": str,
            "enriched": bool,
            "enrichment_details": {
                "added_properties": List[str],
                "added_relationships": List[str]
            }
        }

        Features:
        - Automatic validation of input data structure
        - ConceptNet enrichment for common knowledge (when enabled)
        - Property deduplication and confidence scoring
        - Relationship inference and validation
        """
        try:
            # Parse input
            if isinstance(entity_json, str):
                try:
                    data = json.loads(entity_json)
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "message": "Invalid JSON format",
                        "entity_name": None,
                        "enriched": False
                    }
            else:
                data = entity_json
                
            # Validate input
            try:
                self._validate_entity_data(data)
            except EntityValidationError as e:
                return {
                    "success": False,
                    "message": str(e),
                    "entity_name": None,
                    "enriched": False
                }
                
            # Extract and process fields
            column = data.get("column", "Semantic")
            name = data["name"]
            raw_properties = data.get("properties", {})
            raw_relationships = data.get("relationships", {})
            location = data.get("location")
            
            # Process properties and relationships
            properties = self._process_properties(raw_properties)
            relationships = self._process_relationships(raw_relationships)
            
            # Add to database
            entity_data = {
                "name": name,
                "column": column,
                "properties": properties,
                "relationships": relationships,
                "location": location
            }
            self.db.add_entity(entity_data)
            
            enriched = False
            # Auto-enrich if enabled
            if self.auto_enrich and self.enricher:
                entity_type = data.get("type")
                if entity_type:
                    self.enricher.enrich_entity(self.db, name, entity_type)
                    enriched = True
                    
            return {
                "success": True,
                "message": "Entity added successfully",
                "entity_name": name,
                "enriched": enriched
            }
            
        except Exception as e:
            logger.error(f"Error adding entity: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "entity_name": None,
                "enriched": False
            }
            
    def add_from_text(self, text: str) -> Dict[str, Any]:
        """
        Convert natural language text into an entity and add it to the database.
        
        Args:
            text: Natural language description of the entity to add
            
        Returns:
            Dict containing operation result and entity data
        """
        try:
            # Parse text into structured data using OpenAI
            from .openai_interface import OpenAIInterface
            openai_interface = OpenAIInterface(self.db)
            entity_data = openai_interface.parse_entity_from_text(text)
            
            if not entity_data:
                return {
                    "success": False,
                    "message": "Failed to parse entity from text",
                    "entity_name": None,
                    "entity_data": None
                }
            
            # Add the parsed entity
            result = self.add_entity(entity_data)
            if result["success"]:
                return {
                    "success": True,
                    "message": "Entity successfully added",
                    "entity_name": result["entity_name"],
                    "entity_data": entity_data
                }
            return result
            
        except Exception as e:
            logger.error(f"Error adding entity from text: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "entity_name": None,
                "entity_data": None
            }
            
    def query(self, question: str) -> Dict[str, Any]:
        """
        Answer questions about entities using natural language.
        
        Args:
            question: Natural language question about stored entities
            
        Returns:
            Dict containing the answer and query status
        """
        try:
            # Use OpenAI to parse the question and formulate a response
            from .openai_interface import OpenAIInterface
            openai_interface = OpenAIInterface(self.db)
            response = openai_interface.answer_question(question)
            
            return {
                "success": True,
                "message": "Query processed successfully",
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "response": None
            }

    def query_entity(self, name: str, include_metadata: bool = False) -> Dict[str, Any]:
        """
        Query an entity and return results in LLM-friendly format.
        
        Args:
            name: Name of the entity to query
            include_metadata: Whether to include confidence scores and sources
            
        Returns:
            Dict containing entity data or error message
        """
        results = self.db.query_frames(name)
        
        if not results:
            return {
                "success": False,
                "message": f"No entity found with name: {name}",
                "data": None
            }
            
        output = {}
        for col_name, frame in results.items():
            # Handle both dictionary and object responses
            if isinstance(frame, dict):
                properties = frame.get("properties", {})
                relationships = frame.get("relationships", {})
                location = frame.get("location", {})
            else:
                properties = getattr(frame, "properties", {})
                relationships = getattr(frame, "relationships", {})
                location = getattr(frame, "location", {})

            frame_data = {
                "properties": defaultdict(list),
                "relationships": defaultdict(list),
                "location": location
            }
            
            # Process properties
            for prop_name, candidates in properties.items():
                if isinstance(candidates, (list, tuple)):
                    for candidate in candidates:
                        if isinstance(candidate, PropertyCandidate):
                            if include_metadata:
                                frame_data["properties"][prop_name].append({
                                    "value": candidate.value,
                                    "confidence": candidate.confidence,
                                    "sources": candidate.sources
                                })
                            else:
                                frame_data["properties"][prop_name].append(candidate.value)
                        elif isinstance(candidate, dict):
                            if include_metadata:
                                frame_data["properties"][prop_name].append({
                                    "value": candidate.get("value", candidate),
                                    "confidence": candidate.get("confidence", self.DEFAULT_CONFIDENCE),
                                    "sources": candidate.get("sources", ["direct"])
                                })
                            else:
                                frame_data["properties"][prop_name].append(candidate.get("value", candidate))
                        else:
                            if include_metadata:
                                frame_data["properties"][prop_name].append({
                                    "value": candidate,
                                    "confidence": self.DEFAULT_CONFIDENCE,
                                    "sources": ["direct"]
                                })
                            else:
                                frame_data["properties"][prop_name].append(candidate)
                else:
                    # Handle single value case
                    if include_metadata:
                        frame_data["properties"][prop_name].append({
                            "value": candidates,
                            "confidence": self.DEFAULT_CONFIDENCE,
                            "sources": ["direct"]
                        })
                    else:
                        frame_data["properties"][prop_name].append(candidates)
            
            # Process relationships
            for rel_type, candidates in relationships.items():
                if not isinstance(candidates, list):
                    candidates = [candidates]
                    
                for candidate in candidates:
                    if isinstance(candidate, dict):
                        if include_metadata:
                            frame_data["relationships"][rel_type].append({
                                "value": candidate.get("value", candidate),
                                "confidence": candidate.get("confidence", self.DEFAULT_CONFIDENCE),
                                "sources": candidate.get("sources", ["direct"])
                            })
                        else:
                            frame_data["relationships"][rel_type].append(candidate.get("value", candidate))
                    else:
                        if include_metadata:
                            frame_data["relationships"][rel_type].append({
                                "value": candidate,
                                "confidence": self.DEFAULT_CONFIDENCE,
                                "sources": ["direct"]
                            })
                        else:
                            frame_data["relationships"][rel_type].append(candidate)
            
            output[col_name] = frame_data
            
        return {
            "success": True,
            "message": "Entity found",
            "data": output
        }
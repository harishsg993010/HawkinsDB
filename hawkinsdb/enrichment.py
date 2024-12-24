import requests
import logging
from .core import HawkinsDB
from .base import PropertyCandidate
from collections import defaultdict

logger = logging.getLogger(__name__)

class ConceptNetEnricher:
    """Handles auto-enrichment of entities using ConceptNet."""
    
    def __init__(self, api_key=None, cache_enabled=False):
        """Initialize ConceptNet enricher.
        
        Args:
            api_key: Optional API key for ConceptNet (not required for basic usage)
            cache_enabled: Deprecated, kept for backwards compatibility
        """
        self.api_key = api_key
        self.base_url = "http://api.conceptnet.io"
        if cache_enabled:
            logger.warning("Caching has been deprecated and will be removed in future versions")
        
    def get_basic_knowledge(self, concept):
        """
        Retrieve basic knowledge about a concept from ConceptNet.
        Returns a dictionary with properties and relationships.
        
        Args:
            concept: The concept to query (e.g., "car", "house")
            
        Returns:
            Dictionary containing properties and relationships enriched from ConceptNet
        """
        # Removed cache implementation to simplify the code
        # Direct API call without caching
            
        if not concept:
            logger.warning("Empty concept provided")
            return {"properties": {}, "relationships": {}}

        try:
            # Normalize concept name for API
            concept_normalized = concept.lower().replace(" ", "_")
            # Query both direct and related concepts
            urls = [
                f"{self.base_url}/c/en/{concept_normalized}",
                f"{self.base_url}/query?node=/c/en/{concept_normalized}&other=/c/en"
            ]
            
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            all_data = []
            for url in urls:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    all_data.append(response.json())
                else:
                    logger.warning(f"Failed to get ConceptNet data from {url}: {response.status_code}")
            
            if not all_data:
                return {"properties": {}, "relationships": {}}
            
            properties = defaultdict(list)
            relationships = defaultdict(list)
            
            # Process edges to extract meaningful information from all responses
            edges = []
            for response_data in all_data:
                edges.extend(response_data.get('edges', []))
            
            for edge in edges:
                try:
                    # Validate edge structure and language
                    start_node = edge.get('start', {})
                    end_node = edge.get('end', {})
                    
                    if not (start_node.get('language') == 'en' and 
                           end_node.get('language') == 'en'):
                        continue
                    
                    # Enhanced weight validation with fallback
                    try:
                        weight = float(edge.get('weight', 0))
                    except (TypeError, ValueError):
                        logger.warning(f"Invalid weight value in edge: {edge.get('weight')}")
                        continue
                        
                    if weight < 0.5:  # Filter out low confidence assertions
                        continue
                        
                    # Check for malformed edge data
                    if not all([start_node.get('label'), 
                              end_node.get('label'),
                              edge.get('rel', {}).get('label')]):
                        logger.warning(f"Malformed edge data: {edge}")
                        continue
                        
                except Exception as e:
                    logger.warning(f"Error processing edge: {str(e)}")
                    continue
                
                rel = edge.get('rel', {}).get('label')
                if not rel:
                    continue
                        
                end_term = edge.get('end', {}).get('label')
                if not end_term:
                    continue
                        
                # Convert ConceptNet weight to confidence score (0.5 to 1.0)
                confidence = 0.5 + (weight / 2)
                
                # Enhanced relation mapping with comprehensive categorization
                PROPERTY_RELATIONS = {
                    'HasProperty': 'properties',
                    'HasA': 'features',
                    'MadeOf': 'materials',
                    'PartOf': 'components',
                    'HasContext': 'contexts',
                    'HasSubevent': 'subevents',
                    'HasPrerequisite': 'prerequisites',
                    'HasFirstSubevent': 'first_steps',
                    'HasLastSubevent': 'last_steps',
                    'HasSize': 'size',
                    'HasShape': 'shape',
                    'HasColor': 'color',
                    'HasTexture': 'texture',
                    'HasWeight': 'weight',
                    'HasFeel': 'feel',
                    'HasSound': 'sound',
                    'HasTaste': 'taste',
                    'HasSmell': 'smell',
                }
                
                RELATIONSHIP_RELATIONS = {
                    'IsA': 'categories',
                    'CapableOf': 'capabilities',
                    'UsedFor': 'uses',
                    'AtLocation': 'locations',
                    'CreatedBy': 'creators',
                    'PartOf': 'parent_systems',
                    'HasEffect': 'effects',
                    'MotivatedByGoal': 'goals',
                    'SimilarTo': 'similar_concepts',
                    'DerivedFrom': 'origins',
                    'SymbolOf': 'symbolism',
                    'ReceivesAction': 'actions_received',
                    'HasSubevent': 'related_events',
                    'HasPrerequisite': 'prerequisites',
                    'Causes': 'causes',
                    'HasFirstSubevent': 'initial_stages',
                    'HasLastSubevent': 'final_stages',
                    'RelatedTo': 'related_concepts',
                }
                
                if rel in PROPERTY_RELATIONS:
                    prop_key = PROPERTY_RELATIONS[rel]
                    properties[prop_key].append({
                        'value': end_term,
                        'confidence': confidence,
                        'source': f"ConceptNet:{rel}"
                    })
                
                elif rel in RELATIONSHIP_RELATIONS:
                    rel_key = RELATIONSHIP_RELATIONS[rel]
                    relationships[rel_key].append({
                        'value': end_term,
                        'confidence': confidence,
                        'source': f"ConceptNet:{rel}"
                    })
            
            # Filter and clean the data
            def filter_and_sort_by_confidence(items, min_confidence=0.6, max_items=5):
                """
                Filter and sort knowledge items based on confidence and quality.
                
                Args:
                    items: List of items to filter
                    min_confidence: Minimum confidence threshold (default: 0.6)
                    max_items: Maximum number of items to return (default: 5)
                    
                Returns:
                    List of filtered and sorted items
                """
                seen = set()
                filtered = []
                
                # Sort by confidence and filter
                sorted_items = sorted(items, key=lambda x: x['confidence'], reverse=True)
                
                for item in sorted_items:
                    value = item['value'].lower()
                    confidence = item['confidence']
                    
                    # Apply quality filters
                    if (confidence >= min_confidence and
                        value not in seen and
                        len(value.split()) <= 3 and  # Keep concise terms
                        len(value) >= 3 and  # Avoid too short terms
                        not any(c.isdigit() for c in value)):  # Avoid numerical values
                        
                        seen.add(value)
                        filtered.append(item)
                        
                        if len(filtered) >= max_items:
                            break
                            
                return filtered
            
            filtered_data = {
                "properties": {
                    k: filter_and_sort_by_confidence(v)
                    for k, v in properties.items()
                },
                "relationships": {
                    k: filter_and_sort_by_confidence(v)
                    for k, v in relationships.items()
                }
            }
            
            # Return filtered data directly without caching
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error enriching concept {concept}: {str(e)}")
            return {}
    
    def enrich_entity(self, db, entity_name, entity_type):
        """
        Enrich an entity with ConceptNet knowledge.
        
        Args:
            db: HawkinsDB instance to update
            entity_name: Name of the entity to enrich
            entity_type: Type of entity to query in ConceptNet
            
        Returns:
            Enriched entity data or None if enrichment failed
        """
        knowledge = self.get_basic_knowledge(entity_type)
        if not knowledge:
            logger.warning(f"No knowledge found for entity type: {entity_type}")
            return
            
        try:
            # First, get existing entity data
            frames = db.query_frames(entity_name)
            if not frames:
                logger.warning(f"Entity {entity_name} not found in database")
                return None
                
            semantic_frame = frames.get("Semantic", {})
            if not semantic_frame:
                logger.warning(f"No semantic frame found for entity {entity_name}")
                return None
                
            # Convert ReferenceFrame to dictionary if needed
            if hasattr(semantic_frame, 'to_dict'):
                semantic_frame = semantic_frame.to_dict()
            
            # Initialize with empty dicts if needed
            properties = semantic_frame.get('properties', {}) if isinstance(semantic_frame, dict) else {}
            relationships = semantic_frame.get('relationships', {}) if isinstance(semantic_frame, dict) else {}
            
            semantic_frame = {
                'properties': properties,
                'relationships': relationships
            }
        except Exception as e:
            logger.error(f"Error accessing entity data: {str(e)}")
            return None
            
        # Prepare enriched entity data
        enriched_entity = {
            "name": entity_name,
            "column": "Semantic",  # Always add enrichment to semantic memory
            "properties": {},
            "relationships": {}
        }
        
        # Add existing properties and relationships
        if semantic_frame.get('properties'):
            enriched_entity["properties"].update(semantic_frame['properties'])
            
        if semantic_frame.get('relationships'):
            enriched_entity["relationships"].update(semantic_frame['relationships'])
            
        # Add ConceptNet knowledge
        for prop_key, values in knowledge.get("properties", {}).items():
            if prop_key not in enriched_entity["properties"]:
                enriched_entity["properties"][prop_key] = []
                
            # Add new properties with ConceptNet source
            for value in values[:3]:  # Limit to top 3 values
                if isinstance(value, dict) and "value" in value:
                    val = value["value"]
                    # Convert lists to string representation if needed
                    if isinstance(val, (list, tuple)):
                        # Convert each list item to a separate property
                        for v in val:
                            enriched_entity["properties"][prop_key].append({
                                "value": str(v),
                                "confidence": 0.7,  # Lower confidence for auto-enriched properties
                                "sources": ["ConceptNet"]
                            })
                    else:
                        enriched_entity["properties"][prop_key].append({
                            "value": str(val),
                            "confidence": 0.7,  # Lower confidence for auto-enriched properties
                            "sources": ["ConceptNet"]
                        })
                
        for rel_type, targets in knowledge.get("relationships", {}).items():
            if rel_type not in enriched_entity["relationships"]:
                enriched_entity["relationships"][rel_type] = []
                
            # Add new relationships with ConceptNet source
            for target in targets[:3]:  # Limit to top 3 relationships
                if isinstance(target, dict) and "value" in target:
                    val = target["value"]
                    # Ensure relationship targets are strings
                    # Always convert relationships to individual string entries
                    if isinstance(val, (list, tuple)):
                        for v in val:
                            if v:  # Skip empty values
                                enriched_entity["relationships"][rel_type].append({
                                    "value": str(v).strip(),
                                    "confidence": 0.7,
                                    "sources": ["ConceptNet"]
                                })
                    elif val:  # Skip empty values
                        enriched_entity["relationships"][rel_type].append({
                            "value": str(val).strip(),
                            "confidence": 0.7,
                            "sources": ["ConceptNet"]
                        })
                
        # Update entity with enriched data
        if (enriched_entity["properties"] or enriched_entity["relationships"]):
            logger.info(f"Enriching {entity_name} with ConceptNet knowledge")
            db.add_entity(enriched_entity)  # Use add_entity instead of propose_entity_update
            logger.info(f"Successfully enriched {entity_name} with ConceptNet knowledge")
            return enriched_entity
        return None
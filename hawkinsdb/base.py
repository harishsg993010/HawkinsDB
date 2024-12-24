"""Base classes for HawkinsDB."""
from abc import ABC, abstractmethod
from typing import (
    Any, Dict, List, Optional, Sequence, TypeVar, Generic,
    Protocol, runtime_checkable
)
from typing_extensions import TypeAlias
from datetime import datetime
import time

# Type variables for generic implementations
T = TypeVar('T')
T_PropertyCandidate = TypeVar('T_PropertyCandidate', bound='PropertyCandidate')
T_ReferenceFrame = TypeVar('T_ReferenceFrame', bound='ReferenceFrame')
T_CorticalColumn = TypeVar('T_CorticalColumn', bound='CorticalColumn')

@runtime_checkable
class StorageBackend(Protocol[T_CorticalColumn]):
    """Protocol class for storage backends."""
    
    def load_columns(self) -> Sequence[T_CorticalColumn]:
        """Load all columns from storage."""
        ...
        
    def save_columns(self, columns: Sequence[T_CorticalColumn]) -> None:
        """Save all columns to storage."""
        ...
        
    def initialize(self) -> None:
        """Initialize the storage backend."""
        ...
        
    def cleanup(self) -> None:
        """Cleanup any resources."""
        ...

class PropertyCandidate:
    """Represents a candidate value for a property."""

    def __init__(self, value, confidence=1.0, sources=None):
        """Initialize a property candidate with value and metadata."""
        if isinstance(value, dict):
            if 'value' in value:
                self.value = value['value']
                self.confidence = float(value.get('confidence', confidence))
                self.sources = list(value.get('sources', sources or []))
            else:
                self.value = value
                self.confidence = float(confidence)
                self.sources = list(sources) if sources else []
        elif isinstance(value, PropertyCandidate):
            self.value = value.value
            self.confidence = float(value.confidence)
            self.sources = list(value.sources)
        else:
            self.value = value
            self.confidence = float(confidence)
            self.sources = list(sources) if sources else []
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        self.timestamp = time.time()

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "value": self.value,
            "confidence": self.confidence,
            "sources": self.sources,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(d):
        """Create from dictionary representation."""
        if not isinstance(d, dict):
            raise TypeError(f"Expected dict, got {type(d)}")
            
        if 'value' not in d:
            raise ValueError("Dictionary must contain 'value' key")
            
        return PropertyCandidate(
            value=d["value"],
            confidence=float(d.get("confidence", 1.0)),
            sources=list(d.get("sources", []))
        )

class ReferenceFrame:
    """Represents a concept or object as a reference frame."""

    def __init__(self, name, properties=None, relationships=None, location=None, history=None):
        """Initialize frame with proper dictionary handling."""
        # Handle dictionary input
        if isinstance(name, dict):
            data = name
            self.name = data.get('name')
            properties = data.get('properties', {})
            relationships = data.get('relationships', {})
            location = data.get('location', {})
            history = data.get('history', [])
        else:
            self.name = name
            
        self.properties = properties if properties is not None else {}
        self.relationships = relationships if relationships is not None else {}
        self.location = location if location is not None else {}
        self.history = history if history is not None else []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def to_dict(self):
        """Convert frame to dictionary representation."""
        try:
            return {
                "name": self.name,
                "properties": {
                    k: [c.to_dict() if isinstance(c, PropertyCandidate) else {"value": c} for c in candidates] 
                    for k, candidates in self.properties.items()
                },
                "relationships": {
                    k: [c.to_dict() if isinstance(c, PropertyCandidate) else {"value": c} for c in candidates]
                    for k, candidates in self.relationships.items()
                },
                "location": self.location,
                "history": self.history,
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }
        except Exception as e:
            raise ValueError(f"Error converting frame to dict: {str(e)}")

    def __str__(self):
        return f"ReferenceFrame(name={self.name})"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def from_dict(data):
        """Create frame from dictionary representation."""
        try:
            if not isinstance(data, dict):
                if isinstance(data, str):
                    # Handle string input by creating minimal frame
                    return ReferenceFrame(name=data)
                raise TypeError(f"Input must be a dictionary or string, got {type(data)}")

            props = {}
            for k, vlist in data.get("properties", {}).items():
                if isinstance(vlist, (list, tuple)):
                    processed = []
                    for v in vlist:
                        if isinstance(v, dict):
                            processed.append(PropertyCandidate.from_dict(v))
                        else:
                            processed.append(PropertyCandidate(v))
                    props[k] = processed
                else:
                    props[k] = [PropertyCandidate(vlist)]

            rels = {}
            for k, vlist in data.get("relationships", {}).items():
                if isinstance(vlist, (list, tuple)):
                    processed = []
                    for v in vlist:
                        if isinstance(v, dict):
                            processed.append(PropertyCandidate.from_dict(v))
                        else:
                            processed.append(PropertyCandidate(v))
                    rels[k] = processed
                else:
                    rels[k] = [PropertyCandidate(vlist)]

            frame = ReferenceFrame(
                name=data.get("name", ""),
                properties=props,
                relationships=rels,
                location=data.get("location", {}),
                history=data.get("history", [])
            )
            frame.created_at = data.get("created_at", frame.created_at)
            frame.updated_at = data.get("updated_at", frame.updated_at)
            return frame
            
        except Exception as e:
            raise ValueError(f"Error creating frame from dict: {str(e)}")

class CorticalColumn:
    """Represents a collection of reference frames with error handling."""

    def __init__(self, name, frames=None):
        """Initialize a cortical column with proper dictionary handling."""
        # Handle dictionary input
        if isinstance(name, dict):
            data = name
            self.name = data.get('name')
            frames = data.get('frames', [])
            self.created_at = data.get('created_at', datetime.now().isoformat())
            self.updated_at = data.get('updated_at', self.created_at)
        else:
            if not name:
                raise ValueError("Column name cannot be empty")
            self.name = name
            self.created_at = datetime.now().isoformat()
            self.updated_at = self.created_at
            
        self.frames = []
        if frames:
            for frame in frames:
                if isinstance(frame, dict):
                    self.frames.append(ReferenceFrame(frame))
                else:
                    self.frames.append(frame)

    def to_dict(self):
        """Convert column to dictionary representation with error handling."""
        try:
            return {
                "name": self.name,
                "frames": [f.to_dict() for f in self.frames],
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }
        except Exception as e:
            raise ValueError(f"Error converting column to dict: {str(e)}")

    @staticmethod
    def from_dict(data):
        """Create column from dictionary with validation and error handling."""
        try:
            if not isinstance(data, dict):
                raise TypeError("Input must be a dictionary")
                
            if "name" not in data:
                raise ValueError("Column data must contain 'name' field")
                
            frames = []
            for frame_data in data.get("frames", []):
                try:
                    frame = ReferenceFrame.from_dict(frame_data)
                    frames.append(frame)
                except Exception as e:
                    raise ValueError(f"Error creating frame: {str(e)}")
                    
            col = CorticalColumn(name=data["name"], frames=frames)
            col.created_at = data.get("created_at", col.created_at)
            col.updated_at = data.get("updated_at", col.updated_at)
            return col
            
        except Exception as e:
            raise ValueError(f"Error creating column from dict: {str(e)}")

class BaseJSONStorage(StorageBackend[T_CorticalColumn]):
    """Base class for JSON storage implementation."""
    def load_columns(self) -> Sequence[T_CorticalColumn]:
        raise NotImplementedError("Subclasses must implement load_columns")

    def save_columns(self, columns: Sequence[T_CorticalColumn]) -> None:
        raise NotImplementedError("Subclasses must implement save_columns")

    def initialize(self) -> None:
        raise NotImplementedError("Subclasses must implement initialize")

    def cleanup(self) -> None:
        raise NotImplementedError("Subclasses must implement cleanup")
"""Core classes for HawkinsDB memory management."""
import time
from datetime import datetime

class PropertyCandidate:
    """A property candidate with value and metadata."""
    def __init__(self, value, confidence=1.0, sources=None, timestamp=None):
        self.value = value
        self.confidence = confidence
        self.sources = sources or []
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "value": self.value,
            "confidence": self.confidence,
            "sources": self.sources,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        if isinstance(data, dict):
            return cls(
                data.get("value"),
                data.get("confidence", 1.0),
                data.get("sources", []),
                data.get("timestamp", time.time())
            )
        return cls(data)

class ReferenceFrame:
    """Represents a single concept or object."""
    def __init__(self, name, properties=None, relationships=None, location=None, history=None):
        self.name = name
        self.properties = properties or {}
        self.relationships = relationships or {}
        self.location = location or {}
        self.history = history or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "properties": self.properties,
            "relationships": self.relationships,
            "location": self.location,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            data["name"],
            data.get("properties", {}),
            data.get("relationships", {}),
            data.get("location", {}),
            data.get("history", [])
        )

class CorticalColumn:
    """Base class for memory columns."""
    def __init__(self, name, frames=None):
        self.name = name
        self.frames = frames or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

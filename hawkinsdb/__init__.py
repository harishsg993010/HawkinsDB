"""
HawkinsDB - A memory layer with SQLite backend and error handling.

Core Features:
- Multiple memory types (Semantic, Episodic, Procedural)
- SQLite and JSON storage backends
- Robust error handling and data validation
"""

from .core import HawkinsDB, JSONStorage

__version__ = "1.0.1"
__author__ = "HawkinsDB Contributors"
__email__ = "hawkinsdb@example.com"
__license__ = "MIT"

# Core components only
__all__ = [
    'HawkinsDB',
    'JSONStorage'
]

# Optional components loaded if dependencies are available
try:
    from .enrichment import ConceptNetEnricher
    __all__.append('ConceptNetEnricher')
except ImportError:
    pass

try:
    from .llm_interface import LLMInterface
    __all__.append('LLMInterface')
except ImportError:
    pass

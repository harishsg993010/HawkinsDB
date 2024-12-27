# 🧠 HawkinsDB: Neuroscience-Inspired Memory Layer for LLM Applications

Building smarter LLM applications isn't just about better models - it's about better memory. HawkinsDB is our take on giving AI systems a more human-like way to store and recall information, inspired by how our own brains work. Based on Jeff Hawkins' Thousand Brains Theory, it helps AI models manage complex information in a way that's both powerful and intuitive.

> 📌 **Note for RAG Users**: If you're specifically looking to implement Retrieval-Augmented Generation (RAG), consider using [HawkinsRAG](https://pypi.org/project/hawkins-rag/0.1.0/) - our dedicated package built on top of HawkinsDB that simplifies RAG implementation with support for 22+ data sources. Check out the [documentation](https://github.com/harishsg993010/HawkinsRAG/tree/main/docs) and [examples](https://github.com/harishsg993010/HawkinsRAG/tree/main/examples) for more details.

> 🤖 **Note for Agent Developers**: If you're interested in building AI agents, check out [Hawkins-Agent](https://pypi.org/project/hawkins-agent/) - our specialized framework built on HawkinsDB for creating intelligent agents. Visit our [GitHub repository](https://github.com/harishsg993010/HawkinsAgent) for implementation details.

## Why HawkinsDB?

While vector databases and embeddings have revolutionized AI applications, they often miss the nuanced, multi-dimensional nature of information. Here's why we built HawkinsDB:

- **It's not just another vector database**: Instead of relying on fuzzy similarity searches, we enable precise, context-aware queries that understand the actual meaning and relationships of your data.

- **One memory system to rule them all**: We've unified different types of memory (semantic, episodic, and procedural) into a single framework. Think about a customer support AI that can simultaneously access product specs, past customer interactions, and troubleshooting guides - all working together seamlessly.

- **Inspired by the human brain**: We've based our architecture on neuroscience research, using concepts like Reference Frames and Cortical Columns to create a more robust and adaptable system.

- **You can actually understand what's happening**: Unlike black-box embeddings, our structured approach lets you see and understand how information is connected and why certain decisions are made.

## Requirements

- Python 3.10 or higher
- OpenAI API key (for LLM operations)
- SQLite or JSON storage backend

## Installation

```bash
# Basic installation
pip install hawkinsdb

# Recommended installation with all features
pip install hawkinsdb[all]

# Install specific features
pip install hawkinsdb[conceptnet]  # ConceptNet tools
```

## Quick Start

Here's a simple example showing the power of HawkinsDB:

```python
from hawkinsdb import HawkinsDB, LLMInterface

# Initialize
db = HawkinsDB()
llm = LLMInterface(db)

# Store knowledge with multiple perspectives
db.add_entity({
    "column": "Semantic",
    "name": "Coffee Cup",
    "properties": {
        "type": "Container",
        "material": "Ceramic",
        "capacity": "350ml"
    },
    "relationships": {
        "used_for": ["Drinking Coffee", "Hot Beverages"],
        "found_in": ["Kitchen", "Coffee Shop"]
    }
})

# Query using natural language
response = llm.query("What can you tell me about the coffee cup?")
print(response)
```

For more examples, check out our [examples directory](examples).

## How It Works

HawkinsDB manages information through three core concepts:

### 🧩 Reference Frames
Smart containers for information that capture what something is, its properties, relationships, and context. This enables natural handling of complex queries like "Find kitchen items related to coffee brewing."

### 🌐 Cortical Columns
Just like your brain processes information from multiple perspectives (visual, tactile, conceptual), our system stores knowledge in different "columns." This means an object isn't just stored as a single definition - it's understood from multiple angles.

### Memory Types

We support three key types of memory:

- **Semantic Memory**: For storing facts, concepts, and general knowledge
- **Episodic Memory**: For keeping track of events and experiences over time
- **Procedural Memory**: For capturing step-by-step processes and workflows

### 💾 Storage Options

- **SQLite**: Rock-solid storage for production systems
- **JSON**: Quick and easy for prototyping

### 🔗 Smart Integrations
ConceptNet integration for automatic knowledge enrichment and relationship discovery.

## Contributing

We love contributions! Here's how to help:

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## Development

```bash
# Clone and set up
git clone https://github.com/your-username/hawkinsdb.git
cd hawkinsdb
pip install -e ".[dev]"
pytest tests/
```

## 🗺️ Status and Roadmap

Currently under active development. Our focus areas:

- [ ] Enhanced multi-modal processing
- [ ] Performance optimizations for large-scale deployments
- [ ] Extended LLM provider support
- [ ] Advanced querying capabilities
- [ ] Improved documentation and examples

## License

HawkinsDB is available under the MIT License. See [LICENSE](LICENSE) for details.

---

Built by developers who think memory matters ie Harish Santhanalakshmi Ganesan along with few AI Agents

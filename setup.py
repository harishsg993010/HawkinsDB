from setuptools import setup, find_packages
import os

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from package
def get_version():
    with open(os.path.join("hawkinsdb", "__init__.py"), "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
    return "1.0.1"  # Default version if not found

setup(
    name="hawkinsdb",
    version=get_version(),
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    install_requires=[
        'requests>=2.25.1',
        'sqlalchemy>=2.0.0',
        'sqlalchemy-utils>=0.41.2',
        'filelock>=3.0.0',
        'typing-extensions>=4.0.0',
        'python-dateutil>=2.8.2',
        'setuptools>=42.0.0'
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.1.0',
            'pytest-asyncio>=0.23.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'mypy>=1.0.0',
            'ruff>=0.1.0'
        ],
        'docs': [
            'sphinx>=7.0.0',
            'sphinx-rtd-theme>=1.3.0',
            'myst-parser>=2.0.0'
        ],
        'conceptnet': [
            'networkx>=3.0.0',
            'requests-cache>=1.1.0'
        ],
        'llm': [
            'openai>=1.0.0',
            'tenacity>=8.2.0',
            'tiktoken>=0.5.0'
        ],
        'all': [
            'networkx>=3.0.0',
            'requests-cache>=1.1.0',
            'openai>=1.0.0',
            'tenacity>=8.2.0',
            'tiktoken>=0.5.0'
        ]
    },
    author="HawkinsDB Contributors",
    author_email="hawkinsdb@example.com",
    description="A memory layer with ConceptNet integration and LLM-friendly interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hawkinsdb/hawkinsdb",
    project_urls={
        "Bug Tracker": "https://github.com/hawkinsdb/hawkinsdb/issues",
        "Documentation": "https://hawkinsdb.readthedocs.io/",
        "Source Code": "https://github.com/hawkinsdb/hawkinsdb",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed"
    ],
    python_requires='>=3.8,<4',
    package_data={
        'hawkinsdb': [
            'README.md',
            'LICENSE',
            'py.typed',
            'storage/*.sql',
            'storage/*.json',
            'storage/*.db'
        ],
    },
    include_package_data=True,
)
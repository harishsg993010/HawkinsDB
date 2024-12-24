import os
import logging
from typing import List, Dict, Any
import PyPDF2
from pathlib import Path
from hawkinsdb import HawkinsDB, LLMInterface

os.environ["OPENAI_API_KEY"]=""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFHawkinsRAG:
    def __init__(self, chunk_size: int = 500):
        """Initialize the RAG system."""
        self.db = HawkinsDB(storage_type='sqlite',db_path="rag.db")
        self.llm_interface = LLMInterface(self.db,auto_enrich=True)
        self.chunk_size = chunk_size

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def chunk_text(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """Split text into chunks and prepare for database storage."""
        chunks = []
        words = text.split()
        current_chunk = []
        chunk_number = 1

        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= self.chunk_size:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "name": f"{Path(filename).stem}_chunk_{chunk_number}",
                    "column": "Semantic",
                    "properties": {
                        "content": chunk_text,
                        "source_file": filename,
                        "chunk_number": chunk_number,
                    },
                    "relationships": {
                        "part_of": [filename],
                        "next_chunk": [f"{Path(filename).stem}_chunk_{chunk_number + 1}"] if len(words) > self.chunk_size else []
                    }
                })
                current_chunk = []
                chunk_number += 1

        # Handle remaining text
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "name": f"{Path(filename).stem}_chunk_{chunk_number}",
                "column": "Semantic",
                "properties": {
                    "content": chunk_text,
                    "source_file": filename,
                    "chunk_number": chunk_number,
                },
                "relationships": {
                    "part_of": [filename]
                }
            })

        return chunks

    def ingest_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process and store PDF content in the database."""
        try:
            # Extract text from PDF
            logger.info(f"Processing PDF: {pdf_path}")
            text = self.extract_text_from_pdf(pdf_path)

            # Create document metadata
            filename = Path(pdf_path).name
            doc_metadata = {
                "name": Path(pdf_path).stem,
                "column": "Semantic",
                "properties": {
                    "file_type": "PDF",
                    "file_path": pdf_path,
                    "file_name": filename,
                },
                "relationships": {
                    "contains": []
                }
            }

            # Store document metadata
            self.db.add_entity(doc_metadata)

            # Process and store chunks
            chunks = self.chunk_text(text, filename)
            chunk_names = []
            for chunk in chunks:
                self.db.add_entity(chunk)
                chunk_names.append(chunk["name"])

            # Update document metadata with chunk references
            doc_metadata["relationships"]["contains"] = chunk_names
            self.db.add_entity(doc_metadata)

            return {
                "success": True,
                "message": f"Successfully processed {filename}",
                "chunks_created": len(chunks)
            }

        except Exception as e:
            logger.error(f"Error ingesting PDF: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

    def query(self, question: str) -> Dict[str, Any]:
        """Query the knowledge base with context from stored documents."""
        try:
            return self.llm_interface.query(question)
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "response": None
            }

def test_pdf_rag():
    """Test the PDF RAG system."""
    # Initialize the system
    rag = PDFHawkinsRAG(chunk_size=500)

    # Test with sample PDF
    pdf_path = r"C:\Users\haris\Desktop\personal\AI-Agent\Hawin\tests\document.pdf"  # Replace with actual PDF path
    if os.path.exists(pdf_path):
        # Ingest PDF
        logger.info("Ingesting PDF...")
        result = rag.ingest_pdf(pdf_path)
        logger.info(f"Ingestion result: {result}")

        if result["success"]:
            # Test queries
            test_queries = [
                "What is the main topic of the document?",
                "Summarize the key points from the document.",
                "What are the main conclusions drawn in the document?",
                "what is silha center",
                "who is Charlotte Higgins",
                "Explain the lawsuits",
                "Explain OpenAI's Involvement",
                "who is Mike Masnick"
            ]

            logger.info("\nTesting queries:")
            for query in test_queries:
                logger.info(f"\nQuery: {query}")
                response = rag.query(query)
                logger.info(f"Response: {response}")
    else:
        logger.error(f"PDF file not found: {pdf_path}")

if __name__ == "__main__":
    test_pdf_rag()
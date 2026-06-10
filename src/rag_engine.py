# Import Path to create reliable project paths
from pathlib import Path

# Import dotenv to load OPENAI_API_KEY from .env
from dotenv import load_dotenv

# Import PDF loader for reading PDF knowledge-base files
from langchain_community.document_loaders import PyPDFLoader

# Import text splitter for breaking PDFs into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import OpenAI embeddings for converting text into vectors
from langchain_openai import OpenAIEmbeddings

# Import Chroma vector database
from langchain_community.vectorstores import Chroma


# Load environment variables from .env file
load_dotenv()


# Get project root folder: AI Journey
BASE_DIR = Path(__file__).resolve().parents[1]

# Your actual PDF folder path
KNOWLEDGE_BASE_DIR = BASE_DIR / "datasets" / "knowledge_base"

# Folder where ChromaDB will be stored locally
VECTOR_DB_DIR = BASE_DIR / "vector_db"


# Load all PDF files from datasets/knowledge_base
def load_pdf_documents():
    # Store all loaded PDF pages
    documents = []

    # Find all PDFs in the knowledge_base folder
    pdf_files = list(KNOWLEDGE_BASE_DIR.glob("*.pdf"))

    # Stop if no PDFs are found
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {KNOWLEDGE_BASE_DIR}")

    # Load each PDF one by one
    for pdf_file in pdf_files:
        # Create PDF loader
        loader = PyPDFLoader(str(pdf_file))

        # Load PDF pages as LangChain documents
        pdf_documents = loader.load()

        # Add source file name to metadata for traceability
        for doc in pdf_documents:
            doc.metadata["source_file"] = pdf_file.name

        # Add loaded pages to final list
        documents.extend(pdf_documents)

    # Return all PDF page documents
    return documents


# Split PDF documents into smaller chunks for retrieval
def chunk_documents(documents, chunk_size=800, chunk_overlap=120):
    # Create chunking logic
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    # Split documents into chunks
    chunks = text_splitter.split_documents(documents)

    # Return document chunks
    return chunks


# Build and save ChromaDB vector database
def build_vector_store():
    # Load PDF documents
    documents = load_pdf_documents()

    # Split documents into chunks
    chunks = chunk_documents(documents)

    # Create OpenAI embedding model
    embeddings = OpenAIEmbeddings()

    # Create vector database from chunks
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR)
    )

    # Save vector database locally
    vector_store.persist()

    # Return vector store
    return vector_store


# Load existing ChromaDB vector database
def load_vector_store():
    # Create OpenAI embedding model
    embeddings = OpenAIEmbeddings()

    # Load saved ChromaDB folder
    vector_store = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings
    )

    # Return vector store
    return vector_store


# Retrieve relevant PDF context for a user question
def retrieve_context(question, k=4):
    # Load vector store
    vector_store = load_vector_store()

    # Search for most relevant chunks
    docs = vector_store.similarity_search(question, k=k)

    # Format retrieved chunks with source file names
    context = "\n\n".join(
        [
            f"Source: {doc.metadata.get('source_file', 'Unknown')}\n{doc.page_content}"
            for doc in docs
        ]
    )

    # Return retrieved context
    return context


# Run quick test only when this file is executed directly
if __name__ == "__main__":
    # Show configured PDF folder
    print(f"Knowledge base folder: {KNOWLEDGE_BASE_DIR}")

    # Build vector store from PDFs
    print("Building ChromaDB vector store...")
    build_vector_store()

    # Test retrieval
    question = "What actions should be taken for high overtime?"

    # Retrieve context for the test question
    context = retrieve_context(question)

    # Print retrieved context
    print("\nRetrieved Context:")
    print(context)
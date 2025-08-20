"""
PDF Similarity Search with LangChain + HuggingFace + Chroma
-----------------------------------------------------------
This script:
1. Loads and splits a PDF into text chunks.
2. Embeds chunks using HuggingFace sentence embeddings.
3. Stores them in a Chroma vector database.
4. Runs similarity search on a query and returns results.
"""

# Step 0: Imports
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Step 1: Load PDF (Data Ingestion)
loader = PyPDFLoader("Ikigai.pdf")
pages = loader.load_and_split()
print(f"Total pages loaded: {len(pages)}")


# Step 2: Split documents into smaller chunks
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,   # max characters per chunk
    chunk_overlap=200  # overlap to preserve context
)
splits = recursive_splitter.split_documents(pages)
print(f"Total text chunks created: {len(splits)}")


# Step 3: Create embeddings (HuggingFace sentence transformer)
os.environ["HUGGINGFACE_TOKEN"] = os.getenv("HUGGINGFACE_TOKEN")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Example: Embed a query directly
query = "Wabi sabi"
query_vector = embeddings.embed_query(query)
print(f"Query embedding created (length {len(query_vector)})")


# Step 4: Store document embeddings in Chroma
vector_store = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_store"  # local storage
)
print("Chroma vector store created and persisted.")


# Step 5: Run similarity search
# Reload vector store (simulates retrieval from disk later)
chroma_store = Chroma(
    persist_directory="./chroma_store",
    embedding_function=embeddings
)

# Perform search
results = chroma_store.similarity_search(query, k=5)

# Display results
print("\nTop 5 Similar Results for query:", query)
for i, doc in enumerate(results, 1):
    print(f"\nResult {i}:\n{'-'*40}\n{doc.page_content[:500]}...")

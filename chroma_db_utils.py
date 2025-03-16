import chromadb
from chromadb.config import Settings
from typing import List
import os
import datetime
from mistralai.client import MistralClient

# Hardcoded Mistral API key (NOT RECOMMENDED for production)
MISTRAL_API_KEY = "9x8duC1VJ7n5uEwdV8nG6bmFEIqCftKn"

# Initialize Mistral client
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

class MistralEmbeddingFunction:
    """
    Custom embedding function using Mistral AI API.
    """
    def __call__(self, input: List[str]) -> List[List[float]]:
        embeddings = []
        for text in input:
            response = mistral_client.embeddings.create(
                model="mistral-embed",
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return embeddings

# Initialize the embedding function
embedding_function = MistralEmbeddingFunction()

def create_chroma_db(documents: List[str]):
    """
    Creates a persistent Chroma database using the provided documents.
    """
    # Create a persistent directory for ChromaDB
    persist_directory = "chroma_db"
    os.makedirs(persist_directory, exist_ok=True)
    
    # Initialize the client with persistence
    chroma_client = chromadb.PersistentClient(
        path=persist_directory,
    )
    
    # Get or create collection
    try:
        # Try to get existing collection
        db = chroma_client.get_collection(
            name="document_collection",
            embedding_function=embedding_function
        )
        # Clear existing documents
        db.delete(db.get()["ids"])
    except:
        # Create new collection if it doesn't exist
        db = chroma_client.create_collection(
            name="document_collection",
            embedding_function=embedding_function
        )
    
    # Add documents in batches to avoid memory issues
    batch_size = 20
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        db.add(
            documents=batch,
            ids=[f"doc_{j}" for j in range(i, i + len(batch))]
        )
    
    return db

def get_relevant_passage(query: str, db, n_results: int = 5) -> List[str]:
    start_time = datetime.datetime.now()
    print(f"{start_time}: Starting ChromaDB query for question: {query[:50]}...")  # Log query start

    try:
        results = db.query(
            query_texts=[query],
            n_results=min(n_results, db.count()),
            include=['documents', 'distances']
        )
        end_time = datetime.datetime.now()
        print(f"{end_time}: ChromaDB query finished. Time taken: {end_time - start_time}")  # Log the time taken

        # Ensure results exist and contain at least one document
        if not results or 'documents' not in results or not results['documents'] or not results['documents'][0]:
            print("No relevant passages found.")
            return []

        # Extract valid results
        documents = results['documents'][0]  # List of retrieved documents
        distances = results['distances'][0]  # Corresponding similarity scores

        # Debugging output
        print(f"Number of relevant passages retrieved: {len(documents)}")
        for i, (doc, distance) in enumerate(zip(documents, distances)):
            similarity = 1 - distance  # Convert distance to similarity score
            print(f"Passage {i+1} (Similarity: {similarity:.4f}): {doc[:100]}...")

        return documents  # Return only valid results
    except Exception as e:
        print(f"Error in get_relevant_passage: {str(e)}")
        return []
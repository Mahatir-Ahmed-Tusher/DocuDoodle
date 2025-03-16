import os
from chromadb.api.types import Documents, Embeddings
from chromadb import EmbeddingFunction
from mistralai.client import MistralClient  # Import Mistral client


MISTRAL_API_KEY = "Your_own_api_key"

# Initialize Mistral client
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

class MistralEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function using Mistral AI API.
    """
    def __call__(self, input: Documents) -> Embeddings:
        if not MISTRAL_API_KEY:
            raise ValueError("Mistral API Key not provided. Please set MISTRAL_API_KEY as an environment variable.")
        
        embeddings = []
        for text in input:
            # Generate embeddings using Mistral's API
            response = mistral_client.embeddings.create(
                model="mistral-embed",  # Mistral's embedding model
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return embeddings

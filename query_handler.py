import os
import time
import datetime
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from chroma_db_utils import get_relevant_passage

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 1  # Initial delay in seconds
MODEL_NAME = "mistral-large-latest"  # Mistral's latest model
REQUESTS_PER_MINUTE = 10  # Mistral's rate limit (adjust based on your tier)
REQUEST_INTERVAL = 60 / REQUESTS_PER_MINUTE

# Hardcoded Mistral API Key (NOT RECOMMENDED for production)
MISTRAL_API_KEY = "Paste_your_own_api_key"

# Initialize Mistral client
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

def make_rag_prompt(query: str, relevant_passage: str) -> list[ChatMessage]:
    """
    Creates a chat prompt for the Mistral RAG model.
    """
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    
    return [
        ChatMessage(
            role="system",
            content="You are a helpful bot that answers questions using the provided context. "
                    "If the context is irrelevant, say 'I cannot answer this question based on the provided information.'"
        ),
        ChatMessage(
            role="user",
            content=f"QUESTION: {query}\n\nREFERENCE TEXT: {escaped}\n\nANSWER:"
        )
    ]

def generate_answer(prompt: list[ChatMessage]) -> str:
    """
    Calls the Mistral API with retries and rate limiting.
    """
    for attempt in range(MAX_RETRIES):
        start_time = datetime.datetime.now()
        print(f"{start_time}: Making Mistral API request (attempt {attempt + 1}/{MAX_RETRIES})...")
        
        try:
            response = mistral_client.chat(
                model=MODEL_NAME,
                messages=prompt,
                temperature=0.3
            )
            end_time = datetime.datetime.now()
            print(f"{end_time}: Mistral API request successful. Time taken: {end_time - start_time}")
            
            return response.choices[0].message.content
        
        except Exception as e:
            if "rate limit" in str(e).lower() or attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                print(f"API error: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise

    raise Exception("Max retries exceeded for Mistral API request.")

def handle_query(query: str, db, n_results: int = 5) -> str:
    """
    Handles a user query using Mistral AI.
    """
    relevant_passages = get_relevant_passage(query, db, n_results)
    relevant_passage_str = " ".join(relevant_passages)
    chat_prompt = make_rag_prompt(query, relevant_passage_str)
    return generate_answer(chat_prompt)

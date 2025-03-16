import streamlit as st
import os
from typing import List
import time
from pdf_utils import extract_text_from_file, split_text
from chroma_db_utils import create_chroma_db
from query_handler import handle_query

# Hardcoded API key (NOT RECOMMENDED for production)
MISTRAL_API_KEY = "Paste_your_own_api_key"

def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'db' not in st.session_state:
        st.session_state.db = None
    if 'chunks' not in st.session_state:
        st.session_state.chunks = []

def process_uploaded_file(uploaded_file) -> List[str]:
    """Process the uploaded file and return text chunks."""
    # Create a temporary file to store the uploaded content
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        # Extract text from the file
        extracted_text = extract_text_from_file(uploaded_file.name)
        if extracted_text:
            # Split text into chunks
            chunks = split_text(extracted_text)
            return chunks
        else:
            st.error("No text could be extracted from the file.")
            return []
    finally:
        # Clean up temporary file
        if os.path.exists(uploaded_file.name):
            os.remove(uploaded_file.name)

def main():
    st.title("📚 Document Q&A System")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("Document Upload")
        uploaded_file = st.file_uploader(
            "Upload your document",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_file:
            with st.spinner("Processing document..."):
                # Process the uploaded file
                chunks = process_uploaded_file(uploaded_file)
                
                if chunks:
                    # Create/update the database
                    st.session_state.chunks = chunks
                    st.session_state.db = create_chroma_db(chunks)
                    st.success(f"Document processed! Created {len(chunks)} chunks.")
                    
                    # Add system message to chat history
                    if not st.session_state.messages:
                        st.session_state.messages.append({
                            "role": "system",
                            "content": "I've processed your document. You can now ask questions about it!"
                        })
    
    # Main chat interface
    st.header("💬 Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your document"):
        # Only process if we have a database
        if st.session_state.db is None:
            st.error("Please upload a document first!")
            return
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = handle_query(prompt, st.session_state.db)
                    st.write(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

if __name__ == "__main__":
    main()

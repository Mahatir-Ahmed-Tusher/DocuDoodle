import streamlit as st
import os
from typing import List
import time
from pdf_utils import extimport streamlit as st
import os
from typing import List
import time
from pdf_utils import extract_text_from_file, split_text
from chroma_db_utils import create_chroma_db
from query_handler import handle_query
import base64

# Hardcoded API key (NOT RECOMMENDED for production)
MISTRAL_API_KEY = "9x8duC1VJ7n5uEwdV8nG6bmFEIqCftKn"

# Set page configuration
st.set_page_config(
    page_title="DocuDoodle",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define custom CSS
def local_css():
    st.markdown("""
    <style>
    .main {
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 20px;
    }
    .stApp {
        background-image: linear-gradient(135deg, #6e8efb, #a777e3);
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 10px;
        margin: 5px 0;
        backdrop-filter: blur(5px);
    }
    .chat-container {
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(5px);
    }
    .sidebar .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 600;
    }
    .upload-box {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        backdrop-filter: blur(5px);
        border: 1px dashed #a777e3;
    }
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        text-align: center;
        padding: 10px;
        backdrop-filter: blur(5px);
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'db' not in st.session_state:
        st.session_state.db = None
    if 'chunks' not in st.session_state:
        st.session_state.chunks = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"

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

def add_logo():
    """Add the DocuDoodle logo to the sidebar."""
    try:
        # If the logo exists
        if os.path.exists("DocuDoodle.png"):
            st.sidebar.image("DocuDoodle.png", width=200)
        else:
            # Fallback to text if image doesn't exist
            st.sidebar.title("DocuDoodle")
    except Exception:
        st.sidebar.title("DocuDoodle")

def home_page():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<h1 style='color: white; text-shadow: 2px 2px 4px #000000;'>DocuDoodle 📚</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #f0f0f0;'>Converse with your documents, unleash their knowledge</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: rgba(255, 255, 255, 0.2); border-radius: 10px; padding: 15px; backdrop-filter: blur(5px);'>
        <p style='color: #ffffff; font-size: 18px;'>
        Upload your books or documents in the sidebar (PDF, DOCX, or TXT format) and start a conversation with your content. 
        DocuDoodle analyzes your documents and provides intelligent responses based on the information contained within.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Placeholder for a decorative illustration
        st.markdown("""
        <div style='background-color: rgba(255, 255, 255, 0.3); border-radius: 50%; height: 200px; width: 200px; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 64px; backdrop-filter: blur(5px);'>
        📚
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat interface
    st.markdown("<div class='chat-container'><h2>💬 Chat with your Document</h2>", unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your document..."):
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
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <a href='https://github.com/Mahatir-Ahmed-Tusher/DocuDoodle' target='_blank' style='color: #a777e3; text-decoration: none;'>
            Source Code on GitHub
        </a> | Made with ❤️ using Streamlit
    </div>
    """, unsafe_allow_html=True)

def how_it_works_page():
    st.markdown("<h1 style='color: white; text-shadow: 2px 2px 4px #000000;'>How DocuDoodle Works</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; backdrop-filter: blur(5px);'>
    <h3 style='color: #ffffff;'>The Magic Behind DocuDoodle</h3>
    <p style='color: #f0f0f0;'>
    DocuDoodle uses advanced natural language processing to analyze your documents and provide intelligent responses:
    </p>
    <ol style='color: #f0f0f0;'>
        <li><strong>Document Upload:</strong> Upload your PDF, DOCX, or TXT file through the sidebar.</li>
        <li><strong>Text Extraction:</strong> Our system extracts all text content from your document.</li>
        <li><strong>Chunking:</strong> The text is divided into manageable chunks for efficient processing.</li>
        <li><strong>Embedding:</strong> Each chunk is converted into a numerical representation that captures its semantic meaning.</li>
        <li><strong>Vector Database:</strong> These embeddings are stored in a vector database for quick retrieval.</li>
        <li><strong>Query Processing:</strong> When you ask a question, DocuDoodle finds the most relevant chunks from your document.</li>
        <li><strong>Response Generation:</strong> An AI model uses these relevant chunks to generate a helpful response.</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; margin-top: 20px; backdrop-filter: blur(5px);'>
    <h3 style='color: #ffffff;'>Troubleshooting</h3>
    <p style='color: #f0f0f0;'>
    If you're not getting satisfactory answers from DocuDoodle, try these tips:
    </p>
    <ul style='color: #f0f0f0;'>
        <li><strong>Be Specific:</strong> Ask clear, focused questions related to the content of your document.</li>
        <li><strong>Rephrase:</strong> Try asking the same question in different ways.</li>
        <li><strong>Check Document Quality:</strong> Make sure your document is clearly formatted and readable.</li>
        <li><strong>Document Scope:</strong> Ensure your question is actually covered in the uploaded document.</li>
        <li><strong>Try Smaller Documents:</strong> If using a large book, try uploading specific chapters instead of the entire book.</li>
        <li><strong>Clear and Start Again:</strong> Try refreshing the page and uploading the document again.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

def acknowledgements_page():
    st.markdown("<h1 style='color: white; text-shadow: 2px 2px 4px #000000;'>Acknowledgements</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; backdrop-filter: blur(5px);'>
    <h3 style='color: #ffffff;'>Special Thanks</h3>
    <p style='color: #f0f0f0; font-size: 18px;'>
    A heartfelt thank you to <strong>Sharaf Wasima</strong> for the inspiration behind DocuDoodle. Our conversations sparked the idea for this project, demonstrating how collaboration and sharing ideas can lead to innovative solutions.
    </p>
    <p style='color: #f0f0f0; font-size: 18px;'>
    This project wouldn't have been possible without her insights and encouragement to explore the fascinating intersection of document analysis and conversational AI.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 20px; margin-top: 20px; backdrop-filter: blur(5px);'>
    <h3 style='color: #ffffff;'>Technologies Used</h3>
    <ul style='color: #f0f0f0;'>
        <li>Streamlit - For the interactive web interface</li>
        <li>ChromaDB - For vector storage and semantic search</li>
        <li>Mistral AI - For natural language understanding</li>
        <li>PyPDF2/DocX - For document parsing</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Apply custom CSS
    local_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar configuration
    add_logo()
    st.sidebar.markdown("<h3 style='color: white; margin-top: -15px;'>Document Q&A System</h3>", unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.markdown("### 📍 Navigation")
    pages = {
        "Home": home_page,
        "How It Works": how_it_works_page,
        "Acknowledgements": acknowledgements_page
    }
    
    selected_page = st.sidebar.radio("", list(pages.keys()), index=list(pages.keys()).index(st.session_state.current_page))
    st.session_state.current_page = selected_page
    
    # Document upload section
    st.sidebar.markdown("<div class='upload-box'>", unsafe_allow_html=True)
    st.sidebar.markdown("### 📤 Upload Your Document")
    uploaded_file = st.sidebar.file_uploader(
        "Supported formats: PDF, DOCX, TXT",
        type=['pdf', 'docx', 'txt'],
        help="Upload your book or document to start chatting with it"
    )
    
    processing_placeholder = st.sidebar.empty()
    
    if uploaded_file:
        processing_placeholder.info("Processing document... Please wait.")
        # Process the uploaded file
        chunks = process_uploaded_file(uploaded_file)
        
        if chunks:
            # Create/update the database
            st.session_state.chunks = chunks
            st.session_state.db = create_chroma_db(chunks)
            processing_placeholder.success(f"✅ Document processed! Created {len(chunks)} chunks.")
            
            # Add system message to chat history
            if not st.session_state.messages:
                st.session_state.messages.append({
                    "role": "system",
                    "content": "I've processed your document. You can now ask questions about it!"
                })
        else:
            processing_placeholder.error("Failed to process document.")
    
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    # Clear chat button
    if st.session_state.messages:
        if st.sidebar.button("🧹 Clear Chat History"):
            st.session_state.messages = []
            st.experimental_rerun()
    
    # Display the selected page
    pages[selected_page]()

if __name__ == "__main__":
    main()ract_text_from_file, split_text
from chroma_db_utils import create_chroma_db
from query_handler import handle_query

# Hardcoded API key (NOT RECOMMENDED for production)
MISTRAL_API_KEY = "9x8duC1VJ7n5uEwdV8nG6bmFEIqCftKn"

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
# **DocuDoodle**  
**A Document Q&A System**  

DocuDoodle is a **Document Q&A System** that allows users to upload documents (PDF, DOCX, TXT) and interact with them through a chat interface. Powered by **Mistral AI** for embeddings and question answering, and **ChromaDB** for document storage, DocuDoodle makes it easy to extract insights from your documents.  

👉 **Try it out here:** [DocuDoodle on Hugging Face Spaces](https://huggingface.co/spaces/MahatirTusher/DocuDoodle)  

---

## **How It Works**  

DocuDoodle follows a **Retrieval-Augmented Generation (RAG)** approach to answer user questions based on the uploaded document. Here's a step-by-step breakdown of how it works:  

---

### **1. Document Upload and Text Extraction**  
- **File Upload**:  
  - Users upload a document (PDF, DOCX, or TXT) through the Streamlit interface.  
  - The file is temporarily saved for processing.  

- **Text Extraction**:  
  - For **PDFs**, the system uses **PyMuPDF (fitz)** to extract text.  
  - For **DOCX** files, it uses the `python-docx` library.  
  - For **TXT** files, it reads the file directly with UTF-8 encoding (falling back to Latin-1 if needed).  

- **Text Cleaning**:  
  - The extracted text is cleaned to remove extra whitespace, non-printable characters, and multiple newlines.  

---

### **2. Text Splitting**  
- The text is split into smaller chunks using **LangChain's `RecursiveCharacterTextSplitter`**.  
- **Chunk Size**: 1000 characters.  
- **Overlap**: 200 characters (to ensure context is preserved).  

---

### **3. Embedding Generation**  
- The system uses **Mistral AI** to generate embeddings for each text chunk.  
- The `MistralEmbeddingFunction` class handles the embedding generation by calling the Mistral API.  

---

### **4. Document Storage in ChromaDB**  
- A persistent ChromaDB collection is created to store the embeddings.  
- The collection is named `document_collection`.  
- If the collection already exists, it is cleared before adding new documents.  
- Text chunks and their embeddings are added to ChromaDB in batches to avoid memory issues.  

---

### **5. Query Handling and Answer Generation**  
- **Query Processing**:  
  - When a user submits a query, the system retrieves the most relevant passages from ChromaDB.  
  - The `get_relevant_passage` function queries ChromaDB using the query's embedding and returns the top `n_results` passages.  

- **RAG Prompt Creation**:  
  - The system creates a **Retrieval-Augmented Generation (RAG)** prompt using the query and the retrieved passages.  
  - The prompt includes:  
    - A system message instructing the model to answer based on the provided context.  
    - The user's query.  
    - The retrieved passages as reference text.  

- **Answer Generation**:  
  - The system sends the RAG prompt to Mistral AI using the `mistral_client.chat.complete` method.  
  - The model generates an answer based on the provided context.  
  - If the context is irrelevant, the model responds with: "I cannot answer this question based on the provided information."  

---

### **6. User Interface**  
- **Streamlit App**:  
  - The app has two main sections:  
    1. **Document Upload**:  
       - Users can upload files in the sidebar.  
       - The system processes the file and displays a success message.  
    2. **Chat Interface**:  
       - Users can ask questions about the uploaded document.  
       - The system displays the conversation history, including user queries and model responses.  

- **Session State**:  
  - The app uses Streamlit's session state to store:  
    - Uploaded document chunks.  
    - ChromaDB collection.  
    - Chat history.  

---

## **File Structure**  

Here’s the structure of the project:  

```
DocuDoodle/
├── app.py                       # Main Streamlit app
├── chroma_db_utils.py           # ChromaDB operations (embedding storage, querying)
├── query_handler.py             # Handles user queries and generates answers
├── pdf_utils.py                 # Text extraction from PDFs, DOCX, and TXT files
├── requirements.txt             # List of dependencies
├── README.md                    # Project documentation
└── .env                         # Environment variables (e.g., API keys)
```

---

### **File Descriptions**  

1. **`app.py`**:  
   - The main Streamlit app.  
   - Handles file uploads, chat interface, and session state.  

2. **`chroma_db_utils.py`**:  
   - Manages ChromaDB operations (e.g., creating the database, querying for relevant passages).  

3. **`query_handler.py`**:  
   - Handles user queries, generates RAG prompts, and interacts with Mistral AI.  

4. **`pdf_utils.py`**:  
   - Contains functions for extracting text from PDFs, DOCX files, and TXT files.  

5. **`requirements.txt`**:  
   - Lists all dependencies for the project.  

6. **`.env`**:  
   - Stores environment variables (e.g., Mistral API key).  

---

## **Technologies Used**  
- **Mistral AI**: For generating embeddings and question answering.  
- **ChromaDB**: For storing and retrieving document embeddings.  
- **Streamlit**: For the web interface.  
- **PyMuPDF (fitz)**: For extracting text from PDFs.  
- **python-docx**: For extracting text from DOCX files.  
- **LangChain**: For splitting text into chunks.  

---

## **Deployment**  
DocuDoodle is deployed on **Hugging Face Spaces**:  
👉 [DocuDoodle on Hugging Face Spaces](https://huggingface.co/spaces/MahatirTusher/DocuDoodle)  

---

## **Future Improvements**  
1. **Support for More File Types**:  
   - Add support for images (using OCR) and spreadsheets (using `pandas`).  

2. **Persistent Storage**:  
   - Use a hosted vector database (e.g., Pinecone or Weaviate) for persistent storage of embeddings.  

3. **Enhanced UI**:  
   - Add features like file preview, document summarization, and multi-document support.  

4. **Security**:  
   - Replace hardcoded API keys with environment variables or a secrets manager.  

5. **Performance Optimization**:  
   - Optimize text extraction and embedding generation for faster processing.  

---

## **Contact**  
For questions or feedback, feel free to reach out:  
- **Mahatir Ahmed Tusher**  
- GitHub: [Mahatir-Ahmed-Tusher](https://github.com/Mahatir-Ahmed-Tusher)  
- Email: [mahatir.tusher@gmail.com](mailto:mahatir.tusher@gmail.com)  

---

**Happy Document Exploring with DocuDoodle!** 🚀

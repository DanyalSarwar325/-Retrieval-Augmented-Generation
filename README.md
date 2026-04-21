# Traditional RAG (Retrieval-Augmented Generation)

A Python-based Retrieval-Augmented Generation system that ingests PDF documents, generates embeddings, and stores them in a vector database for semantic search and document retrieval.

## Overview

This project implements a complete RAG pipeline that:
- **Ingests PDFs**: Loads and processes PDF files from a directory
- **Chunks Documents**: Splits large documents into smaller, overlapping chunks for better semantic understanding
- **Generates Embeddings**: Creates vector embeddings using the Sentence Transformer model
- **Stores in Vector DB**: Persists embeddings and documents in ChromaDB
- **Retrieves Documents**: Searches and retrieves relevant documents based on semantic similarity

## Project Structure

```
traditionalRag/
├── notebook/
│   ├── rag.ipynb              # Main notebook implementing the RAG pipeline
│   └── document.ipynb         # Additional documentation notebook
├── data/
│   ├── pdf/                   # Input PDF files for processing
│   ├── text_files/            # Text files directory
│   └── chroma_db/             # Persistent ChromaDB storage
├── main.py                    # Main entry point
├── pyproject.toml             # Project configuration and dependencies
├── requirements.txt           # Python package requirements
└── README.md                  # This file
```

## Installation

### Prerequisites
- Python 3.11 or higher
- pip or poetry package manager

### Setup Instructions

1. **Clone or download the repository**
   ```bash
   cd traditionalRag
   ```

2. **Install dependencies**
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using poetry:
   ```bash
   poetry install
   ```

## Dependencies

The project uses the following key libraries:

| Library | Purpose |
|---------|---------|
| `langchain` | LLM framework and orchestration |
| `langchain-community` | Additional document loaders and tools |
| `langchain-core` | Core abstractions and interfaces |
| `pypdf` | PDF parsing and text extraction |
| `pymupdf` | Alternative PDF library (MuPDF) |
| `sentence-transformers` | Generating semantic embeddings |
| `chromadb` | Vector database for storing embeddings |
| `faiss-cpu` | CPU-based similarity search |
| `ipykernel` | Jupyter kernel support |

## Pipeline Components

### 1. Data Ingestion (`process_all_pdfs`)

Recursively loads all PDF files from the `data/pdf` directory.

**Features:**
- Finds all PDF files recursively in the specified directory
- Extracts text content from each PDF
- Adds metadata (filename, file type) to each document
- Handles errors gracefully with detailed logging

**Usage:**
```python
all_pdf_documents = process_all_pdfs("../data/pdf")
```

### 2. Document Chunking (`split_documents`)

Splits documents into smaller, overlapping chunks for improved semantic search performance.

**Configuration:**
- `chunk_size`: 1000 characters per chunk (default)
- `chunk_overlap`: 200 characters overlap between chunks
- Separators: `["\n\n", "\n", " ", ""]` (hierarchical split strategy)

**Purpose:**
- Large documents are broken down for better semantic matching
- Overlapping ensures context preservation across chunk boundaries
- Improves retrieval precision

**Usage:**
```python
chunked_documents = split_documents(all_pdf_documents, chunk_size=1000, chunk_overlap=200)
```

### 3. EmbeddingManager Class

Handles generation of semantic embeddings using pre-trained Sentence Transformer models.

**Key Methods:**
- `__init__(model_name)`: Initialize with a specific Hugging Face model
- `load_model()`: Load the sentence transformer model
- `generateEmbeddings(texts)`: Generate embeddings for a list of texts

**Default Model:** `all-MiniLM-L6-v2`
- Lightweight model optimized for semantic search
- 384-dimensional embeddings
- Fast inference on CPU

**Usage:**
```python
embedding_manager = EmbeddingManager(model_name="all-MiniLM-L6-v2")
embeddings = embedding_manager.generateEmbeddings(texts)
```

### 4. VectorStore Class

Manages persistent storage of document embeddings in ChromaDB.

**Key Features:**
- **Persistent Storage**: Data persists in `data/chroma_db/`
- **Collection Management**: Stores embeddings in named collections
- **Metadata Support**: Preserves document metadata alongside embeddings

**Key Methods:**
- `__init__(collection_name, persistent_directory)`: Initialize vector store
- `_connect_to_db()`: Connect to ChromaDB and create/get collection
- `add_documents(documents, embeddings)`: Store documents and their embeddings

**Storage Structure:**
```
data/chroma_db/
├── chroma.sqlite3           # Main database file
└── [collection_id]/         # Collection directory
    └── [embedding_files]    # Embedding data
```

**Usage:**
```python
store = VectorStore(collection_name="pdf_chunks")
store.add_documents(chunked_documents, embeddings)
```

### 5. RAGRetriever Class

Retrieves relevant documents based on semantic similarity to user queries.

**Key Methods:**
- `__init__(vector_store, embedding_manager)`: Initialize retriever
- `retrieve(query, top_k, score_threshold)`: Retrieve relevant documents

**Parameters:**
- `query`: The search query string
- `top_k`: Number of top results to return (default: 5)
- `score_threshold`: Minimum similarity score threshold (default: 0.0)

**Returns:**
List of dictionaries containing:
- `id`: Document identifier
- `content`: Document text
- `metadata`: Document metadata
- `similarity_score`: Similarity score (0-1)
- `distance`: Raw distance metric
- `rank`: Result ranking

**Similarity Scoring:**
- Converts ChromaDB cosine distance to similarity score
- Formula: `similarity_score = 1 - distance`
- Score range: 0 (no similarity) to 1 (perfect match)

**Usage:**
```python
rag_retriever = RAGRetriever(store, embedding_manager)
results = rag_retriever.retrieve(query="your search query", top_k=5, score_threshold=0.5)
```

## Usage Workflow

### Complete RAG Pipeline Example

```python
# 1. Load PDFs
all_pdf_documents = process_all_pdfs("../data/pdf")

# 2. Split into chunks
chunked_documents = split_documents(all_pdf_documents)

# 3. Initialize embedding manager
embedding_manager = EmbeddingManager()

# 4. Generate embeddings
texts = [doc.page_content for doc in chunked_documents]
embeddings = embedding_manager.generateEmbeddings(texts)

# 5. Initialize vector store and add documents
store = VectorStore()
store.add_documents(chunked_documents, embeddings)

# 6. Initialize retriever
rag_retriever = RAGRetriever(store, embedding_manager)

# 7. Retrieve documents
query = "What is semantic search?"
results = rag_retriever.retrieve(query, top_k=5, score_threshold=0.5)

# 8. Process results
for result in results:
    print(f"Document {result['rank']}: {result['content'][:100]}...")
    print(f"Similarity Score: {result['similarity_score']:.2f}")
```

## Notebook Organization

The main notebook (`rag.ipynb`) is organized into sections:

1. **Data Ingestion To Vector DB Pipeline**
   - PDF loading and processing
   - Document chunking

2. **Vector Database Setup**
   - Embedding manager initialization
   - ChromaDB vector store creation
   - Document storage

3. **RAG Retriever**
   - Retriever class implementation
   - Query-based document retrieval

## Configuration Parameters

### Chunk Size Settings
- **chunk_size**: 1000 (characters per chunk)
- **chunk_overlap**: 200 (overlap between chunks)
- **Separators**: `["\n\n", "\n", " ", ""]` (hierarchical splitting)

### Embedding Configuration
- **Model**: `all-MiniLM-L6-v2` (384-dimensional)
- **Framework**: Sentence Transformers

### Retrieval Configuration
- **Default top_k**: 5 (return top 5 results)
- **Default score_threshold**: 0.0 (no minimum threshold)
- **Similarity Metric**: Cosine distance → similarity score

### Vector Store Configuration
- **Collection Name**: `pdf_chunks`
- **Persistent Directory**: `../data/chroma_db/`

## Data Format

### Document Structure (LangChain)
Each document is a LangChain Document object containing:
- `page_content`: The actual text content
- `metadata`: Dictionary with:
  - `source_file`: Original PDF filename
  - `file_type`: Document type (e.g., 'pdf')
  - `doc_index`: Index in the document list
  - `content_length`: Length of content in characters

### Embedding Format
- **Type**: NumPy ndarray
- **Shape**: (number_of_chunks, 384)
- **Data Type**: Float32 (default)

### Retrieval Results Format
```python
{
    'id': 'doc_abc123_0',
    'content': 'Document text content...',
    'metadata': {
        'source_file': 'document.pdf',
        'file_type': 'pdf'
    },
    'similarity_score': 0.85,
    'distance': 0.15,
    'rank': 1
}
```

## Error Handling

The system includes error handling for:
- **PDF Loading**: Gracefully skips files that fail to load
- **Model Loading**: Raises exception if embedding model cannot be loaded
- **Database Connection**: Creates directory if it doesn't exist
- **Query Retrieval**: Returns empty list if no results found

## Performance Considerations

### Optimization Tips
1. **Chunk Size**: Adjust based on your document length
   - Smaller chunks: Better precision but more storage
   - Larger chunks: Better context but potentially lower relevance

2. **Overlap**: Increase for better context preservation
   - Default 20% overlap is balanced

3. **Model Selection**: Choose based on performance/accuracy tradeoff
   - `all-MiniLM-L6-v2`: Fast, lightweight
   - `all-mpnet-base-v2`: More accurate, slower
   - `all-roberta-large-v1`: Even more accurate, slowest

4. **Top K Results**: Adjust based on use case
   - Lower values: Faster, more precise
   - Higher values: Better coverage, may include less relevant docs

## Troubleshooting

### Issue: PDF files not found
**Solution**: Ensure PDF files are in `data/pdf/` directory relative to the notebook

### Issue: Model download fails
**Solution**: Check internet connection and Hugging Face accessibility

### Issue: Out of memory
**Solution**: Reduce chunk size or batch process documents

### Issue: Low retrieval quality
**Solution**: 
- Increase chunk_overlap
- Lower score_threshold
- Use a larger embedding model
- Review document chunking strategy

## Future Enhancements

Potential improvements for this project:
- [ ] Integration with LLM for generative responses
- [ ] Web interface for document search
- [ ] Batch indexing for large document sets
- [ ] Advanced filtering and metadata search
- [ ] Hybrid search (keyword + semantic)
- [ ] Query expansion and reranking
- [ ] Document update/deletion support

## Contributing

To extend this project:

1. Add new data processing functions in the Data Ingestion section
2. Implement custom embedding models in EmbeddingManager
3. Extend RAGRetriever with filtering logic
4. Add new vector store backends

## License

Add your license information here

## References

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [RAG Concepts](https://arxiv.org/abs/2005.11401)

## Contact

For questions or issues, please refer to the project documentation or create an issue in the repository.

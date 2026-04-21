from src.data_loader import load_all_documents
from src.embeddings import EmbeddingPipeline
from src.vector_store import FaissVectorStore
from src.search import RAGSearch

# Example usage
if __name__ == "__main__":
    
    #docs = load_all_documents("data")
    store= FaissVectorStore("faiss_store")
    #store.build_from_documents(docs)
    store.load()
    rag_search = RAGSearch()
    query = "What are servers and its types?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Search and Summarize Result:", summary)

    # chunks = EmbeddingPipeline().chunk_documents(docs)
    # embeddings = EmbeddingPipeline().embed_chunks(chunks)
    # st

   
    # store = FaissVectorStore("faiss_store")
    #store.build_from_documents(docs)
    # store.load()
    #print(store.query("What is attention mechanism?", top_k=3))
    # rag_search = RAGSearch()
    # query = "What is attention mechanism?"
    # summary = rag_search.search_and_summarize(query, top_k=3)
    # print("Summary:", summary)
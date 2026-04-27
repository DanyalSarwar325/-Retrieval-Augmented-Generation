import os
import time
from typing import Any, Dict, List, Tuple

from langchain_groq import ChatGroq

from src.data_loader import load_all_documents
from src.vector_store import FaissVectorStore


class RAGService:
    def __init__(self, settings):
        self.settings = settings
        self.vectorstore: FaissVectorStore | None = None
        self.llm = None
        self._is_initialized = False

    def initialize(self) -> None:
        if self._is_initialized:
            return

        self.vectorstore = FaissVectorStore(
            persist_dir=self.settings.persist_dir,
            embedding_model=self.settings.embedding_model,
        )

        faiss_path = os.path.join(self.settings.persist_dir, "faiss.index")
        meta_path = os.path.join(self.settings.persist_dir, "metadata.pkl")

        if os.path.exists(faiss_path) and os.path.exists(meta_path):
            self.vectorstore.load()
        else:
            docs = load_all_documents(self.settings.data_dir)
            self.vectorstore.build_from_documents(docs)

        if self.settings.groq_api_key:
            self.llm = ChatGroq(
                groq_api_key=self.settings.groq_api_key,
                model_name=self.settings.llm_model,
            )

        self._is_initialized = True

    def readiness(self) -> Tuple[bool, str]:
        if not self._is_initialized:
            return False, "service_not_initialized"
        if self.vectorstore is None or self.vectorstore.index is None:
            return False, "vector_store_not_loaded"
        return True, "ready"

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        self.initialize()
        assert self.vectorstore is not None

        raw_results = self.vectorstore.query(query, top_k=top_k)
        results: List[Dict[str, Any]] = []

        for item in raw_results:
            metadata = item.get("metadata") or {}
            distance = float(item.get("distance", 0.0))
            # Normalize L2 distance into a bounded score for API consumers.
            score = 1.0 / (1.0 + max(distance, 0.0))
            results.append(
                {
                    "index": int(item.get("index", -1)),
                    "text": metadata.get("text", ""),
                    "distance": distance,
                    "score": score,
                    "metadata": metadata,
                }
            )

        return results

    def query_and_summarize(self, query: str, top_k: int = 5, include_sources: bool = True) -> Dict[str, Any]:
        self.initialize()

        start = time.perf_counter()
        sources = self.retrieve(query=query, top_k=top_k)
        context = "\n\n".join([src["text"] for src in sources if src.get("text")])

        if not context:
            answer = "No relevant documents found."
        elif self.llm is None:
            answer = "LLM is not configured. Set GROQ_API_KEY in your environment to enable summarization."
        else:
            prompt = (
                f"Summarize the following context for the query: '{query}'\\n\\n"
                f"Context:\\n{context}\\n\\nSummary:"
            )
            response = self.llm.invoke(prompt)
            answer = response.content

        latency_ms = int((time.perf_counter() - start) * 1000)

        return {
            "answer": answer,
            "sources": sources if include_sources else [],
            "top_k": top_k,
            "model": self.settings.llm_model,
            "latency_ms": latency_ms,
        }

    def rebuild_index(self, data_dir: str | None = None) -> Dict[str, Any]:
        self.initialize()
        assert self.vectorstore is not None

        target_data_dir = data_dir or self.settings.data_dir
        start = time.perf_counter()

        docs = load_all_documents(target_data_dir)
        self.vectorstore.build_from_documents(docs)
        self.vectorstore.load()

        duration_ms = int((time.perf_counter() - start) * 1000)

        return {
            "status": "reindexed",
            "document_count": len(docs),
            "duration_ms": duration_ms,
            "data_dir": target_data_dir,
        }

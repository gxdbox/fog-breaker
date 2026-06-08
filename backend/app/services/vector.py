import logging
from typing import List, Optional

import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class VectorService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=DEFAULT_EMBEDDING_MODEL,
        )
        self.collection = self.client.get_or_create_collection(
            name="intelligences",
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, intelligence_id: int, text: str):
        try:
            self.collection.add(
                ids=[str(intelligence_id)],
                documents=[text[:2000]],
            )
        except Exception as e:
            logger.error(f"Vector add error for {intelligence_id}: {e}")

    def is_duplicate(self, text: str, threshold: Optional[float] = None) -> bool:
        threshold = threshold or settings.DEDUP_SIMILARITY_THRESHOLD
        try:
            results = self.collection.query(
                query_texts=[text[:2000]],
                n_results=1,
            )
            if results["distances"] and results["distances"][0]:
                distance = results["distances"][0][0]
                similarity = 1 - distance
                return similarity >= threshold
        except Exception as e:
            logger.error(f"Duplicate check error: {e}")
        return False

    def search(self, query: str, n: int = 10) -> List[dict]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n,
            )
            items = []
            for i in range(len(results["ids"][0])):
                items.append({
                    "id": int(results["ids"][0][i]),
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })
            return items
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

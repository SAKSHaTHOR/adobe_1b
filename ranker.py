
"""
Ranks sections and subsections based on semantic similarity using sentence-transformers
"""

import logging
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class ContentRanker:
    def __init__(self, model_path: str = "./local_model"):
        logger.info(f"Loading model from: {model_path}")
        self.model = SentenceTransformer(model_path)
        self.model_name = model_path
        self.embedding_cache = {}

    def rank_sections(self, sections: List[Dict[str, Any]], query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if not sections:
            return []

        logger.info(f"Ranking {len(sections)} sections for query: {query}")
        section_texts = [f"{s.get('title', '')}. {s.get('content', '')}" for s in sections]

        try:
            query_embedding = self._get_embedding(query)
            section_embeddings = self.model.encode(section_texts, show_progress_bar=False)

            similarities = cosine_similarity([query_embedding], section_embeddings)[0]

            ranked = []
            for i, section in enumerate(sections):
                s = section.copy()
                s['similarity_score'] = float(similarities[i])
                s['relevance_rank'] = 0
                ranked.append(s)

            ranked.sort(key=lambda x: x['similarity_score'], reverse=True)
            for i, s in enumerate(ranked[:top_k]):
                s['relevance_rank'] = i + 1

            logger.info("Top similarity scores:")
            for s in ranked[:3]:
                logger.info(f" - {s['title']} ({s['similarity_score']:.4f})")

            return ranked[:top_k]

        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            for i, s in enumerate(sections[:top_k]):
                s['similarity_score'] = 1.0 - i * 0.1
                s['relevance_rank'] = i + 1
            return sections[:top_k]

    def _get_embedding(self, text: str) -> np.ndarray:
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        embedding = self.model.encode([text], show_progress_bar=False)[0]
        self.embedding_cache[text] = embedding
        return embedding

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "embedding_dim": self.model.get_sentence_embedding_dimension(),
            "cache_size": len(self.embedding_cache)
        }

#!/usr/bin/env python3
"""
Generates structured JSON output for Round 1B challenge
"""

from typing import List, Dict, Any
from datetime import datetime

class OutputGenerator:
    def generate_output(
        self,
        persona: str,
        job_description: str,
        sections: List[Dict[str, Any]],
        subsections: List[Dict[str, Any]],
        processing_time: float,
        document_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:

        output = {
            "metadata": {
                "persona": persona,
                "job_to_be_done": job_description,
                "documents": list(document_metadata.keys()),
                "processing_timestamp": datetime.utcnow().isoformat() + "Z",
                "total_sections_considered": sum([meta['total_sections'] for meta in document_metadata.values()]),
                "total_pages": sum([meta['total_pages'] for meta in document_metadata.values()]),
                "processing_time_seconds": round(processing_time, 2)
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }

        for s in sections:
            output["extracted_sections"].append({
                "document": s.get("document_name"),
                "page_number": s.get("page_number"),
                "section_title": s.get("title"),
                "similarity_score": round(s.get("similarity_score", 0.0), 4),
                "importance_rank": s.get("relevance_rank")
            })

        for sub in subsections:
            output["subsection_analysis"].append({
                "document": sub.get("document_name"),
                "page_number": sub.get("page_number"),
                "subsection_id": sub.get("subsection_id"),
                "refined_text": sub.get("content", "")[:500]  # trimmed preview
            })

        return output

#!/usr/bin/env python3
import json, time, argparse
from pathlib import Path
from typing import List, Dict, Any
import logging

from pdf_parser import PDFParser
from ranker import ContentRanker
from output_generator import OutputGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentIntelligenceSystem:
    def __init__(self, model_path: str = "./local_model"):
        self.pdf_parser = PDFParser()
        self.ranker = ContentRanker(model_path)
        self.output_generator = OutputGenerator()

    def process_documents(self, pdf_paths: List[str], persona: str, job_description: str,
                          top_sections: int = 10, top_subsections: int = 20) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Processing {len(pdf_paths)} PDFs...")
        all_sections = []
        document_metadata = {}

        for pdf_path in pdf_paths:
            logger.info(f"Parsing: {pdf_path}")
            try:
                sections, metadata = self.pdf_parser.parse_pdf(pdf_path)
                logger.info(f"🧩 {len(sections)} sections found")
                document_metadata[pdf_path] = metadata
                for s in sections:
                    s['document_path'] = pdf_path
                    s['document_name'] = Path(pdf_path).name
                all_sections.extend(sections)
            except Exception as e:
                logger.error(f"Error parsing {pdf_path}: {e}")
                continue

        if not all_sections:
            raise ValueError("No content extracted from PDFs")

        query = f"Persona: {persona}. Job: {job_description}"
        ranked_sections = self.ranker.rank_sections(all_sections, query, top_k=top_sections)

        subsections = []
        for section in ranked_sections[:min(5, len(ranked_sections))]:
            subs = self.pdf_parser.extract_subsections(section['content'], section['document_path'], section['page_number'])
            ranked_subs = self.ranker.rank_sections(subs, query, top_k=min(4, len(subs)))
            subsections.extend(ranked_subs)

        processing_time = time.time() - start_time
        logger.info(f"Completed in {processing_time:.2f}s")

        return self.output_generator.generate_output(
            persona, job_description, ranked_sections, subsections[:top_subsections], processing_time, document_metadata
        )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='challenge1b_output.json')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pdfs = [f"/app/pdfs/{doc['filename']}" for doc in data['documents']]
    persona = data['persona']['role']
    job = data['job_to_be_done']['task']

    system = DocumentIntelligenceSystem()
    result = system.process_documents(pdfs, persona, job)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Done: {args.output}")

if __name__ == "__main__":
    main()

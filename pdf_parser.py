
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pdfplumber

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        self.section_patterns = [
            r'^(\d+\.?\s+[A-Z][^.!?]*?)$',
            r'^([A-Z][A-Z\s]{2,}[A-Z])$',
            r'^([A-Z][^.!?]*?)$',
            r'^(Abstract|Introduction|Methods?|Results?|Discussion|Conclusion|References|Bibliography)$',
            r'^(Executive Summary|Overview|Background|Analysis|Recommendations?)$',
        ]

    def parse_pdf(self, pdf_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        sections = []
        metadata = {
            'filename': Path(pdf_path).name,
            'total_pages': 0,
            'total_sections': 0
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata['total_pages'] = len(pdf.pages)
                all_text = ""
                page_breaks = []

                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        page_breaks.append(len(all_text))
                        all_text += f"\n--- PAGE {page_num} ---\n" + page_text + "\n"

                sections = self._extract_sections(all_text, page_breaks, pdf_path)
                metadata['total_sections'] = len(sections)
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")
            raise

        return sections, metadata

    def _extract_sections(self, text: str, page_breaks: List[int], pdf_path: str) -> List[Dict[str, Any]]:
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        current_page = 1

        for line in lines:
            line = line.strip()

            if line.startswith('--- PAGE'):
                match = re.search(r'PAGE (\d+)', line)
                if match:
                    current_page = int(match.group(1))
                continue

            if not line:
                continue

            if self._is_section_header(line):
                if current_section and current_content:
                    current_section['content'] = '\n'.join(current_content).strip()
                    current_section['word_count'] = len(current_section['content'].split())
                    if current_section['word_count'] > 5:
                        sections.append(current_section)

                current_section = {
                    'title': line,
                    'page_number': current_page,
                    'section_id': len(sections) + 1,
                    'content': '',
                    'word_count': 0
                }
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        if current_section and current_content:
            current_section['content'] = '\n'.join(current_content).strip()
            current_section['word_count'] = len(current_section['content'].split())
            if current_section['word_count'] > 5:
                sections.append(current_section)

        if not sections:
            return self._fallback_section_extraction(text)

        return sections

    def _is_section_header(self, line: str) -> bool:
        if len(line) > 100 or len(line) < 3:
            return False
        for pattern in self.section_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False

    def _fallback_section_extraction(self, text: str) -> List[Dict[str, Any]]:
        paragraphs = re.split(r'\n\s*\n', text)
        sections = []
        current_page = 1

        for para in paragraphs:
            para = para.strip()
            if not para or len(para.split()) < 10:
                continue
            match = re.search(r'--- PAGE (\d+) ---', para)
            if match:
                current_page = int(match.group(1))
                continue

            section = {
                'title': f"Section {len(sections) + 1}",
                'page_number': current_page,
                'section_id': len(sections) + 1,
                'content': para,
                'word_count': len(para.split())
            }
            sections.append(section)
            if len(sections) >= 30:
                break

        return sections

    def extract_subsections(self, content: str, document_path: str, page_number: int) -> List[Dict[str, Any]]:
        subsections = []
        sentences = re.split(r'[.!?]+', content)
        chunk_size = 3

        for i in range(0, len(sentences), chunk_size):
            chunk = '. '.join(s.strip() for s in sentences[i:i+chunk_size] if s.strip())
            if chunk and len(chunk.split()) >= 10:
                subsections.append({
                    'title': f"Subsection {len(subsections) + 1}",
                    'content': chunk,
                    'page_number': page_number,
                    'document_path': document_path,
                    'document_name': Path(document_path).name,
                    'subsection_id': len(subsections) + 1,
                    'word_count': len(chunk.split())
                })

        return subsections[:10]

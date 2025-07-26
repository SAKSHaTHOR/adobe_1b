# Challenge 1B: Persona-Driven Document Intelligence

## Problem Understanding

The challenge involves building an intelligent document processing system that extracts and ranks relevant sections from a collection of PDFs. The system must adapt to diverse user personas and tasks (jobs-to-be-done), such as researchers doing literature reviews or analysts evaluating financial documents.

## Solution Overview

Our solution follows a modular architecture and runs efficiently on CPU, using lightweight models. It consists of four primary components:

1. **PDF Parsing (`pdf_parser.py`)**  
   We use `pdfplumber` to extract structured content from PDFs. Sections are identified using regular expressions based on common academic/business headers (e.g., "Introduction", "Methods", "Executive Summary"). In absence of clear headers, fallback heuristics split content by paragraphs. Each section includes metadata like title, page number, and word count.

2. **Semantic Ranking (`ranker.py`)**  
   We use the `paraphrase-MiniLM-L6-v2` model from `sentence-transformers`, which provides compact embeddings ideal for CPU usage (<100MB). For each document, section content is semantically matched against a query string formed by concatenating the persona and the job description. Cosine similarity is computed and top-k sections are selected. Subsections are extracted similarly from top-ranked content.

3. **Subsection Refinement**  
   Within the top 5 sections, we extract finer-grained subsections by splitting content into semantically dense chunks (via sentences or paragraphs). These are ranked independently using the same embedding model.

4. **Output Generation (`output_generator.py`)**  
   The final output JSON contains metadata (persona, job, processing time), extracted sections (with similarity scores and ranks), and refined subsections. Importance levels (e.g., critical, high, medium) are inferred based on similarity scores.

## Technical Constraints

- **Model**: `paraphrase-MiniLM-L6-v2` (size < 100MB)
- **Hardware**: CPU-only (no GPU, no internet at runtime)
- **Runtime**: Designed to complete within 60 seconds for 3–5 PDFs
- **No internet access**: Model is pre-loaded into Docker image

## Extensibility

- Generic enough to handle diverse personas and domains (travel, HR, education, research)
- Can be adapted to other embedding models if needed
- Easily extendable to include more structured document types (tables, figures, etc.)

## How to Run

1. Build the Docker image:

   ```bash
   docker build -t pdf-processor .
   ```

2. Run the Docker container:

   ```bash
   docker run --rm -v "${PWD}\pdfs:/app/pdfs" -v "${PWD}\output:/app/output" -v "${PWD}\input.json:/app/input.json" --network none pdf-processor

   ```
---

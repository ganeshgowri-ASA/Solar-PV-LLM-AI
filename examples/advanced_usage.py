"""Advanced usage examples for IEC PDF ingestion."""

from src.ingestion.api import IECIngestionAPI
from src.ingestion.models import IngestionConfig

# Example 1: Custom Configuration
print("Example 1: Custom Configuration")
print("-" * 50)

config = IngestionConfig(
    chunk_size=1500,
    chunk_overlap=300,
    clause_aware=True,
    qa_enabled=True,
    qa_provider="anthropic",
    qa_model="claude-3-haiku-20240307",
    max_questions_per_chunk=5,
    output_format="json",
    pretty_print=True,
)

api = IECIngestionAPI(config=config)
print("API initialized with custom config")
print(f"  Chunk size: {config.chunk_size}")
print(f"  Chunk overlap: {config.chunk_overlap}")
print(f"  Q&A enabled: {config.qa_enabled}")
print()


# Example 2: Process and Validate
print("\nExample 2: Process and Validate")
print("-" * 50)

# document = api.ingest("data/raw/iec_standard.pdf")

# Validate
# validation = api.validate(document)
# print(f"Valid: {validation['valid']}")
# print(f"Errors: {len(validation['errors'])}")
# print(f"Warnings: {len(validation['warnings'])}")

# if validation['warnings']:
#     print("\nWarnings:")
#     for warning in validation['warnings']:
#         print(f"  - {warning}")

print("Process document and validate results")
print()


# Example 3: Search and Query
print("\nExample 3: Search and Query")
print("-" * 50)

# Search for relevant chunks
# chunks = api.search_chunks(document, "temperature testing", top_k=5)
# print(f"Found {len(chunks)} relevant chunks")

# for i, chunk in enumerate(chunks, 1):
#     print(f"\n{i}. Clause {chunk.clause_info.clause_number if chunk.clause_info else 'N/A'}")
#     print(f"   {chunk.content[:150]}...")

print("Search chunks by keywords")
print()


# Example 4: Export Different Formats
print("\nExample 4: Export Different Formats")
print("-" * 50)

# Export chunks for vector database
# chunks_file = api.export_chunks(document, "vectordb_chunks.jsonl")
# print(f"Chunks exported to: {chunks_file}")

# Export Q&A pairs for training
# qa_file = api.export_qa_pairs(document, "training_qa.jsonl")
# print(f"Q&A pairs exported to: {qa_file}")

# Save full document
# doc_file = api.save(document, "full_document", format="json")
# print(f"Document saved to: {doc_file}")

print("Export in multiple formats")
print()


# Example 5: Batch Processing
print("\nExample 5: Batch Processing")
print("-" * 50)

pdf_files = [
    "data/raw/iec_61730-1.pdf",
    "data/raw/iec_61730-2.pdf",
    "data/raw/iec_61215.pdf",
]

# documents = api.ingest_batch(pdf_files)
# print(f"Processed {len(documents)} documents")

# for doc in documents:
#     stats = api.get_statistics(doc)
#     print(f"\n{doc.metadata.standard_id}:")
#     print(f"  Chunks: {stats['total_chunks']}")
#     print(f"  Q&A pairs: {stats['total_qa_pairs']}")
#     print(f"  Clauses: {stats['total_clauses']}")

print("Process multiple documents in batch")
print()


# Example 6: Get Clause Hierarchy
print("\nExample 6: Get Clause Hierarchy")
print("-" * 50)

# hierarchy = api.get_clause_hierarchy(document)

# def print_hierarchy(h, indent=0):
#     for clause_num, info in sorted(h.items()):
#         title = info.get('title') or 'No title'
#         print("  " * indent + f"{clause_num}: {title}")
#         if info.get('children'):
#             print_hierarchy(info['children'], indent + 1)

# print_hierarchy(hierarchy)

print("Extract and display clause hierarchy")
print()


# Example 7: Dynamic Configuration Updates
print("\nExample 7: Dynamic Configuration Updates")
print("-" * 50)

# Update config on the fly
api.update_config(
    chunk_size=2000,
    chunk_overlap=400,
    qa_enabled=False,
)

updated_config = api.get_config()
print(f"Updated chunk size: {updated_config.chunk_size}")
print(f"Updated chunk overlap: {updated_config.chunk_overlap}")
print(f"Q&A enabled: {updated_config.qa_enabled}")
print()


print("\n" + "=" * 50)
print("Examples complete!")
print("Replace commented code with actual PDF paths to run")
print("=" * 50)

"""Basic usage example for IEC PDF ingestion."""

from src.ingestion.api import quick_ingest, load_document

# Example 1: Quick ingestion with defaults
print("Example 1: Quick Ingestion")
print("-" * 50)

# Process a PDF (replace with actual PDF path)
# document = quick_ingest("data/raw/iec_61730-1.pdf")

# For demonstration, we'll show what you would do with the result:
# print(f"Document ID: {document.document_id}")
# print(f"Standard: {document.metadata.standard_id}")
# print(f"Total chunks: {len(document.chunks)}")
# print(f"Total Q&A pairs: {document.get_total_qa_pairs()}")

print("\nTo run this example, provide a PDF path:")
print("  document = quick_ingest('path/to/iec_standard.pdf')")
print()


# Example 2: Load and explore processed document
print("\nExample 2: Load Processed Document")
print("-" * 50)

# Load previously processed document
# document = load_document("data/output/IEC_61730-1_processed.json")

# Explore chunks
# for i, chunk in enumerate(document.chunks[:3]):  # First 3 chunks
#     print(f"\nChunk {i+1}:")
#     print(f"  Clause: {chunk.clause_info.clause_number if chunk.clause_info else 'N/A'}")
#     print(f"  Content preview: {chunk.content[:100]}...")
#     print(f"  Q&A pairs: {len(chunk.qa_pairs)}")

print("\nTo run this example, load a processed document:")
print("  document = load_document('data/output/your_document.json')")
print()


# Example 3: Access Q&A pairs
print("\nExample 3: Access Q&A Pairs")
print("-" * 50)

# for chunk in document.chunks:
#     if chunk.qa_pairs:
#         print(f"\nClause {chunk.clause_info.clause_number if chunk.clause_info else 'N/A'}:")
#         for qa in chunk.qa_pairs:
#             print(f"  Q: {qa.question}")
#             print(f"  A: {qa.answer}")
#             print()

print("Iterate through chunks and access qa_pairs attribute")
print()

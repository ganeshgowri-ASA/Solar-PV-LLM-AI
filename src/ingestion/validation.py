"""Validation utilities for processed documents."""

import logging
from typing import List, Dict, Any, Tuple
from collections import Counter

from .models import ProcessedDocument, Chunk, DocumentMetadata

logger = logging.getLogger(__name__)


class DocumentValidator:
    """Comprehensive validator for processed documents."""

    def __init__(
        self,
        min_chunk_size: int = 100,
        max_chunk_size: int = 2000,
        min_chunks: int = 1,
        required_metadata_fields: List[str] = None,
    ):
        """Initialize validator.

        Args:
            min_chunk_size: Minimum acceptable chunk size
            max_chunk_size: Maximum acceptable chunk size
            min_chunks: Minimum number of chunks expected
            required_metadata_fields: List of required metadata fields
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.min_chunks = min_chunks
        self.required_metadata_fields = required_metadata_fields or [
            "standard_id",
            "file_path",
        ]

    def validate(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Run comprehensive validation.

        Args:
            document: Document to validate

        Returns:
            Validation results dictionary
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {},
        }

        # Run all validation checks
        checks = [
            self._validate_chunk_count,
            self._validate_chunk_sizes,
            self._validate_metadata,
            self._validate_clause_info,
            self._validate_qa_pairs,
            self._validate_content_quality,
            self._validate_consistency,
        ]

        for check in checks:
            check_name = check.__name__.replace("_validate_", "")
            check_results = check(document)

            results["checks"][check_name] = check_results

            if check_results.get("errors"):
                results["errors"].extend(check_results["errors"])
                results["valid"] = False

            if check_results.get("warnings"):
                results["warnings"].extend(check_results["warnings"])

        return results

    def _validate_chunk_count(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate chunk count.

        Args:
            document: Document to validate

        Returns:
            Check results
        """
        results = {"errors": [], "warnings": [], "stats": {}}

        chunk_count = len(document.chunks)
        results["stats"]["chunk_count"] = chunk_count

        if chunk_count < self.min_chunks:
            results["errors"].append(
                f"Insufficient chunks: {chunk_count} (minimum: {self.min_chunks})"
            )
        elif chunk_count == 0:
            results["errors"].append("No chunks generated")

        return results

    def _validate_chunk_sizes(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate chunk sizes.

        Args:
            document: Document to validate

        Returns:
            Check results
        """
        results = {"errors": [], "warnings": [], "stats": {}}

        if not document.chunks:
            return results

        chunk_sizes = [chunk.char_count for chunk in document.chunks]

        results["stats"]["min_chunk_size"] = min(chunk_sizes)
        results["stats"]["max_chunk_size"] = max(chunk_sizes)
        results["stats"]["avg_chunk_size"] = sum(chunk_sizes) / len(chunk_sizes)

        # Check for undersized chunks
        small_chunks = [c for c in document.chunks if c.char_count < self.min_chunk_size]
        if small_chunks:
            results["warnings"].append(
                f"{len(small_chunks)} chunks below minimum size ({self.min_chunk_size} chars)"
            )

        # Check for oversized chunks
        large_chunks = [c for c in document.chunks if c.char_count > self.max_chunk_size]
        if large_chunks:
            results["warnings"].append(
                f"{len(large_chunks)} chunks exceed maximum size ({self.max_chunk_size} chars)"
            )

        # Check for empty chunks
        empty_chunks = [c for c in document.chunks if not c.content.strip()]
        if empty_chunks:
            results["errors"].append(f"{len(empty_chunks)} empty chunks found")

        return results

    def _validate_metadata(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate document metadata.

        Args:
            document: Document to validate

        Returns:
            Check results
        """
        results = {"errors": [], "warnings": [], "stats": {}}

        metadata = document.metadata

        # Check required fields
        missing_fields = []
        for field in self.required_metadata_fields:
            if not getattr(metadata, field, None):
                missing_fields.append(field)

        if missing_fields:
            results["warnings"].append(f"Missing metadata fields: {', '.join(missing_fields)}")

        # Validate specific fields
        if metadata.year and (metadata.year < 1900 or metadata.year > 2030):
            results["warnings"].append(f"Suspicious year: {metadata.year}")

        if metadata.total_pages and metadata.total_pages < 1:
            results["errors"].append(f"Invalid page count: {metadata.total_pages}")

        # Check for reasonable values
        if metadata.standard_id:
            results["stats"]["has_standard_id"] = True
        else:
            results["warnings"].append("No standard ID extracted")

        return results

    def _validate_clause_info(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate clause information.

        Args:
            document: Document to validate

        Returns:
            Check results
        """
        results = {"errors": [], "warnings": [], "stats": {}}

        results["stats"]["total_clauses"] = len(document.clauses)

        if document.clauses:
            # Check chunks with clause info
            chunks_with_clauses = [c for c in document.chunks if c.clause_info]
            clause_coverage = len(chunks_with_clauses) / len(document.chunks) * 100

            results["stats"]["clause_coverage_percent"] = round(clause_coverage, 2)

            if clause_coverage < 30:
                results["warnings"].append(
                    f"Low clause coverage: {clause_coverage:.1f}% of chunks have clause info"
                )

            # Check for duplicate clause numbers
            clause_numbers = [c.clause_number for c in document.clauses]
            duplicates = [num for num, count in Counter(clause_numbers).items() if count > 1]

            if duplicates:
                results["warnings"].append(
                    f"Duplicate clause numbers found: {', '.join(duplicates)}"
                )

        else:
            results["warnings"].append("No clauses extracted from document")

        return results

    def _validate_qa_pairs(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate Q&A pairs.

        Args:
            document: Document to validate

        Returns:
            Check results
        """
        results = {"errors": [], "warnings": [], "stats": {}}

        total_qa = sum(len(chunk.qa_pairs) for chunk in document.chunks)
        results["stats"]["total_qa_pairs"] = total_qa

        if total_qa == 0:
            results["warnings"].append("No Q&A pairs generated")
            return results

        # Calculate coverage
        chunks_with_qa = [c for c in document.chunks if c.qa_pairs]
        qa_coverage = len(chunks_with_qa) / len(document.chunks) * 100 if document.chunks else 0

        results["stats"]["qa_coverage_percent"] = round(qa_coverage, 2)

        if qa_coverage < 30:
            results["warnings"].append(
                f"Low Q&A coverage: {qa_coverage:.1f}% of chunks have Q&A pairs"
            )

        # Validate Q&A content
        for chunk in document.chunks:
            for qa in chunk.qa_pairs:
                if not qa.question or not qa.question.strip():
                    results["errors"].append(f"Empty question in chunk {chunk.chunk_id}")

                if not qa.answer or not qa.answer.strip():
                    results["errors"].append(f"Empty answer in chunk {chunk.chunk_id}")

                # Check for reasonable lengths
                if len(qa.question) < 10:
                    results["warnings"].append(
                        f"Very short question ({len(qa.question)} chars) in chunk {chunk.chunk_id}"
                    )

                if len(qa.answer) < 10:
                    results["warnings"].append(
                        f"Very short answer ({len(qa.answer)} chars) in chunk {chunk.chunk_id}"
                    )

        return results

    def _validate_content_quality(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate content quality.

        Args:
            document: Document to validate

        Returns:
            Check results
        """
        results = {"errors": [], "warnings": [], "stats": {}}

        if not document.chunks:
            return results

        # Check for very repetitive content
        unique_contents = set(chunk.content for chunk in document.chunks)
        duplicate_rate = 1 - (len(unique_contents) / len(document.chunks))

        results["stats"]["duplicate_content_rate"] = round(duplicate_rate * 100, 2)

        if duplicate_rate > 0.5:
            results["warnings"].append(
                f"High duplicate content rate: {duplicate_rate*100:.1f}%"
            )

        # Check average words per chunk
        total_words = sum(chunk.word_count for chunk in document.chunks)
        avg_words = total_words / len(document.chunks)

        results["stats"]["avg_words_per_chunk"] = round(avg_words, 2)

        if avg_words < 20:
            results["warnings"].append(f"Very low average words per chunk: {avg_words:.1f}")

        return results

    def _validate_consistency(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate internal consistency.

        Args:
            document: Document to validate

        Returns:
            Check results
        """
        results = {"errors": [], "warnings": [], "stats": {}}

        # Check chunk indices are sequential
        expected_indices = set(range(len(document.chunks)))
        actual_indices = set(chunk.chunk_index for chunk in document.chunks)

        if expected_indices != actual_indices:
            results["errors"].append("Chunk indices are not sequential")

        # Check for duplicate chunk IDs
        chunk_ids = [chunk.chunk_id for chunk in document.chunks]
        if len(chunk_ids) != len(set(chunk_ids)):
            results["errors"].append("Duplicate chunk IDs found")

        # Verify processing stats match actual counts
        stats = document.processing_stats
        if "total_chunks" in stats and stats["total_chunks"] != len(document.chunks):
            results["warnings"].append(
                f"Processing stats mismatch: stats says {stats['total_chunks']} chunks, "
                f"but document has {len(document.chunks)}"
            )

        return results


def quick_validate(document: ProcessedDocument) -> Tuple[bool, List[str]]:
    """Quick validation check.

    Args:
        document: Document to validate

    Returns:
        Tuple of (is_valid, list of issues)
    """
    validator = DocumentValidator()
    results = validator.validate(document)

    issues = results["errors"] + results["warnings"]

    return results["valid"], issues


def print_validation_report(validation_results: Dict[str, Any]) -> None:
    """Print human-readable validation report.

    Args:
        validation_results: Results from DocumentValidator.validate()
    """
    print("\n" + "=" * 60)
    print("VALIDATION REPORT")
    print("=" * 60)

    print(f"\nOverall Status: {'✓ VALID' if validation_results['valid'] else '✗ INVALID'}")

    # Print check results
    for check_name, check_results in validation_results["checks"].items():
        print(f"\n{check_name.upper().replace('_', ' ')}:")

        if check_results.get("stats"):
            for key, value in check_results["stats"].items():
                print(f"  - {key}: {value}")

    # Print errors
    if validation_results["errors"]:
        print(f"\n✗ ERRORS ({len(validation_results['errors'])}):")
        for error in validation_results["errors"]:
            print(f"  - {error}")

    # Print warnings
    if validation_results["warnings"]:
        print(f"\n⚠ WARNINGS ({len(validation_results['warnings'])}):")
        for warning in validation_results["warnings"]:
            print(f"  - {warning}")

    if not validation_results["errors"] and not validation_results["warnings"]:
        print("\n✓ No issues found!")

    print("\n" + "=" * 60)

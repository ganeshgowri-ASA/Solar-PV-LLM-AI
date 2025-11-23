"""QA Demo script to verify citation functionality.

This script demonstrates the complete citation workflow with realistic
Solar PV examples and verifies correctness of citations.
"""

from src.citation_manager import (
    CitationManager,
    CitationStyle,
    create_standard_metadata
)


def setup_solar_pv_documents():
    """Set up sample Solar PV standard documents."""
    documents = [
        create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="Photovoltaic (PV) module safety qualification - Part 1: Requirements for construction",
            organization="IEC",
            year=2016,
            url="https://webstore.iec.ch/publication/26210"
        ),
        create_standard_metadata(
            standard_id="IEC 61730-2:2016",
            title="Photovoltaic (PV) module safety qualification - Part 2: Requirements for testing",
            organization="IEC",
            year=2016,
            url="https://webstore.iec.ch/publication/26211"
        ),
        create_standard_metadata(
            standard_id="IEC 61215-1:2016",
            title="Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1: Test requirements",
            organization="IEC",
            year=2016,
            url="https://webstore.iec.ch/publication/26434"
        ),
        create_standard_metadata(
            standard_id="IEC 62804-1:2015",
            title="Photovoltaic (PV) modules - Test methods for the detection of potential-induced degradation - Part 1: Crystalline silicon",
            organization="IEC",
            year=2015,
            url="https://webstore.iec.ch/publication/22773"
        ),
        create_standard_metadata(
            standard_id="IEEE 1547-2018",
            title="IEEE Standard for Interconnection and Interoperability of Distributed Energy Resources with Associated Electric Power Systems Interfaces",
            organization="IEEE",
            year=2018,
            url="https://standards.ieee.org/standard/1547-2018.html"
        )
    ]
    return documents


def create_sample_retrieved_docs():
    """Create sample retrieved documents from RAG."""
    return [
        {
            'document_id': 'IEC 61730-1:2016',
            'content': (
                'Module construction requirements are specified in Clause 10. '
                'The module shall be designed and constructed to withstand the stresses '
                'that can reasonably be expected to occur during normal use.'
            ),
            'score': 0.95,
            'metadata': {'page': 25, 'section': '10'}
        },
        {
            'document_id': 'IEC 61730-2:2016',
            'content': (
                'Module safety testing shall include mechanical load tests as per Clause 10.2. '
                'Test procedures for mechanical load testing are detailed in Section 10.2.1.'
            ),
            'score': 0.92,
            'metadata': {'page': 30, 'section': '10.2'}
        },
        {
            'document_id': 'IEC 61215-1:2016',
            'content': (
                'Design qualification testing includes thermal cycling tests described in Clause 10.11. '
                'Modules shall undergo 200 thermal cycles between -40°C and +85°C.'
            ),
            'score': 0.90,
            'metadata': {'page': 45, 'section': '10.11'}
        },
        {
            'document_id': 'IEC 62804-1:2015',
            'content': (
                'Potential-induced degradation (PID) testing is conducted according to Clause 5.2. '
                'Test conditions require 96 hours at 85°C and 85% relative humidity.'
            ),
            'score': 0.88,
            'metadata': {'page': 12, 'section': '5.2'}
        },
        {
            'document_id': 'IEEE 1547-2018',
            'content': (
                'Grid interconnection requirements are specified in Section 4.1. '
                'The distributed energy resource shall not actively regulate the voltage at the PCC.'
            ),
            'score': 0.85,
            'metadata': {'page': 20, 'section': '4.1'}
        }
    ]


def test_sample_response_1():
    """Test Case 1: Basic safety requirements response."""
    print("\n" + "="*80)
    print("TEST CASE 1: Basic Safety Requirements")
    print("="*80)

    # Initialize manager with IEC style
    manager = CitationManager(style=CitationStyle.IEC, auto_inject_citations=True)

    # Add documents
    docs = setup_solar_pv_documents()
    manager.add_documents(docs)

    # Sample LLM response
    response_text = (
        "Photovoltaic modules must meet stringent safety requirements according to "
        "IEC 61730-1:2016. The construction shall comply with Clause 10 specifications "
        "for mechanical integrity. Additionally, modules must undergo safety testing "
        "as outlined in IEC 61730-2:2016."
    )

    # Retrieved documents
    retrieved_docs = create_sample_retrieved_docs()[:2]  # Use first two docs

    # Process response
    result = manager.process_response(
        response_text=response_text,
        retrieved_documents=retrieved_docs,
        response_id="safety_requirements_001"
    )

    # Display results
    print("\nORIGINAL RESPONSE:")
    print("-" * 80)
    print(result.original_text)

    print("\n\nRESPONSE WITH CITATIONS:")
    print("-" * 80)
    print(result.text_with_citations)

    print("\n\nREFERENCE SECTION:")
    print("-" * 80)
    print(result.reference_section)

    print("\n\nEXTRACTION METADATA:")
    print("-" * 80)
    for key, value in result.extraction_metadata.items():
        print(f"{key}: {value}")

    # Verification
    print("\n\nVERIFICATION:")
    print("-" * 80)
    print(f"✓ Citations found: {len(result.citations_found)}")
    print(f"✓ Standard IDs detected: {len(result.extraction_metadata.get('standard_ids_found', []))}")
    print(f"✓ Clause references detected: {len(result.extraction_metadata.get('clause_refs_found', []))}")

    assert len(result.extraction_metadata.get('standard_ids_found', [])) >= 2, "Should find IEC standards"
    print("✓ Test PASSED: Standard IDs correctly identified")


def test_sample_response_2():
    """Test Case 2: Multi-standard response with clause references."""
    print("\n" + "="*80)
    print("TEST CASE 2: Multi-Standard Response with Clause References")
    print("="*80)

    manager = CitationManager(style=CitationStyle.IEC, auto_inject_citations=True)
    docs = setup_solar_pv_documents()
    manager.add_documents(docs)

    response_text = (
        "The design qualification of PV modules involves multiple testing procedures. "
        "Thermal cycling tests are specified in IEC 61215-1:2016, Clause 10.11, which "
        "requires 200 cycles between -40°C and +85°C. Potential-induced degradation "
        "testing is covered in IEC 62804-1:2015, Section 5.2, with test conditions "
        "of 96 hours at 85°C/85% RH. For grid interconnection, IEEE 1547-2018 provides "
        "voltage regulation requirements in Section 4.1."
    )

    retrieved_docs = create_sample_retrieved_docs()[2:]  # Use last three docs

    result = manager.process_response(
        response_text=response_text,
        retrieved_documents=retrieved_docs,
        response_id="multi_standard_002"
    )

    print("\nORIGINAL RESPONSE:")
    print("-" * 80)
    print(result.original_text)

    print("\n\nRESPONSE WITH CITATIONS:")
    print("-" * 80)
    print(result.text_with_citations)

    print("\n\nREFERENCE SECTION:")
    print("-" * 80)
    print(result.reference_section)

    print("\n\nEXTRACTION METADATA:")
    print("-" * 80)
    for key, value in result.extraction_metadata.items():
        print(f"{key}: {value}")

    print("\n\nVERIFICATION:")
    print("-" * 80)
    print(f"✓ Citations found: {len(result.citations_found)}")
    print(f"✓ Standard IDs detected: {len(result.extraction_metadata.get('standard_ids_found', []))}")
    print(f"✓ Clause references detected: {len(result.extraction_metadata.get('clause_refs_found', []))}")

    # Verify clause references were found
    clause_refs = result.extraction_metadata.get('clause_refs_found', [])
    assert len(clause_refs) >= 3, "Should find multiple clause references"
    print("✓ Test PASSED: Clause references correctly identified")


def test_citation_style_comparison():
    """Test Case 3: Compare different citation styles."""
    print("\n" + "="*80)
    print("TEST CASE 3: Citation Style Comparison")
    print("="*80)

    response_text = (
        "PV module safety qualification requires compliance with IEC 61730 standards."
    )

    retrieved_docs = create_sample_retrieved_docs()[:1]

    styles = [CitationStyle.IEC, CitationStyle.IEEE, CitationStyle.ISO, CitationStyle.APA]

    for style in styles:
        print(f"\n{'='*80}")
        print(f"Citation Style: {style.value.upper()}")
        print('='*80)

        manager = CitationManager(style=style, auto_inject_citations=True)
        docs = setup_solar_pv_documents()
        manager.add_documents(docs)

        result = manager.process_response(
            response_text=response_text,
            retrieved_documents=retrieved_docs
        )

        print("\nREFERENCE FORMAT:")
        print("-" * 80)
        print(result.reference_section)


def test_statistics_and_tracking():
    """Test Case 4: Verify statistics and usage tracking."""
    print("\n" + "="*80)
    print("TEST CASE 4: Statistics and Usage Tracking")
    print("="*80)

    manager = CitationManager(style=CitationStyle.IEC)
    docs = setup_solar_pv_documents()
    manager.add_documents(docs)

    # Process multiple responses
    responses = [
        "First response about IEC 61730 safety requirements.",
        "Second response about IEC 61215 design qualification.",
        "Third response referencing both IEC 61730 and IEC 61215."
    ]

    for i, resp in enumerate(responses, 1):
        retrieved = create_sample_retrieved_docs()[:2]
        manager.process_response(resp, retrieved, response_id=f"stats_test_{i}")

    # Get statistics
    stats = manager.get_statistics()

    print("\nCITATION MANAGER STATISTICS:")
    print("-" * 80)
    print(f"Total documents tracked: {stats['total_documents']}")
    print(f"Total citations: {stats['total_citations']}")
    print(f"Responses processed: {stats['responses_processed']}")
    print(f"Average citations per document: {stats['average_citations_per_document']:.2f}")

    print("\nDocument types:")
    for doc_type, count in stats.get('document_types', {}).items():
        print(f"  - {doc_type}: {count}")

    print("\n\nVERIFICATION:")
    print("-" * 80)
    assert stats['total_documents'] == 5, "Should have 5 documents"
    assert stats['responses_processed'] == 3, "Should have processed 3 responses"
    print("✓ Test PASSED: Statistics correctly tracked")


def test_reference_export_import():
    """Test Case 5: Export and import reference data."""
    print("\n" + "="*80)
    print("TEST CASE 5: Reference Export/Import")
    print("="*80)

    import tempfile
    from pathlib import Path

    manager = CitationManager(style=CitationStyle.IEC)
    docs = setup_solar_pv_documents()
    manager.add_documents(docs)

    # Export to temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        manager.export_references(temp_path)
        print(f"\n✓ References exported to: {temp_path}")

        # Import in new manager
        new_manager = CitationManager()
        new_manager.import_references(temp_path)

        # Verify
        stats = new_manager.get_statistics()
        print(f"✓ Imported {stats['total_documents']} documents")

        # Check specific document
        doc = new_manager.get_document("IEC 61730-1:2016")
        assert doc is not None, "Should find IEC 61730-1:2016"
        print(f"✓ Successfully retrieved: {doc.title}")

        print("\n\nVERIFICATION:")
        print("-" * 80)
        assert stats['total_documents'] == 5, "Should have imported all 5 documents"
        print("✓ Test PASSED: Export/Import successful")

    finally:
        Path(temp_path).unlink()


def run_all_qa_tests():
    """Run all QA test cases."""
    print("\n" + "="*80)
    print("CITATION MANAGER QA VERIFICATION")
    print("Solar PV LLM AI Project")
    print("="*80)

    test_cases = [
        ("Basic Safety Requirements", test_sample_response_1),
        ("Multi-Standard with Clauses", test_sample_response_2),
        ("Citation Style Comparison", test_citation_style_comparison),
        ("Statistics and Tracking", test_statistics_and_tracking),
        ("Reference Export/Import", test_reference_export_import),
    ]

    results = []

    for name, test_func in test_cases:
        try:
            test_func()
            results.append((name, "PASSED"))
            print(f"\n✓ {name}: PASSED")
        except Exception as e:
            results.append((name, f"FAILED: {str(e)}"))
            print(f"\n✗ {name}: FAILED - {str(e)}")

    # Summary
    print("\n" + "="*80)
    print("QA VERIFICATION SUMMARY")
    print("="*80)

    for name, status in results:
        symbol = "✓" if "PASSED" in status else "✗"
        print(f"{symbol} {name}: {status}")

    passed = sum(1 for _, status in results if "PASSED" in status)
    total = len(results)

    print("\n" + "="*80)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*80)

    return passed == total


if __name__ == "__main__":
    success = run_all_qa_tests()
    exit(0 if success else 1)

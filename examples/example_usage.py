"""
Example usage of the Solar PV Multi-LLM Orchestrator.

This script demonstrates various ways to interact with the orchestrator API.
"""

import httpx
import asyncio
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


async def example_calculation_query():
    """Example: Calculation query."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Calculation Query")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "query": "Calculate the energy yield for a 10kW solar system in California with 5 sun hours per day",
                "query_type": "calculation",
                "max_tokens": 2000,
                "temperature": 0.7
            },
            timeout=30.0
        )

        result = response.json()
        print(f"\nQuery Type: {result['query_type']}")
        print(f"Primary LLM: {result['primary_llm']}")
        print(f"Confidence: {result['classification_confidence']:.2f}")
        print(f"Latency: {result['total_latency_ms']:.2f}ms")
        print(f"\nResponse:\n{result['response'][:500]}...")


async def example_technical_explanation():
    """Example: Technical explanation query."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Technical Explanation")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "query": "How does MPPT (Maximum Power Point Tracking) work in solar inverters?",
                "max_tokens": 2000,
                "temperature": 0.7
            },
            timeout=30.0
        )

        result = response.json()
        print(f"\nQuery Type: {result['query_type']}")
        print(f"Primary LLM: {result['primary_llm']}")
        print(f"Confidence: {result['classification_confidence']:.2f}")
        print(f"\nResponse:\n{result['response'][:500]}...")


async def example_code_generation():
    """Example: Code generation query."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Code Generation")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "query": "Write Python code to calculate the performance ratio of a solar PV system given energy yield and expected output",
                "query_type": "code_generation",
                "max_tokens": 2000,
                "temperature": 0.7
            },
            timeout=30.0
        )

        result = response.json()
        print(f"\nQuery Type: {result['query_type']}")
        print(f"Primary LLM: {result['primary_llm']}")
        print(f"\nGenerated Code:\n{result['response'][:500]}...")


async def example_hybrid_response():
    """Example: Hybrid response from multiple LLMs."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Hybrid Response")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "query": "Compare monocrystalline and polycrystalline solar panels in terms of efficiency, cost, and longevity",
                "preferred_llm": "hybrid",
                "max_tokens": 3000,
                "temperature": 0.7
            },
            timeout=60.0
        )

        result = response.json()
        print(f"\nQuery Type: {result['query_type']}")
        print(f"Is Hybrid: {result['is_hybrid']}")
        print(f"Number of Responses: {len(result['responses'])}")
        print(f"\nHybrid Response:\n{result['response'][:600]}...")


async def example_explicit_llm_selection():
    """Example: Explicit LLM selection."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Explicit LLM Selection (Claude)")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "query": "Explain the degradation mechanisms in solar panels over time",
                "preferred_llm": "claude",
                "max_tokens": 2000,
                "temperature": 0.7
            },
            timeout=30.0
        )

        result = response.json()
        print(f"\nQuery Type: {result['query_type']}")
        print(f"Primary LLM: {result['primary_llm']}")
        print(f"\nResponse:\n{result['response'][:500]}...")


async def example_health_check():
    """Example: Health check."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Health Check")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/health")

        result = response.json()
        print(f"\nService Status: {result['status']}")
        print("\nComponents:")
        for component, status in result['components'].items():
            print(f"  - {component}: {status}")
        print("\nConfiguration:")
        for key, value in result['config'].items():
            print(f"  - {key}: {value}")


async def example_list_models():
    """Example: List available models."""
    print("\n" + "="*60)
    print("EXAMPLE 7: List Available Models")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/models")

        result = response.json()
        print("\nAvailable Models:")
        for provider, info in result['models'].items():
            print(f"\n  {provider.upper()}:")
            print(f"    Name: {info['name']}")
            print(f"    Provider: {info['provider']}")
            print(f"    Available: {info['available']}")

        print("\nRouting Configuration:")
        for key, value in result['routing'].items():
            print(f"  - {key}: {value}")


async def example_query_types():
    """Example: List supported query types."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Supported Query Types")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/query-types")

        result = response.json()
        print("\nSupported Query Types:")
        for type_key, type_info in result['query_types'].items():
            print(f"\n  {type_info['name']}:")
            print(f"    Description: {type_info['description']}")
            print(f"    Examples:")
            for example in type_info['examples']:
                print(f"      - {example}")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("Solar PV Multi-LLM Orchestrator - Usage Examples")
    print("="*60)
    print("\nMake sure the orchestrator service is running:")
    print("  python main.py")
    print("\nThen run these examples to see it in action!")

    try:
        # Info endpoints (no LLM calls)
        await example_health_check()
        await example_list_models()
        await example_query_types()

        # Query examples (require API keys)
        print("\n" + "="*60)
        print("NOTE: The following examples require valid API keys")
        print("="*60)

        # Uncomment these when you have valid API keys configured
        # await example_calculation_query()
        # await example_technical_explanation()
        # await example_code_generation()
        # await example_hybrid_response()
        # await example_explicit_llm_selection()

        print("\n" + "="*60)
        print("Examples completed!")
        print("="*60)

    except httpx.ConnectError:
        print("\nERROR: Could not connect to the orchestrator service.")
        print("Make sure it's running at http://localhost:8000")
        print("\nStart the service with: python main.py")
    except Exception as e:
        print(f"\nERROR: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())

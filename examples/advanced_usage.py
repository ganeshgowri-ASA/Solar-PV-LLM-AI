"""
Advanced usage examples for Solar PV Multi-Agent System

This example demonstrates:
1. Custom configurations
2. Direct agent access
3. Detailed response analysis
4. Error handling
"""

import asyncio
from src.api import SolarPVMultiAgent
from src.core.config import SystemConfig
from src.core.protocols import Message, MessageRole


async def custom_configuration_example():
    """Example with custom configuration"""
    print("\n" + "="*80)
    print("Example: Custom Configuration")
    print("="*80)

    # Create custom configuration
    custom_config = SystemConfig(
        default_model="gpt-4-turbo-preview",
        supervisor_model="gpt-4-turbo-preview",
        agent_temperature=0.5,  # Lower temperature for more consistent responses
        max_iterations=3
    )

    agent_system = SolarPVMultiAgent(
        system_config=custom_config,
        log_level="DEBUG"
    )

    result = await agent_system.query(
        "Explain the difference between IEC 61215 and IEC 61730"
    )

    print(f"Response: {result['response'][:300]}...")
    print(f"Configuration used:")
    print(f"  - Model: {custom_config.default_model}")
    print(f"  - Temperature: {custom_config.agent_temperature}")


async def detailed_response_analysis():
    """Example showing detailed response analysis"""
    print("\n" + "="*80)
    print("Example: Detailed Response Analysis")
    print("="*80)

    agent_system = SolarPVMultiAgent(log_level="INFO")

    result = await agent_system.query(
        "What are the common causes of underperformance in solar PV systems?"
    )

    print(f"Query: What are common causes of underperformance?")
    print(f"\nRouting Information:")
    if 'routing_info' in result:
        routing = result['routing_info']
        print(f"  - Primary Agents: {routing.get('primary_agents', [])}")
        print(f"  - Collaboration Required: {routing.get('requires_collaboration', False)}")
        print(f"  - Routing Confidence: {routing.get('confidence', 0):.2f}")
        print(f"  - Task Type: {routing.get('task_type', 'unknown')}")

    print(f"\nAgent Details:")
    if 'agent_details' in result:
        for detail in result['agent_details']:
            print(f"  - {detail['agent_type']}:")
            print(f"      Confidence: {detail['confidence']:.2f}")
            if detail.get('reasoning'):
                print(f"      Reasoning: {detail['reasoning'][:100]}...")

    print(f"\nExecution Metrics:")
    print(f"  - Total Agents Used: {len(result.get('agents_used', []))}")
    print(f"  - Execution Time: {result.get('execution_time', 0):.2f}s")

    print(f"\nFinal Response:")
    print(f"{result['response'][:500]}...")


async def error_handling_example():
    """Example showing error handling"""
    print("\n" + "="*80)
    print("Example: Error Handling")
    print("="*80)

    agent_system = SolarPVMultiAgent(log_level="ERROR")

    # Test with various edge cases
    test_cases = [
        "",  # Empty query
        "What is the weather today?",  # Off-topic query
        "Tell me about solar " * 100,  # Very long query
    ]

    for i, query in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Query: {query[:50]}..." if len(query) > 50 else f"Query: '{query}'")

        try:
            result = await agent_system.query(query)

            if 'error' in result:
                print(f"Error handled gracefully: {result['error']}")
            else:
                print(f"Response received (agents: {len(result.get('agents_used', []))})")
                print(f"Response preview: {result['response'][:100]}...")

        except Exception as e:
            print(f"Exception caught: {type(e).__name__}: {str(e)}")


async def multi_query_batch():
    """Example of processing multiple queries"""
    print("\n" + "="*80)
    print("Example: Batch Query Processing")
    print("="*80)

    agent_system = SolarPVMultiAgent(log_level="WARNING")

    queries = [
        "What is IEC 61215?",
        "How do I test PV modules?",
        "What is performance ratio?",
        "What are soiling losses?",
        "How to commission a solar system?"
    ]

    print(f"Processing {len(queries)} queries...")

    # Process queries sequentially
    results = []
    for query in queries:
        result = await agent_system.query(query)
        results.append(result)

    # Analyze results
    print("\nResults Summary:")
    for i, (query, result) in enumerate(zip(queries, results), 1):
        print(f"\n{i}. {query}")
        print(f"   Agents: {', '.join(result.get('agents_used', []))}")
        print(f"   Time: {result.get('execution_time', 0):.2f}s")
        print(f"   Response length: {len(result.get('response', ''))} chars")

    total_time = sum(r.get('execution_time', 0) for r in results)
    print(f"\nTotal Processing Time: {total_time:.2f}s")
    print(f"Average Time per Query: {total_time / len(queries):.2f}s")


async def agent_comparison():
    """Compare responses from different agents for the same query"""
    print("\n" + "="*80)
    print("Example: Agent Response Comparison")
    print("="*80)

    agent_system = SolarPVMultiAgent(log_level="WARNING")

    query = "What standards apply to solar module testing?"

    # Get responses from each agent type
    agent_types = ["iec_standards_expert", "testing_specialist", "performance_analyst"]

    print(f"Query: {query}\n")

    for agent_type in agent_types:
        result = await agent_system.query_specific_agent(agent_type, query)

        if result:
            print(f"{agent_type}:")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Response: {result['response'][:200]}...")
            print()


async def main():
    """Run all advanced examples"""

    examples = [
        ("Custom Configuration", custom_configuration_example),
        ("Detailed Response Analysis", detailed_response_analysis),
        ("Error Handling", error_handling_example),
        ("Batch Query Processing", multi_query_batch),
        ("Agent Comparison", agent_comparison),
    ]

    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\nError in {name}: {type(e).__name__}: {str(e)}")

        print("\n" + "-"*80)


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              Solar PV Multi-Agent System - Advanced Usage                  ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())

    print("\nAdvanced examples completed!")

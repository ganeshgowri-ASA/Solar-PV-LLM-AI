"""
Basic usage example for Solar PV Multi-Agent System

This example demonstrates how to:
1. Initialize the multi-agent system
2. Submit queries
3. Access different types of responses
"""

import asyncio
from src.api import SolarPVMultiAgent


async def main():
    """Run basic usage examples"""

    # Initialize the multi-agent system
    print("Initializing Solar PV Multi-Agent System...")
    agent_system = SolarPVMultiAgent(log_level="INFO")

    # Get system information
    print("\n" + "="*80)
    print("System Information:")
    print("="*80)
    info = agent_system.get_system_info()
    print(f"Total Agents: {info['total_agents']}")
    print(f"Agent Types: {', '.join(info['agent_types'])}")
    print(f"Model: {info['model']}")

    # Example 1: IEC Standards Query
    print("\n" + "="*80)
    print("Example 1: IEC Standards Query")
    print("="*80)
    result1 = await agent_system.query(
        "What are the key requirements of IEC 61215 for PV module testing?"
    )
    print(f"Question: What are the key requirements of IEC 61215?")
    print(f"Agents Used: {', '.join(result1['agents_used'])}")
    print(f"Response:\n{result1['response'][:500]}...")  # First 500 chars
    print(f"Execution Time: {result1['execution_time']:.2f}s")

    # Example 2: Testing Query
    print("\n" + "="*80)
    print("Example 2: Testing Specialist Query")
    print("="*80)
    result2 = await agent_system.query(
        "How do I perform flash testing on solar panels?"
    )
    print(f"Question: How do I perform flash testing?")
    print(f"Agents Used: {', '.join(result2['agents_used'])}")
    print(f"Response:\n{result2['response'][:500]}...")
    print(f"Execution Time: {result2['execution_time']:.2f}s")

    # Example 3: Performance Query
    print("\n" + "="*80)
    print("Example 3: Performance Analysis Query")
    print("="*80)
    result3 = await agent_system.query(
        "What is a good performance ratio for a solar PV system and how is it calculated?"
    )
    print(f"Question: What is a good performance ratio?")
    print(f"Agents Used: {', '.join(result3['agents_used'])}")
    print(f"Response:\n{result3['response'][:500]}...")
    print(f"Execution Time: {result3['execution_time']:.2f}s")

    # Example 4: Multi-Agent Collaboration
    print("\n" + "="*80)
    print("Example 4: Multi-Agent Collaborative Query")
    print("="*80)
    result4 = await agent_system.query(
        "What IEC standards apply to performance testing of PV modules, "
        "and what are the specific test procedures?"
    )
    print(f"Question: IEC standards for performance testing")
    print(f"Agents Used: {', '.join(result4['agents_used'])}")
    print(f"Collaboration Required: {len(result4['agents_used']) > 1}")
    print(f"Response:\n{result4['response'][:500]}...")
    print(f"Execution Time: {result4['execution_time']:.2f}s")

    # Example 5: Query Specific Agent
    print("\n" + "="*80)
    print("Example 5: Query Specific Agent Directly")
    print("="*80)
    result5 = await agent_system.query_specific_agent(
        agent_type="iec_standards_expert",
        question="What is IEC 61730?"
    )
    if result5:
        print(f"Agent: {result5['agent_type']}")
        print(f"Confidence: {result5['confidence']:.2f}")
        print(f"Response:\n{result5['response'][:500]}...")

    # Get agent capabilities
    print("\n" + "="*80)
    print("Agent Capabilities:")
    print("="*80)
    capabilities = await agent_system.get_capabilities()
    for agent_id, cap in capabilities.items():
        print(f"\n{agent_id} ({cap['agent_type']}):")
        print(f"  Description: {cap['description'][:100]}...")
        print(f"  Keywords: {', '.join(cap['keywords'][:5])}...")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                Solar PV Multi-Agent System - Basic Usage                   ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # Run the async main function
    asyncio.run(main())

    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80)

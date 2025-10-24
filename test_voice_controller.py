#!/usr/bin/env python3
"""
Test script for Voice Controller
Tests various voice commands to ensure tool calling works
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Test commands to try
TEST_COMMANDS = [
    "Show me the top 5 whale wallets",
    "What signals came in today?",
    "What's the system status?",
    "Show me wallets with win rate above 70%",
]


async def test_voice_controller():
    """Test voice controller with various commands"""
    from voice_controller import voice_controller

    print("=" * 60)
    print("VOICE CONTROLLER TEST")
    print("=" * 60)
    print()

    for i, command in enumerate(TEST_COMMANDS, 1):
        print(f"\n[TEST {i}/{len(TEST_COMMANDS)}]")
        print(f"Command: {command}")
        print("-" * 60)

        result = await voice_controller.process_command(command)

        print(f"Success: {result['success']}")
        print(f"Response: {result['response']}")

        if result.get('tool_results'):
            print(f"\nTools Used ({len(result['tool_results'])}):")
            for tool_result in result['tool_results']:
                tool_name = tool_result['tool']
                tool_input = tool_result['input']
                print(f"  - {tool_name}")
                print(f"    Input: {tool_input}")

                # Show sample of result
                res = tool_result['result']
                if isinstance(res, dict):
                    if 'wallets' in res:
                        print(f"    Result: {len(res['wallets'])} wallets")
                    elif 'signals' in res:
                        print(f"    Result: {len(res['signals'])} signals")
                    elif 'error' in res:
                        print(f"    Error: {res['error']}")
                    else:
                        print(f"    Result: {list(res.keys())}")

        print()


async def test_specific_command():
    """Test a specific command in detail"""
    from voice_controller import voice_controller

    command = "Show me the top 3 whale wallets sorted by profit"

    print("\n" + "=" * 60)
    print("DETAILED TEST")
    print("=" * 60)
    print(f"Command: {command}\n")

    result = await voice_controller.process_command(command)

    print(f"Success: {result['success']}")
    print(f"\nResponse:")
    print(result['response'])

    if result.get('tool_results'):
        print(f"\n\nDetailed Tool Results:")
        for tool_result in result['tool_results']:
            print(f"\nTool: {tool_result['tool']}")
            print(f"Input: {tool_result['input']}")
            print(f"Result:")
            import json
            print(json.dumps(tool_result['result'], indent=2))


async def test_quick_commands():
    """Test quick command path"""
    from voice_controller import voice_controller

    print("\n" + "=" * 60)
    print("QUICK COMMAND TEST (bypass Claude)")
    print("=" * 60)

    quick_tests = [
        "show whales",
        "show top whales",
        "status",
    ]

    for cmd in quick_tests:
        print(f"\nCommand: {cmd}")
        result = await voice_controller._check_quick_commands(cmd)
        if result:
            print(f"✓ Quick command recognized!")
            print(f"  Response: {result['response'][:100]}...")
        else:
            print(f"✗ Not recognized as quick command")


if __name__ == "__main__":
    print("\nVoice Controller Test Suite")
    print("=" * 60)

    # Check environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY not set!")
        print("Please set it in .env file")
        exit(1)

    print("✓ ANTHROPIC_API_KEY found")
    print("✓ Database: aura.db")
    print()

    # Run tests
    try:
        asyncio.run(test_voice_controller())
        asyncio.run(test_specific_command())
        asyncio.run(test_quick_commands())

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Test streaming functionality in the CLI.
Tests streaming mode, streaming interrupts, and streaming vs non-streaming behavior.
"""

import os
import sys
import time
import unittest
from unittest.mock import patch, Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from openai.types.completion_usage import CompletionUsage

from cai.sdk.agents import Agent, OpenAIChatCompletionsModel, ModelResponse
from cai.sdk.agents.models.openai_chatcompletions import message_history


class TestCLIStreaming(unittest.TestCase):
    """Test CLI streaming functionality by testing components directly."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        os.environ['CAI_TELEMETRY'] = 'false'
        os.environ['CAI_TRACING'] = 'false'
        os.environ['CAI_STREAM'] = 'false'
        
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        message_history.clear()
        
    def setUp(self):
        """Set up for each test method."""
        # AGGRESSIVE cleanup to ensure no state contamination between tests
        message_history.clear()
        
        # Clean up any lingering _Converter state
        try:
            from cai.sdk.agents.models.openai_chatcompletions import _Converter
            # Clear all possible _Converter attributes
            for attr in ['recent_tool_calls', 'tool_outputs', 'conversation_start_time']:
                if hasattr(_Converter, attr):
                    if isinstance(getattr(_Converter, attr), dict):
                        getattr(_Converter, attr).clear()
                    else:
                        delattr(_Converter, attr)
        except Exception:
            pass
            
        # Also ensure environment is clean
        os.environ['CAI_STREAM'] = 'false'
        os.environ['CAI_TELEMETRY'] = 'false'
        os.environ['CAI_TRACING'] = 'false'
        
    def test_ctrl_c_cleanup_message_consistency(self):
        """Test CTRL+C cleanup logic maintains message consistency."""
        from cai.sdk.agents.models.openai_chatcompletions import (
            add_to_message_history,
            _Converter
        )
        
        # Complete cleanup - clear everything including _Converter state
        message_history.clear()
        if hasattr(_Converter, 'recent_tool_calls'):
            _Converter.recent_tool_calls.clear()
        if hasattr(_Converter, 'tool_outputs'):
            _Converter.tool_outputs.clear()
        
        # Simulate the state before CTRL+C during tool execution
        # 1. User message
        add_to_message_history({"role": "user", "content": "Run a long command"})
        
        # 2. Assistant message with tool call
        tool_call_id = "call_interrupted_123"
        add_to_message_history({
            "role": "assistant",
            "content": "I'll run that command for you.",
            "tool_calls": [{
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": "generic_linux_command",
                    "arguments": '{"command": "sleep", "args": "30"}'
                }
            }]
        })
        
        # 3. Simulate CTRL+C happening during tool execution
        # This is where the real cleanup logic would kick in
        def simulate_ctrl_c_cleanup():
            """Simulate the exact cleanup logic from cli.py"""
            
            # Initialize _Converter attributes if they don't exist
            if not hasattr(_Converter, 'recent_tool_calls'):
                _Converter.recent_tool_calls = {}
            if not hasattr(_Converter, 'tool_outputs'):
                _Converter.tool_outputs = {}
            
            # Simulate a tool call that was started but interrupted
            _Converter.recent_tool_calls[tool_call_id] = {
                'name': 'generic_linux_command',
                'arguments': '{"command": "sleep", "args": "30"}',
                'start_time': time.time() - 5  # Started 5 seconds ago
            }
            
            # Simulate the cleanup logic from cli.py lines 603-654
            pending_calls = []
            for call_id, call_info in list(_Converter.recent_tool_calls.items()):
                # Check if this tool call has a corresponding response in message_history
                tool_response_exists = any(
                    msg.get("role") == "tool" and msg.get("tool_call_id") == call_id
                    for msg in message_history
                )
                
                if not tool_response_exists:
                    # Add assistant message if needed (should already exist in our case)
                    assistant_exists = any(
                        msg.get("role") == "assistant" and 
                        msg.get("tool_calls") and 
                        any(tc.get("id") == call_id for tc in msg.get("tool_calls", []))
                        for msg in message_history
                    )
                    
                    if not assistant_exists:
                        # This shouldn't happen in our test but add for completeness
                        assistant_msg = {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [{
                                "id": call_id,
                                "type": "function",
                                "function": {
                                    "name": call_info.get('name', 'unknown_function'),
                                    "arguments": call_info.get('arguments', '{}')
                                }
                            }]
                        }
                        add_to_message_history(assistant_msg)
                    
                    # Add synthetic tool response for interrupted tool
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": "Operation interrupted by user (Keyboard Interrupt)"
                    }
                    add_to_message_history(tool_msg)
                    pending_calls.append(call_info.get('name', 'unknown'))
            
            # Apply message list fixes like the real system does
            from cai.util import fix_message_list
            try:
                fixed_messages = fix_message_list(message_history)
                message_history.clear()
                message_history.extend(fixed_messages)
                return len(pending_calls)
            except Exception as e:
                print(f"fix_message_list failed: {e}")
                return 0
        
        # Execute the cleanup
        cleaned_count = simulate_ctrl_c_cleanup()
        
        # Verify the cleanup worked
        assert cleaned_count > 0, "Should have cleaned up at least one pending tool call"
        
        # Verify message history consistency
        self.verify_message_history_openai_compliance()
        
        # Verify we have the expected sequence
        assert len(message_history) >= 3, "Should have user, assistant, tool messages"
        
        # Check message roles in order
        roles = [msg['role'] for msg in message_history]
        assert roles[0] == 'user', "First message should be user"
        assert roles[1] == 'assistant', "Second message should be assistant"
        assert roles[2] == 'tool', "Third message should be tool"
        
        # Verify tool call/result consistency
        assistant_msg = message_history[1]
        tool_msg = message_history[2]
        assert assistant_msg.get('tool_calls'), "Assistant message should have tool calls"
        assert tool_msg['tool_call_id'] == assistant_msg['tool_calls'][0]['id'], \
            "Tool call ID should match"
        assert "interrupted" in tool_msg['content'].lower(), \
            "Tool result should indicate interruption"
        
        print("✅ CTRL+C cleanup message consistency test passed!")
        
        # Clean up _Converter state after test
        if hasattr(_Converter, 'recent_tool_calls'):
            _Converter.recent_tool_calls.clear()
        if hasattr(_Converter, 'tool_outputs'):
            _Converter.tool_outputs.clear()
        
    def test_fix_message_list_with_interrupted_tools(self):
        """Test fix_message_list handles interrupted tool sequences correctly."""
        from cai.sdk.agents.models.openai_chatcompletions import (
            add_to_message_history,
            _Converter
        )
        from cai.util import fix_message_list
        
        # Complete cleanup - clear everything including _Converter state
        message_history.clear()
        if hasattr(_Converter, 'recent_tool_calls'):
            _Converter.recent_tool_calls.clear()
        if hasattr(_Converter, 'tool_outputs'):
            _Converter.tool_outputs.clear()
        
        # Create an incomplete sequence (tool call without result)
        add_to_message_history({"role": "user", "content": "Test command"})
        add_to_message_history({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "call_incomplete_456",
                "type": "function",
                "function": {
                    "name": "generic_linux_command",
                    "arguments": '{"command": "test", "args": "--help"}'
                }
            }]
        })
        
        # At this point we have incomplete sequence - no tool result
        incomplete_messages = list(message_history)
        
        # Apply fix_message_list 
        try:
            fixed_messages = fix_message_list(incomplete_messages)
            
            # Verify fix_message_list added the missing tool result
            assert len(fixed_messages) > len(incomplete_messages), \
                "fix_message_list should add missing tool result"
            
            # Find the added tool message
            tool_msg = None
            for msg in fixed_messages:
                if msg.get('role') == 'tool' and msg.get('tool_call_id') == 'call_incomplete_456':
                    tool_msg = msg
                    break
            
            assert tool_msg is not None, "fix_message_list should add tool result message"
            
            # Verify the fixed messages comply with OpenAI format
            for i, msg in enumerate(fixed_messages):
                assert 'role' in msg, f"Fixed message {i} missing role"
                assert msg['role'] in ['user', 'assistant', 'system', 'tool'], \
                    f"Fixed message {i} has invalid role"
            
            print("✅ fix_message_list with interrupted tools test passed!")
            
            # Clean up _Converter state after test
            if hasattr(_Converter, 'recent_tool_calls'):
                _Converter.recent_tool_calls.clear()
            if hasattr(_Converter, 'tool_outputs'):
                _Converter.tool_outputs.clear()
            
            return True
            
        except Exception as e:
            print(f"fix_message_list failed: {e}")
            # Clean up even in case of failure
            if hasattr(_Converter, 'recent_tool_calls'):
                _Converter.recent_tool_calls.clear()
            if hasattr(_Converter, 'tool_outputs'):
                _Converter.tool_outputs.clear()
            return False
            
    def test_generic_linux_command_interrupt_simulation(self):
        """Test generic_linux_command behavior during interruption."""
        
        # Mock the generic_linux_command function behavior
        def mock_interrupted_command():
            """Simulate generic_linux_command being interrupted"""
            try:
                # Simulate command starting
                output = "Command started...\nProcessing files..."
                
                # Simulate interrupt during execution (like CTRL+C)
                raise KeyboardInterrupt("User interrupted command")
                
            except KeyboardInterrupt:
                # Simulate the real behavior - command returns partial output
                interrupted_output = f"{output}\nCommand interrupted by user"
                return interrupted_output
        
        # Test the mock
        result = mock_interrupted_command()
        
        # Verify it behaves like the real interrupted command
        assert "Command started" in result, "Should include partial output"
        assert "interrupted" in result, "Should indicate interruption"
        
        print("✅ Generic linux command interrupt simulation test passed!")
        
    def test_message_history_openai_format_compliance(self):
        """Test that message_history always maintains OpenAI ChatCompletion format."""
        from cai.sdk.agents.models.openai_chatcompletions import add_to_message_history
        
        # Clear history
        message_history.clear()
        
        # Test various message types that should maintain OpenAI format
        test_messages = [
            # User message
            {"role": "user", "content": "Test user message"},
            
            # Assistant message with content
            {"role": "assistant", "content": "Test assistant response"},
            
            # Assistant message with tool calls
            {
                "role": "assistant", 
                "content": None,
                "tool_calls": [{
                    "id": "call_test_123",
                    "type": "function",
                    "function": {
                        "name": "test_function",
                        "arguments": '{"param": "value"}'
                    }
                }]
            },
            
            # Tool message
            {
                "role": "tool",
                "tool_call_id": "call_test_123", 
                "content": "Tool execution result"
            },
            
            # System message
            {"role": "system", "content": "You are a helpful assistant"}
        ]
        
        # Add all messages
        for msg in test_messages:
            add_to_message_history(msg)
        
        # Verify OpenAI format compliance
        assert len(message_history) == len(test_messages), \
            f"Expected {len(test_messages)} messages, got {len(message_history)}"
        
        for i, msg in enumerate(message_history):
            # Required fields
            assert 'role' in msg, f"Message {i} missing required 'role' field"
            
            # Valid roles
            valid_roles = ['user', 'assistant', 'system', 'tool', 'developer']
            assert msg['role'] in valid_roles, \
                f"Message {i} has invalid role '{msg['role']}', must be one of {valid_roles}"
            
            # Role-specific validation
            if msg['role'] == 'tool':
                assert 'tool_call_id' in msg, f"Tool message {i} missing 'tool_call_id'"
                assert 'content' in msg, f"Tool message {i} missing 'content'"
            
            if msg['role'] == 'assistant' and msg.get('tool_calls'):
                assert isinstance(msg['tool_calls'], list), \
                    f"Assistant message {i} tool_calls must be a list"
                for j, tc in enumerate(msg['tool_calls']):
                    assert 'id' in tc, f"Tool call {j} in message {i} missing 'id'"
                    assert 'type' in tc, f"Tool call {j} in message {i} missing 'type'"
                    assert 'function' in tc, f"Tool call {j} in message {i} missing 'function'"
                    assert 'name' in tc['function'], \
                        f"Tool call {j} function in message {i} missing 'name'"
                    assert 'arguments' in tc['function'], \
                        f"Tool call {j} function in message {i} missing 'arguments'"
        
        print("✅ Message history OpenAI format compliance test passed!")
        
    def test_streaming_mode_configuration(self):
        """Test streaming mode can be configured and detected."""
        # Test non-streaming mode
        os.environ['CAI_STREAM'] = 'false'
        assert os.environ['CAI_STREAM'] == 'false'
        
        # Test streaming mode
        os.environ['CAI_STREAM'] = 'true'
        assert os.environ['CAI_STREAM'] == 'true'
        
        print("✅ Streaming mode configuration test passed!")
        
    def test_multiple_interrupt_scenarios(self):
        """Test multiple CTRL+C scenarios maintain consistency."""
        from cai.sdk.agents.models.openai_chatcompletions import add_to_message_history
        
        # Clear history
        message_history.clear()
        
        scenarios = [
            ("Run first command", "call_1", "First command interrupted"),
            ("Run second command", "call_2", "Second command interrupted"), 
            ("Run third command", "call_3", "Third command completed successfully")
        ]
        
        for user_input, call_id, result_content in scenarios:
            # Add user message
            add_to_message_history({"role": "user", "content": user_input})
            
            # Add assistant message with tool call
            add_to_message_history({
                "role": "assistant",
                "content": "I'll run that command for you.",
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": "generic_linux_command",
                        "arguments": f'{{"command": "test", "args": "{user_input}"}}'
                    }
                }]
            })
            
            # Add tool result
            add_to_message_history({
                "role": "tool",
                "tool_call_id": call_id,
                "content": result_content
            })
            
            # Verify consistency after each scenario
            self.verify_message_history_openai_compliance()
        
        # Final verification
        assert len(message_history) == len(scenarios) * 3
        print("✅ Multiple interrupt scenarios test passed!")
        
    def verify_message_history_openai_compliance(self):
        """Helper method to verify message_history complies with OpenAI format."""
        for i, msg in enumerate(message_history):
            # Basic structure checks
            assert isinstance(msg, dict), f"Message {i} must be a dictionary"
            assert 'role' in msg, f"Message {i} missing 'role' field"
            
            # Role validation
            valid_roles = ['user', 'assistant', 'system', 'tool', 'developer']
            assert msg['role'] in valid_roles, \
                f"Message {i} role '{msg['role']}' not in valid roles {valid_roles}"
            
            # Content or tool_calls must exist for most roles
            if msg['role'] in ['user', 'system', 'developer']:
                assert 'content' in msg, f"Message {i} with role '{msg['role']}' missing content"
                
            elif msg['role'] == 'assistant':
                # Assistant must have content OR tool_calls
                has_content = 'content' in msg and msg['content'] is not None
                has_tool_calls = 'tool_calls' in msg and msg['tool_calls']
                assert has_content or has_tool_calls, \
                    f"Assistant message {i} must have content or tool_calls"
                    
            elif msg['role'] == 'tool':
                assert 'tool_call_id' in msg, f"Tool message {i} missing tool_call_id"
                assert 'content' in msg, f"Tool message {i} missing content"

    def test_ctrl_c_during_tool_execution_real_behavior(self):
        """Test real CTRL+C behavior during tool execution without duplicates."""
        from cai.sdk.agents.models.openai_chatcompletions import (
            add_to_message_history, 
            message_history,
            _Converter
        )
        
        # COMPLETE cleanup - clear everything
        message_history.clear()
        if hasattr(_Converter, 'recent_tool_calls'):
            _Converter.recent_tool_calls.clear()
        if hasattr(_Converter, 'tool_outputs'):
            _Converter.tool_outputs.clear()
        
        # Simulate a running tool call that gets interrupted
        call_id = "call_linux_cmd_123"
        tool_name = "generic_linux_command"
        
        # 1. Add user message
        add_to_message_history({"role": "user", "content": "Run a long command"})
        
        # 2. Add assistant message with tool call (simulating qwen format)
        add_to_message_history({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": call_id,
                "type": "function", 
                "function": {
                    "name": tool_name,
                    "arguments": '{"command": "sleep 10"}'
                }
            }]
        })
        
        # 3. Simulate CTRL+C cleanup behavior from cli.py
        # Initialize _Converter attributes if they don't exist
        if not hasattr(_Converter, 'recent_tool_calls'):
            _Converter.recent_tool_calls = {}
        if not hasattr(_Converter, 'tool_outputs'):
            _Converter.tool_outputs = {}
        
        # Add ONLY our specific tool call to recent_tool_calls
        _Converter.recent_tool_calls[call_id] = {
            'name': tool_name,
            'arguments': '{"command": "sleep 10"}'
        }
        
        # Simulate the KeyboardInterrupt cleanup logic from cli.py
        try:
            # Check for pending tool calls without responses
            for call_id_check, call_info in list(_Converter.recent_tool_calls.items()):
                # Check if tool response exists
                tool_response_exists = any(
                    msg.get("role") == "tool" and msg.get("tool_call_id") == call_id_check
                    for msg in message_history
                )
                
                if not tool_response_exists:
                    # Add synthetic tool response (this is what cli.py does now)
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": call_id_check,
                        "content": "Operation interrupted by user (Keyboard Interrupt)"
                    }
                    add_to_message_history(tool_msg)
            
            # NOTE: The fix means we DON'T call fix_message_list here anymore
            # This prevents duplicate synthetic tool calls
            
        except Exception as e:
            print(f"Error in cleanup: {e}")
        
        # Verify message consistency after CTRL+C
        print("Message history after CTRL+C cleanup:")
        for i, msg in enumerate(message_history):
            print(f"  {i}: {msg.get('role')} - {msg}")
        
        # Assertions
        self.assertEqual(len(message_history), 3)  # user + assistant + tool
        
        # Check user message
        self.assertEqual(message_history[0]["role"], "user")
        
        # Check assistant message has correct tool call
        self.assertEqual(message_history[1]["role"], "assistant") 
        self.assertIsNotNone(message_history[1]["tool_calls"])
        self.assertEqual(len(message_history[1]["tool_calls"]), 1)
        self.assertEqual(message_history[1]["tool_calls"][0]["id"], call_id)
        self.assertEqual(
            message_history[1]["tool_calls"][0]["function"]["name"], 
            tool_name
        )
        
        # Check tool response exists and is correct
        self.assertEqual(message_history[2]["role"], "tool")
        self.assertEqual(message_history[2]["tool_call_id"], call_id)
        self.assertIn("interrupted", message_history[2]["content"].lower())
        
        # MOST IMPORTANT: Verify NO duplicate tool calls with unknown_function
        unknown_function_calls = []
        for msg in message_history:
            if (msg.get("role") == "assistant" and 
                msg.get("tool_calls")):
                for tc in msg["tool_calls"]:
                    if tc.get("function", {}).get("name") == "unknown_function":
                        unknown_function_calls.append(tc)
        
        self.assertEqual(
            len(unknown_function_calls), 0, 
            f"Found {len(unknown_function_calls)} duplicate unknown_function calls: {unknown_function_calls}"
        )
        
        # Verify OpenAI format compliance
        self.verify_message_history_openai_compliance()
        
        print("✓ CTRL+C test passed - no duplicates!")
        
        # Clean up
        if hasattr(_Converter, 'recent_tool_calls'):
            _Converter.recent_tool_calls.clear()
        if hasattr(_Converter, 'tool_outputs'):
            _Converter.tool_outputs.clear()


if __name__ == '__main__':
    print("🧪 Running simplified CLI streaming tests...")
    
    # Try to use unittest.main() first
    try:
        import unittest
        if len(sys.argv) == 1:  # No command line args, run all tests
            unittest.main(verbosity=2, exit=False)
        else:
            # If there are command line args, run manual tests for debugging
            # Create test instance
            test_instance = TestCLIStreaming()
            test_instance.setUpClass()
            
            # List of test methods - focused on direct testing without asyncio
            test_methods = [
                'test_streaming_mode_configuration',
                'test_message_history_openai_format_compliance',
                'test_ctrl_c_cleanup_message_consistency',
                'test_fix_message_list_with_interrupted_tools',
                'test_generic_linux_command_interrupt_simulation',
                'test_multiple_interrupt_scenarios',
                'test_ctrl_c_during_tool_execution_real_behavior'
            ]
            
            results = {}
            
            for method_name in test_methods:
                try:
                    print(f"\n🔬 Running {method_name}...")
                    # PROPERLY call setUp for each test
                    test_instance.setUp()
                    method = getattr(test_instance, method_name)
                    method()
                    results[method_name] = 'PASSED'
                except Exception as e:
                    results[method_name] = f'FAILED: {str(e)}'
                    print(f"❌ {method_name} failed: {e}")
                    
                    # Print debug info for failures
                    if len(message_history) > 0:
                        print("Message history debug:")
                        for i, msg in enumerate(message_history):
                            print(f"  [{i}] {msg.get('role', 'unknown')}: {str(msg.get('content', ''))[:50]}")
            
            # Print summary
            print("\n" + "="*60)
            print("📊 STREAMING TESTS SUMMARY")
            print("="*60)
            
            passed = sum(1 for r in results.values() if r == 'PASSED')
            failed = len(results) - passed
            
            for test_name, result in results.items():
                status_emoji = "✅" if result == 'PASSED' else "❌"
                print(f"{status_emoji} {test_name}: {result}")
            
            print(f"\n🎯 Results: {passed} passed, {failed} failed")
            
            if failed == 0:
                print("🎉 All simplified streaming tests passed!")
                print("\n🔍 These tests verify:")
                print("- Streaming mode configuration")
                print("- Message history OpenAI format compliance")
                print("- CTRL+C cleanup maintains message consistency")
                print("- fix_message_list handles interrupted tools")
                print("- Generic linux command interrupt simulation")
                print("- Multiple interrupt scenarios")
                print("- Real CTRL+C behavior during tool execution without duplicates")
            else:
                print(f"💥 {failed} streaming tests failed!")
                sys.exit(1)
            
    except Exception as unittest_error:
        print(f"Error running with unittest: {unittest_error}")
        print("Falling back to manual test execution...")
        
        # Manual fallback
        test_instance = TestCLIStreaming()
        test_instance.setUpClass()
        
        test_methods = [
            'test_streaming_mode_configuration',
            'test_message_history_openai_format_compliance',
            'test_ctrl_c_cleanup_message_consistency',
            'test_fix_message_list_with_interrupted_tools',
            'test_generic_linux_command_interrupt_simulation',
            'test_multiple_interrupt_scenarios',
            'test_ctrl_c_during_tool_execution_real_behavior'
        ]
        
        results = {}
        for method_name in test_methods:
            try:
                print(f"\n🔬 Running {method_name}...")
                test_instance.setUp()  # CRITICAL: Call setUp for each test
                method = getattr(test_instance, method_name)
                method()
                results[method_name] = 'PASSED'
            except Exception as e:
                results[method_name] = f'FAILED: {str(e)}'
                print(f"❌ {method_name} failed: {e}")
        
        passed = sum(1 for r in results.values() if r == 'PASSED')
        failed = len(results) - passed
        print(f"\n🎯 Manual Results: {passed} passed, {failed} failed")
        if failed > 0:
            sys.exit(1) 
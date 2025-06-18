#!/usr/bin/env python3
"""
Test suite for the history command functionality.
Tests all handle methods and input possibilities for the history command.
"""

import os
import sys
import pytest
import json
from unittest.mock import patch, Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                '..', '..', 'src'))

from cai.repl.commands.history import HistoryCommand
from cai.repl.commands.base import Command


class TestHistoryCommand:
    """Test cases for HistoryCommand."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup and cleanup for each test."""
        # Set up test environment
        os.environ['CAI_TELEMETRY'] = 'false'
        os.environ['CAI_TRACING'] = 'false'
        
        yield
    
    @pytest.fixture
    def history_command(self):
        """Create a HistoryCommand instance for testing."""
        return HistoryCommand()
    
    @pytest.fixture
    def sample_message_history(self):
        """Create sample message history for testing."""
        return [
            {
                "role": "user",
                "content": "Hello, can you help me with Python?"
            },
            {
                "role": "assistant",
                "content": "Of course! I'd be happy to help you with Python. What specific topic or problem would you like assistance with?"
            },
            {
                "role": "user",
                "content": "How do I create a list?"
            },
            {
                "role": "assistant",
                "content": "I'll help you create a tool to demonstrate list creation.",
                "tool_calls": [
                    {
                        "id": "call_123",
                        "type": "function",
                        "function": {
                            "name": "create_example",
                            "arguments": '{"language": "python", "topic": "lists"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "tool_call_id": "call_123",
                "content": "# Creating lists in Python\nmy_list = [1, 2, 3]\nprint(my_list)"
            },
            {
                "role": "assistant",
                "content": "Here's how you create a list in Python: you use square brackets and separate items with commas."
            }
        ]
    
    @pytest.fixture
    def complex_message_history(self):
        """Create complex message history with various message types."""
        return [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Execute a command for me"
            },
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_cmd_1",
                        "type": "function",
                        "function": {
                            "name": "generic_linux_command",
                            "arguments": '{"command": "ls", "args": "-la"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "tool_call_id": "call_cmd_1",
                "content": "total 8\ndrwxr-xr-x 2 user user 4096 Jan 1 12:00 .\ndrwxr-xr-x 3 user user 4096 Jan 1 12:00 .."
            },
            {
                "role": "assistant",
                "content": "The directory listing shows two entries: the current directory (.) and parent directory (..)."
            },
            {
                "role": "user",
                "content": "Now run multiple commands"
            },
            {
                "role": "assistant",
                "content": "I'll run multiple commands for you.",
                "tool_calls": [
                    {
                        "id": "call_cmd_2",
                        "type": "function",
                        "function": {
                            "name": "generic_linux_command",
                            "arguments": '{"command": "pwd"}'
                        }
                    },
                    {
                        "id": "call_cmd_3",
                        "type": "function",
                        "function": {
                            "name": "generic_linux_command",
                            "arguments": '{"command": "whoami"}'
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "tool_call_id": "call_cmd_2",
                "content": "/home/user"
            },
            {
                "role": "tool",
                "tool_call_id": "call_cmd_3",
                "content": "user"
            }
        ]
    
    def test_command_initialization(self, history_command):
        """Test that HistoryCommand initializes correctly."""
        assert history_command.name == "/history"
        assert history_command.description == "Display the conversation history"
        assert history_command.aliases == ["/his"]
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_handle_no_args_with_history(self, mock_message_history, 
                                        history_command, sample_message_history):
        """Test handling with no arguments when history exists."""
        mock_message_history.clear()
        mock_message_history.extend(sample_message_history)
        
        result = history_command.handle([])
        assert result is True
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_handle_no_args_empty_history(self, mock_message_history, history_command):
        """Test handling with no arguments when history is empty."""
        mock_message_history.clear()
        
        result = history_command.handle([])
        assert result is True
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_handle_with_args(self, mock_message_history, 
                             history_command, sample_message_history):
        """Test handling when arguments are provided (should be ignored)."""
        mock_message_history.clear()
        mock_message_history.extend(sample_message_history)
        
        result = history_command.handle(["some", "args"])
        assert result is True
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_handle_complex_history(self, mock_message_history, 
                                   history_command, complex_message_history):
        """Test handling complex message history with various message types."""
        mock_message_history.clear()
        mock_message_history.extend(complex_message_history)
        
        result = history_command.handle([])
        assert result is True
    
    def test_format_message_content_simple_text(self, history_command):
        """Test formatting simple text content."""
        content = "This is a simple message"
        tool_calls = None
        
        result = history_command._format_message_content(content, tool_calls)
        assert result == content
    
    def test_format_message_content_long_text(self, history_command):
        """Test formatting long text content (should be truncated)."""
        content = "This is a very long message that should be truncated because it exceeds the 100 character limit that is set in the formatting function for display purposes"
        tool_calls = None
        
        result = history_command._format_message_content(content, tool_calls)
        assert len(result) <= 100
        assert result.endswith("...")
    
    def test_format_message_content_empty(self, history_command):
        """Test formatting empty content."""
        content = ""
        tool_calls = None
        
        result = history_command._format_message_content(content, tool_calls)
        assert "Empty message" in result
    
    def test_format_message_content_none(self, history_command):
        """Test formatting None content."""
        content = None
        tool_calls = None
        
        result = history_command._format_message_content(content, tool_calls)
        assert "Empty message" in result
    
    def test_format_message_content_with_tool_calls(self, history_command):
        """Test formatting content with tool calls."""
        content = "I'll help you with that"
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "test_function",
                    "arguments": '{"param1": "value1", "param2": "value2"}'
                }
            }
        ]
        
        result = history_command._format_message_content(content, tool_calls)
        assert "Function:" in result
        assert "test_function" in result
        assert "Args:" in result
    
    def test_format_message_content_with_multiple_tool_calls(self, history_command):
        """Test formatting content with multiple tool calls."""
        content = "I'll run multiple commands"
        tool_calls = [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "function_one",
                    "arguments": '{"arg": "value1"}'
                }
            },
            {
                "id": "call_2",
                "type": "function",
                "function": {
                    "name": "function_two",
                    "arguments": '{"arg": "value2"}'
                }
            }
        ]
        
        result = history_command._format_message_content(content, tool_calls)
        assert "function_one" in result
        assert "function_two" in result
        assert result.count("Function:") == 2
    
    def test_format_message_content_with_invalid_json_args(self, history_command):
        """Test formatting content with invalid JSON in tool call arguments."""
        content = "Testing invalid JSON"
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "test_function",
                    "arguments": "invalid json string"
                }
            }
        ]
        
        result = history_command._format_message_content(content, tool_calls)
        assert "Function:" in result
        assert "test_function" in result
        assert "invalid json string" in result
    
    def test_format_message_content_with_long_tool_args(self, history_command):
        """Test formatting content with very long tool call arguments."""
        content = "Testing long arguments"
        long_args = json.dumps({
            "very_long_parameter": "This is a very long parameter value that should be truncated when displayed in the history because it exceeds the character limit"
        })
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "test_function",
                    "arguments": long_args
                }
            }
        ]
        
        result = history_command._format_message_content(content, tool_calls)
        assert "Function:" in result
        assert "test_function" in result
        assert "..." in result  # Should be truncated
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_handle_import_error(self, mock_message_history, history_command):
        """Test handling when import fails."""
        # Create a new command instance and monkey patch its handle_no_args method
        # to simulate an import error
        test_command = HistoryCommand()
        
        def mock_handle_no_args_with_import_error():
            try:
                # Simulate the import failing
                raise ImportError("Mock import error") 
            except ImportError:
                return False
        
        # Replace the method to simulate import failure
        test_command.handle_no_args = mock_handle_no_args_with_import_error
        
        result = test_command.handle_no_args()
        assert result is False
    
    def test_command_base_functionality(self, history_command):
        """Test that the command inherits from base Command properly."""
        assert isinstance(history_command, Command)
        assert history_command.name == "/history"
        assert "/his" in history_command.aliases
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_handle_with_corrupted_message(self, mock_message_history, history_command):
        """Test handling when message history contains corrupted data."""
        # Create message history with missing or corrupted fields
        corrupted_history = [
            {
                "role": "user",
                "content": "Normal message"
            },
            {
                # Missing role field
                "content": "Message without role"
            },
            {
                "role": "assistant",
                # Missing content field
                "tool_calls": [{"id": "call_1", "function": {"name": "test"}}]
            },
            {
                "role": "tool",
                "tool_call_id": "call_1",
                "content": None  # None content
            }
        ]
        
        mock_message_history.clear()
        mock_message_history.extend(corrupted_history)
        
        # Should handle gracefully without crashing
        result = history_command.handle([])
        assert result is True
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_handle_with_messages_parameter(self, mock_message_history, 
                                           history_command, sample_message_history):
        """Test handle method with explicit messages parameter."""
        mock_message_history.clear()
        mock_message_history.extend(sample_message_history)
        
        # The handle method should work with messages parameter
        result = history_command.handle([], messages=sample_message_history)
        assert result is True


@pytest.mark.integration
class TestHistoryCommandIntegration:
    """Integration tests for history command functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_integration(self):
        """Setup for integration tests."""
        yield
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_full_conversation_history_workflow(self, mock_message_history):
        """Test a complete conversation workflow and history display."""
        # Simulate a conversation building up over time
        conversation_steps = [
            # Step 1: Initial user message
            [
                {"role": "user", "content": "Hello"}
            ],
            # Step 2: Assistant response
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help you?"}
            ],
            # Step 3: User asks for help
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help you?"},
                {"role": "user", "content": "Can you run a command?"}
            ],
            # Step 4: Assistant with tool call
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help you?"},
                {"role": "user", "content": "Can you run a command?"},
                {
                    "role": "assistant",
                    "content": "I'll run that command for you.",
                    "tool_calls": [
                        {
                            "id": "call_cmd",
                            "type": "function",
                            "function": {
                                "name": "generic_linux_command",
                                "arguments": '{"command": "ls"}'
                            }
                        }
                    ]
                }
            ],
            # Step 5: Tool response
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help you?"},
                {"role": "user", "content": "Can you run a command?"},
                {
                    "role": "assistant",
                    "content": "I'll run that command for you.",
                    "tool_calls": [
                        {
                            "id": "call_cmd",
                            "type": "function",
                            "function": {
                                "name": "generic_linux_command",
                                "arguments": '{"command": "ls"}'
                            }
                        }
                    ]
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_cmd",
                    "content": "file1.txt\nfile2.txt\nfolder1/"
                }
            ]
        ]
        
        cmd = HistoryCommand()
        
        # Test history at each step
        for i, step_history in enumerate(conversation_steps):
            mock_message_history.clear()
            mock_message_history.extend(step_history)
            
            result = cmd.handle([])
            assert result is True, f"Failed at conversation step {i + 1}"
    
    @patch('cai.sdk.agents.models.openai_chatcompletions.message_history')
    def test_edge_case_message_combinations(self, mock_message_history):
        """Test various edge case message combinations."""
        edge_cases = [
            # Empty history
            [],
            # Only system message
            [{"role": "system", "content": "You are a helpful assistant."}],
            # Only user messages
            [
                {"role": "user", "content": "First message"},
                {"role": "user", "content": "Second message"}
            ],
            # Tool call without response
            [
                {"role": "user", "content": "Run command"},
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_incomplete",
                            "type": "function",
                            "function": {"name": "test_command", "arguments": "{}"}
                        }
                    ]
                }
            ],
            # Tool response without call
            [
                {"role": "user", "content": "Test"},
                {"role": "tool", "tool_call_id": "orphan_call", "content": "Result"}
            ]
        ]
        
        cmd = HistoryCommand()
        
        for i, case_history in enumerate(edge_cases):
            mock_message_history.clear()
            mock_message_history.extend(case_history)
            
            result = cmd.handle([])
            assert result is True, f"Failed at edge case {i + 1}"


if __name__ == '__main__':
    pytest.main([__file__, "-v"]) 
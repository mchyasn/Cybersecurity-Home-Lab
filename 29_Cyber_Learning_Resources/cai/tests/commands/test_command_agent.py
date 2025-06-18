#!/usr/bin/env python3
"""
Test suite for the agent command functionality.
Tests all handle methods and input possibilities for the agent command.
"""

import os
import sys
import pytest
from unittest.mock import patch, Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                '..', '..', 'src'))

from cai.repl.commands.agent import AgentCommand
from cai.repl.commands.base import Command


class TestAgentCommand:
    """Test cases for AgentCommand."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup and cleanup for each test."""
        # Set up test environment
        os.environ['CAI_TELEMETRY'] = 'false'
        os.environ['CAI_TRACING'] = 'false'
        
        # Clear any agent-related environment variables
        env_vars_to_clear = [
            'CAI_AGENT_TYPE', 'CTF_MODEL', 'CAI_CODE_MODEL',
            'CAI_TEST_MODEL', 'CAI_CUSTOM_MODEL'
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
        
        yield
        
        # Cleanup after each test
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
    
    @pytest.fixture
    def agent_command(self):
        """Create an AgentCommand instance for testing."""
        return AgentCommand()
    
    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        agents = {}
        
        # Create mock agent objects with required attributes
        for name in ['code', 'test', 'custom', 'basic']:
            mock_agent = Mock()
            mock_agent.name = name
            mock_agent.model = f"model-for-{name}"
            mock_agent.description = f"Description for {name} agent"
            mock_agent.instructions = f"Instructions for {name} agent"
            
            # Configure properties that need len() to work
            mock_agent.functions = []  # Empty list instead of Mock
            mock_agent.handoffs = []   # Empty list instead of Mock
            mock_agent.tools = []      # Empty list instead of Mock
            mock_agent.input_guardrails = []   # Empty list instead of Mock
            mock_agent.output_guardrails = []  # Empty list instead of Mock
            mock_agent.hooks = []      # Empty list instead of Mock
            
            # Other optional properties
            mock_agent.parallel_tool_calls = False
            mock_agent.handoff_description = None
            mock_agent.output_type = None
            
            agents[name] = mock_agent
        
        return agents
    
    def test_command_initialization(self, agent_command):
        """Test that AgentCommand initializes correctly."""
        assert agent_command.name == "/agent"
        assert agent_command.description == "Manage and switch between agents"
        assert agent_command.aliases == ["/a"]
        
        # Check subcommands are available
        expected_subcommands = ["list", "select", "info", "multi"]
        assert set(agent_command.get_subcommands()) == set(expected_subcommands)
    
    def test_get_model_display_code_agent(self, agent_command):
        """Test model display for code agent."""
        mock_agent = Mock()
        mock_agent.model = "gpt-4"
        
        result = agent_command._get_model_display("code", mock_agent)
        assert result == "gpt-4"
    
    def test_get_model_display_with_ctf_model(self, agent_command):
        """Test model display when CTF_MODEL is set."""
        os.environ['CTF_MODEL'] = "claude-3"
        
        mock_agent = Mock()
        mock_agent.model = "claude-3"
        
        result = agent_command._get_model_display("test", mock_agent)
        assert result == ""  # Should return empty for non-code agents with CTF_MODEL
    
    def test_get_model_display_with_env_var(self, agent_command):
        """Test model display with agent-specific environment variable."""
        os.environ['CAI_TEST_MODEL'] = "custom-model"
        
        mock_agent = Mock()
        mock_agent.model = "default-model"
        
        result = agent_command._get_model_display("test", mock_agent)
        assert result == "custom-model"
    
    def test_get_model_display_for_info_code_agent(self, agent_command):
        """Test model display for info view with code agent."""
        mock_agent = Mock()
        mock_agent.model = "gpt-4"
        
        result = agent_command._get_model_display_for_info("code", mock_agent)
        assert result == "gpt-4"
    
    def test_get_model_display_for_info_with_ctf_model(self, agent_command):
        """Test model display for info view when CTF_MODEL is set."""
        os.environ['CTF_MODEL'] = "claude-3"
        
        mock_agent = Mock()
        mock_agent.model = "claude-3"
        
        result = agent_command._get_model_display_for_info("test", mock_agent)
        assert result == "Default CTF Model"
    
    @patch('cai.repl.commands.agent.get_available_agents')
    @patch('cai.repl.commands.agent.get_agent_module')
    def test_handle_list(self, mock_get_module, mock_get_agents, 
                        agent_command, mock_agents):
        """Test listing available agents."""
        mock_get_agents.return_value = mock_agents
        mock_get_module.return_value = "test_module"
        
        result = agent_command.handle_list([])
        assert result is True
        
        # Verify get_available_agents was called
        mock_get_agents.assert_called_once()
    
    @patch('cai.repl.commands.agent.get_available_agents')
    @patch('cai.repl.commands.agent.visualize_agent_graph')
    def test_handle_select_by_name(self, mock_visualize, mock_get_agents, 
                                  agent_command, mock_agents):
        """Test selecting an agent by name."""
        mock_get_agents.return_value = mock_agents
        
        result = agent_command.handle_select(["code"])
        assert result is True
        assert os.environ.get('CAI_AGENT_TYPE') == "code"
        
        # Verify visualization was called
        mock_visualize.assert_called_once_with(mock_agents["code"])
    
    @patch('cai.repl.commands.agent.get_available_agents')
    @patch('cai.repl.commands.agent.visualize_agent_graph')
    def test_handle_select_by_number(self, mock_visualize, mock_get_agents, 
                                    agent_command, mock_agents):
        """Test selecting an agent by number."""
        mock_get_agents.return_value = mock_agents
        
        result = agent_command.handle_select(["2"])
        assert result is True
        
        # Should select the second agent in the dict (order may vary)
        agent_keys = list(mock_agents.keys())
        expected_key = agent_keys[1]  # Second agent (0-indexed)
        assert os.environ.get('CAI_AGENT_TYPE') == expected_key
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_handle_select_invalid_name(self, mock_get_agents, 
                                       agent_command, mock_agents):
        """Test selecting an invalid agent name."""
        mock_get_agents.return_value = mock_agents
        
        result = agent_command.handle_select(["invalid_agent"])
        assert result is False
        assert 'CAI_AGENT_TYPE' not in os.environ
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_handle_select_invalid_number(self, mock_get_agents, 
                                         agent_command, mock_agents):
        """Test selecting an invalid agent number."""
        mock_get_agents.return_value = mock_agents
        
        result = agent_command.handle_select(["99"])
        assert result is False
        assert 'CAI_AGENT_TYPE' not in os.environ
    
    def test_handle_select_no_args(self, agent_command):
        """Test select command with no arguments."""
        result = agent_command.handle_select([])
        assert result is False
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_handle_info_by_name(self, mock_get_agents, 
                                agent_command, mock_agents):
        """Test getting info for an agent by name."""
        mock_get_agents.return_value = mock_agents
        
        result = agent_command.handle_info(["code"])
        assert result is True
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_handle_info_by_number(self, mock_get_agents, 
                                  agent_command, mock_agents):
        """Test getting info for an agent by number."""
        mock_get_agents.return_value = mock_agents
        
        result = agent_command.handle_info(["1"])
        assert result is True
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_handle_info_invalid_name(self, mock_get_agents, 
                                     agent_command, mock_agents):
        """Test getting info for an invalid agent name."""
        mock_get_agents.return_value = mock_agents
        
        result = agent_command.handle_info(["invalid_agent"])
        assert result is False
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_handle_info_invalid_number(self, mock_get_agents, 
                                       agent_command, mock_agents):
        """Test getting info for an invalid agent number."""
        mock_get_agents.return_value = mock_agents
        
        result = agent_command.handle_info(["99"])
        assert result is False
    
    def test_handle_info_no_args(self, agent_command):
        """Test info command with no arguments."""
        result = agent_command.handle_info([])
        assert result is False
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_handle_info_with_complex_agent(self, mock_get_agents, agent_command):
        """Test info command with agent that has complex attributes."""
        # Create a more complex mock agent
        complex_agent = Mock()
        complex_agent.name = "complex_agent"
        complex_agent.description = "A complex agent for testing"
        complex_agent.instructions = lambda: "Dynamic instructions"
        # Use real lists instead of Mocks for len() to work
        complex_agent.functions = [Mock(), Mock()]
        complex_agent.parallel_tool_calls = True
        complex_agent.handoff_description = "Handoff description"
        complex_agent.handoffs = [Mock()]
        complex_agent.tools = [Mock(), Mock(), Mock()]
        complex_agent.input_guardrails = [Mock()]
        complex_agent.output_guardrails = [Mock(), Mock()]
        complex_agent.output_type = "str"
        complex_agent.hooks = [Mock()]
        
        mock_get_agents.return_value = {"complex": complex_agent}
        
        result = agent_command.handle_info(["complex"])
        assert result is True
    
    def test_command_base_functionality(self, agent_command):
        """Test that the command inherits from base Command properly."""
        assert isinstance(agent_command, Command)
        assert agent_command.name == "/agent"
        assert "/a" in agent_command.aliases
    
    @patch('cai.repl.commands.agent.get_available_agents')
    @patch('cai.repl.commands.agent.get_agent_module')
    def test_handle_main_command_routing(self, mock_get_module, mock_get_agents, 
                                        agent_command, mock_agents):
        """Test that main handle method routes to correct subcommands."""
        mock_get_agents.return_value = mock_agents
        mock_get_module.return_value = "test_module"
        
        # Test routing to list (no args defaults to list)
        result1 = agent_command.handle([])
        assert result1 is True
        
        # Test routing to list explicitly
        result2 = agent_command.handle(["list"])
        assert result2 is True
        
        # Test routing to info
        result3 = agent_command.handle(["info", "code"])
        assert result3 is True
        
        # Test direct agent selection (not a subcommand)
        result4 = agent_command.handle(["code"])
        assert result4 is True
        assert os.environ.get('CAI_AGENT_TYPE') == "code"
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_agent_with_callable_instructions(self, mock_get_agents, agent_command):
        """Test agent with callable instructions."""
        mock_agent = Mock()
        mock_agent.name = "callable_agent"
        mock_agent.description = "Agent with callable instructions"
        mock_agent.instructions = lambda context_variables=None: "Callable instructions"
        # Configure required properties
        mock_agent.functions = []
        mock_agent.handoffs = []
        mock_agent.tools = []
        mock_agent.input_guardrails = []
        mock_agent.output_guardrails = []
        mock_agent.hooks = []
        mock_agent.parallel_tool_calls = False
        mock_agent.handoff_description = None
        mock_agent.output_type = None
        
        mock_get_agents.return_value = {"callable": mock_agent}
        
        result = agent_command.handle_info(["callable"])
        assert result is True
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_agent_with_multiline_description(self, mock_get_agents, agent_command):
        """Test agent with multiline description that should be cleaned."""
        mock_agent = Mock()
        mock_agent.name = "multiline_agent"
        mock_agent.description = """This is a
        multiline description
        that should be cleaned"""
        mock_agent.instructions = "Simple instructions"
        # Configure required properties
        mock_agent.functions = []
        mock_agent.handoffs = []
        mock_agent.tools = []
        mock_agent.input_guardrails = []
        mock_agent.output_guardrails = []
        mock_agent.hooks = []
        mock_agent.parallel_tool_calls = False
        mock_agent.handoff_description = None
        mock_agent.output_type = None
        
        mock_get_agents.return_value = {"multiline": mock_agent}
        
        result = agent_command.handle_info(["multiline"])
        assert result is True


@pytest.mark.integration
class TestAgentCommandIntegration:
    """Integration tests for agent command functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_integration(self):
        """Setup for integration tests."""
        # Clear environment variables
        env_vars_to_clear = [
            'CAI_AGENT_TYPE', 'CTF_MODEL', 'CAI_CODE_MODEL',
            'CAI_TEST_MODEL', 'CAI_CUSTOM_MODEL'
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
        
        yield
        
        # Cleanup
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
    
    @patch('cai.repl.commands.agent.get_available_agents')
    @patch('cai.repl.commands.agent.get_agent_module')
    @patch('cai.repl.commands.agent.visualize_agent_graph')
    def test_full_workflow(self, mock_visualize, mock_get_module, mock_get_agents):
        """Test a complete workflow of listing, selecting, and getting info."""
        # Setup mock agents
        agents = {}
        for name in ['agent1', 'agent2', 'agent3']:
            mock_agent = Mock()
            mock_agent.name = name
            mock_agent.model = f"model-{name}"
            mock_agent.description = f"Description for {name}"
            mock_agent.instructions = f"Instructions for {name}"
            
            # Configure properties that need len() to work
            mock_agent.functions = []
            mock_agent.handoffs = []
            mock_agent.tools = []
            mock_agent.input_guardrails = []
            mock_agent.output_guardrails = []
            mock_agent.hooks = []
            mock_agent.parallel_tool_calls = False
            mock_agent.handoff_description = None
            mock_agent.output_type = None
            
            agents[name] = mock_agent
        
        mock_get_agents.return_value = agents
        mock_get_module.return_value = "test_module"
        
        cmd = AgentCommand()
        
        # List agents
        result1 = cmd.handle(["list"])
        assert result1 is True
        
        # Select an agent by name
        result2 = cmd.handle(["select", "agent1"])
        assert result2 is True
        assert os.environ.get('CAI_AGENT_TYPE') == "agent1"
        
        # Get info for an agent
        result3 = cmd.handle(["info", "agent2"])
        assert result3 is True
        
        # Select by number
        result4 = cmd.handle(["select", "2"])
        assert result4 is True
        
        # Direct selection (not using select subcommand)
        result5 = cmd.handle(["agent3"])
        assert result5 is True
        assert os.environ.get('CAI_AGENT_TYPE') == "agent3"
    
    @patch('cai.repl.commands.agent.get_available_agents')
    def test_environment_variable_handling(self, mock_get_agents):
        """Test how environment variables affect model display."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.model = "default-model"
        
        mock_get_agents.return_value = {"test": mock_agent}
        
        cmd = AgentCommand()
        
        # Test without environment variables
        result1 = cmd._get_model_display("test", mock_agent)
        assert result1 == "default-model"
        
        # Test with agent-specific environment variable
        os.environ['CAI_TEST_MODEL'] = "env-specific-model"
        result2 = cmd._get_model_display("test", mock_agent)
        assert result2 == "env-specific-model"
        
        # Test with CTF_MODEL
        os.environ['CTF_MODEL'] = "default-model"
        result3 = cmd._get_model_display("test", mock_agent)
        assert result3 == ""  # Should be empty for table display
        
        result4 = cmd._get_model_display_for_info("test", mock_agent)
        assert result4 == "Default CTF Model"  # Should show this for info display


if __name__ == '__main__':
    pytest.main([__file__, "-v"]) 
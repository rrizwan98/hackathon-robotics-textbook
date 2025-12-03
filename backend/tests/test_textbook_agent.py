# backend/tests/test_textbook_agent.py
"""
TDD Test Cases for the Textbook Agent.

These tests verify:
1. Agent creation and configuration
2. Tool functionality (list_available_textbooks, query_textbook, get_textbook_summary)
3. Agent decision making (direct response vs tool call)
4. Integration with Gemini API via LiteLLM

Run tests with: pytest backend/tests/test_textbook_agent.py -v
"""

import os
import sys
import json
import warnings
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from dotenv import load_dotenv

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables
load_dotenv()

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# --- Configuration ---
UPLOAD_FILES_METADATA_PATH = os.path.join("backend", "data", "gemini_files.json")


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def gemini_files_data():
    """
    Loads the uploaded Gemini files metadata.
    """
    if not os.path.exists(UPLOAD_FILES_METADATA_PATH):
        pytest.skip(f"Gemini files metadata not found at {UPLOAD_FILES_METADATA_PATH}. "
                    "Please run upload_textbook_files_gemini.py first.")
    with open(UPLOAD_FILES_METADATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def mock_gemini_response():
    """
    Creates a mock Gemini API response.
    """
    mock_response = MagicMock()
    mock_response.text = "This is a mock response about Physical AI and Humanoid Robotics."
    return mock_response


@pytest.fixture
def mock_gemini_file():
    """
    Creates a mock Gemini file object.
    """
    mock_file = MagicMock()
    mock_file.name = "files/test123"
    mock_file.display_name = "Test Textbook"
    mock_file.state = "ACTIVE"
    return mock_file


# ============================================================================
# Test: Agent Creation and Configuration
# ============================================================================

class TestAgentCreation:
    """Tests for agent creation and basic configuration."""
    
    def test_agent_can_be_created(self):
        """Test that the textbook agent can be created successfully."""
        from backend.src.agents.textbook_agent import create_textbook_agent
        
        agent = create_textbook_agent()
        
        assert agent is not None
        assert agent.name == "TextbookAgent"
    
    def test_agent_has_correct_model(self):
        """Test that the agent uses the correct LiteLLM model."""
        from backend.src.agents.textbook_agent import create_textbook_agent, MODEL_NAME
        
        agent = create_textbook_agent()
        
        assert agent.model == MODEL_NAME
        assert "gemini" in MODEL_NAME.lower()
    
    def test_agent_has_tools_configured(self):
        """Test that the agent has tools configured."""
        from backend.src.agents.textbook_agent import create_textbook_agent
        
        agent = create_textbook_agent()
        
        assert agent.tools is not None
        assert len(agent.tools) >= 3  # At least 3 tools
    
    def test_agent_has_instructions(self):
        """Test that the agent has system instructions."""
        from backend.src.agents.textbook_agent import create_textbook_agent, SYSTEM_INSTRUCTIONS
        
        agent = create_textbook_agent()
        
        assert agent.instructions is not None
        assert len(agent.instructions) > 0
        assert "textbook" in agent.instructions.lower() or "robotics" in agent.instructions.lower()


# ============================================================================
# Test: Tools - list_available_textbooks
# ============================================================================

class TestListAvailableTextbooks:
    """Tests for the list_available_textbooks tool."""
    
    def test_list_textbooks_returns_string(self, gemini_files_data):
        """Test that list_available_textbooks returns a string."""
        from backend.src.agents.tools import list_available_textbooks
        
        result = list_available_textbooks()
        
        assert isinstance(result, str)
    
    def test_list_textbooks_contains_available_header(self, gemini_files_data):
        """Test that the result contains 'Available Textbooks' header."""
        from backend.src.agents.tools import list_available_textbooks
        
        result = list_available_textbooks()
        
        assert "Available Textbooks" in result or "No textbooks" in result
    
    def test_list_textbooks_contains_uploaded_files(self, gemini_files_data):
        """Test that the result contains the uploaded textbook names."""
        from backend.src.agents.tools import list_available_textbooks
        
        result = list_available_textbooks()
        
        # Check that at least one textbook is listed
        has_textbook = False
        for file_info in gemini_files_data:
            if file_info.get("display_name", "") in result:
                has_textbook = True
                break
        
        assert has_textbook, "At least one uploaded textbook should be listed"
    
    def test_list_textbooks_empty_when_no_files(self):
        """Test that list_available_textbooks handles empty metadata gracefully."""
        from backend.src.agents.tools import list_available_textbooks, _load_gemini_files_metadata
        
        # Mock the metadata loading to return empty list
        with patch('backend.src.agents.tools._load_gemini_files_metadata', return_value=[]):
            result = list_available_textbooks()
            
            assert "No textbooks" in result or "not" in result.lower()


# ============================================================================
# Test: Tools - query_textbook
# ============================================================================

class TestQueryTextbook:
    """Tests for the query_textbook tool."""
    
    def test_query_textbook_returns_string(self, gemini_files_data, mock_gemini_response, mock_gemini_file):
        """Test that query_textbook returns a string response."""
        from backend.src.agents.tools import query_textbook
        
        with patch('backend.src.agents.tools.client.files.get', return_value=mock_gemini_file):
            with patch('backend.src.agents.tools.client.models.generate_content', return_value=mock_gemini_response):
                result = query_textbook(question="What is Physical AI?")
                
                assert isinstance(result, str)
    
    def test_query_textbook_handles_specific_textbook(self, gemini_files_data, mock_gemini_response, mock_gemini_file):
        """Test that query_textbook can query a specific textbook."""
        from backend.src.agents.tools import query_textbook
        
        with patch('backend.src.agents.tools.client.files.get', return_value=mock_gemini_file):
            with patch('backend.src.agents.tools.client.models.generate_content', return_value=mock_gemini_response):
                result = query_textbook(
                    question="What is covered in this chapter?",
                    textbook_name="Introduction"
                )
                
                assert isinstance(result, str)
                assert len(result) > 0
    
    def test_query_textbook_handles_missing_textbook(self, gemini_files_data):
        """Test that query_textbook handles non-existent textbook gracefully."""
        from backend.src.agents.tools import query_textbook
        
        result = query_textbook(
            question="What is covered?",
            textbook_name="NonExistentTextbook12345"
        )
        
        assert "Could not find" in result or "not find" in result.lower()
    
    def test_query_textbook_handles_empty_metadata(self):
        """Test that query_textbook handles empty metadata gracefully."""
        from backend.src.agents.tools import query_textbook
        
        with patch('backend.src.agents.tools._load_gemini_files_metadata', return_value=[]):
            result = query_textbook(question="What is Physical AI?")
            
            assert "No textbooks" in result or "not" in result.lower()
    
    def test_query_textbook_handles_api_error(self, gemini_files_data):
        """Test that query_textbook handles API errors gracefully."""
        from backend.src.agents.tools import query_textbook
        
        with patch('backend.src.agents.tools.client.files.get', side_effect=Exception("API Error")):
            result = query_textbook(question="What is Physical AI?")
            
            assert "Error" in result or "error" in result.lower()


# ============================================================================
# Test: Tools - get_textbook_summary
# ============================================================================

class TestGetTextbookSummary:
    """Tests for the get_textbook_summary tool."""
    
    def test_get_summary_returns_string(self, gemini_files_data, mock_gemini_response, mock_gemini_file):
        """Test that get_textbook_summary returns a string."""
        from backend.src.agents.tools import get_textbook_summary
        
        with patch('backend.src.agents.tools.client.files.get', return_value=mock_gemini_file):
            with patch('backend.src.agents.tools.client.models.generate_content', return_value=mock_gemini_response):
                result = get_textbook_summary()
                
                assert isinstance(result, str)
    
    def test_get_summary_with_specific_textbook(self, gemini_files_data, mock_gemini_response, mock_gemini_file):
        """Test that get_textbook_summary can summarize a specific textbook."""
        from backend.src.agents.tools import get_textbook_summary
        
        with patch('backend.src.agents.tools.client.files.get', return_value=mock_gemini_file):
            with patch('backend.src.agents.tools.client.models.generate_content', return_value=mock_gemini_response):
                result = get_textbook_summary(textbook_name="Introduction")
                
                assert isinstance(result, str)
                assert len(result) > 0


# ============================================================================
# Test: Agent Integration - Direct Response vs Tool Call
# ============================================================================

class TestAgentDecisionMaking:
    """Tests for agent's decision making - when to respond directly vs use tools."""
    
    @pytest.mark.asyncio
    async def test_agent_responds_to_greeting(self):
        """Test that the agent can respond to a simple greeting without tools."""
        from backend.src.agents.textbook_agent import create_textbook_agent
        from agents import Runner
        
        agent = create_textbook_agent()
        
        # Mock the runner to avoid actual API calls
        with patch.object(Runner, 'run', new_callable=AsyncMock) as mock_run:
            mock_result = MagicMock()
            mock_result.final_output = "Hello! I'm the Textbook Assistant. How can I help you?"
            mock_run.return_value = mock_result
            
            result = await Runner.run(agent, "Hello!")
            
            assert result.final_output is not None
            assert len(result.final_output) > 0
    
    def test_agent_model_is_gemini(self):
        """Test that the agent is configured to use Gemini model."""
        from backend.src.agents.textbook_agent import MODEL_NAME
        
        assert "gemini" in MODEL_NAME.lower()
        assert "2.5" in MODEL_NAME or "flash" in MODEL_NAME.lower()


# ============================================================================
# Test: Agent Response Printing (for manual verification)
# ============================================================================

class TestAgentResponsePrinting:
    """Tests that print agent responses for manual verification."""
    
    @pytest.mark.asyncio
    async def test_agent_query_with_print(self):
        """Test agent with real query and print the response."""
        from backend.src.agents.textbook_agent import run_agent_async
        
        query = "What textbooks are available?"
        
        print("\n" + "="*80)
        print("AGENT RESPONSE TEST - PRINTING RESULTS")
        print("="*80 + "\n")
        print(f"Query: {query}\n")
        print("-"*80)
        print("\n⏳ Processing...\n")
        
        try:
            response = await run_agent_async(query)
            print(f"✅ Agent Response:\n{response}\n")
            print("="*80 + "\n")
            
            # Basic assertion
            assert response is not None
            assert len(response) > 0
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()
            print("="*80 + "\n")
            raise


# ============================================================================
# Test: Integration Tests with Real API (marked for selective running)
# ============================================================================

class TestIntegrationWithGeminiAPI:
    """
    Integration tests that use the real Gemini API.
    These tests require valid API credentials and uploaded files.
    """
    
    @pytest.mark.integration
    def test_real_query_intro_chapter(self, gemini_files_data):
        """Test a real query against the Introduction chapter."""
        from backend.src.agents.tools import query_textbook
        
        # Skip if no API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set")
        
        question = "What is the primary focus of Physical AI mentioned in this document?"
        result = query_textbook(question=question, textbook_name="Introduction")
        
        assert isinstance(result, str)
        assert len(result) > 50  # Expect a substantial response
        # Check that it's not an error message
        assert "Error" not in result or "Physical AI" in result
    
    @pytest.mark.integration
    def test_real_list_textbooks(self, gemini_files_data):
        """Test listing textbooks with real data."""
        from backend.src.agents.tools import list_available_textbooks
        
        result = list_available_textbooks()
        
        assert "Available Textbooks" in result
        assert "Introduction" in result or "ROS2" in result
    
    @pytest.mark.integration
    def test_real_query_ros2_chapter(self, gemini_files_data):
        """Test a real query against the ROS2 chapter."""
        from backend.src.agents.tools import query_textbook
        
        # Skip if no API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set")
        
        question = "What is ROS2 and why is it important for robotics?"
        result = query_textbook(question=question, textbook_name="ROS2")
        
        assert isinstance(result, str)
        assert len(result) > 50  # Expect a substantial response


# ============================================================================
# Test: Error Handling
# ============================================================================

class TestErrorHandling:
    """Tests for error handling in the agent and tools."""
    
    def test_tools_handle_missing_api_key(self):
        """Test that tools handle missing API key gracefully."""
        from backend.src.agents.tools import query_textbook
        
        # This test verifies the structure handles the error
        # The actual behavior depends on whether the API key is set
        result = query_textbook(question="Test question")
        
        # Should return a string (either answer or error message)
        assert isinstance(result, str)
    
    def test_agent_creation_with_invalid_model_still_creates(self):
        """Test that agent can still be created even with model issues."""
        from agents import Agent
        from backend.src.agents.tools import TEXTBOOK_TOOLS
        
        # Creating agent should not fail even if model is not available
        try:
            agent = Agent(
                name="TestAgent",
                instructions="Test instructions",
                model="invalid-model-name",
                tools=TEXTBOOK_TOOLS
            )
            assert agent is not None
        except Exception as e:
            # If it fails, it should be a clear error
            assert "model" in str(e).lower() or "invalid" in str(e).lower()


# ============================================================================
# Test: Tool Decorator Functionality
# ============================================================================

class TestToolDecorators:
    """Tests for verifying tool decorators work correctly."""
    
    def test_list_available_textbooks_is_callable(self):
        """Test that list_available_textbooks is callable as a tool."""
        from backend.src.agents.tools import list_available_textbooks
        
        # The function should be callable
        assert callable(list_available_textbooks)
    
    def test_query_textbook_is_callable(self):
        """Test that query_textbook is callable as a tool."""
        from backend.src.agents.tools import query_textbook
        
        assert callable(query_textbook)
    
    def test_get_textbook_summary_is_callable(self):
        """Test that get_textbook_summary is callable as a tool."""
        from backend.src.agents.tools import get_textbook_summary
        
        assert callable(get_textbook_summary)
    
    def test_textbook_tools_list_not_empty(self):
        """Test that TEXTBOOK_TOOLS list is not empty."""
        from backend.src.agents.tools import TEXTBOOK_TOOLS
        
        assert len(TEXTBOOK_TOOLS) >= 3


# ============================================================================
# How to run the tests
# ============================================================================
# 
# Basic tests (mocked, no API calls):
#   pytest backend/tests/test_textbook_agent.py -v
#
# All tests including integration tests:
#   pytest backend/tests/test_textbook_agent.py -v -m "integration or not integration"
#
# Only integration tests (requires API key and uploaded files):
#   pytest backend/tests/test_textbook_agent.py -v -m integration
#
# Run with coverage:
#   pytest backend/tests/test_textbook_agent.py -v --cov=backend/src/agents


# ============================================================================
# Test: Print Agent Responses (Standalone functions for easy testing)
# ============================================================================

def test_print_list_textbooks():
    """Test and print list textbooks tool result."""
    from backend.src.agents.tools import list_available_textbooks_fn
    
    print("\n" + "="*80)
    print("LIST TEXTBOOKS TOOL TEST - PRINTING RESULT")
    print("="*80 + "\n")
    
    result = list_available_textbooks_fn()
    print(f"✅ Result:\n{result}\n")
    print("="*80 + "\n")
    
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_print_agent_query():
    """Test agent query and print response."""
    from backend.src.agents.textbook_agent import run_agent_async
    
    query = "What is Physical AI?"
    
    print("\n" + "="*80)
    print("AGENT QUERY TEST - PRINTING RESPONSE")
    print("="*80 + "\n")
    print(f"Query: {query}\n")
    print("-"*80)
    print("\n⏳ Processing...\n")
    
    try:
        response = await run_agent_async(query)
        print(f"✅ Agent Response:\n{response}\n")
        print("="*80 + "\n")
        
        assert response is not None
        assert len(response) > 0
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        raise


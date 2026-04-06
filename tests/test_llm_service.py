from unittest.mock import patch

from vp_core.llm.llm_service import LlmService


@patch("vp_core.llm.llm_service.GeminiService")
@patch("vp_core.llm.llm_service.OpenaiService")
def test_llm_service_chooses_openai_for_gpt(mock_openai, mock_gemini):
    mock_openai_instance = mock_openai.return_value
    mock_openai_instance.llm.return_value = "mock_openai_llm"
    
    mock_gemini_instance = mock_gemini.return_value
    mock_gemini_instance.llm.return_value = "mock_gemini_llm"
    
    service = LlmService("openai")
    
    # Passing a gpt model should route to OpenaiService
    result = service.llm(model="gpt-4o")
    
    mock_openai_instance.llm.assert_called_once_with(model="gpt-4o")
    assert result == "mock_openai_llm"
    mock_gemini_instance.llm.assert_not_called()


@patch("vp_core.llm.llm_service.GeminiService")
@patch("vp_core.llm.llm_service.OpenaiService")
def test_llm_service_chooses_gemini_for_others(mock_openai, mock_gemini):
    mock_openai_instance = mock_openai.return_value
    mock_openai_instance.llm.return_value = "mock_openai_llm"
    
    mock_gemini_instance = mock_gemini.return_value
    mock_gemini_instance.llm.return_value = "mock_gemini_llm"
    
    service = LlmService("gemini")
    
    # By default, should route to GeminiService
    result = service.llm(model="gemini-1.5-pro")
    
    mock_gemini_instance.llm.assert_called_once_with(model="gemini-1.5-pro")
    assert result == "mock_gemini_llm"
    mock_openai_instance.llm.assert_not_called()

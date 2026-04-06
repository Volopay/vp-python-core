import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from vp_core.helpers.url_helper import download_from_url

@pytest.mark.asyncio
async def test_download_from_url_success():
    # Mock the AsyncClient and its context manager behavior
    mock_client_instance = AsyncMock()
    
    # Mock the response object returned by client.get()
    mock_response = MagicMock()
    mock_response.content = b"test content"
    mock_response.headers.get.return_value = "text/plain"
    
    mock_client_instance.get.return_value = mock_response

    # Patch httpx.AsyncClient so it returns our mocked instance when used in 'async with'
    with patch("vp_core.helpers.url_helper.httpx.AsyncClient", autospec=True) as mock_client_class:
        # Set up __aenter__ to return the mock_client_instance
        mock_client_class.return_value.__aenter__.return_value = mock_client_instance
        
        # Run the function
        file_obj, content_type = await download_from_url("https://example.com/test.txt")
        
        # Verify the returned values
        assert file_obj is not None
        assert file_obj.read() == b"test content"
        assert content_type == "text/plain"
        
        # Verify the mocked client was called correctly
        mock_client_instance.get.assert_called_once_with("https://example.com/test.txt", timeout=10)
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_download_from_url_failure():
    # Mock the AsyncClient and its context manager behavior
    mock_client_instance = AsyncMock()
    
    # Setup client.get() to raise an exception simulating a network error
    mock_client_instance.get.side_effect = Exception("Network timeout")

    with patch("vp_core.helpers.url_helper.httpx.AsyncClient", autospec=True) as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = mock_client_instance
        
        # The helper catches the exception and logs it, returning (None, None)
        file_obj, content_type = await download_from_url("https://example.com/fail.txt")
        
        # Verify failure response
        assert file_obj is None
        assert content_type is None

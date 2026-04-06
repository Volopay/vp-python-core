import pytest
from unittest.mock import MagicMock, patch
from vp_core.helpers import S3Helper

@pytest.fixture
def s3_helper():
    return S3Helper(
        aws_access_key_id="test-key",
        aws_secret_access_key="test-secret",
        region_name="us-east-1"
    )

def test_s3_helper_initialization():
    # Should initialize correctly with credentials
    helper = S3Helper(
        aws_access_key_id="key",
        aws_secret_access_key="secret",
        region_name="region"
    )
    assert helper.s3_client is not None

def test_s3_helper_initialization_failure():
    # Should fail if credentials are missing
    with pytest.raises(TypeError):
        S3Helper()

@pytest.mark.asyncio
async def test_put_object_success(s3_helper):
    # Mock the s3_client's put_object method
    with patch.object(s3_helper.s3_client, 'put_object') as mock_put:
        mock_put.return_value = {}
        
        result = await s3_helper.put_object(
            bucket_name="test-bucket",
            body=b"test-body",
            object_key="test-key",
            content_type="text/plain"
        )
        
        assert result == "test-key"
        mock_put.assert_called_once_with(
            Bucket="test-bucket",
            Key="test-key",
            Body=b"test-body",
            ACL="public-read",
            ContentType="text/plain"
        )

@pytest.mark.asyncio
async def test_put_object_failure(s3_helper):
    # Mock the s3_client's put_object method to raise an exception
    with patch.object(s3_helper.s3_client, 'put_object') as mock_put:
        mock_put.side_effect = Exception("S3 Upload Failed")
        
        with pytest.raises(Exception) as excinfo:
            await s3_helper.put_object(
                bucket_name="test-bucket",
                body=b"test-body",
                object_key="test-key"
            )
        
        assert "S3 Upload Failed" in str(excinfo.value)

@pytest.mark.asyncio
async def test_get_object_success(s3_helper):
    # Mock the s3_client's get_object method
    with patch.object(s3_helper.s3_client, 'get_object') as mock_get:
        mock_response = {"Body": MagicMock(), "ContentType": "text/plain"}
        mock_get.return_value = mock_response
        
        result = await s3_helper.get_object(
            bucket_name="test-bucket",
            key="test-key"
        )
        
        assert result == mock_response
        mock_get.assert_called_once_with(
            Bucket="test-bucket",
            Key="test-key"
        )

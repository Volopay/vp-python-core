from unittest.mock import patch

from vp_core.security import sign_request, verify_request

# Shared cross-language test vector.
# The same inputs MUST produce the same signature when Ruby signs via
# OpenSSL::HMAC.hexdigest. volo-be/spec/clients/volo_agents_client_spec.rb
# asserts the same EXPECTED_SIG below — any drift breaks auth in production.
SHARED_SECRET = "test_secret_do_not_use_in_prod"
SHARED_METHOD = "POST"
SHARED_PATH = "/api/v1/keywords/suggest"
SHARED_BODY = b'{"seeds":["beer"]}'
SHARED_TIMESTAMP = 1712419200
EXPECTED_SIG = "95975a61fdd5896a2e3ada649ead58c1a96dbf3c2a338a8d862580ec05b44e69"


def test_shared_vector_matches_ruby():
    """Cross-language contract — Ruby's OpenSSL::HMAC must produce this hex."""
    sig, ts = sign_request(
        SHARED_SECRET, SHARED_METHOD, SHARED_PATH, SHARED_BODY, SHARED_TIMESTAMP
    )
    assert sig == EXPECTED_SIG
    assert ts == SHARED_TIMESTAMP


def test_sign_and_verify_round_trip():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello")
    with patch("vp_core.security.hmac.time.time", return_value=ts):
        assert verify_request("s3cret", sig, "POST", "/x", b"hello", ts) is True


def test_verify_tampered_body():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello")
    with patch("vp_core.security.hmac.time.time", return_value=ts):
        assert verify_request("s3cret", sig, "POST", "/x", b"tampered", ts) is False


def test_verify_tampered_path():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello")
    with patch("vp_core.security.hmac.time.time", return_value=ts):
        assert verify_request("s3cret", sig, "POST", "/y", b"hello", ts) is False


def test_verify_tampered_method():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello")
    with patch("vp_core.security.hmac.time.time", return_value=ts):
        assert verify_request("s3cret", sig, "DELETE", "/x", b"hello", ts) is False


def test_verify_wrong_secret():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello")
    with patch("vp_core.security.hmac.time.time", return_value=ts):
        assert verify_request("wrong", sig, "POST", "/x", b"hello", ts) is False


def test_verify_expired_timestamp():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello", timestamp=1_000_000)
    # now is 61s past the signed timestamp — outside 60s window
    with patch("vp_core.security.hmac.time.time", return_value=1_000_061):
        assert verify_request("s3cret", sig, "POST", "/x", b"hello", ts) is False


def test_verify_future_timestamp():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello", timestamp=1_000_000)
    # now is 61s before the signed timestamp — clock skew outside window
    with patch("vp_core.security.hmac.time.time", return_value=999_939):
        assert verify_request("s3cret", sig, "POST", "/x", b"hello", ts) is False


def test_verify_within_window_edge():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello", timestamp=1_000_000)
    # exactly 60s off — still valid (boundary is inclusive)
    with patch("vp_core.security.hmac.time.time", return_value=1_000_060):
        assert verify_request("s3cret", sig, "POST", "/x", b"hello", ts) is True


def test_sign_request_normalizes_method_case():
    sig_upper, _ = sign_request("s3cret", "POST", "/x", b"", timestamp=1)
    sig_lower, _ = sign_request("s3cret", "post", "/x", b"", timestamp=1)
    assert sig_upper == sig_lower


def test_sign_request_empty_body():
    """GET requests have empty body — should still sign cleanly."""
    sig, ts = sign_request("s3cret", "GET", "/_ping", b"")
    with patch("vp_core.security.hmac.time.time", return_value=ts):
        assert verify_request("s3cret", sig, "GET", "/_ping", b"", ts) is True


def test_sign_request_uses_current_time_when_no_timestamp():
    with patch("vp_core.security.hmac.time.time", return_value=1234567890):
        _, ts = sign_request("s3cret", "POST", "/x", b"")
        assert ts == 1234567890


def test_verify_custom_window():
    sig, ts = sign_request("s3cret", "POST", "/x", b"hello", timestamp=1_000_000)
    # 10s old — inside custom 5s window? No.
    with patch("vp_core.security.hmac.time.time", return_value=1_000_010):
        assert verify_request("s3cret", sig, "POST", "/x", b"hello", ts, window_seconds=5) is False
    # 10s old — inside custom 15s window? Yes.
    with patch("vp_core.security.hmac.time.time", return_value=1_000_010):
        assert verify_request("s3cret", sig, "POST", "/x", b"hello", ts, window_seconds=15) is True

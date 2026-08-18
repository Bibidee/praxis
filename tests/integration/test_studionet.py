"""Opt-in wrapper for the persistent Studionet verification matrix."""
import os
import subprocess
import pytest


@pytest.mark.skipif(os.getenv("RUN_STUDIONET") != "1", reason="Set RUN_STUDIONET=1 for funded live verification")
def test_studionet_matrix():
    required = ("PRAXIS_CONTRACT", "PRAXIS_KEYSTORE", "PRAXIS_WALLET_PASSWORD")
    assert all(os.getenv(item) for item in required)
    result = subprocess.run(["node", "scripts/studionet_verify.mjs"], check=False, text=True, capture_output=True)
    print(result.stdout)
    assert result.returncode == 0, result.stderr
    assert '"exactSafety":true' in result.stdout

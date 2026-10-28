import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

PURGE_SCRIPT = Path(__file__).resolve().parents[2] / "ocr_purge" / "purge.sh"

pytestmark = pytest.mark.skipif(shutil.which("jq") is None, reason="purge.sh needs jq")

# Stands in for curl: the Keycloak token request gets a token, the API DELETE answers with
# the HTTP status given in STUB_DELETE_STATUS (the script reads it from the last line).
FAKE_CURL = """#!/bin/bash
case "$*" in
  *grant_type=client_credentials*) echo '{"access_token": "token"}' ;;
  *"-X DELETE"*) printf '%s\\n%s' "${STUB_DELETE_BODY}" "${STUB_DELETE_STATUS}" ;;
esac
"""


def _run_purge_script(tmp_path: Path, delete_status: str, delete_body: str = "") -> subprocess.CompletedProcess:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, content in (("curl", FAKE_CURL), ("sleep", "#!/bin/sh\n")):
        stub = bin_dir / name
        stub.write_text(content)
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)

    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "CLIENT_SECRET": "secret",
        "STUB_DELETE_STATUS": delete_status,
        "STUB_DELETE_BODY": delete_body,
    }
    return subprocess.run(["bash", str(PURGE_SCRIPT)], env=env, capture_output=True, text=True, timeout=30)


def test_purge_script_succeeds_on_the_204_the_delete_endpoint_returns(tmp_path):
    result = _run_purge_script(tmp_path, delete_status="204")

    assert result.returncode == 0, result.stdout
    assert "Purge réussie pour tous les statuts" in result.stdout


def test_purge_script_still_counts_the_deleted_tasks_of_a_200_response(tmp_path):
    result = _run_purge_script(tmp_path, delete_status="200", delete_body='[{"id": "a"}, {"id": "b"}]')

    assert result.returncode == 0, result.stdout
    assert "Total de tâches supprimées: 4" in result.stdout


def test_purge_script_fails_when_the_delete_endpoint_is_refused(tmp_path):
    result = _run_purge_script(tmp_path, delete_status="403")

    assert result.returncode == 1
    assert "Échecs pour les statuts" in result.stdout

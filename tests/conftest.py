import atexit
import os
import sys
import pytest


@pytest.fixture(autouse=True)
def _reset_contract_registry():
    yield
    try:
        import genlayer.gl.genvm_contracts as contracts
    except ImportError:
        return
    contracts.__known_contract__ = None


def warp_to(direct_vm, iso_timestamp: str) -> None:
    direct_vm.warp(iso_timestamp)
    gl = sys.modules.get("genlayer.gl")
    if gl is None: return
    raw = getattr(gl, "message_raw", None)
    if isinstance(raw, dict): raw["datetime"] = iso_timestamp
    message = getattr(gl, "message", None)
    nested = getattr(message, "raw", None)
    if isinstance(nested, dict): nested["datetime"] = iso_timestamp


if sys.platform == "win32":
    from gltest.direct import loader as _loader
    _leaked = []
    _unlink = os.unlink
    def _tolerant(path, *args, **kwargs):
        try: return _unlink(path, *args, **kwargs)
        except PermissionError: _leaked.append(os.fspath(path))
    _original = _loader._inject_message_to_fd0
    def _inject(vm):
        os.unlink = _tolerant
        try: return _original(vm)
        finally: os.unlink = _unlink
    _loader._inject_message_to_fd0 = _inject
    @atexit.register
    def _sweep():
        for path in _leaked:
            try: _unlink(path)
            except OSError: pass

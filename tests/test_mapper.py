from sockmap.mapper import probe_port, KNOWN
import pytest
def test_refuses_remote():
    with pytest.raises(ValueError):
        probe_port(80, host='8.8.8.8')
def test_known_ports():
    assert KNOWN[22] == 'ssh'
def test_local_probe_runs():
    res = probe_port(1)  # likely closed, returns None, must not raise
    assert res is None or 'port' in res

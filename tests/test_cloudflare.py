import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('coffee_cloudflare', Path(__file__).resolve().parents[1] / 'deployment/configure-cloudflare.py')
cloudflare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloudflare)


def test_route_preserves_every_unrelated_rule_and_setting():
    config = {'originRequest': {'connectTimeout': 30}, 'ingress': [{'hostname': '*.fusenv.com', 'service': 'http://wildcard:3000', 'originRequest': {'httpHostHeader': 'example.test'}}, {'hostname': 'other.example.com', 'path': '/api/.*', 'service': 'http://other:8080'}, {'service': 'http_status:404'}]}
    updated = cloudflare.route_config(config)
    assert updated['ingress'][0] == {'hostname': cloudflare.HOSTNAME, 'service': cloudflare.ORIGIN}
    assert updated['ingress'][1:] == config['ingress']
    assert updated['originRequest'] == config['originRequest']
    assert cloudflare.route_config(updated) == updated


def test_conflicting_route_stops_before_replacement():
    config = {'ingress': [{'hostname': cloudflare.HOSTNAME, 'service': 'http://different:3000'}, {'service': 'http_status:404'}]}
    with pytest.raises(RuntimeError, match='different tunnel route'):
        cloudflare.route_config(config)

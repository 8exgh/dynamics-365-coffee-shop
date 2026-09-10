import copy
import json
import os
import urllib.parse
import urllib.request

HOSTNAME = 'd365-coffee-shop.fusenv.com'
ORIGIN = 'http://192.168.4.56:3067'
ACCOUNT = 'be2484925dc7150169c09e6770fb7e38'
TUNNEL = '39498ef8-d3c6-4d42-9d0d-575835d98207'
API = 'https://api.cloudflare.com/client/v4'


def route_config(config):
    updated = copy.deepcopy(config)
    rules = updated.get('ingress')
    if not isinstance(rules, list) or not rules or rules[-1].get('hostname') is not None:
        raise RuntimeError('The existing tunnel must have an ingress list ending in a catch-all.')
    matches = [rule for rule in rules if rule.get('hostname') == HOSTNAME]
    if len(matches) > 1 or any(rule.get('service') != ORIGIN or rule.get('path') for rule in matches):
        raise RuntimeError('The coffee hostname already has a different tunnel route.')
    if not matches:
        updated['ingress'] = [{'hostname': HOSTNAME, 'service': ORIGIN}, *rules]
    before = [rule for rule in config['ingress'] if rule.get('hostname') != HOSTNAME]
    after = [rule for rule in updated['ingress'] if rule.get('hostname') != HOSTNAME]
    if before != after:
        raise RuntimeError('Unrelated tunnel configuration would change.')
    return updated


def main():
    dns_token = os.environ['CF_DNS_TOKEN']
    tunnel_token = os.environ['CF_TUNNEL_TOKEN']

    def request(token, path, method='GET', payload=None):
        body = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(API + path, data=body, method=method, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=40) as response:
            result = json.load(response)
        if not result.get('success'):
            raise RuntimeError('Cloudflare rejected the requested configuration change.')
        return result['result']

    zones = request(dns_token, '/zones?' + urllib.parse.urlencode({'name': 'fusenv.com'}))
    if len(zones) != 1:
        raise RuntimeError('Expected exactly one fusenv.com zone.')
    records_path = f"/zones/{zones[0]['id']}/dns_records"
    records = request(dns_token, records_path + '?' + urllib.parse.urlencode({'name': HOSTNAME}))
    target = f'{TUNNEL}.cfargotunnel.com'
    if len(records) > 1 or any(record['type'] != 'CNAME' or record['content'] != target for record in records):
        raise RuntimeError('The coffee hostname already has DNS belonging to a different service.')
    tunnel_path = f'/accounts/{ACCOUNT}/cfd_tunnel/{TUNNEL}/configurations'
    current = request(tunnel_token, tunnel_path)
    updated = route_config(current['config'])
    if updated != current['config']:
        latest = request(tunnel_token, tunnel_path)
        if latest['config'] != current['config']:
            raise RuntimeError('The shared tunnel changed during this operation. Rerun with the new configuration.')
        request(tunnel_token, tunnel_path, 'PUT', {'config': updated})
    record_body = {'type': 'CNAME', 'name': HOSTNAME, 'content': target, 'proxied': True, 'ttl': 1}
    if not records:
        request(dns_token, records_path, 'POST', record_body)
    elif not records[0].get('proxied'):
        request(dns_token, f"{records_path}/{records[0]['id']}", 'PUT', record_body)
    verified = request(tunnel_token, tunnel_path)['config']
    if verified != updated:
        raise RuntimeError('Tunnel read-back did not match the intended configuration.')
    dns = request(dns_token, records_path + '?' + urllib.parse.urlencode({'name': HOSTNAME}))
    if len(dns) != 1 or dns[0]['content'] != target or not dns[0]['proxied']:
        raise RuntimeError('DNS verification failed.')
    print(f'{HOSTNAME} routes to {ORIGIN}; {len(verified["ingress"]) - 1} other ingress rules preserved.')


if __name__ == '__main__':
    main()

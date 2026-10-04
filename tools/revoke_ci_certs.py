#!/usr/bin/env python3
"""Revoke the throw-away development certificates that CI signing leaves behind.

Every `xcodebuild -allowProvisioningUpdates` run on a fresh runner makes Apple issue a new
"Created via API" development certificate whose private key dies with the runner. They pile up
until the account hits its limit and signing fails. Personal and distribution certificates are
never touched. Needs ASC_KEY_ID, ASC_ISSUER_ID and the key in ASC_API_KEY_P8 (or ASC_KEY_PATH).
"""
import json, os, time, urllib.request, urllib.error
import jwt

kid, iss = os.environ['ASC_KEY_ID'], os.environ['ASC_ISSUER_ID']
key = os.environ.get('ASC_API_KEY_P8') or open(os.environ['ASC_KEY_PATH']).read()
now = int(time.time())
tok = jwt.encode({'iss': iss, 'iat': now, 'exp': now + 600, 'aud': 'appstoreconnect-v1'}, key, algorithm='ES256', headers={'kid': kid, 'typ': 'JWT'})

def call(method, path):
    r = urllib.request.Request('https://api.appstoreconnect.apple.com' + path, method=method, headers={'Authorization': 'Bearer ' + tok})
    try:
        with urllib.request.urlopen(r) as resp: return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()

st, body = call('GET', '/v1/certificates?limit=200')
certs = json.loads(body)['data']
orphans = [c for c in certs if c['attributes']['certificateType'] == 'DEVELOPMENT' and c['attributes'].get('displayName') == 'Created via API']
print(f'{len(certs)} certificates, {len(orphans)} CI leftovers')
for c in orphans:
    st, _ = call('DELETE', '/v1/certificates/' + c['id'])
    print('revoke', c['id'], st)

"""Put a build on the external TestFlight group (TF3, public link) and send it to beta review.
usage: asc_tf.py <buildNumber> [whatsNew text, zh-Hant]"""
import sys, json, time
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; TF3 = '695fec60-131b-49aa-9c81-550c15ff1399'
def call(m, p, b=None):
    st, tx = req(m, p, b); return st, (json.loads(tx) if tx.strip().startswith('{') else {})
bn = sys.argv[1]; notes = sys.argv[2] if len(sys.argv) > 2 else None
for k in range(40):      # the build takes a few minutes to finish processing after upload
    st, d = call('GET', f'/v1/builds?filter[app]={APP}&filter[version]={bn}&fields[builds]=version,processingState,expired')
    b = d.get('data') or []
    if b and b[0]['attributes']['processingState'] == 'VALID': break
    print('waiting for build', bn, b[0]['attributes']['processingState'] if b else 'not there yet'); time.sleep(30)
else: raise SystemExit('build never became VALID')
BUILD = b[0]['id']; print('build', bn, BUILD, 'VALID')
if notes:
    st, d = call('GET', f'/v1/builds/{BUILD}/betaBuildLocalizations')
    for l in d.get('data', []):
        st2, _ = call('PATCH', f"/v1/betaBuildLocalizations/{l['id']}", {'data': {'type': 'betaBuildLocalizations', 'id': l['id'], 'attributes': {'whatsNew': notes}}}); print('whatsNew', l['attributes']['locale'], st2)
st, d = call('POST', f'/v1/betaGroups/{TF3}/relationships/builds', {'data': [{'type': 'builds', 'id': BUILD}]}); print('add to TF3', st, json.dumps(d.get('errors', ''), ensure_ascii=False)[:300])
st, d = call('POST', '/v1/betaAppReviewSubmissions', {'data': {'type': 'betaAppReviewSubmissions', 'relationships': {'build': {'data': {'type': 'builds', 'id': BUILD}}}}}); print('beta review', st, (d.get('data') or {}).get('attributes') or json.dumps(d.get('errors', ''), ensure_ascii=False)[:400])
st, d = call('GET', f'/v1/builds/{BUILD}/buildBetaDetail'); print('state', (d.get('data') or {}).get('attributes'))
st, d = call('GET', f'/v1/betaGroups/{TF3}?fields[betaGroups]=name,publicLink,publicLinkEnabled'); print('group', (d.get('data') or {}).get('attributes'))

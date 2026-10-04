import sys, json, time
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; VID = 'fed92070-816f-4540-a87c-128f9011c636'
def call(m, p, body=None):
    st, tx = req(m, p, body); return st, (json.loads(tx) if tx.strip().startswith('{') else {})
# wait for screenshots to finish processing
for attempt in range(20):
    bad = 0; tot = 0
    st, locs = call('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')
    for l in locs['data']:
        st, sets = call('GET', f"/v1/appStoreVersionLocalizations/{l['id']}/appScreenshotSets?include=appScreenshots&limit=50")
        for s in sets.get('included', []):
            tot += 1; state = (s['attributes'].get('assetDeliveryState') or {}).get('state')
            if state != 'COMPLETE': bad += 1; err = (s['attributes'].get('assetDeliveryState') or {}).get('errors')
    print('screenshots', tot, 'not complete', bad)
    if bad == 0: break
    time.sleep(15)
if bad: print('screenshot problem', err); raise SystemExit(1)
if '--submit' not in sys.argv: raise SystemExit(0)
st, subs = call('GET', f'/v1/reviewSubmissions?filter[app]={APP}&filter[state]=READY_FOR_REVIEW,WAITING_FOR_REVIEW,IN_REVIEW,UNRESOLVED_ISSUES')
print('open submissions', [(s['id'], s['attributes']['state']) for s in subs.get('data', [])])
sub = next((s for s in subs.get('data', []) if s['attributes']['state'] == 'READY_FOR_REVIEW'), None)
if not sub:
    st, r = call('POST', '/v1/reviewSubmissions', {'data': {'type': 'reviewSubmissions', 'attributes': {'platform': 'IOS'}, 'relationships': {'app': {'data': {'type': 'apps', 'id': APP}}}}})
    print('create submission', st, json.dumps(r.get('errors', ''), ensure_ascii=False)[:600]); sub = r['data']
st, r = call('POST', '/v1/reviewSubmissionItems', {'data': {'type': 'reviewSubmissionItems', 'relationships': {'reviewSubmission': {'data': {'type': 'reviewSubmissions', 'id': sub['id']}}, 'appStoreVersion': {'data': {'type': 'appStoreVersions', 'id': VID}}}}})
print('add item', st, json.dumps(r.get('errors', ''), ensure_ascii=False)[:1500])
if st not in (200, 201): raise SystemExit(1)
st, r = call('PATCH', f"/v1/reviewSubmissions/{sub['id']}", {'data': {'type': 'reviewSubmissions', 'id': sub['id'], 'attributes': {'submitted': True}}})
print('submit', st, r.get('data', {}).get('attributes', {}).get('state'), json.dumps(r.get('errors', ''), ensure_ascii=False)[:1500])
st, v = call('GET', f'/v1/appStoreVersions/{VID}?fields[appStoreVersions]=versionString,appStoreState,appVersionState')
print('version state', v['data']['attributes'])

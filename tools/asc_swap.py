"""Swap the build (and optionally the screenshots) on the version waiting for review, then resubmit.
usage: asc_swap.py <buildNumber> [screenshotDir]"""
import sys, json, time, os, hashlib, urllib.request
sys.path.insert(0, '/root'); from asc_api import req
APP = '6782641107'; VID = os.environ.get('ASC_VID', 'fed92070-816f-4540-a87c-128f9011c636')
def call(m, p, b=None):
    st, tx = req(m, p, b); return st, (json.loads(tx) if tx.strip().startswith('{') else {})
def must(m, p, b=None):
    st, d = call(m, p, b)
    if st not in (200, 201, 204): print('!!', m, p, st, json.dumps(d.get('errors', d), ensure_ascii=False)[:800]); raise SystemExit(1)
    return d
bn = sys.argv[1]; shots = sys.argv[2] if len(sys.argv) > 2 else None
b = must('GET', f'/v1/builds?filter[app]={APP}&filter[version]={bn}&fields[builds]=version,processingState')['data']
assert b and b[0]['attributes']['processingState'] == 'VALID', b
BUILD = b[0]['id']
state = must('GET', f'/v1/appStoreVersions/{VID}?fields[appStoreVersions]=appStoreState')['data']['attributes']['appStoreState']; print('state', state)
if state not in ('WAITING_FOR_REVIEW', 'PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED'): print('not touching: state is', state); raise SystemExit(2)
if state == 'WAITING_FOR_REVIEW':
    for s in must('GET', f'/v1/reviewSubmissions?filter[app]={APP}&filter[state]=WAITING_FOR_REVIEW')['data']:
        d = must('PATCH', f"/v1/reviewSubmissions/{s['id']}", {'data': {'type': 'reviewSubmissions', 'id': s['id'], 'attributes': {'canceled': True}}}); print('cancel', d['data']['attributes']['state'])
    for k in range(30):
        state = must('GET', f'/v1/appStoreVersions/{VID}?fields[appStoreVersions]=appStoreState')['data']['attributes']['appStoreState']
        if state in ('PREPARE_FOR_SUBMISSION', 'DEVELOPER_REJECTED'): break
        time.sleep(6)
    print('state now', state)
must('PATCH', f'/v1/appStoreVersions/{VID}/relationships/build', {'data': {'type': 'builds', 'id': BUILD}})
print('build on version', must('GET', f'/v1/appStoreVersions/{VID}/build?fields[builds]=version')['data']['attributes']['version'])
def upload(set_id, path):
    data = open(path, 'rb').read()
    r = must('POST', '/v1/appScreenshots', {'data': {'type': 'appScreenshots', 'attributes': {'fileName': os.path.basename(path), 'fileSize': len(data)}, 'relationships': {'appScreenshotSet': {'data': {'type': 'appScreenshotSets', 'id': set_id}}}}})['data']
    for op in r['attributes']['uploadOperations']:
        q = urllib.request.Request(op['url'], data=data[op['offset']:op['offset'] + op['length']], method=op['method'])
        for h in op['requestHeaders']: q.add_header(h['name'], h['value'])
        urllib.request.urlopen(q).read()
    must('PATCH', f"/v1/appScreenshots/{r['id']}", {'data': {'type': 'appScreenshots', 'id': r['id'], 'attributes': {'uploaded': True, 'sourceFileChecksum': hashlib.md5(data).hexdigest()}}})
if shots:
    for l in must('GET', f'/v1/appStoreVersions/{VID}/appStoreVersionLocalizations')['data']:
        lc, lid = l['attributes']['locale'], l['id']
        for s in must('GET', f'/v1/appStoreVersionLocalizations/{lid}/appScreenshotSets?limit=50')['data']: must('DELETE', f"/v1/appScreenshotSets/{s['id']}")
        for typ, pre in (('APP_IPHONE_67', 'iphone'), ('APP_IPAD_PRO_3GEN_129', 'ipad')):
            sid = must('POST', '/v1/appScreenshotSets', {'data': {'type': 'appScreenshotSets', 'attributes': {'screenshotDisplayType': typ}, 'relationships': {'appStoreVersionLocalization': {'data': {'type': 'appStoreVersionLocalizations', 'id': lid}}}}})['data']['id']
            for i in range(1, 6): upload(sid, f'{shots}/{pre}_{i}.png')
        print('screenshots replaced', lc)

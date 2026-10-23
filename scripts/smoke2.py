import requests, json, time
B = 'http://127.0.0.1:8000'
tok = requests.post(B+'/api/auth/login', json={'email':'test@example.com','password':'password123'}).json()['access_token']
H = {'Authorization': f'Bearer {tok}'}
art = "WASHINGTON (Reuters) - The Federal Reserve held interest rates steady on Wednesday, saying it will be patient as it assesses how global developments affect the outlook for the U.S. economy. The central bank's policy statement offered reassurance that it remained on track to raise rates at some point this year. Fed Chair said inflation is expected to move back toward the 2 percent objective over the medium term."
head = "Fed holds rates steady, signals patience on future hikes"
t0 = time.time()
r = requests.post(B+'/api/predict', headers=H, json={'headline': head, 'article_content': art}, timeout=120)
print('predict', r.status_code, f'{time.time()-t0:.1f}s')
d = r.json()
print(json.dumps({k: (d.get(k) if not isinstance(d.get(k), (list, dict)) else (d[k][:3] if isinstance(d[k], list) else list(d[k].keys()))) for k in ['ml_prediction','ml_confidence','model_name','verification_status','verification_summary','final_assessment']}, indent=1))
print('sources:', len(d.get('sources', [])))
if d.get('sources'): print(d['sources'][0])
r = requests.get(B+'/api/predictions', headers=H)
print('history', len(r.json()))
r = requests.get(B+'/api/dashboard', headers=H)
print('dashboard', {k: v for k, v in r.json().items() if k != 'recent'})

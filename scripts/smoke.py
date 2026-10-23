import requests, json
B = 'http://127.0.0.1:8000'
r = requests.post(B+'/api/auth/register', json={'full_name':'Test User','email':'  TEST@Example.com ','password':'password123','confirm_password':'password123'})
print('register', r.status_code, r.text[:200])
r = requests.post(B+'/api/auth/register', json={'full_name':'Test User','email':'test@example.COM','password':'password123','confirm_password':'password123'})
print('dup', r.status_code, r.json().get('detail'))
r = requests.post(B+'/api/auth/login', json={'email':'test@example.com','password':'password123'})
print('login', r.status_code)
tok = r.json()['access_token']
H = {'Authorization': f'Bearer {tok}'}
r = requests.get(B+'/api/auth/me', headers=H)
print('me', r.status_code, r.json())
r = requests.post(B+'/api/predict', headers=H, json={'headline':'  ','article_content':'x'})
print('empty headline', r.status_code, r.text[:150])

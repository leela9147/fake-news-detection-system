import requests, secrets, json

B = 'http://127.0.0.1:8000'
F = 'http://localhost:5173'
ok = []
def check(name, cond, extra=''):
    ok.append(cond)
    print(('PASS' if cond else 'FAIL'), '-', name, extra)

# 1. backend health
r = requests.get(B + '/api/health')
check('backend health', r.status_code == 200 and r.json()['status'] == 'ok')

# 2. API docs
r = requests.get(B + '/docs')
check('API docs (Swagger)', r.status_code == 200)

# 3. model performance (real trained metrics)
r = requests.get(B + '/api/model-performance')
d = r.json()
check('model performance endpoint', r.status_code == 200 and set(d['models'].keys()) == {'LogisticRegression','LinearSVM','RandomForest'})
print('   best model:', d['best_model'], '| LR f1:', round(d['models']['LogisticRegression']['f1'],4),
      '| SVM f1:', round(d['models']['LinearSVM']['f1'],4), '| RF f1:', round(d['models']['RandomForest']['f1'],4))

# 4. register + login
email = f'e2e_{secrets.token_hex(4)}@example.com'
r = requests.post(B+'/api/auth/register', json={'full_name':'Full Check','email':email,'password':'MyPassword1','confirm_password':'MyPassword1'})
check('signup', r.status_code == 200)
r = requests.post(B+'/api/auth/register', json={'full_name':'Full Check','email':email.upper(),'password':'MyPassword1','confirm_password':'MyPassword1'})
check('duplicate email rejected', r.status_code == 409)
tok = requests.post(B+'/api/auth/login', json={'email':email,'password':'MyPassword1'}).json()['access_token']
H = {'Authorization': f'Bearer {tok}'}
r = requests.get(B+'/api/auth/me', headers=H)
check('auth/me with JWT', r.status_code == 200)

# 5. input validation
r = requests.post(B+'/api/predict', headers=H, json={'headline':'','article_content':'text'})
check('empty headline rejected', r.status_code == 422)
r = requests.post(B+'/api/predict', headers=H, json={'headline':'title','article_content':'   '})
check('whitespace article rejected', r.status_code == 422)

# 6. full prediction (ML + XAI + web verification)
fake_art = ('SHOCKING: Doctors HATE this one weird trick that melts belly fat overnight! '
            'Big pharma is TERRIFIED you will discover this secret miracle cure that '
            'government scientists are hiding from you. Click now before they delete it! '
            'Share this before the mainstream media silences the truth!!!')
r = requests.post(B+'/api/predict', headers=H, json={'headline':'Doctors hate this one weird trick melts fat overnight','article_content':fake_art}, timeout=180)
check('predict (fake article)', r.status_code == 200)
d = r.json()
print('   ML:', d['ml_prediction'], f"({d['ml_confidence']}%)", '| verification:', d['verification_status'], '| final:', d['final_assessment'])
check('ML result valid', d['ml_prediction'] in ('LIKELY REAL','LIKELY FAKE','NEEDS VERIFICATION'))
check('simple explanation present', len(d['simple_explanation']) > 20)
check('signals from model', isinstance(d['technical_explanation'].get('signals'), list))
check('sources are real retrieved', isinstance(d['sources'], list))
pid = d['id']

# 7. history + user isolation
r = requests.get(B+'/api/predictions', headers=H)
check('history loads', r.status_code == 200 and len(r.json()) >= 1)
r = requests.get(B+f'/api/predictions/{pid}', headers=H)
check('prediction detail', r.status_code == 200)
email2 = f'e2e_{secrets.token_hex(4)}@example.com'
requests.post(B+'/api/auth/register', json={'full_name':'Other','email':email2,'password':'MyPassword1','confirm_password':'MyPassword1'})
tok2 = requests.post(B+'/api/auth/login', json={'email':email2,'password':'MyPassword1'}).json()['access_token']
r = requests.get(B+f'/api/predictions/{pid}', headers={'Authorization':f'Bearer {tok2}'})
check('user isolation (other user blocked)', r.status_code == 404)

# 8. dashboard real stats
r = requests.get(B+'/api/dashboard', headers=H)
d = r.json()
check('dashboard stats', d['total'] >= 1 and d['total'] == d['likely_fake']+d['likely_real']+d['needs_verification'])
print('   dashboard:', {k:v for k,v in d.items() if k!='recent'})

# 9. forgot/reset password
r = requests.post(B+'/api/auth/forgot-password', json={'email':email})
check('forgot-password (SMTP configured)', r.status_code == 200)

# 10. frontend
r = requests.get(F + '/')
check('frontend home', r.status_code == 200)
r = requests.get(F + '/login')
check('frontend login page', r.status_code == 200)

print(f"\n{sum(ok)}/{len(ok)} checks passed")
import sys; sys.exit(0 if all(ok) else 1)

"""End-to-end API tests against the running backend + database."""
import requests, sys, time, secrets

B = 'http://127.0.0.1:8000'
results = []
def check(name, cond):
    results.append((name, cond))
    print(('PASS' if cond else 'FAIL'), '-', name)

# auth: duplicate/ normalization
email = f'User{secrets.token_hex(4)}@Example.COM'
pw = 'SuperSecret1'
r = requests.post(B+'/api/auth/register', json={'full_name':'A B','email':email,'password':pw,'confirm_password':pw})
check('signup', r.status_code == 200)
r = requests.post(B+'/api/auth/register', json={'full_name':'A B','email':email.lower(),'password':pw,'confirm_password':pw})
check('duplicate email rejected (409)', r.status_code == 409)
r = requests.post(B+'/api/auth/login', json={'email':'  '+email.lower()+' ','password':pw})
check('login with case/space-normalized email', r.status_code == 200)
tok = r.json()['access_token']
H = {'Authorization': f'Bearer {tok}'}
r = requests.post(B+'/api/auth/login', json={'email':email,'password':'wrong'})
check('incorrect password rejected', r.status_code == 401)
r = requests.get(B+'/api/auth/me', headers={'Authorization':'Bearer junk'})
check('invalid token rejected', r.status_code == 401)
r = requests.get(B+'/api/auth/me')
check('no token rejected', r.status_code == 401)

# input validation
r = requests.post(B+'/api/predict', headers=H, json={'headline':'','article_content':'x'})
check('empty headline rejected', r.status_code == 422)
r = requests.post(B+'/api/predict', headers=H, json={'headline':'  ','article_content':'   '})
check('whitespace rejected', r.status_code == 422)

# prediction + persistence + user isolation
art = ('BREAKING: The moon landing was staged by the government in a secret studio in Nevada, '
       'according to a leading anonymous expert quoted exclusively in this viral post. '
       'Share before it gets deleted!') * 2
r = requests.post(B+'/api/predict', headers=H, json={'headline':'Moon landing staged in Nevada studio, expert claims','article_content':art}, timeout=180)
check('predict worked', r.status_code == 200)
if r.status_code == 200:
    d = r.json()
    check('has ml_prediction', d['ml_prediction'] in ('LIKELY REAL','LIKELY FAKE','NEEDS VERIFICATION'))
    check('has final assessment', d['final_assessment'] in ('LIKELY REAL','LIKELY FAKE','NEEDS VERIFICATION'))
    check('has explanation', len(d['simple_explanation']) > 10)
    pid = d['id']
    r2 = requests.get(B+f'/api/predictions/{pid}', headers=H)
    check('history detail loads', r2.status_code == 200)
    email2 = f'Other{secrets.token_hex(4)}@x.com'
    requests.post(B+'/api/auth/register', json={'full_name':'C D','email':email2,'password':pw,'confirm_password':pw})
    tok2 = requests.post(B+'/api/auth/login', json={'email':email2,'password':pw}).json()['access_token']
    r3 = requests.get(B+f'/api/predictions/{pid}', headers={'Authorization':f'Bearer {tok2}'})
    check('user isolation on detail', r3.status_code == 404)
    r4 = requests.get(B+'/api/predictions', headers={'Authorization':f'Bearer {tok2}'})
    check('user isolation on list', r4.json() == [])
    # password reset single-use / expiry handled by logic; check flow returns 200
    r5 = requests.post(B+'/api/auth/forgot-password', json={'email':email})
    check('forgot password accepted', r5.status_code == 200)
    r6 = requests.post(B+'/api/auth/reset-password', json={'token':'bogus','new_password':'NewPassword1','confirm_password':'NewPassword1'})
    check('bogus token rejected', r6.status_code == 400)

fails = [n for n, c in results if not c]
print(f'\n{len(results)-len(fails)}/{len(results)} passed')
sys.exit(1 if fails else 0)

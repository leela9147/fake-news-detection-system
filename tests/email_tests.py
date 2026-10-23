"""Tests for the email service and forgot-password flow (no real SMTP needed)."""
import os, sys, secrets
from unittest import mock

sys.path.insert(0, 'D:/documents/FNDS/backend')
sys.path.insert(0, 'D:/documents/FNDS')

results = []
def check(name, cond):
    results.append((name, cond))
    print(('PASS' if cond else 'FAIL'), '-', name)

# 1. send_email raises EmailNotConfiguredError when SMTP not set
from app import email_service
with mock.patch.object(email_service, 'SMTP_HOST', ''):
    try:
        email_service.send_email(to_email='a@b.c', subject='s', body='b')
        check('unconfigured SMTP raises', False)
    except email_service.EmailNotConfiguredError:
        check('unconfigured SMTP raises', True)

# 2. send_email delivers through smtplib with correct recipient/subject/sender
sent = {}
class FakeSMTP:
    def __init__(self, host, port, timeout=None): sent['host'], sent['port'] = host, port
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def ehlo(self): pass
    def starttls(self): pass
    def login(self, u, p): sent['login'] = (u, p)
    def send_message(self, msg): sent['msg'] = msg

with mock.patch.object(email_service, 'SMTP_HOST', 'smtp.example.com'), \
     mock.patch.object(email_service, 'SMTP_FROM_EMAIL', 'noreply@example.com'), \
     mock.patch.object(email_service, 'SMTP_USERNAME', 'user'), \
     mock.patch.object(email_service, 'SMTP_PASSWORD', 'pass'), \
     mock.patch('smtplib.SMTP', FakeSMTP):
    email_service.send_password_reset_email('victim@example.com', 'http://x/reset?token=abc')
check('email delivered via SMTP', sent['msg']['To'] == 'victim@example.com')
check('sender set', sent['msg']['From'] == 'noreply@example.com')
check('reset link in body', 'http://x/reset?token=abc' in sent['msg'].get_content())

# 3. forgot-password with SMTP unconfigured -> 503 (no false "sent" claim)
import requests
B = 'http://127.0.0.1:8000'
r = requests.post(B+'/api/auth/forgot-password', json={'email': 'whoever@example.com'})
check('unconfigured forgot-password returns 503', r.status_code == 503)
check('503 message is safe', 'unavailable' in r.json()['detail'].lower())

fails = [n for n, c in results if not c]
print(f'\n{len(results)-len(fails)}/{len(results)} passed')
sys.exit(1 if fails else 0)

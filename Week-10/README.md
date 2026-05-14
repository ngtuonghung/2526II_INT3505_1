# Week-10: Auth API Security & Monitoring Demo

Simple Flask auth API with JWT, rate limiting, WAF (XSS sanitization), and suspicious-event logging.

## Setup

```bash
pip install -r requirements.txt
cd Week-10
python app.py
```

Server runs at `http://localhost:5000`.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | None | Register user |
| POST | `/auth/login` | None | Login, returns JWT |
| GET | `/me` | Bearer JWT | Current user profile |

## Security features

- **JWT**: HS256, 1-hour expiry
- **Password hashing**: werkzeug `pbkdf2:sha256`
- **Rate limiting**: login 5/min, register 3/min
- **Lockout**: 5 failed logins triggers 15-min block
- **WAF**: HTML-escapes `< > " ' &` in `username` and `display_name`; logs XSS probes
- **Logging**: `app.log` records only suspicious events (failed logins, lockouts, rate-limit hits, XSS attempts)

## Try it

Register:

```bash
curl -s -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Secret123","display_name":"Alice"}'
```

Login:

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Secret123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

Profile:

```bash
curl -s http://localhost:5000/me -H "Authorization: Bearer $TOKEN"
```

XSS probe (display_name will be escaped in response):

```bash
curl -s -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","password":"Pass12345","display_name":"<script>alert(1)</script>"}'
```

Trigger lockout (run 6 times with wrong password, then check app.log):

```bash
for i in {1..6}; do
  curl -s -X POST http://localhost:5000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"alice","password":"wrong"}'; echo
done
```

## Log format

```
2026-05-14 10:00:01 | WARNING | 127.0.0.1 | LOGIN_FAILED | username=alice attempts=1
2026-05-14 10:00:05 | WARNING | 127.0.0.1 | ACCOUNT_LOCKED | username=alice
2026-05-14 10:00:10 | WARNING | 127.0.0.1 | XSS_ATTEMPT | field=display_name value='<script>...'
```

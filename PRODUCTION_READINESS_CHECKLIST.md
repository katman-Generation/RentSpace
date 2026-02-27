# Production Readiness Checklist

Current status: **Not ready for public launch**. Suitable for limited beta after fixing critical items.

## Critical (Must Fix Before Launch)

- [ ] Fix register auto-login bug (uses email where username is required).
  - File: `frontend/rentspace/src/context/AuthContext.jsx`
  - Why: New users can fail immediate login after registration.

- [ ] Add API tests for auth and authorization.
  - Files currently empty: `rentspace/users/tests.py`, `rentspace/spaces/tests.py`
  - Why: No regression protection for login/register/profile and owner-only space updates.

- [ ] Add rate limiting/throttling to auth and write endpoints.
  - File: `rentspace/rentspace/settings.py` (`REST_FRAMEWORK` has no throttles)
  - Why: Brute-force and abuse risk on login/register/create/update.

## High Priority

- [ ] Tighten authentication defaults.
  - File: `rentspace/rentspace/settings.py`
  - Current: default auth is `SessionAuthentication`, default permission is `AllowAny`.
  - Why: You mostly use JWT explicitly on views; permissive defaults are risky for future endpoints.

- [ ] Remove debug printing from register endpoint.
  - File: `rentspace/users/views.py`
  - Why: `print(serializer.errors)` can leak data into logs.

- [ ] Decide and document phone number privacy policy.
  - File: `rentspace/spaces/serializers.py`
  - Why: `owner_phone` is returned on space APIs and can be scraped.

## Medium Priority

- [ ] Clarify and unify auth URL structure.
  - Files: `rentspace/rentspace/urls.py`, `rentspace/users/urls.py`
  - Why: Both `/api/auth/login/` and `/api/login/` exist; this can confuse clients and ops.

- [ ] Restrict localhost CORS defaults in production env.
  - File: `rentspace/rentspace/settings.py`
  - Why: default now allows localhost origins unless overridden by env.

- [ ] Add health checks and error monitoring.
  - Why: No visible Sentry/log-alert wiring; production failures may go unnoticed.

## Verification Gate (Run Before Every Deploy)

```bash
# Frontend
cd frontend/rentspace
npm run lint
npm run build

# Backend
cd ../../rentspace
source ../env/bin/activate
python manage.py check
python manage.py test
```

## Suggested Launch Plan

1. Fix critical items and add minimum automated tests.
2. Run a private beta (10-30 users).
3. Track failures/abuse for 1-2 weeks.
4. Open public onboarding after stability metrics are acceptable.

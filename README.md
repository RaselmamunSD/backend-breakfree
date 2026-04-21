# Break Free Backend (Django + DRF)

Backend API for Flutter app integration with JWT authentication, admin control, Redis/Celery support, and PostgreSQL/SQLite switch.

## Stack
- Django
- Django REST Framework
- JWT (SimpleJWT)
- SQLite (default) or PostgreSQL
- Redis + Celery
- Postman collection

## Quick Start
1. Create and activate virtual environment.
2. Install packages:
   - `pip install -r requirements.txt`
3. Copy environment file:
   - `.env.example` to `.env`
4. Run migrations:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
5. Create super admin:
   - `python manage.py createsuperuser`
6. Run server:
   - `python manage.py runserver`

## API Endpoints
- Auth:
  - `POST /api/auth/register/`
  - `POST /api/auth/signup/send-otp/`
  - `POST /api/auth/signup/verify-otp/`
  - `POST /api/auth/signup/complete/`
  - `POST /api/auth/login/`
  - `POST /api/auth/firebase-login/` (Google/Apple via Firebase ID token)
  - `POST /api/auth/forgot-password/send-otp/`
  - `POST /api/auth/forgot-password/verify-otp/`
  - `POST /api/auth/forgot-password/reset/`
  - `POST /api/auth/refresh/`
  - `GET/PATCH /api/auth/me/`
- Wellness:
  - `/api/moods/`
  - `/api/journals/`
  - `/api/breathing-sessions/`
  - `/api/habits/`
  - `/api/subscription-plans/`
  - `/api/my-subscriptions/`
  - `/api/preferences/`
  - `/api/profile/dashboard/`
- Onboarding (JWT required):
  - `GET /api/onboarding/status/`
  - `POST /api/onboarding/safety/` — body: `{"agreed": true, "content_version": "1.0"}`
  - `GET /api/onboarding/subscription-tiers/`
  - `POST /api/onboarding/subscription-tier/` — body: `{"tier_slug": "quiet-peaks"}`
  - `GET /api/onboarding/programs/`
  - `POST /api/onboarding/program/` — body: `{"program_slug": "foundation"}`
- Onboarding list payloads match Figma copy: tiers include `frequency_badge` + `display_line` (e.g. `RARE: Quiet Peaks`); programs include `journey_badge` + `display_title` (e.g. `14 DAYS OF GENTLE GROWTH: The Foundation`).

## API Docs
- Swagger: `/api/docs/swagger/`
- Redoc: `/api/docs/redoc/`
- OpenAPI schema: `/api/schema/`

## Celery
- Start worker:
  - `celery -A config worker -l info`

## Firebase Social Login (Google + Apple)
1. Enable Google and Apple sign-in providers in Firebase Authentication.
2. Download Firebase service account JSON key.
3. Set `FIREBASE_CREDENTIALS_PATH` in `.env`.
4. From Flutter, complete Firebase sign-in and send Firebase `idToken` to:
   - `POST /api/auth/firebase-login/`
   - Body:
     - `id_token`: Firebase ID token
     - `provider`: `google.com` or `apple.com` (optional)
5. Backend verifies token and returns Django JWT (`access`, `refresh`) for API calls.

# Local Services Marketplace

Local Services Marketplace ek Django-based web application hai jo local customers ko nearby service providers se connect karne ke liye banaya gaya hai. Customer services browse karke booking request bhej sakta hai, aur provider apni services publish karke bookings manage kar sakta hai.

## Problem

Local services jaise plumbing, electrical work, cleaning, painting, carpentry aur gardening ke liye customers ko reliable provider dhoondhne, price compare karne aur appointment book karne me difficulty hoti hai. Providers ke paas apni services, experience aur availability dikhane ke liye ek central platform nahi hota.

## Proposed Solution

Application ek two-sided marketplace provide karti hai:

- Customers categories aur available services browse kar sakte hain.
- Service providers apna provider profile aur service listings create kar sakte hain.
- Customers date, time aur instructions ke saath booking request bhej sakte hain.
- Completed booking ke baad customer rating aur review de sakta hai.
- Authenticated users ke liye customer aur provider dashboards available hain.

## Current Features

### Customer features

- User registration aur login/logout
- Customer dashboard
- Service listing aur category filter
- Service detail page with price, provider aur reviews
- Date/time ke saath service booking
- My Bookings page
- Future-date validation, slot conflict checks aur customer cancellation
- Favorites aur My Favorites page
- Completed services ke liye rating aur review
- Real in-app notifications with unread count
- Contact form

### Provider features

- Provider account registration with category, rate, service area, description aur experience
- Provider dashboard
- Service add karna with description, price, category, location aur optional image
- Provider ke active services aur bookings dekhna
- Booking confirm, reject, start, complete aur status notifications
- Completed bookings se earnings summary
- Provider rating/review pages
- Recurring weekly availability slots

### Platform features

- Django authentication and session-based access control
- SQLite database
- Django admin support
- Responsive templates and shared static CSS (`static/css/home.css` powers the home page)
- Booking statuses: pending, confirmed, in progress, completed aur cancelled
- Optional Razorpay order/webhook integration; default local flow pay-after-service hai
- WebSocket chat routing with participant authorization and persisted messages
- Email notification hooks using console backend locally and SMTP settings in production
- Sample data/create scripts available

## Feature Status

| Area | Status | Notes |
| --- | --- | --- |
| Authentication | Complete | Registration, login, logout aur role-based redirect implemented |
| Customer dashboard | Complete | Booking counts, total spent aur recent bookings |
| Provider dashboard | Complete | Services, bookings, earnings aur rating summary |
| Service marketplace | Complete | Listing, detail, category filter aur provider service creation |
| Home page | Complete | Featured services, categories aur top rated providers real database data se render hote hain |
| Booking creation | Complete | Booking request save hoti hai with date, time aur notes |
| Booking management | Complete | Provider transitions aur customer future pending/confirmed cancellation |
| Reviews | Complete | Completed booking guard, unique constraint, stored provider rating/count |
| Chat | Complete | ASGI routing, participant authorization and persisted messages; requires ASGI server |
| Search | Complete | Name, description, category, location/provider area, filters and pagination |
| Notifications | Complete | In-app records, unread count and email trigger hooks |
| Payments | Partial | Razorpay order/webhook endpoints; default documented pay-after-service flow |
| Favorites | Complete | Unique model, toggle endpoint, detail UI and favorites page |
| Provider availability calendar | Complete for recurring schedule | Provider can add weekly slots and bookings enforce them; date-specific exceptions are future work |
| Security/config | Complete for baseline | Env config, secure cookie settings and logging; production env must enable HTTPS redirect |
| Tests | Partial | Core workflow tests present; broader browser/payment/WebSocket coverage remains |

## Project Structure

```text
cityservices/
├── accounts/       # Users, profiles, authentication and dashboards
├── services/       # Categories, services and service browsing
├── bookings/       # Bookings, status transitions and payments
├── reviews/        # Ratings and reviews
├── chat/           # Persisted authorized WebSocket chat
├── cityservices/   # Project settings, root URLs and WSGI/ASGI config
├── static/         # Shared CSS
├── templates/      # Shared pages such as home, about and contact
├── db.sqlite3      # Local development database
├── manage.py       # Django management entry point
├── create_sample_services.py
└── cleanup_services.py
```

## Requirements

- Python 3.10 or newer recommended
- Django 5.2.x
- Pillow, if image uploads are used
- Channels and channels-redis (Redis is optional while the configured development layer is in-memory)
- python-decouple for environment configuration
- razorpay SDK for optional online payments

Pinned dependencies `requirements.txt` me hain. Fresh setup:

```bash
python -m pip install -r requirements.txt
copy .env.example .env
```

Local `.env` me `DEBUG=True` rakhein. Production me strong `SECRET_KEY`, `DEBUG=False`, real `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT=True` aur SMTP/Razorpay values set karein.

## Local Setup

Project ke Django root me jaayein:

```bash
cd cityservices
```

Migrations apply karein:

```bash
python manage.py migrate
```

Optional admin user banayein:

```bash
python manage.py createsuperuser
```

Development server start karein:

```bash
python manage.py runserver
```

Application normally `http://127.0.0.1:8000/` par available hogi.

## Main URLs

- `/` - Home page
- `/services/` - Available services
- `/services/add/` - Provider service creation
- `/accounts/register/` - Registration
- `/accounts/login/` - Login
- `/accounts/dashboard/` - Provider dashboard
- `/accounts/user-dashboard/` - Customer dashboard
- `/bookings/my/` - Customer bookings
- `/bookings/provider/` - Provider booking actions
- `/accounts/notifications/` - Notifications
- `/services/favorites/` - My Favorites
- `/reviews/provider/<id>/` - Provider reviews
- `/chat/<user_id>/` - Authorized participant chat page
- `/admin/` - Django admin

## Typical User Flow

1. Customer register/login karta hai.
2. Customer service list me category select karke service detail open karta hai.
3. Customer date, time, contact details aur instructions ke saath booking request submit karta hai.
4. Booking initially `pending` status me save hoti hai.
5. Completed booking ke baad customer review aur rating submit kar sakta hai.
6. Provider register karke service add karta hai aur dashboard se bookings/earnings dekhta hai.

## Known Limitations and Next Steps

Current limitations:

- Payment flow intentionally pay-after-service hai unless Razorpay credentials are configured; booking confirmation is not blocked by payment.
- `near_me` is a text area match, not GPS distance calculation.
- Availability is a recurring weekly model; date-specific exceptions and a richer calendar editor are future work.
- Development chat uses an in-memory channel layer. Configure Redis-backed `CHANNEL_LAYERS` for multi-process production deployment.
- S3/cloud media storage is not installed by default. For production, optionally add `django-storages[boto3]`, set `DEFAULT_FILE_STORAGE`/`STORAGES`, bucket credentials and media CDN settings.
- Broader integration/browser tests for Razorpay callbacks, WebSockets and email delivery should be added before production launch.

## Verification

Project checks aur commands hamesha `cityservices` directory ke andar se run karein:

```bash
python manage.py check
python manage.py check --deploy
python manage.py showmigrations
python manage.py test
```

`check --deploy` local `.env` me `SECURE_SSL_REDIRECT=False` hone par warning de sakta hai; production me ise `True` set karein. Media files local development me `media/` ke andar serve hoti hain.
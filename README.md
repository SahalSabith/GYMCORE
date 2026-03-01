# IronCore Gym Management Platform

A full-stack Django gym management platform with role-based access control (Admin / Trainer / Member), custom user model, and a dark Tailwind CSS UI.

---

## Quick Start

### 1. Clone & set up virtual environment
```bash
git clone <repo>
cd gymplatform
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Apply migrations
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

### 3. Create an Admin superuser
```bash
python manage.py createsuperuser
```
Then visit `/admin/` and manually set the user's **role** to `ADMIN`.

### 4. Run the development server
```bash
python manage.py runserver
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Project Structure
```
gymplatform/
├── gymcore/             # Django project config (settings, urls, wsgi)
├── accounts/            # Custom user model, auth views, forms, decorators
│   ├── models.py        # User extends AbstractUser
│   ├── forms.py         # Registration, Login, ProfileUpdate forms
│   ├── views.py         # CBVs: Register, Login, Logout, Profile, ProfileEdit
│   ├── decorators.py    # role_required, admin_required, trainer_required, member_required
│   ├── urls.py
│   └── templates/accounts/
│       ├── login.html
│       ├── register.html
│       ├── profile.html
│       └── profile_edit.html
├── dashboard/           # Role-specific dashboards
│   ├── views.py
│   ├── urls.py
│   └── templates/dashboard/
│       ├── admin.html
│       ├── trainer.html
│       └── member.html
├── templates/           # Shared templates
│   ├── base.html
│   └── partials/
│       ├── navbar.html
│       ├── sidebar.html
│       └── messages.html
├── static/              # CSS / JS assets
├── media/               # Uploaded files (profile photos)
└── manage.py
```

---

## Switching to PostgreSQL
In `gymcore/settings.py`, comment out the SQLite block and uncomment the PostgreSQL section:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gymplatform',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## User Roles

| Role    | Created via         | Dashboard URL      |
|---------|---------------------|--------------------|
| Admin   | Django admin panel  | `/dashboard/admin/`   |
| Trainer | Registration form   | `/dashboard/trainer/` |
| Member  | Registration form   | `/dashboard/member/`  |

Role decorators in `accounts/decorators.py` enforce strict access — trying to hit another role's dashboard redirects with a flash message.

---

## Security Notes
- Custom user model uses **email as USERNAME_FIELD**.
- Passwords hashed with Django's default PBKDF2.
- CSRF protection on all POST forms.
- `login_required` + `role_required` on every dashboard view.
- Profile photo uploads validated via `Pillow`.
- In production: set `DEBUG=False`, use a real `SECRET_KEY` via environment variable, and configure `ALLOWED_HOSTS`.

---

## Next Steps (extend the platform)
- `TrainerMember` through-model to formally assign members to trainers.
- Workout plans & session logging.
- Membership billing / subscription tracking.
- Attendance system.

# IronForge — New Modules Setup Guide

This documents all 5 new modules added to the existing Gym Management Platform.

---

## Apps Created

| App | Command | Purpose |
|-----|---------|---------|
| `memberships` | already exists | Membership plans & subscriptions |
| `trainers` | already exists | Trainer profiles & assignments |
| `workouts` | already exists | Workout plans & tracking |
| `diet` | already exists | Diet plans & meals |
| `sessions_booking` | already exists | Personal training session booking |

---

## Step 1: Register all apps in settings.py

In `gymcore/settings.py`, `INSTALLED_APPS` must include:

```python
INSTALLED_APPS = [
    # ... django apps ...
    'accounts',
    'dashboard',
    'memberships',
    'trainers',
    'workouts',
    'diet',
    'sessions_booking',
]
```

---

## Step 2: Add URL routes in gymcore/urls.py

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('memberships/', include('memberships.urls', namespace='memberships')),
    path('trainers/', include('trainers.urls', namespace='trainers')),
    path('workouts/', include('workouts.urls', namespace='workouts')),
    path('diet/', include('diet.urls', namespace='diet')),
    path('sessions/', include('sessions_booking.urls', namespace='sessions')),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Step 3: Run migrations

```bash
python manage.py makemigrations memberships
python manage.py makemigrations trainers
python manage.py makemigrations workouts
python manage.py makemigrations diet
python manage.py makemigrations sessions_booking
python manage.py migrate
```

---

## Module 1: Memberships — `memberships/`

**URL prefix:** `/memberships/`

| URL | View | Access |
|-----|------|--------|
| `/memberships/plans/` | `PlanListView` | All |
| `/memberships/plans/<id>/subscribe/` | `SubscribeView` | Member |
| `/memberships/my/` | `MySubscriptionView` | Member |
| `/memberships/all/` | `AdminSubscriptionListView` | Admin |

**Workflow:**
1. Admin creates plans via Django admin panel (`/admin/`)
2. Members browse plans at `/memberships/plans/`
3. Member clicks Subscribe → chooses start date → `end_date` auto-calculated from `plan.duration_days`
4. Expired status shown when `today > end_date`

---

## Module 2: Trainers — `trainers/`

**URL prefix:** `/trainers/`

| URL | View | Access |
|-----|------|--------|
| `/trainers/` | `TrainerListView` | All |
| `/trainers/<id>/` | `TrainerDetailView` | All |
| `/trainers/my-profile/` | `MyTrainerProfileView` | Trainer |
| `/trainers/my-profile/edit/` | `TrainerProfileEditView` | Trainer |
| `/trainers/my-trainer/` | `MyTrainerView` | Member |
| `/trainers/assign/` | `AssignTrainerView` | Admin |
| `/trainers/assignments/` | `AssignmentListView` | Admin |
| `/trainers/assignments/<id>/delete/` | `DeleteAssignmentView` | Admin |

**Workflow:**
1. Trainer registers → goes to `/trainers/my-profile/edit/` to fill bio, experience, specialization
2. Admin assigns a trainer to a member via `/trainers/assign/`
3. Member sees their trainer at `/trainers/my-trainer/`

---

## Module 3: Workouts — `workouts/`

**URL prefix:** `/workouts/`

| URL | View | Access |
|-----|------|--------|
| `/workouts/my-plans/` | `TrainerWorkoutListView` | Trainer |
| `/workouts/create/` | `CreateWorkoutPlanView` | Trainer |
| `/workouts/<id>/add-day/` | `AddWorkoutDayView` | Trainer |
| `/workouts/<id>/detail/` | `WorkoutPlanDetailView` | Trainer |
| `/workouts/my-workouts/` | `MemberWorkoutView` | Member |
| `/workouts/complete/<id>/` | `MarkCompleteView` | Member |
| `/workouts/history/` | `WorkoutHistoryView` | Member |

**Workflow:**
1. Trainer creates plan → selects member → adds workout days with exercises
2. Member views plan at `/workouts/my-workouts/`
3. Member taps ✓ button to mark exercises complete for today
4. History tracked in `WorkoutCompletion` model

**Key model notes:**
- `WorkoutPlan.description` (not `notes`) — this field exists in the model
- `WorkoutDay.notes` — used for focus area (e.g. "Chest & Triceps")
- `Exercise` has `sets`, `reps` (CharField), `instructions`, `order`

---

## Module 4: Diet Plans — `diet/`

**URL prefix:** `/diet/`

| URL | View | Access |
|-----|------|--------|
| `/diet/my-plans/` | `TrainerDietListView` | Trainer |
| `/diet/create/` | `DietPlanCreateView` | Trainer |
| `/diet/<id>/` | `DietPlanDetailView` | Trainer |
| `/diet/<id>/add-meal/` | `MealCreateView` | Trainer |
| `/diet/meal/<id>/delete/` | `MealDeleteView` | Trainer |
| `/diet/my-diet/` | `MemberDietView` | Member |

**Meal types:** BREAKFAST, MORNING_SNACK, LUNCH, AFTERNOON_SNACK, DINNER, POST_WORKOUT

**Workflow:**
1. Trainer creates diet plan with macros (calories, protein, carbs, fats)
2. Trainer adds meals to the plan from the plan detail page
3. Member views their diet plan at `/diet/my-diet/`

---

## Module 5: Session Booking — `sessions_booking/`

**URL prefix:** `/sessions/`

| URL | View | Access |
|-----|------|--------|
| `/sessions/book/` | `BookSessionView` | Member |
| `/sessions/my/` | `MemberSessionListView` | Member |
| `/sessions/<id>/cancel/` | `CancelSessionView` | Member |
| `/sessions/requests/` | `TrainerSessionListView` | Trainer |
| `/sessions/<id>/respond/` | `RespondToSessionView` | Trainer |

**Session statuses:** PENDING → APPROVED / REJECTED → COMPLETED (or CANCELLED by member)

**Workflow:**
1. Member picks a trainer, date, and time at `/sessions/book/`
2. Trainer sees incoming requests at `/sessions/requests/`
3. Trainer clicks "Respond" to approve, reject, or mark complete
4. Member sees status updates in real-time at `/sessions/my/`

---

## Files Changed in Existing Project

| File | Change |
|------|--------|
| `gymcore/settings.py` | Added 5 new apps to `INSTALLED_APPS` |
| `gymcore/urls.py` | Added URL includes for all 5 modules |
| `templates/partials/sidebar.html` | Added full role-based nav links for all modules |
| `workouts/forms.py` | Fixed field names to match actual model (`description` not `notes` for WorkoutPlan, `notes` not `focus` for WorkoutDay) |
| `diet/urls.py` | Fixed view class name references |
| `diet/templates/diet/` | Rewrote templates to use correct Tailwind CSS class names matching base.html |

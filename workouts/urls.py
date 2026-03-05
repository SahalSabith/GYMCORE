from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    # Trainer
    path('my-plans/', views.TrainerWorkoutListView.as_view(), name='trainer_plans'),
    path('create/', views.CreateWorkoutPlanView.as_view(), name='create_plan'),
    path('plans/<int:plan_id>/add-day/', views.AddWorkoutDayView.as_view(), name='add_day'),
    path('days/<int:day_id>/edit/', views.EditWorkoutDayView.as_view(), name='edit_day'),
    path('<int:pk>/detail/', views.WorkoutPlanDetailView.as_view(), name='plan_detail'),
    # Member
    path('my-workouts/', views.MemberWorkoutView.as_view(), name='my_workouts'),
    path('complete/<int:exercise_id>/', views.MarkCompleteView.as_view(), name='mark_complete'),
    path('history/', views.WorkoutHistoryView.as_view(), name='history'),
]

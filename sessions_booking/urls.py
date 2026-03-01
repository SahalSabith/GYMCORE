from django.urls import path
from . import views

app_name = 'sessions_booking'

urlpatterns = [
    # Member
    path('book/', views.BookSessionView.as_view(), name='book'),
    path('my/', views.MemberSessionListView.as_view(), name='my_sessions'),
    path('<int:pk>/cancel/', views.CancelSessionView.as_view(), name='cancel'),
    # Trainer
    path('requests/', views.TrainerSessionListView.as_view(), name='trainer_sessions'),
    path('<int:pk>/respond/', views.RespondToSessionView.as_view(), name='respond'),
]

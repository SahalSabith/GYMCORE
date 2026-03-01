from django.urls import path
from . import views

app_name = 'sessions'

urlpatterns = [
    # Member
    path('my/', views.MemberSessionListView.as_view(), name='member_list'),
    path('book/', views.SessionRequestView.as_view(), name='book'),
    path('<int:pk>/cancel/', views.CancelSessionView.as_view(), name='cancel'),

    # Trainer
    path('trainer/', views.TrainerSessionListView.as_view(), name='trainer_lists'),
    path('trainer/<int:pk>/respond/', views.SessionResponseView.as_view(), name='respond'),
]

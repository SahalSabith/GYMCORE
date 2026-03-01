from django.urls import path
from . import views

app_name = 'trainers'

urlpatterns = [
    path('', views.TrainerListView.as_view(), name='list'),
    path('<int:pk>/', views.TrainerDetailView.as_view(), name='detail'),
    path('my-profile/', views.MyTrainerProfileView.as_view(), name='my_profile'),
    path('my-profile/edit/', views.TrainerProfileEditView.as_view(), name='edit_profile'),
    path('my-trainer/', views.MyTrainerView.as_view(), name='my_trainer'),
    path('assign/', views.AssignTrainerView.as_view(), name='assign'),
    path('assignments/', views.AssignmentListView.as_view(), name='assignments'),
    path('assignments/<int:pk>/delete/', views.DeleteAssignmentView.as_view(), name='delete_assignment'),
]

from django.urls import path
from . import views

app_name = 'diet'

urlpatterns = [
    path('my-plans/', views.TrainerDietListView.as_view(), name='trainer_list'),
    path('create/', views.DietPlanCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DietPlanDetailView.as_view(), name='detail'),
    path('<int:pk>/add-meal/', views.MealCreateView.as_view(), name='add_meal'),
    path('meal/<int:pk>/delete/', views.MealDeleteView.as_view(), name='delete_meal'),
    path('my-diet/', views.MemberDietView.as_view(), name='my_diet'),
]

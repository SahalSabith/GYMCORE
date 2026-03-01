from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardRedirectView.as_view(), name='redirect'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin'),
    path('trainer/', views.TrainerDashboardView.as_view(), name='trainer'),
    path('member/', views.MemberDashboardView.as_view(), name='member'),
]

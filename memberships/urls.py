from django.urls import path
from . import views

app_name = 'memberships'

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plans'),
    path('plans/<int:plan_id>/subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('my/', views.MySubscriptionView.as_view(), name='my_subscription'),
    path('all/', views.AdminSubscriptionListView.as_view(), name='admin_list'),
]

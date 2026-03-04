from django.urls import path
from . import views

app_name = 'memberships'

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plans'),
    path('plans/new/', views.PlanCreateView.as_view(), name='plan_create'),
    path('plans/<int:plan_id>/edit/', views.PlanEditView.as_view(), name='plan_edit'),
    path('plans/<int:plan_id>/delete/', views.PlanDeleteView.as_view(), name='plan_delete'),
    path('plans/<int:plan_id>/subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('my/', views.MySubscriptionView.as_view(), name='my_subscription'),
    path('all/', views.AdminSubscriptionListView.as_view(), name='admin_list'),
]
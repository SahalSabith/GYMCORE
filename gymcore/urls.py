from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('memberships/', include('memberships.urls', namespace='memberships')),
    path('trainers/', include('trainers.urls', namespace='trainers')),
    path('workouts/', include('workouts.urls', namespace='workouts')),
    path('diet/', include('diet.urls', namespace='diet')),
    path('sessions_booking/', include('sessions_booking.urls', namespace='sessions_booking')),
    path('sessions/', include('sessions.urls', namespace='sessions')),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

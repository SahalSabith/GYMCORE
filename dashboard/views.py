from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model

from accounts.decorators import admin_required, trainer_required, member_required

User = get_user_model()


class DashboardRedirectView(View):
    """Route authenticated users to their role-specific dashboard."""

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        role = request.user.role
        if role == 'ADMIN':
            return redirect('dashboard:admin')
        elif role == 'TRAINER':
            return redirect('dashboard:trainer')
        return redirect('dashboard:member')


@method_decorator([login_required, admin_required], name='dispatch')
class AdminDashboardView(View):
    template_name = 'dashboard/admin.html'

    def get(self, request):
        context = {
            'total_members': User.objects.filter(role='MEMBER').count(),
            'total_trainers': User.objects.filter(role='TRAINER').count(),
            'recent_users': User.objects.exclude(role='ADMIN').order_by('-date_joined')[:10],
        }
        return render(request, self.template_name, context)


@method_decorator([login_required, trainer_required], name='dispatch')
class TrainerDashboardView(View):
    template_name = 'dashboard/trainer.html'

    def get(self, request):
        # Assigned members will be a real queryset once a TrainerMember model exists
        assigned_members = User.objects.filter(role='MEMBER').order_by('first_name')[:8]
        return render(request, self.template_name, {'assigned_members': assigned_members})


@method_decorator([login_required, member_required], name='dispatch')
class MemberDashboardView(View):
    template_name = 'dashboard/member.html'

    def get(self, request):
        return render(request, self.template_name)

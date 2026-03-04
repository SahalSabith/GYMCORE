from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View, TemplateView

from accounts.decorators import role_required
from .models import MembershipPlan, Subscription
from .forms import MembershipPlanForm, SubscribeForm


class PlanListView(LoginRequiredMixin, ListView):
    """All active membership plans — visible to everyone logged in."""
    model = MembershipPlan
    template_name = 'memberships/plans.html'
    context_object_name = 'plans'

    def get_queryset(self):
        # Admins see all plans (including inactive); members only see active
        if self.request.user.role == 'ADMIN':
            return MembershipPlan.objects.all()
        return MembershipPlan.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.role == 'MEMBER':
            ctx['active_sub'] = (
                Subscription.objects
                .filter(member=self.request.user, is_active=True)
                .order_by('-start_date')
                .first()
            )
        return ctx


@method_decorator(role_required('ADMIN'), name='dispatch')
class PlanCreateView(LoginRequiredMixin, View):
    """Admin creates a new membership plan."""

    def get(self, request):
        form = MembershipPlanForm()
        return self._render(request, form)

    def post(self, request):
        form = MembershipPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plan "{plan.name}" created successfully.')
            return redirect('memberships:plans')
        return self._render(request, form)

    def _render(self, request, form):
        from django.shortcuts import render
        return render(request, 'memberships/plan_form.html', {'form': form})


@method_decorator(role_required('ADMIN'), name='dispatch')
class PlanEditView(LoginRequiredMixin, View):
    """Admin edits an existing membership plan."""

    def get(self, request, plan_id):
        plan = get_object_or_404(MembershipPlan, pk=plan_id)
        form = MembershipPlanForm(instance=plan)
        return self._render(request, form)

    def post(self, request, plan_id):
        plan = get_object_or_404(MembershipPlan, pk=plan_id)
        form = MembershipPlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plan "{plan.name}" updated successfully.')
            return redirect('memberships:plans')
        return self._render(request, form)

    def _render(self, request, form):
        from django.shortcuts import render
        return render(request, 'memberships/plan_form.html', {'form': form})


@method_decorator(role_required('ADMIN'), name='dispatch')
class PlanDeleteView(LoginRequiredMixin, View):
    """Admin deletes a membership plan (POST only)."""

    def post(self, request, plan_id):
        plan = get_object_or_404(MembershipPlan, pk=plan_id)
        name = plan.name
        plan.delete()
        messages.success(request, f'Plan "{name}" has been deleted.')
        return redirect('memberships:plans')


@method_decorator(role_required('MEMBER'), name='dispatch')
class SubscribeView(LoginRequiredMixin, View):
    """Member subscribes to a plan."""

    def get(self, request, plan_id):
        plan = get_object_or_404(MembershipPlan, pk=plan_id, is_active=True)
        form = SubscribeForm()
        return self._render(request, plan, form)

    def post(self, request, plan_id):
        plan = get_object_or_404(MembershipPlan, pk=plan_id, is_active=True)
        form = SubscribeForm(request.POST)
        if form.is_valid():
            Subscription.objects.filter(member=request.user, is_active=True).update(is_active=False)
            sub = form.save(commit=False)
            sub.member = request.user
            sub.plan = plan
            sub.save()
            messages.success(request, f'Successfully subscribed to {plan.name}!')
            return redirect('memberships:my_subscription')
        return self._render(request, plan, form)

    def _render(self, request, plan, form):
        from django.shortcuts import render
        return render(request, 'memberships/subscribe.html', {'plan': plan, 'form': form})


@method_decorator(role_required('MEMBER'), name='dispatch')
class MySubscriptionView(LoginRequiredMixin, TemplateView):
    template_name = 'memberships/my_subscription.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['subscriptions'] = Subscription.objects.filter(member=self.request.user)
        ctx['active_sub'] = ctx['subscriptions'].filter(is_active=True).first()
        return ctx


@method_decorator(role_required('ADMIN'), name='dispatch')
class AdminSubscriptionListView(LoginRequiredMixin, ListView):
    """Admin view of all subscriptions."""
    model = Subscription
    template_name = 'memberships/admin_subscriptions.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        return Subscription.objects.select_related('member', 'plan').order_by('-created_at')
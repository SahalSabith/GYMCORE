from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, View

from accounts.decorators import role_required
from .forms import TrainerProfileForm, TrainerAssignmentForm
from .models import TrainerProfile, TrainerAssignment

User = get_user_model()


class TrainerListView(LoginRequiredMixin, ListView):
    """Public list of all trainers — visible to all authenticated users."""
    template_name = 'trainers/trainer_list.html'
    context_object_name = 'trainers'

    def get_queryset(self):
        return User.objects.filter(role='TRAINER').select_related('trainer_profile')


class TrainerDetailView(LoginRequiredMixin, DetailView):
    """Trainer public profile page."""
    template_name = 'trainers/trainer_detail.html'
    context_object_name = 'trainer'

    def get_queryset(self):
        return User.objects.filter(role='TRAINER').select_related('trainer_profile')


@method_decorator(role_required('TRAINER'), name='dispatch')
class TrainerProfileEditView(LoginRequiredMixin, View):
    """Trainer edits their own profile."""
    template_name = 'trainers/profile_edit.html'

    def get_object(self):
        profile, _ = TrainerProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get(self, request):
        form = TrainerProfileForm(instance=self.get_object())
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TrainerProfileForm(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
            messages.success(request, 'Trainer profile updated.')
            return redirect('trainers:my_profile')
        return render(request, self.template_name, {'form': form})


@method_decorator(role_required('TRAINER'), name='dispatch')
class MyTrainerProfileView(LoginRequiredMixin, DetailView):
    template_name = 'trainers/my_profile.html'
    context_object_name = 'trainer'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['assignments'] = TrainerAssignment.objects.filter(
            trainer=self.request.user
        ).select_related('member')
        try:
            ctx['profile'] = self.request.user.trainer_profile
        except TrainerProfile.DoesNotExist:
            ctx['profile'] = None
        return ctx


@method_decorator(role_required('ADMIN'), name='dispatch')
class AssignTrainerView(LoginRequiredMixin, CreateView):
    form_class = TrainerAssignmentForm
    template_name = 'trainers/assign.html'
    success_url = reverse_lazy('trainers:assignments')

    def form_valid(self, form):
        messages.success(self.request, 'Trainer assigned successfully.')
        return super().form_valid(form)


@method_decorator(role_required('ADMIN'), name='dispatch')
class AssignmentListView(LoginRequiredMixin, ListView):
    model = TrainerAssignment
    template_name = 'trainers/assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return TrainerAssignment.objects.select_related('trainer', 'member').order_by('-assigned_at')


@method_decorator(role_required('ADMIN'), name='dispatch')
class DeleteAssignmentView(LoginRequiredMixin, DeleteView):
    model = TrainerAssignment
    template_name = 'trainers/confirm_delete.html'
    success_url = reverse_lazy('trainers:assignments')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Assignment removed.')
        return super().delete(request, *args, **kwargs)


@method_decorator(role_required('MEMBER'), name='dispatch')
class MyTrainerView(LoginRequiredMixin, ListView):
    """Member views their assigned trainer."""
    template_name = 'trainers/my_trainer.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return TrainerAssignment.objects.filter(
            member=self.request.user
        ).select_related('trainer', 'trainer__trainer_profile')

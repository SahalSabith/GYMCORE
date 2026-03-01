from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, View

from accounts.decorators import role_required
from .forms import BookSessionForm, TrainerResponseForm
from .models import TrainingSession as TrainingSession_Booking
from sessions.models import TrainingSession


# ─── Member: book and view sessions ──────────────────────────────────────────

@method_decorator(role_required('MEMBER'), name='dispatch')
class BookSessionView(LoginRequiredMixin, CreateView):
    form_class = BookSessionForm
    template_name = 'sessions_booking/book.html'
    success_url = reverse_lazy('sessions:my_sessions')

    def form_valid(self, form):
        form.instance.member = self.request.user
        messages.success(self.request, 'Session request sent! Waiting for trainer approval.')
        return super().form_valid(form)


@method_decorator(role_required('MEMBER'), name='dispatch')
class MemberSessionListView(LoginRequiredMixin, ListView):
    template_name = 'sessions_booking/member_sessions.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return TrainingSession.objects.filter(
            member=self.request.user
        ).select_related('trainer').order_by('-date', '-time')


@method_decorator(role_required('MEMBER'), name='dispatch')
class CancelSessionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(
            TrainingSession, pk=pk, member=request.user, status='PENDING'
        )
        session.status = 'CANCELLED'
        session.save()
        messages.success(request, 'Session request cancelled.')
        return redirect('sessions:my_sessions')


# ─── Trainer: manage incoming requests ───────────────────────────────────────

@method_decorator(role_required('TRAINER'), name='dispatch')
class TrainerSessionListView(LoginRequiredMixin, ListView):
    template_name = 'sessions_booking/trainer_sessions.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return TrainingSession.objects.filter(
            trainer=self.request.user
        ).select_related('member').order_by('-date', '-time')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pending_count'] = TrainingSession.objects.filter(
            trainer=self.request.user, status='PENDING'
        ).count()
        return ctx


@method_decorator(role_required('TRAINER'), name='dispatch')
class RespondToSessionView(LoginRequiredMixin, View):
    """Trainer approves, rejects, or marks a session complete."""
    template_name = 'sessions_booking/respond.html'

    def get_session(self, pk):
        return get_object_or_404(TrainingSession, pk=pk, trainer=self.request.user)

    def get(self, request, pk):
        session = self.get_session(pk)
        form = TrainerResponseForm(instance=session)
        return render(request, self.template_name, {'session': session, 'form': form})

    def post(self, request, pk):
        session = self.get_session(pk)
        form = TrainerResponseForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, f'Session marked as {session.get_status_display()}.')
            return redirect('sessions:trainer_sessions')
        return render(request, self.template_name, {'session': session, 'form': form})

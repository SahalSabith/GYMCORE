from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, View, UpdateView

from accounts.decorators import role_required
from .models import TrainingSession
from .forms import SessionRequestForm, SessionResponseForm


STATUS_COLORS = {
    'PENDING': 'bg-yellow-500/20 text-yellow-400',
    'APPROVED': 'bg-green-500/20 text-green-400',
    'REJECTED': 'bg-red-500/20 text-red-400',
    'COMPLETED': 'bg-blue-500/20 text-blue-400',
    'CANCELLED': 'bg-iron-600 text-iron-400',
}


@method_decorator(role_required('MEMBER'), name='dispatch')
class MemberSessionListView(LoginRequiredMixin, ListView):
    template_name = 'sessions/member_list.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return TrainingSession.objects.filter(member=self.request.user).select_related('trainer')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_colors'] = STATUS_COLORS
        return ctx


@method_decorator(role_required('MEMBER'), name='dispatch')
class SessionRequestView(LoginRequiredMixin, CreateView):
    model = TrainingSession
    form_class = SessionRequestForm
    template_name = 'sessions/book.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['member'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.member = self.request.user
        session = form.save()
        messages.success(self.request, f'Session request sent to {session.trainer.get_full_name()} for {session.date}.')
        return redirect('sessions:member_list')


@method_decorator(role_required('MEMBER'), name='dispatch')
class CancelSessionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(TrainingSession, pk=pk, member=request.user)
        if session.status in ('PENDING', 'APPROVED'):
            session.status = TrainingSession.Status.CANCELLED
            session.save()
            messages.success(request, 'Session cancelled.')
        else:
            messages.error(request, 'Cannot cancel this session.')
        return redirect('sessions:member_list')


@method_decorator(role_required('TRAINER'), name='dispatch')
class TrainerSessionListView(LoginRequiredMixin, ListView):
    template_name = 'sessions/trainer_list.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return TrainingSession.objects.filter(trainer=self.request.user).select_related('member')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pending'] = self.get_queryset().filter(status='PENDING')
        ctx['upcoming'] = self.get_queryset().filter(status='APPROVED')
        ctx['past'] = self.get_queryset().filter(status__in=['COMPLETED', 'REJECTED', 'CANCELLED'])
        ctx['status_colors'] = STATUS_COLORS
        return ctx


@method_decorator(role_required('TRAINER'), name='dispatch')
class SessionResponseView(LoginRequiredMixin, UpdateView):
    model = TrainingSession
    form_class = SessionResponseForm
    template_name = 'sessions/respond.html'

    def get_queryset(self):
        return TrainingSession.objects.filter(trainer=self.request.user)

    def form_valid(self, form):
        session = form.save()
        messages.success(self.request, f'Session {session.get_status_display().lower()}.')
        return redirect('sessions:trainer_lists')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_colors'] = STATUS_COLORS
        return ctx

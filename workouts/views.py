from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View

from accounts.decorators import role_required
from .forms import WorkoutPlanForm, WorkoutDayForm, ExerciseFormSet
from .models import WorkoutPlan, WorkoutDay, Exercise, WorkoutCompletion


@method_decorator(role_required('TRAINER'), name='dispatch')
class TrainerWorkoutListView(LoginRequiredMixin, ListView):
    template_name = 'workouts/trainer_plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return WorkoutPlan.objects.filter(trainer=self.request.user).select_related('member')


@method_decorator(role_required('TRAINER'), name='dispatch')
class CreateWorkoutPlanView(LoginRequiredMixin, CreateView):
    form_class = WorkoutPlanForm
    template_name = 'workouts/create_plan.html'

    def form_valid(self, form):
        plan = form.save(commit=False)
        plan.trainer = self.request.user
        plan.save()
        messages.success(self.request, 'Workout plan created. Now add workout days.')
        return redirect('workouts:add_day', plan_id=plan.pk)


@method_decorator(role_required('TRAINER'), name='dispatch')
class AddWorkoutDayView(LoginRequiredMixin, View):
    template_name = 'workouts/add_day.html'

    def get_plan(self, plan_id):
        return get_object_or_404(WorkoutPlan, pk=plan_id, trainer=self.request.user)

    def get(self, request, plan_id):
        plan = self.get_plan(plan_id)
        day_form = WorkoutDayForm()
        formset = ExerciseFormSet()
        return render(request, self.template_name, {
            'plan': plan, 'day_form': day_form, 'formset': formset,
            'existing_days': plan.days.prefetch_related('exercises'),
        })

    def post(self, request, plan_id):
        plan = self.get_plan(plan_id)
        day_form = WorkoutDayForm(request.POST)
        formset = ExerciseFormSet(request.POST)
        if day_form.is_valid() and formset.is_valid():
            day = day_form.save(commit=False)
            day.workout_plan = plan
            day.save()
            formset.instance = day
            formset.save()
            messages.success(request, f'{day.get_day_of_week_display()} added successfully.')
            # Redirect to self with fresh forms — fixes the "can't add again" issue
            return redirect('workouts:add_day', plan_id=plan.pk)
        return render(request, self.template_name, {
            'plan': plan, 'day_form': day_form, 'formset': formset,
            'existing_days': plan.days.prefetch_related('exercises'),
        })


@method_decorator(role_required('TRAINER'), name='dispatch')
class EditWorkoutDayView(LoginRequiredMixin, View):
    template_name = 'workouts/edit_day.html'

    def get_day(self, day_id, trainer):
        return get_object_or_404(
            WorkoutDay, pk=day_id, workout_plan__trainer=trainer
        )

    def get(self, request, day_id):
        day = self.get_day(day_id, request.user)
        day_form = WorkoutDayForm(instance=day)
        formset = ExerciseFormSet(instance=day)
        return render(request, self.template_name, {
            'plan': day.workout_plan,
            'day': day,
            'day_form': day_form,
            'formset': formset,
        })

    def post(self, request, day_id):
        day = self.get_day(day_id, request.user)
        day_form = WorkoutDayForm(request.POST, instance=day)
        formset = ExerciseFormSet(request.POST, instance=day)
        if day_form.is_valid() and formset.is_valid():
            day_form.save()
            formset.save()
            messages.success(request, f'{day.get_day_of_week_display()} updated.')
            return redirect('workouts:add_day', plan_id=day.workout_plan.pk)
        return render(request, self.template_name, {
            'plan': day.workout_plan,
            'day': day,
            'day_form': day_form,
            'formset': formset,
        })

@method_decorator(role_required('TRAINER'), name='dispatch')
class WorkoutPlanDetailView(LoginRequiredMixin, DetailView):
    template_name = 'workouts/plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return WorkoutPlan.objects.filter(trainer=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['days'] = self.object.days.prefetch_related('exercises')
        return ctx


@method_decorator(role_required('MEMBER'), name='dispatch')
class MemberWorkoutView(LoginRequiredMixin, ListView):
    template_name = 'workouts/member_workout.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return WorkoutPlan.objects.filter(
            member=self.request.user, is_active=True
        ).prefetch_related('days__exercises')


@method_decorator(role_required('MEMBER'), name='dispatch')
class MarkCompleteView(LoginRequiredMixin, View):
    """Toggle exercise completion for today."""

    def post(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, pk=exercise_id)
        today = timezone.localdate()
        completion, created = WorkoutCompletion.objects.get_or_create(
            member=request.user,
            exercise=exercise,
            date=today,
            defaults={'completed': True},
        )
        if not created:
            completion.completed = not completion.completed
            completion.save()
        return redirect(request.META.get('HTTP_REFERER', 'workouts:my_workouts'))


@method_decorator(role_required('MEMBER'), name='dispatch')
class WorkoutHistoryView(LoginRequiredMixin, ListView):
    template_name = 'workouts/history.html'
    context_object_name = 'completions'
    paginate_by = 20

    def get_queryset(self):
        return WorkoutCompletion.objects.filter(
            member=self.request.user, completed=True
        ).select_related('exercise__workout_day__workout_plan').order_by('-date')

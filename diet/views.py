from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, View

from accounts.decorators import role_required
from .models import DietPlan, Meal
from .forms import DietPlanForm, MealForm


@method_decorator(role_required('TRAINER'), name='dispatch')
class TrainerDietListView(LoginRequiredMixin, ListView):
    template_name = 'diet/trainer_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return DietPlan.objects.filter(trainer=self.request.user).select_related('member')


@method_decorator(role_required('TRAINER'), name='dispatch')
class DietPlanCreateView(LoginRequiredMixin, CreateView):
    model = DietPlan
    form_class = DietPlanForm
    template_name = 'diet/plan_form.html'

    def get_form_kwargs(self):
        return {**super().get_form_kwargs()}

    def form_valid(self, form):
        form.instance.trainer = self.request.user
        plan = form.save()
        messages.success(self.request, f'Diet plan "{plan.title}" created.')
        return redirect('diet:detail', pk=plan.pk)


@method_decorator(role_required('TRAINER'), name='dispatch')
class DietPlanDetailView(LoginRequiredMixin, DetailView):
    template_name = 'diet/plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return DietPlan.objects.filter(trainer=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['meals'] = self.object.meals.all()
        ctx['meal_form'] = MealForm()
        return ctx


@method_decorator(role_required('TRAINER'), name='dispatch')
class MealCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(DietPlan, pk=pk, trainer=request.user)
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.diet_plan = plan
            meal.save()
            messages.success(request, f'{meal.get_meal_type_display()} added.')
        return redirect('diet:detail', pk=pk)


@method_decorator(role_required('TRAINER'), name='dispatch')
class MealDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        meal = get_object_or_404(Meal, pk=pk, diet_plan__trainer=request.user)
        plan_pk = meal.diet_plan.pk
        meal.delete()
        messages.success(request, 'Meal removed.')
        return redirect('diet:detail', pk=plan_pk)


@method_decorator(role_required('MEMBER'), name='dispatch')
class MemberDietView(LoginRequiredMixin, ListView):
    template_name = 'diet/member_view.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return DietPlan.objects.filter(member=self.request.user, is_active=True).prefetch_related('meals')

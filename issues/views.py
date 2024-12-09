from django.views.generic import(
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Status, Issue
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin
)


class IssueListView(LoginRequiredMixin, ListView):
    template_name = "issues/list.html"
    model = Issue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["to_do_list"] = (
            Issue.objects
            .filter(status__name = "to do")
            .order_by("-created_on")
        )
        context["in_progress_list"] = (
            Issue.objects
            .filter(status__name="in progress")
            .order_by("-created_on")
        )
        context["done_list"] = (
            Issue.objects
            .filter(status__name="done")
            .order_by("-created_on")
        )
        context["title"] = "By Status"
        return context
        
    
class IssueDetailView(LoginRequiredMixin, DetailView):
    template_name = "issues/detail.html"
    model = Issue
    
class IssueCreateView(LoginRequiredMixin, CreateView):
    template_name = "issues/new.html"
    model = Issue
    fields = [
        "name", "summary", "description", "assignee"
    ]

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        status_instance = Status.objects.get(name="to do")
        form.instance.status = status_instance
        response = super().form_valid(form)
        action = self.request.POST.get("action")
        
        if action == "submit_and_new":
            return HttpResponseRedirect(reverse("new"))
        if action == "submit":
            return HttpResponseRedirect(reverse("list"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create New"
        return context
    

class IssueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "issues/update.html"
    model = Issue
    fields = [
        "name", "summary", "description", "assignee", "status"
    ]
    

    def test_func(self):
        issue = self.get_object()
        is_true = issue.reporter == self.request.user or issue.assignee == self.request.user
        return is_true
    
class IssueDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "issues/delete.html"
    model = Issue
    success_url = reverse_lazy("list")

    def test_func(self):
        issue = self.get_object()
        return issue.reporter == self.request.user
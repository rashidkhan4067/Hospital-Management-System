from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'alerts/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = Notification
    template_name = 'alerts/notification_detail.html'
    context_object_name = 'notification'

    def get_object(self):
        obj = super().get_object()
        if not obj.is_read:
            obj.is_read = True
            obj.read_at = timezone.now()
            obj.save()
        return obj

class NotificationCreateView(LoginRequiredMixin, CreateView):
    model = Notification
    template_name = 'alerts/notification_form.html'
    fields = ['recipient', 'title', 'message', 'notification_type', 'priority']
    success_url = reverse_lazy('alerts:notification_list')

    def form_valid(self, form):
        form.instance.sender = self.request.user
        messages.success(self.request, 'Notification sent successfully.')
        return super().form_valid(form)

class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

        messages.success(request, 'Notification marked as read.')
        return redirect('alerts:notification_list')

class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

        messages.success(request, 'All notifications marked as read.')
        return redirect('alerts:notification_list')

class NotificationSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'alerts/notification_settings.html'

class UnreadCountAPIView(LoginRequiredMixin, View):
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return JsonResponse({'unread_count': count})

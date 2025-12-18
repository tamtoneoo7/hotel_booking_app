from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth.decorators import login_required
import json
from django.core.exceptions import ValidationError
from .models import Room, Customer, Booking, User

# Access Mixins
class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == User.MANAGER

class ReceptionistRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in [User.MANAGER, User.RECEPTIONIST]

# Dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'booking/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = Room.objects.all()
        context['customers'] = Customer.objects.all()
        context['bookings'] = Booking.objects.select_related('customer', 'room').order_by('-created_at')
        return context

# Landing Page
def landing_page(request):
    return render(request, 'booking/landing.html')

# Room CRUD (Manager Only)
class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'booking/room_list.html'
    context_object_name = 'rooms'

class RoomCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    model = Room
    fields = ['number', 'room_type', 'capacity', 'price_per_night']
    template_name = 'booking/room_form.html'
    success_url = reverse_lazy('room_list')

class RoomUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Room
    fields = ['number', 'room_type', 'capacity', 'price_per_night']
    template_name = 'booking/room_form.html'
    success_url = reverse_lazy('room_list')

class RoomDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Room
    template_name = 'booking/room_confirm_delete.html'
    success_url = reverse_lazy('room_list')

# Customer CRUD (Receptionist + Manager)
class CustomerListView(LoginRequiredMixin, ReceptionistRequiredMixin, ListView):
    model = Customer
    template_name = 'booking/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(LoginRequiredMixin, ReceptionistRequiredMixin, CreateView):
    model = Customer
    fields = ['name', 'email', 'phone', 'gender']
    template_name = 'booking/customer_form.html'
    success_url = reverse_lazy('customer_list')

class CustomerUpdateView(LoginRequiredMixin, ReceptionistRequiredMixin, UpdateView):
    model = Customer
    fields = ['name', 'email', 'phone', 'gender']
    template_name = 'booking/customer_form.html'
    success_url = reverse_lazy('customer_list')

class CustomerDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Customer
    template_name = 'booking/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')

# Booking API
@login_required
@require_POST
def create_booking_api(request):
    try:
        data = json.loads(request.body)
        customer_id = data.get('customer')
        room_id = data.get('room')
        check_in = data.get('check_in')
        check_out = data.get('check_out')

        with transaction.atomic():
            booking = Booking(
                customer_id=customer_id,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out
            )
            booking.full_clean() # Calls clean() which handles overlap validation
            booking.save()
            
        return JsonResponse({'status': 'success', 'message': 'Booking created successfully!', 'booking_id': booking.id})
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'message': str(e.message_dict if hasattr(e, 'message_dict') else e)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

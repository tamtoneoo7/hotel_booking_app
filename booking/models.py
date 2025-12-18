from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    MANAGER = 'MANAGER'
    RECEPTIONIST = 'RECEPTIONIST'
    ROLE_CHOICES = [
        (MANAGER, 'Manager'),
        (RECEPTIONIST, 'Receptionist'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=RECEPTIONIST)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return self.name

class Room(models.Model):
    SINGLE = 'SINGLE'
    DOUBLE = 'DOUBLE'
    SUITE = 'SUITE'
    TYPE_CHOICES = [
        (SINGLE, 'Single'),
        (DOUBLE, 'Double'),
        (SUITE, 'Suite'),
    ]
    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    capacity = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.number} ({self.get_room_type_display()})"

class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Basic validation
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValidationError("Check-out date must be after check-in date.")
        
        # Overlap check
        if self.room_id and self.check_in and self.check_out:
            overlapping_bookings = Booking.objects.filter(
                room=self.room,
                check_in__lt=self.check_out,
                check_out__gt=self.check_in
            )
            if self.pk:
                overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)
                
            if overlapping_bookings.exists():
                raise ValidationError(f"Room {self.room.number} is already booked for these dates.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} - {self.room} ({self.check_in} to {self.check_out})"

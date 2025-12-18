import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_project.settings')
django.setup()

from booking.models import User

if not User.objects.filter(username='manager').exists():
    User.objects.create_superuser('manager', 'manager@example.com', 'manager123', role=User.MANAGER)
    print("Created Manager: manager / manager123")
else:
    print("Manager already exists")

if not User.objects.filter(username='receptionist').exists():
    u = User.objects.create_user('receptionist', 'reception123@example.com', 'receptionist123', role=User.RECEPTIONIST)
    print("Created Receptionist: receptionist / receptionist123")
else:
    print("Receptionist already exists")

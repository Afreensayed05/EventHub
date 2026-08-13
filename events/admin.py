from django.contrib import admin
from .models import Event, Registration, Feedback
from .models import StudentProfile
from .models import Category
from .models import Organizer

admin.site.register(Event)
admin.site.register(Registration)
admin.site.register(Feedback)
admin.site.register(StudentProfile)
admin.site.register(Category)
admin.site.register(Organizer)

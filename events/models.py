from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File


class Category(models.Model):

    name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Organizer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Event(models.Model):

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    organizer = models.ForeignKey(Organizer,on_delete=models.CASCADE)
    venue = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(
    upload_to="event_images/",
    blank=True,
    null=True
)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Active"
    )

    def __str__(self):
        return self.title
    


class Registration(models.Model):
    ATTENDANCE_CHOICES = [
        ("Pending", "Pending"),
        ("Present", "Present"),
        ("Absent", "Absent"),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=15)

    college = models.CharField(max_length=100)

    department = models.CharField(max_length=100)

    year = models.CharField(max_length=20)

    registered_on = models.DateTimeField(auto_now_add=True)

    qr_code = models.ImageField(
        upload_to="qr_codes/",
        blank=True,
        null=True
    )
    attendance = models.CharField(
        max_length=20,
        choices=ATTENDANCE_CHOICES,
        default="Pending"
    )

    @property
    def ticket_id(self):
        return f"EVT{self.id:05d}"
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):

        # Save first to generate ID
        super().save(*args, **kwargs)

        if not self.qr_code:

            qr = qrcode.make(
                f"""
Ticket ID: {self.ticket_id}
Name: {self.name}
Event: {self.event.title}
Venue: {self.event.venue}
Date: {self.event.date}
"""
            )

            buffer = BytesIO()

            qr.save(buffer, format="PNG")

            filename = f"{self.ticket_id}.png"

            self.qr_code.save(
                filename,
                File(buffer),
                save=False
            )

            super().save(update_fields=["qr_code"])

class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.event.title

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class StudentProfile(models.Model):

    ROLE_CHOICES = [

        ("Participant","Participant"),

        ("Organizer","Organizer"),

    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="Participant"
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    college = models.CharField(
        max_length=100,
        blank=True
    )

    department = models.CharField(
        max_length=100,
        blank=True
    )

    year = models.CharField(
        max_length=20,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username

class Feedback(models.Model):

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    registration = models.ForeignKey(
        Registration,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    rating = models.IntegerField()

    comments = models.TextField()

    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.title} - {self.rating}"


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.user.username} - {self.message}"

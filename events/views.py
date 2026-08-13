from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q,Sum
from .models import Category, Notification
from .models import Organizer,Event,Registration
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
import json

from .models import (
    Event,
    Registration,
    Feedback,
    Wishlist,
    StudentProfile,
)


# ==========================
# HOME
# ==========================

def home(request):
    return render(request, "index.html")


# ==========================
# LOGIN
# ==========================

def login(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            auth_login(request, user)

            # Admin
            if user.is_superuser:
                return redirect("admin_dashboard")

            # Student Profile
            profile = StudentProfile.objects.get(user=user)

            # Participant
            if profile.role == "Participant":
                return redirect("student_dashboard")

            # Organizer
            elif profile.role == "Organizer":
                return redirect("organizer_dashboard")

        else:

            messages.error(
                request,
                "Invalid Username or Password!"
            )

            return redirect("login")

    return render(request, "login.html")

# ==========================
# REGISTER
# ==========================

@transaction.atomic
def register(request):

    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        role = request.POST["role"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        StudentProfile.objects.create(
            user=user,
            role=role
        )

        if role == "Organizer":

            Organizer.objects.create(
                user=user,
                name=username,
                email=email,
                phone="",
                department="",
                designation=""
            )

        messages.success(
            request,
            "Registration Successful!"
        )

        return redirect("login")

    return render(request, "register.html")

# ==========================
# ADMIN DASHBOARD
# ==========================

@login_required(login_url="login")
def admin_dashboard(request):

    total_events = Event.objects.count()

    active_events = Event.objects.filter(
        status="Active"
    ).count()

    completed_events = Event.objects.filter(
        status="Completed"
    ).count()

    total_registrations = Registration.objects.count()

    total_feedbacks = Feedback.objects.count()

    registrations = Registration.objects.select_related(
        "event"
    ).all()[:5]

    events = Event.objects.all()[:5]

    context = {

        "total_events": total_events,

        "active_events": active_events,

        "completed_events": completed_events,

        "total_registrations": total_registrations,

        "total_feedbacks": total_feedbacks,

        "events": events,

        "registrations": registrations,

    }

    return render(
        request,
        "admin-dashboard.html",
        context,
    )

@login_required(login_url="login")
def organizer_dashboard(request):

    print("Logged in User:", request.user)
    print("User ID:", request.user.id)

    organizer = get_object_or_404(
        Organizer,
        user=request.user
    )

    print("Organizer:", organizer)

    total_events = Event.objects.filter(
        organizer=organizer
    ).count()

    active_events = Event.objects.filter(
        organizer=organizer,
        status="Active"
    ).count()

    completed_events = Event.objects.filter(
        organizer=organizer,
        status="Completed"
    ).count()

    return render(
        request,
        "organizer-dashboard.html",
        {
            "total_events": total_events,
            "active_events": active_events,
            "completed_events": completed_events,
        }
    )

# ==========================
# USER DASHBOARD
# ==========================

@login_required(login_url="login")
def user_dashboard(request):

    total_registrations = Registration.objects.count()

    upcoming_events = Event.objects.filter(
        status="Active"
    ).count()

    completed_events = Event.objects.filter(
        status="Completed"
    ).count()

    wishlist_count = Wishlist.objects.count()

    context = {

        "total_registrations": total_registrations,

        "upcoming_events": upcoming_events,

        "completed_events": completed_events,

        "wishlist_count": wishlist_count,

    }

    return render(
        request,
        "student-dashboard.html",
        context,
    )


# ==========================
# CREATE EVENT
# ==========================

@login_required(login_url="login")
def create_event(request):

    organizer = get_object_or_404(
        Organizer,
        user=request.user
    )

    if request.method == "POST":

        Event.objects.create(

            title=request.POST["title"],

            category=Category.objects.get(
                id=request.POST["category"]
            ),

            organizer=organizer,

            venue=request.POST["venue"],

            date=request.POST["date"],

            time=request.POST["time"],

            description=request.POST["description"],

            price=request.POST["price"],

            image=request.FILES.get("image"),

            status=request.POST["status"],
        )

        messages.success(
            request,
            "Event created successfully!"
        )

        return redirect("my_events")

    return render(
        request,
        "create-event.html",
        {
            "categories": Category.objects.all(),
        }
    )


# ==========================
# EDIT EVENT
# ==========================

@login_required(login_url="login")
def edit_event(request, id):

    # Admin can edit any event
    if request.user.is_superuser:

        event = get_object_or_404(
            Event,
            id=id
        )

    else:

        organizer = get_object_or_404(
            Organizer,
            user=request.user
        )

        event = get_object_or_404(
            Event,
            id=id,
            organizer=organizer
        )

    if request.method == "POST":

        event.title = request.POST["title"]

        event.category = Category.objects.get(
            id=request.POST["category"]
        )

        # Organizer should never change here
        event.organizer = organizer if not request.user.is_superuser else event.organizer

        event.venue = request.POST["venue"]
        event.date = request.POST["date"]
        event.time = request.POST["time"]
        event.price = request.POST["price"]
        event.description = request.POST["description"]
        event.status = request.POST["status"]

        if request.FILES.get("image"):
            event.image = request.FILES["image"]

        event.save()

        messages.success(
            request,
            "Event updated successfully!"
        )

        if request.user.is_superuser:
            return redirect("event_list")

        return redirect("my_events")

    return render(
        request,
        "edit-event.html",
        {
            "event": event,
            "categories": Category.objects.all(),
        }
    )
@login_required(login_url="login")
def participants(request, id):

    event = get_object_or_404(Event, id=id)

    registrations = Registration.objects.filter(event=event)

    return render(
        request,
        "participants.html",
        {
            "event": event,
            "registrations": registrations,
            "total_participants": registrations.count(),
        }
    )


@login_required(login_url="login")
def calendar_view(request):

    organizer = get_object_or_404(
        Organizer,
        user=request.user
    )

    events = Event.objects.filter(
        organizer=organizer
    )

    calendar_events = []

    for event in events:

        calendar_events.append({

            "title": event.title,

            "start": str(event.date),

            "description": event.description,

            "venue": event.venue,

        })

    return render(

        request,

        "calendar.html",

        {

            "calendar_events": json.dumps(calendar_events)

        }

    )
# ==========================
# DELETE EVENT
# ==========================

@login_required(login_url="login")
def delete_event(request, id):

    if request.user.is_superuser:

        event = get_object_or_404(
            Event,
            id=id
        )

    else:

        organizer = get_object_or_404(
            Organizer,
            user=request.user
        )

        event = get_object_or_404(
            Event,
            id=id,
            organizer=organizer
        )

    event.delete()

    messages.success(
        request,
        "Event deleted successfully!"
    )

    if request.user.is_superuser:
        return redirect("event_list")

    return redirect("my_events")


# ==========================
# EVENT LIST
# ==========================

@login_required(login_url="login")
def event_list(request):

    query = request.GET.get("q")

    events = Event.objects.filter(status="Active")

    if query:

        events = events.filter(

            Q(title__icontains=query) |
            Q(category__name__icontains=query) |
            Q(venue__icontains=query)

        )

    profile = get_object_or_404(
    StudentProfile,
    user=request.user
)

    wishlist_ids = []

    if profile.role == "Participant":

        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list(
            "event_id",
            flat=True
        )
        return render(
    request,
    "event-list.html",      # ✅ Correct
    {
        "events": events,
        "query": query,
        "profile": profile,
        "wishlist_ids": wishlist_ids,
    }
)
@login_required(login_url="login")
def attendance(request):

    organizer = get_object_or_404(
        Organizer,
        user=request.user
    )

    registrations = Registration.objects.filter(
        event__organizer=organizer
    ).order_by("-registered_on")

    context = {
        "registrations": registrations,
        "total": registrations.count(),
        "present": registrations.filter(attendance="Present").count(),
        "absent": registrations.filter(attendance="Absent").count(),
        "pending": registrations.filter(attendance="Pending").count(),
    }

    return render(
        request,
        "attendance.html",
        context
    )

@login_required(login_url="login")
def my_attendance(request):

    registrations = Registration.objects.filter(
        user=request.user
    ).order_by("-registered_on")

    return render(
        request,
        "my-attendance.html",
        {
            "registrations": registrations,
        }
    )

@login_required(login_url="login")
def mark_attendance(request, id, status):

    registration = get_object_or_404(
        Registration,
        id=id
    )

    if status in ["Present", "Absent"]:

        registration.attendance = status

        registration.save()

    return redirect(
        "participants",
        registration.event.id
    )

@login_required(login_url="login")
def my_events(request):

    organizer = Organizer.objects.get(user=request.user)

    events = Event.objects.filter(organizer=organizer)

    query = request.GET.get("q")

    if query:
        events = events.filter(title__icontains=query)

    return render(
        request,
        "my-events.html",
        {
            "events": events,
            "query": query,
        }
    )
# ==========================
# EVENT DETAILS
# ==========================

def event_details(request, id):

    event = get_object_or_404(
        Event,
        id=id,
    )

    return render(

        request,

        "event-details.html",

        {

            "event": event,

        },

    )
# ==========================
# REGISTER EVENT
# ==========================
@login_required(login_url="login")
def register_event(request, id):

    event = get_object_or_404(Event, id=id)

    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    # Prevent duplicate registration
    if Registration.objects.filter(
        user=request.user,
        event=event
    ).exists():

        messages.warning(
            request,
            "You have already registered for this event."
        )

        return redirect("my_registrations")

    registration = Registration.objects.create(

        user=request.user,

        event=event,

        name=request.user.username,

        email=request.user.email,

        phone=profile.phone,

        college=profile.college,

        department=profile.department,

        year=profile.year,

    )

    messages.success(
        request,
        "Registration Successful!"
    )
    Notification.objects.create(
    user=event.organizer.user,
    message=f"{request.user.username} registered for {event.title}"
)

    return redirect(
        "ticket",
        id=registration.id
    )


 

# ==========================
# TICKET
# ==========================

@login_required(login_url="login")
def ticket(request, id):

    registration = get_object_or_404(
        Registration,
        id=id
    )

    return render(
        request,
        "ticket.html",
        {
            "registration": registration
        }
    )
@login_required(login_url="login")
def analytics(request):

    organizer = get_object_or_404(
        Organizer,
        user=request.user
    )

    # Events created by this organizer
    events = Event.objects.filter(
        organizer=organizer
    )

    # Registrations for this organizer's events
    registrations = Registration.objects.filter(
        event__organizer=organizer
    )

    # ==============================
    # EVENTS BY CATEGORY
    # ==============================

    category_data = (
        events
        .values("category__name")
        .annotate(total=Count("id"))
        .order_by("category__name")
    )

    category_labels = [
        c["category__name"]
        for c in category_data
    ]

    category_counts = [
        c["total"]
        for c in category_data
    ]


    # ==============================
    # ATTENDANCE DISTRIBUTION
    # ==============================

    attendance_data = (
        registrations
        .values("attendance")
        .annotate(total=Count("id"))
        .order_by("attendance")
    )

    attendance_labels = [
        a["attendance"]
        for a in attendance_data
    ]

    attendance_counts = [
        a["total"]
        for a in attendance_data
    ]


    # ==============================
    # MONTHLY REGISTRATIONS
    # ==============================

    monthly_data = (
        registrations
        .annotate(
            month=TruncMonth("registered_on")
        )
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    month_labels = [
        m["month"].strftime("%b %Y")
        for m in monthly_data
    ]

    month_counts = [
        m["total"]
        for m in monthly_data
    ]


    # ==============================
    # CONTEXT
    # ==============================

    context = {

        "category_labels": category_labels,
        "category_counts": category_counts,

        "attendance_labels": attendance_labels,
        "attendance_counts": attendance_counts,

        "month_labels": month_labels,
        "month_counts": month_counts,

    }


    return render(
        request,
        "analytics.html",
        context
    )
# ==========================
# PAYMENT
# ==========================

@login_required(login_url="login")
def payment(request):

    return render(
        request,
        "payment.html"
    )


# ==========================
# MY REGISTRATIONS
# ==========================
@login_required(login_url="login")
def my_registrations(request):

    registrations = Registration.objects.filter(
        user=request.user
    ).order_by("-registered_on")

    return render(
        request,
        "my-registrations.html",
        {
            "registrations": registrations,
        }
    )

# ==========================
# MY TICKETS
# ==========================

@login_required(login_url="login")
def my_tickets(request):

    tickets = Registration.objects.filter(
        email=request.user.email
    ).select_related("event")

    return render(
        request,
        "my-tickets.html",
        {
            "tickets": tickets
        }
    )
# ==========================
# JOIN EVENT LIST
# ==========================

@login_required(login_url="login")
def join_event_list(request):

    registrations = Registration.objects.select_related("event").all()

    return render(
        request,
        "join-event-list.html",
        {
            "registrations": registrations
        }
    )


# ==========================
# COMPLETED EVENTS
# ==========================

@login_required(login_url="login")
def completed_events(request):

    events = Event.objects.filter(
        status="Completed"
    )

    return render(
        request,
        "completed-events.html",
        {
            "events": events
        }
    )
# ==========================
# WISHLIST
# ==========================

@login_required(login_url="login")
def wishlist(request):

    wishlist = Wishlist.objects.filter(
        user=request.user
    )

    return render(
        request,
        "wishlist.html",
        {
            "wishlist": wishlist,
        }
    )


@login_required(login_url="login")
def add_to_wishlist(request, id):

    event = get_object_or_404(Event, id=id)

    wishlist = Wishlist.objects.filter(
        user=request.user,
        event=event
    )

    if wishlist.exists():

        wishlist.delete()

        messages.success(
            request,
            "Event removed from Wishlist."
        )

    else:

        Wishlist.objects.create(
            user=request.user,
            event=event
        )

        messages.success(
            request,
            "Event added to Wishlist."
        )

    return redirect(request.META.get("HTTP_REFERER", "event_list"))


@login_required(login_url="login")
def participants(request, id):

    event = get_object_or_404(
        Event,
        id=id
    )

    query = request.GET.get("q")

    registrations = Registration.objects.filter(
        event=event
    )

    if query:
        registrations = registrations.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(college__icontains=query)
        )

    return render(
    request,
    "participants.html",
    {
        "event": event,
        "registrations": registrations,
        "query": query,
        "total_participants": registrations.count(),
        "present": registrations.filter(attendance="Present").count(),
        "absent": registrations.filter(attendance="Absent").count(),
        "pending": registrations.filter(attendance="Pending").count(),
    }
)
# ==========================
# FEEDBACK PAGE
# ==========================

@login_required(login_url="login")
def feedback(request, id):

    event = get_object_or_404(Event, id=id)

    return render(
        request,
        "feedback.html",
        {
            "event": event
        }
    )


# ==========================
# FEEDBACK FORM
# ==========================

@login_required(login_url="login")
def feedback_form(request, id):

    event = get_object_or_404(Event, id=id)

    if request.method == "POST":

        registration = Registration.objects.filter(
            event=event
        ).first()

        Feedback.objects.create(

            event=event,

            registration=registration,

            rating=request.POST["rating"],

            comments=request.POST["comments"]

        )

        messages.success(
            request,
            "Feedback Submitted Successfully!"
        )

        return redirect("view_feedback")

    return render(
        request,
        "feedback-form.html",
        {
            "event": event
        }
    )


# ==========================
# VIEW FEEDBACK
# ==========================

@login_required(login_url="login")
def view_feedback(request):

    feedbacks = Feedback.objects.all()

    return render(
        request,
        "view-feedback.html",
        {
            "feedbacks": feedbacks
        }
    )


@login_required(login_url="login")
def student_dashboard(request):

    events = Event.objects.filter(status="Active").order_by("date")

    total_registrations = Registration.objects.filter(
        email=request.user.email
    ).count()

    upcoming_count = events.count()

    completed_events = Event.objects.filter(
        status="Completed"
    ).count()

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    return render(
        request,
        "student-dashboard.html",
        {
            "events": events,
            "total_registrations": total_registrations,
            "upcoming_count": upcoming_count,
            "completed_events": completed_events,
            "wishlist_count": wishlist_count,
        }
    )


def category_list(request):

    categories = Category.objects.all()

    return render(
        request,
        "category-list.html",
        {
            "categories": categories
        }
    )


@login_required(login_url="login")
def reports(request):

    organizer = get_object_or_404(
        Organizer,
        user=request.user
    )

    events = Event.objects.filter(
        organizer=organizer
    )

    registrations = Registration.objects.filter(
        event__organizer=organizer
    )

    total_events = events.count()

    active_events = events.filter(
        status="Active"
    ).count()

    completed_events = events.filter(
        status="Completed"
    ).count()

    total_participants = registrations.count()

    present = registrations.filter(
        attendance="Present"
    ).count()

    absent = registrations.filter(
        attendance="Absent"
    ).count()

    pending = registrations.filter(
        attendance="Pending"
    ).count()

    total_feedback = Feedback.objects.filter(
        event__organizer=organizer
    ).count()

    revenue = events.aggregate(
        total=Sum("price")
    )["total"] or 0

    attendance_percentage = 0

    if total_participants > 0:
        attendance_percentage = round(
            (present / total_participants) * 100,
            2
        )

    context = {

        "total_events": total_events,

        "active_events": active_events,

        "completed_events": completed_events,

        "participants": total_participants,

        "present": present,

        "absent": absent,

        "pending": pending,

        "feedback": total_feedback,

        "revenue": revenue,

        "attendance_percentage": attendance_percentage,

    }

    return render(
        request,
        "reports.html",
        context
    )

def edit_category(request, id):

    category = get_object_or_404(Category, id=id)

    if request.method == "POST":

        category.name = request.POST["name"]
        category.description = request.POST["description"]

        category.save()

        messages.success(
            request,
            "Category updated successfully!"
        )

        return redirect("category_list")

    return render(
        request,
        "edit-category.html",
        {
            "category": category
        }
    )


def delete_category(request, id):

    category = get_object_or_404(Category, id=id)

    category.delete()

    messages.success(
        request,
        "Category deleted successfully!"
    )

    return redirect("category_list")

def add_member(request):

    if request.method == "POST":

        Organizer.objects.create(

            name=request.POST["name"],
            email=request.POST["email"],
            phone=request.POST["phone"],
            department=request.POST["department"],
            designation=request.POST["designation"]

        )

        messages.success(
            request,
            "Organizer Added Successfully!"
        )

        return redirect("member_list")

    return render(request, "add-member.html")

def member_list(request):

    members = Organizer.objects.all()

    return render(
        request,
        "member-list.html",
        {
            "members": members
        }
    )

def edit_member(request, id):

    member = get_object_or_404(
        Organizer,
        id=id
    )

    if request.method == "POST":

        member.name = request.POST["name"]
        member.email = request.POST["email"]
        member.phone = request.POST["phone"]
        member.department = request.POST["department"]
        member.designation = request.POST["designation"]

        member.save()

        messages.success(
            request,
            "Organizer Updated Successfully!"
        )

        return redirect("member_list")

    return render(
        request,
        "edit-member.html",
        {
            "member": member
        }
    )

def delete_member(request, id):

    member = get_object_or_404(
        Organizer,
        id=id
    )

    member.delete()

    messages.success(
        request,
        "Organizer Deleted Successfully!"
    )

    return redirect("member_list")

@login_required
def settings(request):
    return render(request, "settings.html")


@login_required(login_url="login")
def edit_profile(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        profile.phone = request.POST["phone"]
        profile.college = request.POST["college"]
        profile.department = request.POST["department"]
        profile.year = request.POST["year"]

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        messages.success(
            request,
            "Profile Updated Successfully!"
        )

        return redirect("profile")

    return render(
        request,
        "edit-profile.html",
        {
            "profile": profile
        }
    )

@login_required(login_url="login")
def profile(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    total_registrations = Registration.objects.filter(
        email=request.user.email
    ).count()

    total_tickets = Registration.objects.filter(
        email=request.user.email
    ).count()

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    feedback_count = Feedback.objects.filter(
        registration__email=request.user.email
    ).count()

    return render(
        request,
        "profile.html",
        {
            "profile": profile,
            "total_registrations": total_registrations,
            "total_tickets": total_tickets,
            "wishlist_count": wishlist_count,
            "feedback_count": feedback_count,
        }
    )

def create_category(request):

    if request.method == "POST":

        Category.objects.create(
            name=request.POST["name"],
            description=request.POST["description"]
        )

        messages.success(
            request,
            "Category created successfully!"
        )

        return redirect("category_list")

    return render(
        request,
        "create-category.html"
    )

@login_required(login_url="login")
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    data = []

    for notification in notifications:

        data.append({
            "id": notification.id,
            "message": notification.message,
            "created_at": notification.created_at.strftime(
                "%d %b %Y %I:%M %p"
            ),
            "is_read": notification.is_read,
        })

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        "notifications": data,
        "unread_count": unread_count,
    })

@login_required(login_url="login")
def mark_notifications_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True
    )

    return JsonResponse({
        "success": True
    })

def logout_user(request):

    # Clear any pending messages
    storage = messages.get_messages(request)
    for _ in storage:
        pass

    logout(request)

    messages.success(request, "Logged out successfully!")

    return redirect("login")


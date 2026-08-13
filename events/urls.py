from django.urls import path
from . import views


urlpatterns = [

    path("", views.home, name="home"),

    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("user-dashboard/", views.user_dashboard, name="user_dashboard"),

    path("create-category/", views.create_category, name="create_category"),
    path("category-list/", views.category_list, name="category_list"),
    path("edit-category/<int:id>/", views.edit_category, name="edit_category"),
    path("delete-category/<int:id>/", views.delete_category, name="delete_category"),

    path("create-event/", views.create_event, name="create_event"),
    path("event-list/", views.event_list, name="event_list"),

    path("edit-event/<int:id>/", views.edit_event, name="edit_event"),
    path("delete-event/<int:id>/", views.delete_event, name="delete_event"),

    path("event-details/<int:id>/", views.event_details, name="event_details"),

    path("register-event/<int:id>/",views.register_event,name="register_event",),
    path("join-event-list/", views.join_event_list, name="join_event_list"),
    path("my-registrations/",views.my_registrations,name="my_registrations"),
    path("my-tickets/",views.my_tickets,name="my_tickets"),
    
    path("complete-event/", views.completed_events, name="complete_event_list"),

    path("payment/", views.payment, name="payment"),
    path("ticket/<int:id>/", views.ticket, name="ticket"),
    
    path("feedback/<int:id>/", views.feedback, name="feedback"),
    path("feedback-form/<int:id>/", views.feedback_form, name="feedback_form"),
    path("feedback/",views.view_feedback,name="view_feedback"),
    path("wishlist/",views.wishlist,name="wishlist"),
    path("add-to-wishlist/<int:id>/",views.add_to_wishlist,name="add_to_wishlist"),
    path("profile/",views.profile,name="profile"),
    path("logout/", views.logout_user, name="logout"),
    path("add-member/",views.add_member,name="add_member"),
    path("member-list/",views.member_list,name="member_list"),
    path("edit-member/<int:id>/",views.edit_member,name="edit_member"),
    path("delete-member/<int:id>/",views.delete_member,name="delete_member"),
    path("settings/", views.settings, name="settings"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),

path(
    "organizer-dashboard/",
    views.organizer_dashboard,
    name="organizer_dashboard"
),
path(
    "my-events/",
    views.my_events,
    name="my_events"
),
path(
    "participants/<int:id>/",
    views.participants,
    name="participants"
),
path(
    "my-attendance/",
    views.my_attendance,
    name="my_attendance",
),

path(
    "mark-attendance/<int:id>/<str:status>/",
    views.mark_attendance,
    name="mark_attendance",
),
path(
    "reports/",
    views.reports,
    name="reports",
),

path(
    "analytics/",
    views.analytics,
    name="analytics",
),
path(
    "calendar/",
    views.calendar_view,
    name="calendar",
),
path(
    "notifications/",
    views.notifications,
    name="notifications"
),

path(
    "notifications/read/",
    views.mark_notifications_read,
    name="mark_notifications_read"
),
]

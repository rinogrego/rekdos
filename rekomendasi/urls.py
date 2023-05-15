from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:profile_username>", views.profile, name="profile"),
    path("profile/<str:profile_username>/save", views.profile_save, name="profile-save"),
    path("petunjuk", views.petunjuk, name="petunjuk"),
    
    path("run/<int:run_id>", views.run, name="run"),
    path("run/create", views.run_create, name="run-create"),
    path("run/join/<int:run_id>", views.run_join, name="run-join"),
    path("run/leave/<int:run_id>", views.run_leave, name="run-leave"),
    path("run/finish/<int:run_id>", views.run_finish, name="run-finish"),
]
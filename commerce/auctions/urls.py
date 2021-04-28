from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-new", views.create_listing, name="new"),
    path("listing/<int:l_id>/", views.listing, name="info"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category/<str:cat>", views.categories, name="categories")
]

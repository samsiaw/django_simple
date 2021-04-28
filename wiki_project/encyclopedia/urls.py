from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('wiki/<str:entry_name>', views.entry_view, name = "entry_site"),

    path('query', views.query_search, name = "search"),
    path('new-page', views.create_new_page, name = "create_new"),
    path('edit-page', views.edit_page, name= "edit"),
    path('random', views.random_page, name= "random_page"),
    path('delete-page', views.delete_page, name= "delete_page")
]

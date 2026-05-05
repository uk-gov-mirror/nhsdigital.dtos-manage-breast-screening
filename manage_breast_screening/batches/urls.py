from django.urls import path

from . import views

app_name = "batches"

urlpatterns = [
    path("upload-csv/", views.upload_csv, name="upload_csv"),
]

from django.urls import path

from . import views

app_name = "reading"

urlpatterns = [
    path("", views.show_reading_dashboard_view, name="show_reading_dashboard"),
    path(
        "sessions/<uuid:session_pk>/reads/<uuid:pk>/",
        views.ShowImageReadView.as_view(),
        name="image_read",
    ),
    path(
        "sessions/<uuid:session_pk>/reads/<uuid:read_pk>/technical-recall/",
        views.AddTechnicalRecallView.as_view(),
        name="add_technical_recall",
    ),
]

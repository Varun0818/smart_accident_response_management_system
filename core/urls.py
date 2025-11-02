from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reporter/login/', views.reporter_login, name='reporter_login'),
    path('reporter/report/', views.report_accident, name='report_accident'),
    path('reporter/tracking/<int:report_id>/', views.reporter_tracking, name='reporter_tracking'),
    path('responder/login/', views.responder_login, name='responder_login'),
    path('responder/dashboard/', views.responder_dashboard, name='responder_dashboard'),
    path('responder/case/<int:report_id>/', views.case_detail, name='case_detail'),
    path("api/accept/", views.api_accept, name="api_accept"),
    path("api/reject/", views.api_reject, name="api_reject"),
    path("api/resolve/", views.api_resolve, name="api_resolve"),
    path('api/update_responder_location/', views.update_responder_location, name='update_responder_location'),
]
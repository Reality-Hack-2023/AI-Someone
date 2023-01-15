from django.urls import path

from . import views

app_name = "Homapage"

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('edit/<str:title>', views.edit, name='edit'),
    path('depth/<str:title>', views.generate_depth, name='depth'),
    path('model/<str:title>', views.generate_model, name='model'),
    path('viewer/<str:title>', views.view_model, name='viewer'),
    # path('details/', views.details, name='details')
]

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='auth_freedom/home.html'), name='home'),
    path('', include('auth_freedom.urls')),
    path('recruiting/', include('recruiting_system.urls')),
    path('analyze/', include('analyze_candidates.urls')),
    path('convertor/', include('convertor_to_json.urls', namespace='convertor_to_json')),
]
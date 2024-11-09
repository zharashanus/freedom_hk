from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auth_freedom.urls')),
    path('recruiting/', include('recruiting_system.urls')),
    path('analyze/', include('analyze_candidates.urls')),
    path('convertor/', include('convertor_to_json.urls', namespace='convertor_to_json')),
]
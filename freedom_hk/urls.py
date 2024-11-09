from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auth_freedom.urls')),
    path('recruiting/', include('recruiting_system.urls')),  # Добавляем это
    path('ai/', include('ai_assistant.urls')),
    path('convertor/', include('convertor_to_json.urls', namespace='convertor_to_json')),
]
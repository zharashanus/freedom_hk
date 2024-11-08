from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings
import jwt

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/admin/') and not request.path.startswith('/login/'):
            access_token = request.COOKIES.get('access_token')
            if not access_token:
                return JsonResponse({'error': 'No access token'}, status=401)
            
            try:
                jwt.decode(access_token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response
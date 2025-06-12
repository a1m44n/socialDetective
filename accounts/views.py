from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    logger.debug(f"Attempting login with email: {email}")

    if not email or not password:
        logger.warning("Email or password not provided")
        return Response(
            {'error': 'Please provide both email and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(email=email, password=password)
    if not user:
        logger.warning("Invalid credentials")
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    logger.info(f"Login successful for email: {email}")

    refresh = RefreshToken.for_user(user)
    return Response({
        'token': str(refresh.access_token),
        'user': {
            'email': user.email,
            'role': user.role
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    return Response({
        'user': {
            'email': request.user.email,
            'role': request.user.role
        }
    })

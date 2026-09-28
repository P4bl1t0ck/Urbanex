from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer
# Create your views here.

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(email=email).first()

        if user and user.is_locked:
            return Response({"detail": "Cuenta bloqueada. Contacta al administrador."}, status=403)

        if not user or not user.check_password(password):
            if user:
                user.failed_attempts += 1
                if user.failed_attempts >= 5:
                    user.is_locked = True
                user.save()
            return Response({"detail": "Credenciales inválidas."}, status=401)

        user.failed_attempts = 0
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
        })
        
class PropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = sself.request.user
        if user.role == 'admin'
            return Property.objects.all()
        return Property.objects.filter(agent=user)
    def perfomr_create(self, serializer):
        serializer.save(agent=self.request.user, status='captacion')
        
class PropertyPublishView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            property_obj = Property.objects.get(pk=pk)
        except Property.DoesNotExist:
            return Response ({"detail":"Propiedad no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    property_obj.status = 'disponible'
    property_obj.save()
    
    return Response({
        "detail": "Propiedad publicada con éxito. Ahora es visible en el catálogo público.",
        "status": property_obj.status
    }), status= status.HTTP_200_OK
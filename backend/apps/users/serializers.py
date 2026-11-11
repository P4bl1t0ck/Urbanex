from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
import hashlib
import logging
import re
import secrets
import smtplib
import resend
from resend.exceptions import ResendError

from .authentication import token_matches_password_version
from .models import PasswordResetToken, Property, PropertyImage, UserActivationToken

User = get_user_model()
logger = logging.getLogger(__name__)


class ActivationEmailError(APIException):
    status_code = 502
    default_detail = (
        "No se pudo enviar el correo de activación. Verifica la configuración "
        "del remitente y del proveedor de correo."
    )
    default_code = "activation_email_failed"


class PasswordResetEmailError(Exception):
    pass


def build_username(email):
    base = email[:150]
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix_text = f"-{suffix}"
        username = f"{base[:150 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    return username


def send_activation_email(user):
    raw_token = secrets.token_urlsafe(32)
    UserActivationToken.objects.create(
        user=user,
        token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        expires_at=timezone.now() + timedelta(hours=24),
    )
    activation_url = (
        f"{settings.FRONTEND_BASE_URL.rstrip('/')}/activate#{raw_token}"
    )
    subject = "Activa tu cuenta de Urbanex"
    message = (
        f"Hola {user.first_name or user.email},\n\n"
        "El administrador creó una cuenta para ti. "
        "Usa este enlace dentro de las próximas 24 horas para establecer tu "
        f"contraseña y activarla:\n{activation_url}\n"
    )

    if settings.EMAIL_PROVIDER == "resend":
        resend.api_key = settings.RESEND_API_KEY
        try:
            resend.Emails.send(
                {
                    "from": settings.DEFAULT_FROM_EMAIL,
                    "to": [user.email],
                    "subject": subject,
                    "text": message,
                }
            )
        except ResendError as exc:
            logger.error(
                "Resend rejected activation email for user_id=%s: %s (%s)",
                user.pk,
                exc.message,
                exc.error_type,
            )
            raise ActivationEmailError() from exc
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_password_reset_email(user, token):
    reset_url = (
        f"{settings.FRONTEND_BASE_URL.rstrip('/')}/reset-password#token={token}"
    )
    subject = "Restablece tu contraseña de Urbanex"
    message = (
        f"Hola {user.first_name or user.email},\n\n"
        "Recibimos una solicitud para restablecer tu contraseña. "
        "El enlace es de un solo uso y vence en 60 minutos:\n"
        f"{reset_url}\n\n"
        "Si no solicitaste este cambio, puedes ignorar este mensaje."
    )

    if settings.EMAIL_PROVIDER == "resend":
        resend.api_key = settings.RESEND_API_KEY
        try:
            resend.Emails.send(
                {
                    "from": settings.DEFAULT_FROM_EMAIL,
                    "to": [user.email],
                    "subject": subject,
                    "text": message,
                }
            )
        except ResendError as exc:
            logger.error(
                "Resend rejected password reset email for user_id=%s: %s (%s)",
                user.pk,
                exc.message,
                exc.error_type,
            )
            raise PasswordResetEmailError from exc
        return

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except (smtplib.SMTPException, OSError) as exc:
        logger.exception(
            "Could not send password reset email for user_id=%s",
            user.pk,
        )
        raise PasswordResetEmailError from exc


class ManagedUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    def validate_email(self, value):
        email = value.strip().lower()
        users = User.objects.filter(email__iexact=email)
        if self.instance:
            users = users.exclude(pk=self.instance.pk)
        if users.exists():
            raise serializers.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def validate_phone(self, value):
        if self.instance and value == self.instance.phone:
            return value

        normalized_phone = re.sub(r"[\s().-]", "", value)
        if normalized_phone and not re.fullmatch(r"09\d{8}", normalized_phone):
            raise serializers.ValidationError(
                "Ingresa un celular ecuatoriano de 10 dígitos que empiece con 09."
            )
        return normalized_phone

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_active",
            "deactivation_reason",
            "failed_attempts",
            "is_locked",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "username",
            "is_active",
            "deactivation_reason",
            "failed_attempts",
            "is_locked",
            "date_joined",
        )

    def validate(self, attrs):
        if self.instance and "email" in self.initial_data:
            raise serializers.ValidationError(
                {"email": "El correo no se puede editar desde esta pantalla."}
            )
        if self.instance is None and not attrs.get("email"):
            raise serializers.ValidationError({"email": "Este campo es obligatorio."})
        if (
            self.instance
            and self.instance.is_active
            and self.instance.role == User.Role.ADMIN
            and attrs.get("role") == User.Role.ADVISOR
            and User.objects.filter(is_active=True, role=User.Role.ADMIN).count() == 1
        ):
            raise serializers.ValidationError(
                {"role": "Debe permanecer al menos un administrador activo."}
            )
        return attrs

    def create(self, validated_data):
        email = validated_data.pop("email").strip().lower()
        user = User(
            username=build_username(email),
            email=email,
            **validated_data,
        )
        user.set_unusable_password()
        user.is_active = False
        with transaction.atomic():
            user.save()
            send_activation_email(user)
        return user


class UserActivationSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        token_hash = hashlib.sha256(attrs["token"].encode("utf-8")).hexdigest()
        activation = (
            UserActivationToken.objects.select_related("user")
            .filter(
                token_hash=token_hash,
                used_at__isnull=True,
                expires_at__gt=timezone.now(),
                user__is_active=False,
                user__deactivation_reason="",
            )
            .first()
        )
        if activation is None:
            raise serializers.ValidationError(
                {"token": "El enlace no es válido, ya se usó o venció."}
            )

        try:
            password_validation.validate_password(attrs["password"], activation.user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc
        attrs["activation"] = activation
        return attrs


class UserDeactivationSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)

    def validate_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError("El motivo es obligatorio.")
        return value.strip()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    #Maybe this is the reason why the login is not working, because the serializer is not returning the token. 
    #YEAH that what i think ! 


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True, trim_whitespace=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        raw_token = attrs["token"]
        generator_token, separator, _nonce = raw_token.rpartition(".")
        if not separator or not generator_token:
            raise serializers.ValidationError(
                {"token": "El enlace no es válido, ya se usó o venció."}
            )

        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        reset_token = (
            PasswordResetToken.objects.select_related("user")
            .filter(
                token_hash=token_hash,
                is_used=False,
                expires_at__gt=timezone.now(),
                user__is_active=True,
            )
            .first()
        )
        if reset_token is None or not default_token_generator.check_token(
            reset_token.user,
            generator_token,
        ):
            raise serializers.ValidationError(
                {"token": "El enlace no es válido, ya se usó o venció."}
            )

        try:
            password_validation.validate_password(
                attrs["password"],
                reset_token.user,
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"password": exc.messages}
            ) from exc

        attrs["reset_token_id"] = reset_token.pk
        attrs["generator_token"] = generator_token
        return attrs


class PasswordAwareRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs["refresh"])
        except TokenError as exc:
            raise InvalidToken("El refresh token no es válido o venció.") from exc

        user_id = refresh.payload.get(jwt_api_settings.USER_ID_CLAIM)
        user = User.objects.filter(
            **{jwt_api_settings.USER_ID_FIELD: user_id}
        ).first()
        if user is None or not user.is_active:
            raise AuthenticationFailed("El refresh token no es válido.")
        if not token_matches_password_version(user, refresh.payload):
            raise AuthenticationFailed(
                "La sesión fue invalidada porque cambió la contraseña.",
                code="password_changed",
            )

        return {"access": str(refresh.access_token)}
    
class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['uploaded_at']

#Now we create the class thats going to handle the property Serializer
class PropertyWithdrawalSerializer(serializers.Serializer):
    unavailability_reason = serializers.CharField(trim_whitespace=True)


class PropertySerializer(serializers.ModelSerializer):
    agent_name = serializers.SerializerMethodField()
    #Agregamos las imagenes vinculadas.
    images = PropertyImageSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        #fields = '__all__' # No hace caso a las peticiones y comrpobaciones durante las modificaciones de json files.
        fields = [
            'id', 'agent', 'agent_name', 'title', 'description', 
            'property_type', 'status', 'price', 'area_m2', 
            'bedrooms', 'bathrooms', 'parking_spaces', 'location',
            'latitude', 'longitude',
            'images',
            'unavailability_reason', 'created_at', 'updated_at'
        ]
        # DT-09: status solo cambia por acciones de negocio (PropertyPublishView, HU-53),
        # nunca por un POST/PATCH generico.
        read_only_fields = ('agent', 'status', 'created_at', 'updated_at')
    
    def get_agent_name(self,obj): #This function it made for get the full name and user name of who make or add the proerty.
        if obj.agent:
            return obj.agent.get_full_name() or obj.agent.username
        return None
    
    def validate(self, attrs): 
        # Obtener el estado del objeto actual o de los datos entrantes
        status = attrs.get('status', getattr(self.instance, 'status', None))
        unavailability_reason = attrs.get('unavailability_reason', getattr(self.instance, 'unavailability_reason', None))

        if status == 'no_disponible' and not unavailability_reason:
            raise serializers.ValidationError({
                "unavailability_reason": "Debe especificar un motivo para marcar la propiedad como No disponible."
            })

        return attrs
    
    ##Remember Delete this code  before of the second commit.
    ''' # Its not making the validation on each field of the .json file
    def validate(self, attrs):
        if data.get('status') == 'no_disponible' and not data.get('unavailability_reason'):
            raise serializers.ValidationError({
                "unavailability_reason":"Debe especificar un motivo para marcar la propiedad como No disponible."
            })
        if data.get('status') in ['vendido', 'arrendado']:
            raise serializers.ValidationError({
                "status":"Las propiedaes se encuentran en estasdos Vendido o Arrendado solo pueden asignarse mediante la confirmación de Cierre definitivo"
            })
            
        return data
    '''
    
    def get_agent_name(self, obj):
        if obj.agent:
            # Intenta con el nombre completo; si está vacío, devuelve el username o el email
            full_name = f"{obj.agent.first_name} {obj.agent.last_name}".strip()
            return full_name if full_name else (obj.agent.username or obj.agent.email)
        return ""

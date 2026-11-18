"""Fotos públicas: proveedor de escritura configurable y lectura compatible."""

import uuid
from collections.abc import Mapping

import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.utils import cloudinary_url
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible
from rest_framework.exceptions import APIException


class MediaUploadUnavailable(APIException):
    status_code = 503
    default_detail = "No se pudo guardar la fotografía. Intenta nuevamente."
    default_code = "media_upload_unavailable"


class MediaDeleteUnavailable(APIException):
    status_code = 503
    default_detail = "No se pudo eliminar la fotografía. Comprueba la configuración e intenta nuevamente."
    default_code = "media_delete_unavailable"


def public_media_config(environ: Mapping[str, str]) -> dict:
    provider = environ.get("MEDIA_PROVIDER", "local").strip().lower()
    if provider not in {"local", "cloudinary"}:
        raise ImproperlyConfigured("MEDIA_PROVIDER debe ser 'local' o 'cloudinary'.")
    options = {"provider": provider}
    for key in ("cloud_name", "api_key", "api_secret"):
        value = environ.get(f"CLOUDINARY_{key.upper()}", "").strip()
        if provider == "cloudinary" and not value:
            raise ImproperlyConfigured(
                f"CLOUDINARY_{key.upper()} es obligatorio cuando MEDIA_PROVIDER=cloudinary."
            )
        options[key] = value
    return {"BACKEND": "config.media_storage.PublicMediaStorage", "OPTIONS": options}


@deconstructible
class PublicMediaStorage(Storage):
    """Las rutas anteriores siguen locales; cloudinary/<cuenta>/<id> es remoto.

    Cambiar de proveedor afecta nuevas subidas, no mueve archivos ni reinterpreta
    rutas guardadas. Document.file tiene su propio storage privado explícito.
    """

    prefix = "cloudinary/"

    def __init__(self, provider="local", cloud_name="", api_key="", api_secret=""):
        self.provider = provider
        self.cloud_name = cloud_name
        self._credentials = {"cloud_name": cloud_name, "api_key": api_key, "api_secret": api_secret}
        self.local = FileSystemStorage()

    def _remote_parts(self, name):
        if not name.startswith(self.prefix):
            return None
        parts = name.split("/")
        if len(parts) != 3 or not parts[1] or len(parts[2]) != 32:
            raise ValueError("Referencia de imagen de Cloudinary inválida.")
        if not all(char in "0123456789abcdef" for char in parts[2]):
            raise ValueError("Referencia de imagen de Cloudinary inválida.")
        return parts[1], f"urbanex/{parts[2]}"

    def save(self, name, content, max_length=None):
        if self.provider == "local":
            return self.local.save(name, content, max_length=max_length)
        # Identidad nueva: no sobrescribe fotos ni utiliza nombres del cliente.
        token = uuid.uuid4().hex
        reference = f"{self.prefix}{self.cloud_name}/{token}"
        if max_length and len(reference) > max_length:
            raise ValueError("La referencia de Cloudinary excede la longitud del campo.")
        content.seek(0)
        try:
            cloudinary.uploader.upload(
                content,
                public_id=f"urbanex/{token}",
                resource_type="image",
                type="upload",
                overwrite=False,
                unique_filename=False,
                timeout=30,
                **self._credentials,
            )
        except (CloudinaryError, OSError):
            # No propagar mensajes del proveedor ni sus parámetros al cliente.
            raise MediaUploadUnavailable() from None
        return reference

    def url(self, name):
        remote = self._remote_parts(name)
        if remote is None:
            return self.local.url(name)
        cloud_name, public_id = remote
        return cloudinary_url(
            public_id, cloud_name=cloud_name, resource_type="image", type="upload",
            secure=True, quality="auto", fetch_format="auto",
        )[0]

    def _open(self, name, mode="rb"):
        if self._remote_parts(name) is not None:
            raise NotImplementedError("Las fotos de Cloudinary se consultan mediante su URL HTTPS.")
        return self.local.open(name, mode)

    def path(self, name):
        if self._remote_parts(name) is not None:
            raise NotImplementedError("Cloudinary no tiene una ruta local.")
        return self.local.path(name)

    def exists(self, name):
        if self._remote_parts(name) is not None:
            # No se hace una consulta remota: no usado para nombres aleatorios.
            raise NotImplementedError("La existencia remota requiere consultar Cloudinary.")
        return self.local.exists(name)

    def size(self, name):
        if self._remote_parts(name) is not None:
            raise NotImplementedError("El tamaño remoto no se consulta al representar la ficha.")
        return self.local.size(name)

    def delete(self, name):
        remote = self._remote_parts(name)
        if remote is None:
            try:
                return self.local.delete(name)
            except OSError:
                raise MediaDeleteUnavailable() from None
        cloud_name, public_id = remote
        if cloud_name != self.cloud_name or not self._credentials["api_key"] or not self._credentials["api_secret"]:
            raise MediaDeleteUnavailable()
        try:
            result = cloudinary.uploader.destroy(
                public_id, resource_type="image", type="upload", invalidate=True,
                timeout=30, **self._credentials,
            )
        except (CloudinaryError, OSError):
            raise MediaDeleteUnavailable() from None
        if result.get("result") not in {"ok", "not found"}:
            raise MediaDeleteUnavailable()

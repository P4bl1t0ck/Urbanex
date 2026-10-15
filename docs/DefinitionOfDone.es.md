# Definiciones de Listo - Urbanex
- El siguiente criterio es el que utilizamos para evaluar y probar si cada historial de usuario (HU) es suficiente para ser funcional y proporcionar al usuario el valor de negocio que realmente buscamos.
- Pruebas realizadas con Postmant.
*Traducción al español [Español](DefinitionOfDone.es.md)*

## Criterios de Backend (Pruebas de Caja Negra)
- [ ] Autenticación estricta: Todas las rutas de escritura (POST, PUT, PATCH, DELETE) requieren un token JWT válido. Las solicitudes sin token devuelven un error `401 No autorizado`.
- [ ] Autorización basada en roles: El sistema valida que el usuario sea el propietario o administrador del recurso. Las infracciones devuelven un error `403 Prohibido`.
- [ ] Integridad de la carga útil: Las solicitudes con campos obligatorios vacíos o tipos de datos incorrectos se rechazan con un error `400 Solicitud incorrecta`.
- [ ] Disponibilidad pública: Los endpoints de consulta (GET) destinados al cliente final, como el catálogo de propiedades, responden con `200 OK` sin necesidad de autenticación.

## Criterios de la interfaz (MVP funcional)
- [ ] Navegabilidad: El usuario puede acceder al flujo desde la interfaz principal sin bloqueos ni errores 404.
- [ ] Consumo de API: La interfaz se comunica correctamente con el backend, gestionando de forma segura los tokens en las cabeceras.
- [ ] Retroalimentación visual: La interfaz reacciona al éxito o fracaso de una operación (por ejemplo, la propiedad recién publicada aparece inmediatamente en la cuadrícula).
- [ ] Gestión de multimedia: Se permiten imágenes externas (como las que proporciona Django) y se renderizan sin afectar al diseño.

---*Nota: Ninguna funcionalidad se considera completa si solo funciona en Postman. Debe poder ejecutarse a través de la interfaz gráfica.*
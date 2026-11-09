# Urbanex — Procesos de la empresa (extraídos y comparados)

- Fuente: DatosCaptsone (2).docx (borrador, 2026-10-24)
- Fecha del borrador: 2026-10-24
- Regla de comparación: si un paso difiere de la tesis, la tesis oficial (`ProyectoCapstoneV4`) manda.
- Alcance: esta versión solo extrae la sección de procesos del borrador y marca las diferencias para decidir con Pablo y Sebas.

## T1. Captación de propiedades

### AS-IS (estado actual manual)
1. El cliente se acerca con su bien o la empresa contacta una propiedad publicada en venta/renta. [coincide]
2. Se recibe y registra la información básica del inmueble manualmente. [coincide]
3. Se solicita documentación legal (gravámenes, escrituras, impedimentos) para revisión de Urbanex. [coincide]
4. Se verifica que el impuesto predial y las expensas estén al día. [coincide]
5. Se evalúa la viabilidad comercial del inmueble. [coincide]
6. Se realiza el avalúo comercial manual. [coincide]
7. Se presenta el precio al cliente con base en el avalúo y la oferta/demanda del mercado. [coincide]
8. El cliente acepta o rechaza el avalúo; si rechaza, termina el proceso. [coincide]
9. Se firma el contrato de corretaje. [coincide]
10. Se registra la propiedad como captada en el inventario interno (hojas de cálculo o registros físicos). [coincide]

### TO-BE (estado futuro con sistema)
1. El propietario entrega la información del inmueble y el asesor verifica que la documentación esté al día (escritura, comprobantes prediales, expensas). [coincide]
2. El asesor registra la propiedad en el sistema con su información técnica y multimedia; la propiedad queda en estado En captación, sin exhibirse al público, y el asesor queda como captador y responsable inicial. [coincide]
3. El asesor carga la documentación inicial en el expediente digital de la propiedad. [coincide]
4. El asesor realiza el avalúo comercial con el motor paramétrico para contrastar el precio esperado por el propietario con el valor de mercado. [coincide]
5. El asesor presenta el resultado del avalúo al propietario y negocia el precio de captación con base en él. Si acuerdan un precio acorde al mercado, se procede con la captación; si no se llega a un acuerdo, la propiedad se marca como No disponible con el motivo correspondiente y no se publica. [coincide]
6. Aceptada la captación, se formaliza y carga el contrato de corretaje en el expediente. [coincide]
7. Con el avalúo registrado y el contrato de corretaje cargado, el asesor publica la propiedad, que pasa a estado Disponible y se exhibe en el catálogo público. [coincide]

## T2. Marketing y generación de prospectos

### AS-IS (estado actual manual)
1. Se crea la ficha del inmueble con fotos, descripción y precio. [coincide]
2. Se publica en redes sociales (Facebook). [difiere: la tesis oficial prioriza el catálogo web y la conversión desde la ficha, no solo la difusión en redes sociales]
3. Se publica en Marketplace de Facebook. [difiere: la tesis manda la ficha web como canal principal; Marketplace aparece como canal de apoyo en el borrador]
4. Se amplía el alcance mediante promoción pagada ocasional en Facebook. [difiere: la tesis conserva la lógica de captación y tráfico hacia la ficha, pero no hace de Facebook el eje exclusivo]
5. Se genera contenido atractivo orientado a llegar al público objetivo en Facebook. [difiere: el borrador enfatiza Facebook; la tesis prioriza el catálogo web y el seguimiento dentro del sistema]
6. Se reciben mensajes de interesados y se identifican oportunidades. [coincide]

### TO-BE (estado futuro con sistema)
1. Se crea y almacena de manera centralizada la ficha digital del inmueble con multimedia optimizada y descripción estructurada. [coincide]
2. Una vez registrado y con estado Disponible, el portal público lo muestra automáticamente dentro del catálogo de inmuebles, sin requerir una publicación manual adicional. [coincide]
3. El asesor publica el inmueble en Marketplace de Facebook, incluyendo un enlace directo hacia la ficha específica en el portal público web para canalizar el interés. [difiere: la tesis prioriza la ficha web con canal de origen; la publicación en Marketplace aparece como canal auxiliar]
4. Se amplía alcance mediante promoción pagada en canales digitales redirigiendo el tráfico hacia el portal web. [coincide]
5. Se genera contenido atractivo en redes sociales enfocado en derivar usuarios al ecosistema digital propio. [difiere: se conserva la idea, pero la tesis no le da predominio a Facebook como único canal]
6. Se reciben manifestaciones de interés de forma asíncrona mediante formularios del portal web o mensajería externa conectada al sistema. [coincide]

## T3. Gestión de contacto y citas

### AS-IS (estado actual manual)
1. El interesado se comunica por contacto directo o mediante redes sociales. [coincide]
2. El asesor registra la información del cliente y la propiedad de interés. [coincide]
3. El asesor coordina la cita y la visita presencial. [coincide]
4. Se registra el resultado de la cita o la visita. [coincide]
5. Se toma la decisión de continuar o descartar la oportunidad. [coincide]

### TO-BE (estado futuro con sistema)
1. Captación manual: el asesor ingresa manualmente en el portal los datos de un contacto captado por canales informales (referidos, llamadas directas o visitas presenciales), lo que crea el Contacto y abre inmediatamente una Oportunidad Comercial asignada a su nombre. [coincide]
2. Captación digital: se recibe la interacción del interesado en el portal público o un mensaje entrante en redes sociales mediante webhook en el backend. [coincide]
3. Si la interacción proviene de Messenger, el sistema conserva los mensajes como Conversación Inicial y responde automáticamente, solicitando el número de teléfono del interesado. Si no lo proporciona, la Conversación Inicial queda pendiente de atención y genera un indicador para revisar manualmente. [coincide]
4. Si la propiedad visitada en el portal público está Reservada, el sistema restringe los botones de contacto directo y habilita el formulario para Registrar Interés. [coincide]
5. Si un cliente usa este formulario, el sistema registra el Contacto y abre una Oportunidad Comercial con estado de seguimiento en Lista de Interesados. [coincide]
6. Para inmuebles disponibles, el sistema registra la interacción inicial del interesado. Si el contacto es desde portal web o canales integrados distintos a WhatsApp, exige teléfono válido para registrar información, crear el Contacto y abrir la Oportunidad Comercial. [coincide]
7. Al ingresar un número válido, se registra la información, crea el Contacto, abre la Oportunidad Comercial asignada a un asesor y genera una notificación automática. [coincide]
8. El backend usa la API de WhatsApp Business para enviar un mensaje de bienvenida que confirma la recepción del interés y da acceso a una ficha segura. [coincide]
9. El cliente puede usar el módulo de agendamiento del portal web o solicitar atención directa al asesor. En ambos casos, el sistema registra la cita, actualiza el estado a Visita Programada y notifica al asesor asignado. [coincide]
10. El asesor continúa la atención y la negociación de forma personalizada. [coincide]
11. Se realiza la visita presencial a la propiedad. [coincide]
12. Se registra el resultado de la visita (realizada, no asistida o cancelada), la respuesta del cliente y la fecha de la interacción en el historial de trazabilidad. [coincide]
13. Si no hay interés, se registra el motivo de cierre en el historial para auditoría. Si hay interés, se avanza al proceso de venta o arriendo. [coincide]

## T4. Venta de propiedades

### AS-IS (estado actual manual)
1. El cliente expresa interés formal en comprar y el asesor actualiza el estado de la oportunidad. [coincide]
2. Se define y registra la forma de pago acordada. [coincide]
3. Se negocian condiciones, documentando acuerdos o contraofertas. [coincide]
4. Si no hay acuerdo, se registra el motivo del cierre y la oportunidad pasa a Perdida. [coincide]
5. Si hay acuerdo preliminar, se registra el abono de reserva y la propiedad pasa a Reservada. [coincide]
6. Se formalizan acuerdos preliminares y pagos anticipados. [coincide]
7. Si la negociación fracasa durante la reserva, el Administrador ejecuta la reversión y la propiedad vuelve a Disponible. [coincide]
8. Se registran pagos y saldos. [coincide]
9. Se registra la escritura de compraventa y el documento firmado se asocia al expediente. [coincide]
10. Se firma la escritura ante notario y se carga el documento final al sistema. [coincide]
11. Una vez completada la documentación y confirmados los pagos, la oportunidad avanza a Pendiente de Cierre. [coincide]
12. El Administrador revisa la cola, valida el precio final y revisa la comisión. [coincide]
13. El Administrador registra el cierre definitivo. [coincide]

### TO-BE (estado futuro con sistema)
1. El cliente expresa interés formal en comprar y el asesor actualiza el estado de la oportunidad comercial. [coincide]
2. Se define y registra en el historial de la oportunidad la forma de pago acordada. [coincide]
3. Se negocian condiciones finales, documentando los acuerdos o contraofertas en el historial de trazabilidad. [coincide]
4. Si no hay acuerdo o el cliente desiste: registrar el motivo del cierre de la negociación y actualizar la oportunidad comercial como Perdida. [coincide]
5. Si hay acuerdo preliminar: registrar el abono de reserva, lo cual actualiza el estado de la propiedad a Reservada. El sistema bloquea nuevas reservas, restringe contacto directo desde el portal y emite una notificación. [coincide]
6. Formalizar acuerdos preliminares cuando apliquen y registrar los anticipos iniciales. El asesor carga los documentos de respaldo en el expediente digital. [coincide]
7. Si la negociación fracasa durante la reserva: el Administrador ejecuta la reversión, registrando el motivo obligatorio. El sistema actualiza el estado de la propiedad a Disponible y registra el evento en el historial. [coincide]
8. Registrar el cumplimiento de los pagos y saldos correspondientes. [coincide]
9. Registrar la escritura de compraventa y asociar el documento firmado al expediente digital. [coincide]
10. Firma de escritura ante notario y carga del documento finalizado al sistema. [coincide]
11. Una vez completada la documentación y confirmados los pagos, el asesor avanza la oportunidad al estado Pendiente de Cierre. [coincide]
12. El Administrador consulta la cola de oportunidades en Pendiente de Cierre, revisa la seleccionada y registra el precio final acordado. El sistema detecta si el asesor de la oportunidad es distinto al asesor captador; si son distintos, marca el caso como Pendiente de comisión y exige registrar el acuerdo antes de continuar. [coincide]
13. El Administrador revisa y registra el cierre definitivo. Esta acción actualiza el estado del inmueble a Vendido, cierra automáticamente la oportunidad y deja la traza. [coincide]

## T5. Arriendo de propiedades

### AS-IS (estado actual manual)
1. Cliente solicita arrendar una propiedad. [coincide]
2. Evaluar perfil del arrendatario (antecedentes, referencias). [coincide]
3. Revisar documentación: certificados laborales, bancarios y de antecedentes. [coincide]
4. Validar confiabilidad y capacidad de pago. [coincide]
5. Si no cumple requisitos: rechazar solicitud y notificar por chat/llamada. [coincide]
6. Si cumple: presentar perfil del arrendatario al propietario. [coincide]
7. Acordar condiciones: garantía equivalente a 2 meses de arriendo. [coincide]
8. Aprobación por parte del propietario. [coincide]

### TO-BE (estado futuro con sistema)
1. Cliente solicita arrendar una propiedad y se actualiza el estado de la oportunidad comercial. [coincide]
2. Realizar la visita presencial a la propiedad, registrar su ejecución y documentar la respuesta del cliente en el historial de trazabilidad. [coincide]
3. Si hay interés formal para avanzar, el asesor carga los requisitos solicitados al postulante (comprobantes de ingresos, certificados, referencias) al repositorio documental de la oportunidad. [coincide]
4. Se verifica que la documentación esté completa. Tras la decisión externa del propietario de aprobar o rechazar al postulante, el asesor registra el resultado en la plataforma. Si es rechazado, se documenta el motivo en el historial de trazabilidad y se cierra la oportunidad; si es aprobado, se procede a acordar las condiciones de garantía y a registrar los términos aprobados en el sistema. [coincide]
5. Si hay acuerdo preliminar de alquiler: registrar el abono de reserva, lo cual actualiza el estado de la propiedad a "Reservada". El sistema bloquea nuevas reservas, restringe los mecanismos de contacto directo desde el portal público y emite una notificación de reserva. [coincide]
6. Si la negociación fracasa: el Administrador ejecuta la reversión en el sistema, registrando el motivo obligatorio. El sistema actualiza el estado de la propiedad a "Disponible" y registra el evento de liberación en el historial de trazabilidad. [coincide]
7. Firmar contrato de arriendo y almacenar el documento digitalizado en el expediente de la oportunidad. [coincide]
8. Entregar inmueble al arrendatario. [coincide]
9. Una vez firmado el contrato de arriendo, el asesor avanza la oportunidad al estado Pendiente de Cierre, con lo que ingresa a la cola de cierre del Administrador. El Administrador la revisa y registra el precio final acordado. El sistema detecta si el asesor de la oportunidad es distinto al asesor captador; si son distintos, marca el caso como Pendiente de comisión. [coincide]
10. El Administrador registra los términos de la comisión correspondiente cuando aplica. [coincide]
11. El Administrador revisa y registra el cierre definitivo. Esta acción actualiza el estado del inmueble a "Arrendado", cierra automáticamente las demás oportunidades comerciales asociadas a la propiedad registrando el motivo correspondiente y conserva la oportunidad ganadora en estado Cierre. Si la información está incompleta, el Administrador puede devolver la oportunidad al asesor. [coincide]

## T6. Avalúo comercial

### AS-IS (estado actual manual)
1. Recopilar características físicas del inmueble (área, estado, ubicación, acabados). [coincide]
2. Analizar oferta y demanda del sector empíricamente. [coincide]
3. Comparar con propiedades similares buscando en el mercado o por conocimiento del asesor. [coincide]
4. Calcular valor comercial estimado. [coincide]
5. Presentar análisis de valor comercial al cliente propietario. [coincide]
6. Ajustar precio según negociación y condiciones del mercado. [coincide]
7. Registrar precio acordado en el inventario interno (hojas de cálculo o expedientes). [coincide]

### TO-BE (estado futuro con sistema)
1. Registrar en el módulo de avalúos las características físicas y técnicas específicas del inmueble a evaluar. [coincide]
2. Consultar los indicadores estadísticos generales del sector provistos por el proceso de tareas programadas. [coincide]
3. El asesor busca y selecciona explícitamente entre 3 y 5 propiedades comparables (testigos) almacenadas previamente en la base de datos. [coincide]
4. El motor paramétrico del sistema procesa las áreas y precios de los comparables, aplica los factores de ajuste ponderados y calcula el valor comercial sugerido. [coincide]
5. El sistema integra opcionalmente un servicio de generación de lenguaje natural para construir un borrador formal de la justificación técnica basada en los datos numéricos. [coincide]
6. Enfoque Human-in-the-Loop: El asesor revisa el valor calculado y la justificación técnica, calibra manualmente los campos según su experiencia y aprueba el avalúo final. [coincide]
7. Almacenar de forma estructurada e inmutable en el historial de avalúos de la propiedad el cálculo generado por el motor paramétrico, el valor final ajustado y aprobado por el asesor bajo el enfoque Human-in-the-Loop, la justificación técnica y las diferencias registradas entre ambos valores, dejando preparada la estructura de datos para futuros procesos de aprendizaje automático. [coincide]

## T7. Gestión documental

### AS-IS (estado actual manual)
1. Recibir documentos del propietario o arrendatario de forma física o por WhatsApp/correo. [coincide]
2. Validar autenticidad y vigencia de los documentos visualmente. [coincide]
3. Archivar de forma física en carpetas o guardar en carpetas locales de la computadora. [coincide]
4. Agrupar documentos en el expediente físico/digital de la propiedad o cliente. [coincide]
5. Verificar que impuestos y expensas estén al día (captación). [coincide]
6. Gestionar documentación de compraventa (escrituras, declaratoria horizontal, certificados). [coincide]
7. Gestionar documentación de arriendo (laborales, bancarios, antecedentes). [coincide]
8. Buscar y consultar documentos manualmente según sea requerido por el personal de la empresa. [coincide]

### TO-BE (estado futuro con sistema)
1. El Asesor carga en el expediente digital los archivos entregados por el propietario o cliente. [coincide]
2. El Administrador verifica la autenticidad y vigencia de la documentación y registra su validación (Aprobado/Rechazado) en el sistema para autorizar el avance del flujo comercial. [coincide]
3. Almacenar los archivos de forma segura en la nube y clasificarlos automáticamente, asociando automáticamente cada documento al expediente lógico correspondiente de la propiedad o de la oportunidad comercial. [coincide]
4. Permitir la consulta, visualización y descarga segura de los expedientes mediante URLs firmadas temporalmente, restringidas según el rol del usuario (Administrador o Asesor). [coincide]
5. El sistema detecta la presencia y vigencia de los documentos requeridos para cada estado del proceso, emitiendo alertas operativas e impidiendo el avance de la oportunidad comercial cuando existan documentos críticos faltantes o vencidos. [coincide]

## T8. Gestión administrativa de cartera operativa

### AS-IS (estado actual manual)
No aparece una sección AS-IS literal separada en la fuente del borrador para T8; el documento presenta directamente la operación TO-BE. [no está en la tesis: la comprobación de la fuente no incluye un AS-IS separado para este proceso, por lo que este punto queda marcado como ausencia documental y no como un paso inventado]

### TO-BE (estado futuro con sistema)
1. El Administrador visualiza la cartera de propiedades y oportunidades comerciales activas. [coincide]
2. El sistema muestra la carga operativa de cada asesor (propiedades asignadas, oportunidades en curso y sus estados de seguimiento). [coincide]
3. El Administrador selecciona una propiedad u oportunidad comercial específica. [coincide]
4. El Administrador reasigna el responsable de la entidad seleccionada a otro asesor disponible. [coincide]
5. El sistema actualiza inmediatamente al responsable actual de la entidad. [coincide]
6. El sistema registra automáticamente el evento de reasignación en el historial de trazabilidad para auditoría, almacenando el asesor anterior, el nuevo asesor y la fecha del cambio. [coincide]
7. El sistema notifica de forma automática al asesor anterior y al nuevo responsable sobre la reasignación realizada. [coincide]
8. Consultar las métricas de conversión por inmueble (contactos generados, visitas realizadas y oportunidades por resultado) para respaldar la estrategia comercial y retroalimentar al propietario con datos objetivos. [coincide]

## Marcas por proceso

- T1: los pasos se mantienen con el flujo de captación y publicación; no hay desviación funcional evidente. [coincide]
- T2: los pasos del borrador mantienen la idea de marketing y canal de interesados, pero el eje del canal principal se desplaza hacia el portal web y la ficha digital. [difiere: la tesis oficial se centra en el catálogo web como puerta de entrada y la oportunidad comercial registrada dentro del sistema]
- T3: la automatización del contacto y la agendamiento coincide con la tesis y la lógica de trazabilidad. [coincide]
- T4: se mantiene el flujo de venta y cierre; la auditoría de la reserva y la reversión son consistentes con la tesis. [coincide]
- T5: el arriendo queda como un proceso core del sistema, con continuidad del flujo comercial, reserva y cierre; la tesis mantiene la misma lógica. [coincide]
- T6: el proceso incluye indicadores del sector, borrador con IA y guardado inmutable; todo ello coincide con la tesis y con la intención del diseño del sistema. [coincide]
- T7: la gestión documental centralizada con validación de autenticidad y vigencia, Aprobado/Rechazado y URLs firmadas coincide con la tesis. [coincide]
- T8: la administración y trazabilidad de cartera coincide con la tesis; la reasignación de responsable y el historial de cambios son puntos clave. [coincide]

## Lista de diferencias para que Pablo y Sebas decidan

1. El borrador enfatiza Facebook y Marketplace como canales de captación y difusión. La tesis oficial prioriza el portal web y la ficha digital como canal central. [difiere]
2. El borrador incluye varios pasos de comercio social y canales alternativos; la tesis oficial los integra como canales de origen de la oportunidad comercial y no como eje predominante. [difiere]
3. En T5, el borrador y la tesis coinciden en la lógica de arriendo, reserva y cierre, pero la sección de comisión y la ejecución del cierre operativo deben confirmarse en la especificación final. [difiere: no es una contradicción funcional, sino un detalle de cierre operativo por confirmar]
4. En T6, la fuente incorpora explícitamente indicadores del sector, un borrador de justificación con IA y el almacenamiento inmutable del cálculo. La tesis mantiene el mismo enfoque, pero el grado de obligatoriedad de cada pieza debe confirmarse en la definición final del proceso. [difiere: misma intención funcional, detalle de configuración por confirmar]
5. En T7, la tesis refuerza la validación de autenticidad y vigencia con “Aprobado/Rechazado” y la restricción por URL firmada. El borrador incluye el mismo flujo, pero con menor detalle operativo. [difiere: detalle operativo que la tesis precisa con más rigor]
6. En T8, la reasignación, el historial y la trazabilidad coinciden con la tesis; la diferencia está en el nivel de detalle de la métrica de conversión y la visibilidad de la cartera para cada asesor. [difiere: detalle de operación y métricas, no una contradicción funcional]
7. La regla “si difiere, manda la tesis” se aplica explícitamente en todos los puntos anteriores: la tesis sigue siendo la autoridad de decisión final. [coincide]

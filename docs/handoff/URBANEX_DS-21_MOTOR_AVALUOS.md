# Urbanex — DS-21: propuesta del motor de avalúos (plan B de D-04)

| Campo | Valor |
|---|---|
| Estado | **APROBADA POR PABLO el 2026-10-28, con carácter provisional.** C-02 (opción A) queda provisional hasta que lo confirme el tutor, porque contradice RF-11. θ v1 queda EN OBSERVACIÓN. Pablo confirmará F4 y F5 contra los originales. Las decisiones y los ajustes están en la §10 |
| Fecha | 2026-10-28 (propuesta y aprobación) |
| Origen | D-04: el plazo de la fórmula del motor (2026-10-28, 08:00) venció sin respuesta. Pablo activó el plan B de `Project_Progress.md` |
| Arquitectura | Decidida por Pablo: y = f(x; θ) en tres capas (estructura, factores, parámetros) |
| Historias | HU-04 (comparables), HU-05 (características), HU-06 (valor sugerido determinista), HU-08 (calibración e historial inmutable); RF-11 |
| Decisiones relacionadas | D-04 (esta propuesta la resolvería), C-02, N-02, N-03, N-05; DS-02 (registro manual), DS-06 (reevaluación); DT-19 (faltan campos), DT-73 (valores no plausibles) |

> **Cómo leer las fuentes.** Cada afirmación normativa lleva su fuente en la §2. Lo que no se pudo verificar en una fuente primaria aparece como **POR CONFIRMAR**. Los valores de θ sin fuente aparecen como **diseño propio, EN OBSERVACIÓN**: son provisionales y se cambian desde la configuración, sin tocar el código.

---

## 1. Resumen

El motor estima el **valor comercial** de una propiedad en captación con el **método comparativo de mercado**:

1. Toma entre 3 y 5 comparables del mismo tipo y la misma zona (HU-04).
2. Convierte el precio de cada uno a precio por m².
3. Homogeniza cada comparable con factores de ajuste.
4. Descarta los atípicos.
5. Combina los comparables con pesos y multiplica por la superficie del sujeto.
6. Mide la confianza por la cantidad de comparables y su dispersión.

El cálculo es **determinista** (HU-06). Cada avalúo guarda los comparables, los factores y la **versión de θ** que usó (HU-08).

Lo que esta propuesta **no** hace:
- no usa el avalúo catastral municipal como valor comercial;
- no inventa factores para campos que la propiedad no tiene (DT-19);
- no resuelve C-02 ni N-03: ofrece opciones con una recomendación.

**Límite importante con los datos de hoy.** `Property` solo tiene tipo, precio, superficie, dormitorios, baños, parqueaderos, ubicación en texto y coordenadas (DT-19). Por eso el único factor con datos reales es la **superficie**. Hasta que existan `zone`, `age_years` y `conservation_state`, el resultado será, en la práctica, un precio por m² homogenizado por tamaño.

## 2. Fuentes consultadas (2026-10-28)

| # | Fuente | Qué se usa | Verificación |
|---|---|---|---|
| F1 | **COOTAD** (Código Orgánico de Organización Territorial, Autonomía y Descentralización), R.O. Suplemento 303, 19-10-2010. **Art. 495**, "Avalúo de los predios", reformado por el art. 18 de la Ley s/n, R.O. 966-2S, 20-03-2017. **Art. 496**, actualización bienal. Texto consultado en la compilación de Andersen Ecuador (jun. 2018): <https://ec.andersen.com/wp-content/uploads/2017/03/Legislacio%CC%81n-Ecuador-16-Co%CC%81digo-Orga%CC%81nico-Territorial-junio-2018.pdf> | Art. 495 a): el valor del suelo es "el precio unitario de suelo […] determinado por un proceso de comparación con precios unitarios de venta de inmuebles de condiciones similares u homogéneas del mismo sector, multiplicado por la superficie del inmueble". Art. 495 b) y c): edificaciones por el **método de reposición**, "depreciada de forma proporcional al tiempo de vida útil". Las municipalidades fijan los parámetros "mediante ordenanza" | **Verificado** (texto literal en la compilación de 2018). El primer inciso coincide con su transcripción en la ordenanza de Baños de Agua Santa de 2025 (F6). Reformas posteriores a 2018: **POR CONFIRMAR** contra el texto oficial vigente |
| F2 | **Superintendencia de Bancos**, Codificación de Normas, Libro I, Título XVII, **Capítulo IV**, "Norma de control para la calificación y registro de los peritos valuadores de las entidades de los sectores financieros público y privado", **Resolución SB-2020-0573, 15-06-2020**: <https://www.superbancos.gob.ec/bancos/wp-content/uploads/downloads/2020/07/L1_XVII_cap_IV.pdf> | **Anexo 1, num. 2.2.4:** "Se deberán identificar un mínimo de tres bienes que hayan sido vendidos u ofertados recientemente y que sean iguales o similares al predio valuado […] así como efectuar la homologación y ajustes correspondientes." **Num. 1.2.8:** fotografías de los comparables "para el método comparativo de mercado". **Num. 2.3.9:** los tres enfoques (sustitución, previsión de beneficios, equilibrio) | **Verificado** en el PDF de 2020. Rige para peritos de entidades financieras: para Urbanex es **referencia de buena práctica**, no una obligación. Reformas posteriores: **POR CONFIRMAR** |
| F3 | **Código Municipal para el Distrito Metropolitano de Quito, Libro III.5** (valoración inmobiliaria), versión publicada en gob.ec (jun. 2019): <https://www.gob.ec/sites/default/files/regulations/2019-06/Codigo_Municipal%20Libro%20III.5.pdf> | **Art. III.5.10:** valor por **zonas homogéneas** (AIVAU) aplicado a un **lote tipo**. **Arts. III.5.14–15:** factores de frente, fondo y tamaño, `Fcsu = Ff × Fp × Fta`, con un total "no […] menor a 0,85 ni mayor a 1,20". **Art. III.5.26:** construcción por costo de reposición. **Art. III.5.29:** depreciación por edad, vida útil y **estado de conservación**. **Art. III.5.31:** `Vd = Vn (R + (1 − R)(1 − D))` | **Verificado** en la versión de 2019. Si sigue vigente o la reemplazó la ordenanza de F4: **POR CONFIRMAR**. Los valores de sus Tablas 3, 5, 6 y 7 **no se extrajeron** |
| F4 | **Ordenanza Metropolitana No. 108-2025** (Quito), valoración del suelo urbano del DMQ, **bienio 2026-2027**: <https://www7.quito.gob.ec/mdmq_ordenanzas/Administraci%C3%B3n%202023-2027/Ordenanzas/2025/ORD-108-2025-MET%20-%20VALORACI%C3%93N.pdf> | Plano y listado del valor del suelo urbano 2026-2027 (anexos 1 y 2, según el extracto del buscador) | **Existencia verificada** por el título y el extracto del buscador. **Contenido POR CONFIRMAR:** el servidor del Municipio respondió 403 a la descarga automática. Pablo puede abrirla en el navegador |
| F5 | **Norma Técnica de Valoración para los bienes inmuebles urbanos, rurales y edificaciones del DMQ**, Dirección Metropolitana de Catastro, **diciembre de 2025** ("codificada"). Copia de terceros en Scribd: <https://es.scribd.com/document/989854798/Norma-Tecnica-Valoracion-Dmq-2026-Codificada> | **Al menos tres datos válidos.** "El valor comercial del bien es el promedio de los valores homogeneizados, siempre que el **coeficiente de variación** sea igual o inferior […] **15 %**." Se excluyen los datos "sub valorados y sobre valorados". **Factor tamaño:** `Fta = 0,25·St/S + 0,75` (mín. 0,75, máx. 1,20; lotes ≤ 15.000 m²), con `FTAM = 1/Fta`. También frente `[Ft/Fm]^0,25` (0,84–1,19), fondo `[Fom/Fot]^0,5` (0,80–1,20), localización en la manzana y acceso (tablas) | **Fuente secundaria: POR CONFIRMAR contra el original** (copia subida por un tercero, no por el Municipio). No se identificó la resolución que la aprueba; un candidato es la Resolución GADDMQ-SHOT-DMC-2025-0419-R (el enlace del Municipio respondió 403): **POR CONFIRMAR** |
| F6 | Ordenanza de valoración de los predios urbanos y rurales de **Baños de Agua Santa**, bienio 2026-2027: <https://www.municipiobanos.gob.ec/wp-content/uploads/2025/12/11.-LA-ORDENANZA-DE-VALORACION-DE-LOS-PREDIOS-URBANOS-Y-RURALES.pdf> | Transcribe el COOTAD art. 495. Usa factores de depreciación "remitidos por la AME" y coeficientes de conservación (estable / a reparar / total deterioro) | **Verificado.** **No es de Quito:** solo muestra que la práctica municipal ecuatoriana sigue el mismo esquema |

**Lo que no se encontró o no se pudo verificar (POR CONFIRMAR):**
- un descuento de negociación oficial entre precio de oferta y precio de cierre;
- una antigüedad máxima del dato comparable en días. F2 dice solo "recientemente";
- ajustes por dormitorio, baño o parqueadero;
- una regla numérica para descartar atípicos. F5 dice que se excluyen, pero no cómo.

**Advertencia de alcance.** El COOTAD, el Código Municipal y la Norma Técnica regulan el **avalúo catastral**, que sirve de base para los impuestos (F1: "valor intrínseco, propio o natural del inmueble"). Urbanex necesita el **valor comercial**. Del marco catastral se toma el **método** (comparación, homogeneización, zonas homogéneas, depreciación); sus **valores**, como el plano del suelo o las tarifas, no se trasladan. F2 sí trata del valor comercial pericial y fija el mínimo de tres comparables.

## 3. Capa 1 — Estructura (la decide el equipo; fija en el código)

### 3.1 Notación

| Símbolo | Significado | Campo |
|---|---|---|
| s | Propiedad sujeto (la que se avalúa) | `Property` |
| i = 1…n | Comparables confirmados por el asesor en I-11 (3 ≤ n ≤ 5) | `Property` |
| Pᵢ, Sᵢ | Precio y superficie del comparable | `price` (Decimal), `area_m2` (Float → Decimal por `str`) |
| S_s | Superficie del sujeto | `area_m2` |
| qᵢ = Pᵢ / Sᵢ | Precio unitario (USD/m²) | calculado |
| f_k(s, i; θ) | Factor de ajuste k (capa 2) | calculado |
| θ | Parámetros versionados (capa 3) | `EngineParameters` (nuevo) |

### 3.2 Pasos

1. **Datos mínimos del sujeto (HU-05).** El sujeto necesita `property_type`, `area_m2 > 0` y una zona (§7). Si falta alguno, no hay cálculo: el avalúo se registra en manual (DS-02).
2. **Candidatos (HU-04).** Entran las propiedades del **mismo tipo** (RF-11: "jamás se mezclan tipos") y de la **misma zona**, con un estado de `θ.estados_comparables`, un dato no más antiguo que `θ.antiguedad_max_dias`, `price > 0` y `area_m2 > 0`. El sujeto queda fuera.
   - Se ordenan de forma determinista: primero por |ln(Sᵢ / S_s)| (el tamaño más parecido), luego por distancia si hay coordenadas y, al final, por `id`.
   - El sistema **sugiere** los 5 primeros. **El asesor confirma entre 3 y 5** en I-11 (contexto maestro, I-11).
3. **Mínimo y máximo.** Con n < 3 se aplica C-02 (§6). Con n > 5, la selección se rechaza (HU-04, F2, F5).
4. **Homogeneización.** Fᵢ = acotar( ∏ₖ f_k(s, i; θ), `θ.factor_total_min`, `θ.factor_total_max` ) y q*ᵢ = qᵢ · Fᵢ.
5. **Atípicos (F5).** Solo si n ≥ 4. Sea m̃ la mediana de q*. Se descarta, empezando por el más alejado, cada q*ᵢ con |q*ᵢ − m̃| / m̃ > `θ.desvio_max`. **Nunca se baja de 3** comparables.
6. **Combinación con pesos.**
   - Ajuste bruto: ABᵢ = Σₖ |f_k − 1|.
   - Peso: wᵢ = 1 / (1 + `θ.alfa` · ABᵢ).
   - Precio combinado: q̄ = Σ wᵢ q*ᵢ / Σ wᵢ.

   El comparable que necesita menos ajuste pesa más. **Con `θ.alfa = 0` queda el promedio simple de F5.**
7. **Valor sugerido.** V = redondear( q̄ · S_s , 2 ). **Se guarda exacto** en `suggested_value`, y la diferencia de HU-08 se calcula contra ese valor exacto. **La interfaz lo muestra redondeado a cientos de dólares** (`ROUND_HALF_UP`; p. ej. 143.861,35 → "≈ USD 143.900"), sin cambiar lo guardado (ajuste de Pablo, 2026-10-28).
8. **Confianza (RF-11, F5).** Se mide con el coeficiente de variación muestral de los q*ᵢ conservados: CV = desviación estándar / media.
   - **ALTO:** n ≥ 3 y CV ≤ `θ.cv_max`.
   - **MEDIO:** n ≥ 3 y CV > `θ.cv_max` (RF-11: "alta dispersión").
   - **BAJO:** sin cálculo, registro manual (DS-02, RNF-07). Para n = 1–2, ver C-02.
9. **Registro (HU-06, HU-08).** Al **crear** el avalúo, nunca después (GPS, precaución de HU-08), se escriben:
   - `suggested_value = V`, `confidence_level` e `is_manual_fallback = False`;
   - `comparables_snapshot`, con el id, el estado, P, S, q, cada f_k con su explicación, F, q*, w y si se descartó, y además m̃, q̄ y CV;
   - la **versión de θ** usada (campo nuevo, §5.2).

### 3.3 Determinismo (HU-06)

- Todo con `Decimal`. `area_m2` es `Float`: se convierte con `Decimal(str(valor))`, nunca con `Decimal(float)`.
- Redondeo `ROUND_HALF_UP` en puntos fijos: factores a 6 decimales, montos y q a 2, CV a 4.
- Orden determinista de los comparables, sin aleatoriedad y sin depender de la hora: la antigüedad del dato se mide contra la fecha de creación del avalúo.
- **Criterio de prueba:** con el mismo `comparables_snapshot` y la misma versión de θ, el resultado es idéntico. El ejemplo de la §8 sirve como prueba automática.

## 4. Capa 2 — Factores de ajuste (los define el equipo; piezas intercambiables)

Cada factor es una clase registrada por **nombre y versión** (p. ej. `superficie@1`) en un registro. La configuración θ lista los factores activos y sus parámetros. Cada factor declara:
- los campos que necesita;
- `aplica(s, i)`: si falta un dato, el factor no se aplica y lo deja escrito;
- `calcular(s, i, params)`, que devuelve el valor y una explicación legible para el snapshot y para el borrador de HU-07.

**Cambiar una fórmula = registrar una versión nueva** del factor. Así, los avalúos antiguos se pueden recalcular igual.

**Factores por tipo de propiedad (ajuste de Pablo, 2026-10-28).** θ define qué factores se aplican, y con qué parámetros, **para cada tipo** (`casa`, `departamento`, `local`, `terreno`), con una entrada `default` para los tipos no listados. Así se puede **desactivar** un factor en un tipo (quitándolo de su lista) o **suavizarlo** con sus parámetros, sin cambiar código. Para eso, `superficie@1` tiene un parámetro de **intensidad** γ ∈ [0, 1]: f = (1 / Ftaᵢ)^γ. Con γ = 1 es el factor de F5; con γ = 0 es neutro (f = 1). En θ v1, γ = 1 en todos los tipos.

| Factor | Campos | Fórmula propuesta | Referencia | Estado |
|---|---|---|---|---|
| `superficie@1` | `area_m2` | Ftaᵢ = acotar(a · S_s/Sᵢ + b, mín, máx); f = 1 / Ftaᵢ. El sujeto hace de "lote tipo": un comparable más grande que el sujeto tiene un precio por m² menor por escala, y el factor lo sube | F5 (factor tamaño y FTAM = 1/Fta); F3 art. III.5.14 c) | **Activo.** F5 lo define para **lotes de terreno**; aplicarlo a casas y departamentos es una **adaptación propia, EN OBSERVACIÓN**. F5: POR CONFIRMAR contra el original |
| `negociacion@1` | `status` | f = `θ.factor_oferta` si el comparable es una **oferta** (`disponible`, `reservador`) y 1 si es una transacción (`vendido`) | F2 num. 2.2.4 ("vendidos u ofertados"); F5 distingue transacción directa (vendido) e indirecta (oferta) | **Activo con valor neutro 1,00** hasta tener una fuente del descuento de negociación (POR CONFIRMAR) |
| `depreciacion@1` | `age_years`, `conservation_state` (**no existen**, DT-19) | Con dᵢ = R + (1 − R)(1 − Dᵢ): f = (1 − φ) + φ · d_s / dᵢ, donde φ es la fracción del valor que corresponde a la construcción | F3 art. III.5.31 (Vd = Vn(R + (1 − R)(1 − D))); F1 art. 495 c); F5 tablas 28, 30 y 31 | **Definido, inactivo** hasta DT-19. Tablas de R, vida útil y D: **POR CONFIRMAR** (no extraídas). φ: **POR CONFIRMAR** |
| `frente@1`, `fondo@1`, `forma@1`, `localizacion_manzana@1`, `acceso@1` | frente, fondo, perímetro, posición en la manzana, tipo de vía (**no existen**) | Fórmulas y tablas de F5 | F5; F3 arts. III.5.14–15 | **Futuro**, solo para `terreno`. Requiere campos nuevos |
| Ubicación | `zone` o coordenadas | No es un factor: es el **filtro** de la misma zona. Dentro de una zona homogénea no se ajusta | F3 art. III.5.10 (AIVAU, zonas homogéneas); F1 art. 495 a) ("del mismo sector") | Ver §7 |
| Dormitorios, baños, parqueaderos | existen | Ajuste por unidad | **Sin fuente verificada** | **No propuesto** (POR CONFIRMAR). La superficie ya recoge buena parte de esa diferencia |

## 5. Capa 3 — Parámetros θ (EN OBSERVACIÓN)

### 5.1 θ inicial (versión 1)

| Parámetro | Valor | Fuente | Estado |
|---|---|---|---|
| `factores_por_tipo` | `default`: `superficie@1` y `negociacion@1` (los mismos para `casa`, `departamento`, `local` y `terreno` en v1) | §4 | EN OBSERVACIÓN |
| `superficie.intensidad` (γ) | 1 en todos los tipos | Ajuste de Pablo; con γ = 1 se aplica F5 tal cual | EN OBSERVACIÓN (pregunta para el tutor: ¿suavizar en viviendas?) |
| `superficie.a`, `superficie.b` | 0,25 y 0,75 | F5 | POR CONFIRMAR (F5 secundaria) |
| `superficie.min`, `superficie.max` | 0,75 y 1,20 | F5 | POR CONFIRMAR (F5 secundaria) |
| `factor_oferta` | 1,00 (neutro) | Sin fuente | EN OBSERVACIÓN: **pendiente de una fuente** |
| `factor_total_min`, `factor_total_max` | 0,85 y 1,20 | F3 art. III.5.15 (límite del factor total del suelo), **por analogía** | EN OBSERVACIÓN |
| `desvio_max` (atípicos) | 0,30 (30 % sobre la mediana) | Diseño propio; F5 pide excluir atípicos sin fijar la regla | EN OBSERVACIÓN |
| `alfa` (peso por ajuste bruto) | 5 | Diseño propio; con 0 se obtiene el promedio de F5 | EN OBSERVACIÓN |
| `cv_max` (ALTO frente a MEDIO) | 0,15 | F5 ("coeficiente de variación […] 15 %") | POR CONFIRMAR (F5 secundaria) |
| `estados_comparables` | `disponible`, `reservador`, `vendido` | N-02 (pregunta de negocio). Quedan fuera `captacion` (sin requisitos de HU-53), `no_disponible` y `arrendado` (su precio podría ser un canon de arriendo: falta `operation_type`, DT-19) | **POR CONFIRMAR (N-02)** |
| `antiguedad_max_dias` | 365 | Diseño propio; F2 solo dice "recientemente" | POR CONFIRMAR (N-02) |
| `radio_km_sin_zona` | 1,5 | Diseño propio, mientras no exista `zone` (§7) | EN OBSERVACIÓN |

El mínimo de 3 y el máximo de 5 comparables **no son θ**: vienen de HU-04, F2 y F5 y quedan en la capa 1.

### 5.2 Cómo se guarda θ (HU-08)

- **Modelo nuevo `EngineParameters`** en `apps.appraisals` (en inglés, como los demás modelos; antes se llamaba `ParametrosMotor` en esta propuesta), que no es una app compartida: `version` (consecutivo), `parametros` (JSON validado contra un esquema), `fuentes` (JSON: cada valor con su fuente y estado), `nota`, `creado_por`, `creado_en` y `activo`.
  - Una versión es **inmutable**, con el mismo patrón que `Document` y `Appraisal`.
  - Editar θ crea **otra versión**. Solo hay una activa.
- Solo un **admin** crea y activa versiones. La validación rechaza un factor que no esté registrado o un parámetro fuera de rango.
- **`Appraisal` suma un campo:** la FK a la versión de θ, nula en los avalúos manuales. Es una migración en `apps.appraisals` (amplía DS-03). La versión también queda copiada en `comparables_snapshot`, para que la auditoría (A-05 / HU-50) no dependa de la FK.

## 6. Impacto de C-02 (1–2 comparables)

Las fuentes se contradicen:
- RF-11 (contexto maestro) dice "Medio: pocos comparables (1–2) o alta dispersión".
- HU-04 dice que no se calcula con menos de 3 y que, sin comparables suficientes, el avalúo es manual.
- F2 (num. 2.2.4) y F5 exigen un **mínimo de tres** comparables.

| Opción | Qué pasa con 1–2 comparables | A favor | En contra |
|---|---|---|---|
| **A (recomendada)** | Sin valor sugerido: registro manual con confianza BAJO (DS-02). El snapshot guarda los 1–2 encontrados **como referencia** para el asesor. MEDIO queda solo para la dispersión alta | Coincide con HU-04, F2 y F5. Sin un número calculado con poca base, DT-73 no se agrava | Contradice la letra de RF-11. Hay que corregir RF-11 en el contexto maestro |
| B | Se calcula con 1–2 y confianza MEDIO | Literal de RF-11. El asesor siempre recibe un número | Contradice HU-04 y las dos normas. Con 1 comparable el CV no existe y la confianza no se puede medir |

**Decisión de Pablo (y del tutor).** Con la opción A, la base de desarrollo da **manual** en casi todos los casos hasta que existan los comparables sintéticos que pide el contexto maestro ("0, 1–2 y 3+ comparables, dispersión y tipo de inmueble").

## 7. Impacto de la falta del campo `zone` (N-03, DT-19)

El método exige comparables "del mismo sector" (F1, art. 495 a)) y la valoración de Quito se organiza por **zonas homogéneas** (F3, art. III.5.10). Hoy `Property` no tiene `zone`. En la auditoría del 2026-10-22, las 28 propiedades de desarrollo de entonces no tenían coordenadas (GPS §2); las 4 del seeder sí las tienen.

| Opción | Cómo se define "misma zona" | A favor | En contra |
|---|---|---|---|
| 1 (**recomendada como destino**) | Campo `zone` con una **lista controlada** de sectores, alineada en lo posible con las zonas homogéneas del DMQ | Es la regla de F1 y F3, y el asesor la entiende | Requiere una migración en `users/models.py` (archivo **compartido**, GPS §3: coordinar con Sebas) y decidir la lista (N-03) |
| 2 (**provisional**) | Distancia ≤ `θ.radio_km_sin_zona` entre coordenadas | No requiere migración | La cercanía no garantiza un mercado homogéneo (Cumbayá y Tumbaco están cerca y tienen precios distintos). Necesita coordenadas en el sujeto y en los comparables; sin ellas, el resultado es manual |
| 3 | Coincidencia de texto en `location` | Sin migración | Texto libre ("Cumbayá, Quito" frente a "Quito, Cumbaya, San pedro"): **no recomendada** |

**Diseño:** el motor pregunta por la zona a una sola función, `misma_zona(s, i, θ)`. Pasar de la opción 2 a la 1 cambia esa función, no el resto.

## 8. Ejemplo resuelto

**Datos hipotéticos** (no son de la BD). Sujeto: departamento de **95 m²** en La Carolina. El asesor confirma 5 comparables del mismo tipo y zona. θ es la versión 1 de la §5.1.

| Comp. | Estado | P (USD) | S (m²) | q = P/S | Fta = 0,25·95/S + 0,75 | f_sup = 1/Fta | f_neg | F | q* = q·F | AB | w = 1/(1+5·AB) |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| C1 | disponible | 150.000 | 100 | 1.500,00 | 0,987500 | 1,012658 | 1,00 | 1,012658 | 1.518,99 | 0,012658 | 0,940477 |
| C2 | disponible | 128.000 | 80 | 1.600,00 | 1,046875 | 0,955224 | 1,00 | 0,955224 | 1.528,36 | 0,044776 | 0,817074 |
| C3 | vendido | 168.000 | 120 | 1.400,00 | 0,947917 | 1,054945 | 1 | 1,054945 | 1.476,92 | 0,054945 | 0,784483 |
| C4 | vendido | 139.500 | 90 | 1.550,00 | 1,013889 | 0,986301 | 1 | 0,986301 | 1.528,77 | 0,013699 | 0,935896 |
| C5 | disponible | 92.000 | 90 | 1.022,22 | 1,013889 | 0,986301 | 1,00 | 0,986301 | 1.008,22 | — | — |

1. **Atípicos** (n = 5 ≥ 4). La mediana de q* es 1.518,99. C5 se aleja |1.008,22 − 1.518,99| / 1.518,99 = **33,6 % > 30 %**: **se descarta**. Los demás se alejan 2,8 % o menos. Quedan 4.
2. **Combinación.** Σw = 3,477930 y q̄ = Σ wᵢ q*ᵢ / Σ wᵢ = **1.514,33 USD/m²**. El promedio simple sería 1.513,26.
3. **Valor sugerido.** V = 1.514,33 × 95 = **USD 143.861,35**.
4. **Confianza.** n = 4. Media de q* = 1.513,26 y desviación estándar muestral = 24,64, así que **CV = 1,63 % ≤ 15 % → ALTO**.

**Variante de dispersión.** Supongamos que solo hay C1, C2 y un C3 de USD 120.000 por 120 m² (q* = 1.054,95). Con n = 3 no se descartan atípicos, porque nunca se baja de 3. La media es 1.367,43, la desviación estándar 270,66 y **CV = 19,79 % > 15 % → MEDIO**.

**Variante C-02.** Si solo hay 2 comparables: con la **opción A**, no hay valor sugerido. El avalúo es manual (BAJO) y los 2 comparables quedan en el snapshot como referencia.

**Calibración (HU-08).** Si el asesor aprueba USD 148.000, se guarda una diferencia de USD 4.138,65 (+2,88 %) contra el valor del motor. Esa diferencia es la que A-05 audita y la base para tratar DT-73 con un umbral (fuera de esta propuesta).

## 9. Lo que habría que construir (después de la aprobación)

En fases con pruebas, cada una con su commit, en la rama `feat/URB-10-11-motor-avaluos` (desde `develop`). **Orden ajustado por Pablo (2026-10-28): los comparables sintéticos van antes de I-11**, porque sin ellos el motor siempre cae en manual y no hay nada que demostrar.
1. **Núcleo puro:** el registro de factores, `superficie@1` y `negociacion@1`, el cálculo de la capa 1 como funciones sin acceso a la BD, y pruebas de determinismo, límites, atípicos, CV, factores por tipo y el ejemplo de la §8.
2. `EngineParameters` (inmutable, versionado) con θ v1, la FK en `Appraisal` y la migración en `apps.appraisals`. Admin para crear y activar versiones.
3. **Comparables sintéticos** para desarrollo: un comando aparte, solo con `DEBUG=True`, que los crea en estado **`vendido`** (no es un estado público). Cubren los casos de 0, 1–2 y 3+ comparables y de dispersión alta (contexto maestro). Es una excepción acotada a DS-17 (ver DS-23).
4. **HU-04 y HU-06 en el backend:** endpoint de candidatos, y `Appraisal.create_draft()` usa el motor si hay entre 3 y 5 comparables confirmados; si no, queda en manual (DS-02).
5. **Pantalla I-11** (ruta nueva, sin tocar `dashboard/page.tsx`) y el resultado del motor en I-12, redondeado a cientos. Después, una ronda de validación visual.

`users/models.py` (`zone` y los campos de DT-19) **no se toca** en estas fases sin acordarlo con Sebas (GPS §3).

## 10. Decisiones de Pablo (2026-10-28)

| # | Pregunta | Decisión |
|---|---|---|
| 1 | ¿Se aprueban la estructura de la §3 y el registro de factores de la §4? | **Aprobadas** |
| 2 | C-02: ¿opción A o B? | **A** (con 1–2 comparables, avalúo manual). **Provisional** hasta que lo confirme el tutor, porque contradice RF-11 |
| 3 | `zone`: ¿opción 1 como destino y 2 como provisional? | **Sí.** La lista de zonas queda en N-03 |
| 4 | ¿`estados_comparables` = disponible, reservador y vendido? | **Aprobado** (N-02) |
| 5 | ¿Se acepta θ v1 de la §5.1 como provisional? | **Aprobado, EN OBSERVACIÓN** |
| 6 | ¿Quién confirma F4 y F5 contra los originales? | **Pablo**, desde el navegador |

**Ajustes pedidos por Pablo e incorporados:**
- factores por tipo de propiedad, con la intensidad γ de `superficie@1` (§4 y §5.1);
- comparables sintéticos antes de I-11 (§9);
- valor exacto guardado y mostrado redondeado a cientos (§3.2, paso 7).

**Efecto:** **D-04 queda resuelta provisionalmente con DS-21.** DS-02 (registro manual) sigue vigente para los casos sin comparables suficientes. HU-08 completa sigue **POR CONFIRMAR** hasta que el motor esté implementado y validado.

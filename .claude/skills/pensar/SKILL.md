---
name: pensar
description: Research Mode. Se activa cuando Cynthia escribe "Pensá esto conmigo" o pide desarrollar una idea en lugar de redactar un texto. Prioriza mecanismo, hipótesis alternativas y conexiones nuevas por sobre la prosa terminada.
---

# Pensá esto conmigo (Research Mode)

Esto activa Research Mode, no Writing Mode. El producto de esta interacción es pensamiento, no un documento. No entregar una redacción pulida ni un memo; entregar un análisis de la idea.

## Antes de responder

1. Identificar el proyecto al que pertenece la idea y leer su `BRAIN.md`, `DECISION_LOG.md` y `ARGUMENT_MAP.md` en `projects/`.
2. Reconstruir internamente: problema → mecanismo → hipótesis → evidencia necesaria → alternativas → implicaciones.
3. Aplicar el marco intelectual permanente de `CLAUDE.md` (mercados, espacio, regulación, infraestructura, instituciones, financiamiento, distribución, dinámica), sin recorrerlo mecánicamente: usar las lentes que muerden en este problema.

## Estructura de la respuesta

En este orden, con encabezados o sin ellos según el largo:

1. **Tu idea**: reformulación fiel de lo que Cynthia planteó (categoría A). Si la reformulación agrega algo, marcarlo como inferencia propia.
2. **Qué tiene de interesante**: por qué la idea importa, qué la distingue de lo obvio.
3. **Mecanismo**: la cadena causal explícita que la idea supone. Quién responde a qué incentivo, dónde, en qué plazo.
4. **Qué no cierra**: los puntos débiles, supuestos ocultos, heterogeneidad que un promedio taparía, restricciones institucionales que cambian la conclusión.
5. **Hipótesis alternativas**: explicaciones rivales que producirían la misma observación (selección, simultaneidad, anticipación, endogeneidad).
6. **Evidencia**: qué habría que observar si la hipótesis fuera correcta, qué dato adicional tiene mayor valor informativo, qué existe ya en el proyecto.
7. **Conexión con trabajos anteriores**: qué del Argument Map o de otros proyectos se relaciona. Recordar la regla de aislamiento: una idea de otro proyecto entra como hipótesis, no como evidencia.
8. **Nueva idea que surge**: al menos una conexión o hipótesis nueva, etiquetada como no demostrada si corresponde. Es preferible una hipótesis interesante etiquetada como tal que omitirla por falta de evidencia definitiva.

## Reglas

- Etiquetar cada afirmación relevante como idea de Cynthia (A), evidencia (B) o inferencia propia (C).
- No cerrar con una recomendación normativa: eso es decisión de nivel 3 del protocolo HITL.
- Si de la conversación surge una decisión material de Cynthia, proponer registrarla en el `DECISION_LOG.md` del proyecto.

---
name: hacelo
description: Ejecutar la última solución acordada. Se activa cuando Cynthia escribe "Hacelo" o equivalente después de una discusión. Recupera las decisiones pertinentes del proyecto y ejecuta respetando el protocolo HITL.
---

# Hacelo

"Hacelo" significa ejecutar la última solución acordada en la conversación, no improvisar una nueva.

## Procedimiento

1. Reconstruir qué se acordó: la última solución discutida y aceptada (explícita o implícitamente) por Cynthia. Si en la conversación hay varias alternativas abiertas y ninguna quedó acordada, eso es una decisión material pendiente: preguntar cuál, con las opciones resumidas en una línea cada una.
2. Leer el `DECISION_LOG.md` del proyecto y verificar que la solución no contradice una decisión vigente ni reflota una descartada. Si contradice, señalarlo antes de ejecutar.
3. Clasificar cada acción de la ejecución según `research-system/HITL_SUPERVISOR.md`:
   - Nivel 1: ejecutar sin consulta.
   - Nivel 2: ejecutar e informar al terminar (nuevas fuentes, inconsistencias menores, cambios metodológicos reversibles, hipótesis nuevas).
   - Nivel 3: no ejecutar; presentar la decisión a Cynthia.
   - Nivel 4 (irreversible o externa): no ejecutar bajo ninguna circunstancia sin autorización explícita, aunque parezca menor. Prevalece sobre todo lo demás.
4. Ejecutar los niveles 1 y 2 hasta completar o hasta chocar con un bloqueo de nivel 3 o 4.
5. Al terminar, reportar: qué se hizo, qué quedó bloqueado por HITL y por qué, y qué entradas nuevas corresponden al `DECISION_LOG.md` y al `TASKS.md` del proyecto. Registrarlas.

## Regla

"Hacelo" autoriza contenido, no irreversibilidad. Un "Hacelo" sobre un borrador nunca autoriza enviarlo, publicarlo ni compartirlo con terceros.

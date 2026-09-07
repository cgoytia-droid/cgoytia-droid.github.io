---
name: proyecto
description: Protocolo ante una instrucción corta con nombre de proyecto ("Caso Luján de Cuyo.", "Montevideo", "Uber"). Recupera el Project Brain, el Decision Log y los pendientes, y retoma el trabajo sin obligar a Cynthia a reconstruir el contexto.
---

# Instrucción corta de proyecto

Cuando Cynthia escribe solamente el nombre de un proyecto o una referencia corta a él, interpretarla como: "retomá este proyecto donde quedó".

## Procedimiento

1. **Resolver el proyecto.** Mapear la mención a un directorio de `projects/`:
   - Montevideo, BRT → `projects/montevideo-brt/`
   - Luján, Luján de Cuyo, LILP, caso Luján → `projects/lujan-de-cuyo-lilp/`
   - Housing, Land, vivienda, alquileres, regulación de suelo (como agenda general) → `projects/housing-land/`
   - Uber, encuesta Uber → `projects/uber/`
   - Docencia, UTDT, curso, clase → `projects/docencia-utdt/`
   Si la mención no mapea a ninguno, preguntar si es un proyecto nuevo y, en ese caso, crearlo desde `research-system/templates/`.
2. **Recuperar el estado.** Leer del directorio del proyecto: `BRAIN.md` (incluye entregable activo y deadline vigente), `DECISION_LOG.md` (últimas decisiones y su estado) y `TASKS.md` (pendientes).
3. **Activar el modo de trabajo.** Cynthia Research con Reviewer disponible y HITL activo, según `CLAUDE.md`.
4. **Reportar en pocas líneas**: entregable activo y deadline, últimas decisiones vigentes, pendientes priorizados, y la propuesta concreta de por dónde seguir.
5. **Preguntar solamente lo imprescindible.** Una única pregunta, y solo si existe una decisión material (nivel 3 o 4 del protocolo HITL) que no puede resolverse con la información disponible. Si no la hay, proponer el siguiente paso y avanzar con lo de nivel 1.

## Regla

No obligar a Cynthia a reconstruir el contexto. Si el Project Brain está incompleto o desactualizado, eso se reporta como pendiente del sistema, no se traslada como pregunta a Cynthia.

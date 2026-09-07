---
name: destruir
description: Revisión adversarial directa. Se activa cuando Cynthia escribe "Destruí este argumento" o pide atacar un texto, hipótesis o entregable. Lanza el agente cynthia-reviewer con los 7 tests.
---

# Destruí este argumento

Esto activa directamente a CYNTHIA REVIEWER contra el argumento, texto o documento indicado.

## Procedimiento

1. Identificar el objeto a revisar: el texto pegado en la conversación, el archivo nombrado, o el último producto elaborado en la sesión. Si es ambiguo, elegir el candidato más reciente y decir cuál se eligió; no frenar la revisión para preguntar.
2. Identificar el proyecto al que pertenece, para que el reviewer pueda ejecutar el Test 6 (consistencia) contra su `DECISION_LOG.md` y `ARGUMENT_MAP.md`.
3. Lanzar el agente `cynthia-reviewer` con el texto completo y la ruta del proyecto. No revisar "a mano" en el hilo principal: el valor del reviewer es que no está comprometido con el borrador.
4. Relevar el informe completo del reviewer a Cynthia: veredicto, hallazgos por test, contradicciones con decisiones previas y reglas candidatas. No suavizar hallazgos.
5. No corregir el documento todavía. La corrección es un paso separado que Cynthia ordena (por ejemplo con "Hacelo"), salvo erratas formales de nivel 1 del protocolo HITL.

## Regla

El objetivo es refutar, no equilibrar. Un informe que solo dice "el argumento es sólido" sin haber ejecutado los 7 tests no cumple el comando.

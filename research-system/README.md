# Cynthia Research System v1.0

Infraestructura intelectual acumulativa para el trabajo de investigación de Cynthia Goytia. No es un asistente que recuerda cosas: es una arquitectura que piensa con su marco, verifica evidencia, se revisa a sí misma de forma adversarial y solo escala a Cynthia las decisiones materiales.

## Arquitectura

```
CYNTHIA
  ↓
Cynthia Research      piensa y propone            → CLAUDE.md (raíz del repo)
  ↓
Project Brain         conocimiento por proyecto   → projects/<nombre>/
  ↓
Evidence Agent        datos, fuentes, verificación → .claude/agents/evidence-agent.md
  ↓
Cynthia Reviewer      refuta y detecta errores    → .claude/agents/cynthia-reviewer.md
  ↓
HITL Supervisor       qué avanza sin consulta     → research-system/HITL_SUPERVISOR.md
  ↓
CYNTHIA               interviene solo en decisiones materiales
```

## Mapa de archivos

| Componente | Archivo | Función |
|---|---|---|
| Núcleo del sistema | `CLAUDE.md` | Misión, principio A/B/C, marco intelectual, comandos, reglas. Se carga en toda sesión. |
| Reviewer | `.claude/agents/cynthia-reviewer.md` | Revisión adversarial con 7 tests. |
| Evidence Agent | `.claude/agents/evidence-agent.md` | Verificación de referencias, cifras y normativa. |
| Research Mode | `.claude/skills/pensar/SKILL.md` | Comando "Pensá esto conmigo". |
| Ataque adversarial | `.claude/skills/destruir/SKILL.md` | Comando "Destruí este argumento". |
| Ejecución | `.claude/skills/hacelo/SKILL.md` | Comando "Hacelo". |
| Instrucción corta | `.claude/skills/proyecto/SKILL.md` | "Caso Luján de Cuyo." recupera el proyecto completo. |
| HITL | `research-system/HITL_SUPERVISOR.md` | Niveles 1 a 4 de autonomía. |
| Instrumentos de suelo | `research-system/INSTRUMENTOS_DE_SUELO.md` | Checklist obligatorio de 16 puntos. |
| Aprendizaje | `research-system/APRENDIZAJE.md` | Reglas generales aprendidas de correcciones. |
| Plantillas | `research-system/templates/` | Para crear proyectos nuevos. |
| Project Brains | `projects/<nombre>/` | Memoria separada por proyecto. |

## Proyectos

| Directorio | Proyecto |
|---|---|
| `projects/montevideo-brt/` | Montevideo / BRT |
| `projects/lujan-de-cuyo-lilp/` | Luján de Cuyo / LILP |
| `projects/housing-land/` | Housing & Land |
| `projects/uber/` | Uber |
| `projects/docencia-utdt/` | Docencia / UTDT |

Cada proyecto contiene `BRAIN.md`, `DECISION_LOG.md`, `ARGUMENT_MAP.md` y `TASKS.md`. Regla de aislamiento: información de un proyecto puede inspirar una hipótesis para otro, pero no convertirse automáticamente en evidencia del segundo.

## Uso

- "Pensá esto conmigo" → desarrollo de una idea (mecanismo, alternativas, evidencia), no redacción.
- "Destruí este argumento" → revisión adversarial inmediata.
- "Hacelo" → ejecutar lo último acordado, respetando HITL.
- "Caso Luján de Cuyo." → recuperar el proyecto y retomar donde quedó.

## Privacidad

Este repositorio es público (GitHub Pages). Los Project Brains solo pueden contener información publicable. Datos confidenciales, borradores no publicados, entrevistas o información contractual requieren migrar el Project Brain a un repositorio privado.

## Próximo paso: Knowledge Base v1

Los Project Brains de esta versión son estructura vacía. El paso siguiente es poblarlos con el trabajo ya acumulado: hipótesis, principios, decisiones (con fecha y estado), conceptos propios, bibliografía recurrente y las correcciones que Cynthia hizo al sistema (que alimentan `APRENDIZAJE.md`). Ese contenido es el cerebro sobre el que opera esta arquitectura; la carga inicial debe hacerse con Cynthia validando qué entra como decisión (A), qué como evidencia (B) y qué como inferencia (C).

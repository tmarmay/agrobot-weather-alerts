# Agrobot - Sistema de Alertas Climáticas

API REST construida con FastAPI y PostgreSQL que evalúa periódicamente eventos climáticos y genera notificaciones cuando las condiciones superan los umbrales configurados por el usuario.

---

## Supuestos y aclaraciones

**Matching geográfico resuelto por la ingesta**
Se asume que el matching entre eventos meteorológicos y campos ya fue resuelto en la capa de ingesta. Los datos climáticos llegan asociados a un `field_id`, evitando modelar lógica geográfica fuera del alcance del challenge. Cada `Field` pertenece a un único `User`.

**Una entrada por combinación field + tipo + día**
En la realidad los pronósticos climáticos se actualizan continuamente (el 60% de lluvia de la mañana puede ser 80% a la tarde). Sin embargo, no se conoce si el job real de ingesta modela esto como UPDATEs sobre el registro existente o como nuevos snapshots. Se optó por asumir una única entrada por `(field_id, event_type, forecast_date)` — modelada con un `UniqueConstraint` — porque simplifica el sistema y es coherente con el alcance del challenge.

---

---

## Optimizaciones

**Scheduler periódico**
Se implementó un scheduler (APScheduler) que evalúa eventos cada N minutos. Es la solución más simple y directa para el alcance del challenge. Una alternativa para producción sería que el job de ingesta publique cada nuevo evento climático en un sistema de mensajería (Pub/Sub) y que la evaluación de alertas ocurra como subscriber en tiempo real. Esto eliminaría el polling periódico a la base de datos y reduciría la latencia entre la llegada del evento y la generación de la notificación.

**Filtro de ventana temporal en la query principal**
`get_unevaluated_matches` filtra eventos con `forecast_date >= hoy - 3 días`, descartando registros históricos que nunca van a generar una notificación. Los eventos futuros no son afectados. Esto reduce el conjunto de filas que entran al JOIN y al `~exists()`, mejorando el rendimiento en escenarios de alto volumen.


## Trabajos futuros

**Integración real con WhatsApp**
`Notification` fue diseñada con estados y reintentos (`PENDING`, `SENT`, `FAILED`, `retry_count`, etc.) aunque no se implementa el envío real, ya que está fuera del alcance del challenge. El modelo está preparado para conectar esta lógica en producción.

**Celery para desacoplar el envío**
Lo ideal sería encolar cada notificación en Celery. El job quedaría reducido a detectar matches y encolar tareas, sin lidiar con lógica de envío ni reintentos. La responsabilidad de cada reintento recaería en el worker de Celery.

**Scheduler externo**
En producción se podría reemplazar APScheduler por un cron externo (cron de sistema, Kubernetes CronJob, o YAML de tarea programada). Esto simplifica el proceso principal de la app y permite escalar el job de evaluación de forma independiente.

---

## Flujo del sistema

```
scheduler (APScheduler, cada N minutos)
    └─> alert_evaluator.py
            └─> WeatherEvaluationService.evaluate_pending_alerts()
                    ├─> weather_event_repository.get_unevaluated_matches()
                    │       — eventos recientes con alerta activa y threshold superado
                    │       — sin notificación previa para ese par (idempotencia)
                    └─> notification_repository.create()  →  status: PENDING
```

---

## Instalación

Requiere Python 3.11+, Docker y Docker Compose.

```bash
git clone git@github.com:tmarmay/agrobot-weather-alerts.git
cd agrobot-weather-alerts
bash setup.sh
```

El script crea el entorno virtual, instala dependencias, levanta PostgreSQL, aplica las migraciones y carga datos de prueba.

Activar el entorno virtual:
```bash
source .venv/bin/activate
```

Levantar la API:
```bash
uvicorn app.main:app --reload
```

Documentación interactiva disponible en `http://localhost:8000/docs`.

> **Nota:** el endpoint `POST /api/v1/weather-events/` existe únicamente para simular la ingesta de eventos climáticos a modo de prueba. En un sistema real, este paso lo realizaría un job externo que persiste los pronósticos automáticamente.

---

## Tests

```bash
pytest tests/ -v
```

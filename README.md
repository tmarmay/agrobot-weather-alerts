# Agrobot - Sistema de Alertas Climáticas

## Notas y supuestos de diseño

**Nota #1**
No se utiliza Pub/Sub porque el requerimiento define explícitamente una evaluación periódica mediante background jobs. Un scheduler es la solución más simple y alineada con el problema actual.

**Nota #2**
Se asume que el matching entre eventos meteorológicos y campos ya fue resuelto por la ingesta. Los datos climáticos llegan asociados a un `field_id`, evitando modelar lógica geográfica fuera del alcance del challenge. Adicionalmente, se asume que cada `Field` pertenece a un único `User`.

**Nota #3**
`Notification` fue diseñada con estados y reintentos (`PENDING`, `SENT`, `FAILED`, `retry_count`, etc.) aunque no se implementa esta lógica, ya que no existe integración con WhatsApp en el alcance del challenge. Se consideró importante dejarlo explícito en el modelo de datos por su relevancia en un escenario de producción.

**Nota #4**
No se conoce el comportamiento real del job de ingesta (si actualiza pronósticos existentes o crea nuevos snapshots), por lo que no se cubre el caso de actualización de probabilidad para un mismo `(field_id, event_type, forecast_date)`. El testing asume una única entrada de `WeatherEvent` por combinación field + event_type + día, consistente con el unique constraint del modelo.

**Nota #5**
`get_unevaluated_matches` filtra eventos con `forecast_date >= hoy - 3 días` para evitar evaluar registros históricos que nunca van a generar una notificación. Los eventos futuros no son afectados. Esto reduce el conjunto de filas que entran al JOIN y al `~exists()`, mejorando el rendimiento en escenarios de alto volumen.



**Nota #6**
Para desacoplar el trabajo del job de alertas, lo ideal sería encolar cada notificación en Celery. Así el job solo se encarga de detectar matches y encolar tareas, sin lidiar con la lógica de envío, estados (`PENDING`, `SENT`, `FAILED`) ni reintentos. El job queda lo más corto posible y la responsabilidad de cada reintento recae en el worker de Celery.

**Nota #7**
En producción se podría reemplazar el scheduler embebido (APScheduler) por un cron externo (cron de sistema, Kubernetes CronJob, o un archivo YAML de tarea programada). Esto simplifica el proceso principal de la app, que no necesitaría correr el scheduler, y permite escalar el job de evaluación de forma independiente.

scheduler (APScheduler, corre solo cada N minutos)
    └─> app/jobs/alert_evaluator.py (corutina, orquesta)
            └─> weather_evaluation_service.evaluate_pending_alerts()  ← el corazón
                    ├─> weather_event_repository.get_unevaluated_events()
                    ├─> notification_repository.create()  (por cada match)
                    └─> (status PENDING, no se manda nada de verdad, ya quedó documentado en Nota #3)
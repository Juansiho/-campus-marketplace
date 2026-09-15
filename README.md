# Campus Marketplace — Capa ORM (Guía 4, Sesiones 7-8)

Implementación del ORM moderno (SQLAlchemy 2.0) para el proyecto semestral
**Campus Marketplace** (plataforma de subastas en línea para artículos de
segunda mano), correspondiente a la Guía 4 de Taller de Programación.

## Contenido

- `app/models.py` — 6 entidades mapeadas: `Usuario`, `Articulo`, `Subasta`,
  `Puja`, `Notificacion`, `MetricaConcurrencia`.
- `app/repositories/` — repositorios CRUD (`Usuario`, `Articulo`, `Subasta`,
  `Puja`). `ArticuloRepository.listar_por_vendedor` y
  `PujaRepository.historial_por_subasta` usan `joinedload` para resolver el
  problema N+1.
- `migrations/` — 2 migraciones de Alembic (creación de tablas + índices de
  rendimiento).
- `tests/test_integration.py` — 3 pruebas de integración con SQLite en
  memoria.
- `.github/workflows/ci.yml` — pipeline de CI que corre las pruebas y valida
  las migraciones en cada push.

## Cómo correrlo localmente

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

Para aplicar las migraciones contra MySQL (ajusta `DATABASE_URL`):

```bash
export DATABASE_URL="mysql+pymysql://usuario:clave@localhost:3306/campus_marketplace"
alembic -c migrations/alembic.ini upgrade head
```

## Pendiente por el equipo antes de entregar

- [ ] Reemplazar los datos de conexión de `DATABASE_URL` por los reales.
- [ ] Ejecutar la demo en vivo del sistema multicapa (UI→Negocio→ORM→BD).
- [ ] Correr el análisis de SonarCloud y capturar las métricas.
- [ ] Grabar y subir el video de comprobación (1-3 min, en inglés).

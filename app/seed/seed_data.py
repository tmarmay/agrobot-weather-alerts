import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.enums import WeatherEventType
from app.models.alert import Alert
from app.models.field import Field
from app.models.user import User


async def run_seed() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            existing = await session.execute(select(User))
            if existing.scalars().first():
                print("seed: data already exists, skipping.")
                return

            user1 = User(name="Juan Pérez", phone_number="+5491112345678")
            user2 = User(name="María García", phone_number="+5491187654321")
            session.add_all([user1, user2])
            await session.flush()

            field1 = Field(user_id=user1.id, name="Lote Norte", latitude=-31.41, longitude=-64.18)
            field2 = Field(user_id=user1.id, name="Lote Sur", latitude=-31.45, longitude=-64.20)
            field3 = Field(user_id=user2.id, name="Campo Este", latitude=-32.10, longitude=-63.90)
            field4 = Field(user_id=user2.id, name="Campo Oeste", latitude=-32.15, longitude=-64.05)
            session.add_all([field1, field2, field3, field4])
            await session.flush()

            # Alertas pre-cargadas — quien clone el repo puede probar el job
            # cargando un WeatherEvent directamente sin crear alertas a mano.
            alerts = [
                Alert(user_id=user1.id, field_id=field1.id, event_type=WeatherEventType.RAIN, threshold=50.0),
                Alert(user_id=user1.id, field_id=field2.id, event_type=WeatherEventType.FROST, threshold=60.0),
                Alert(user_id=user2.id, field_id=field3.id, event_type=WeatherEventType.HAIL, threshold=70.0),
                Alert(user_id=user2.id, field_id=field4.id, event_type=WeatherEventType.RAIN, threshold=40.0),
            ]
            session.add_all(alerts)

    print("seed: done.")
    print(f"  users : {user1.name} (id={user1.id}), {user2.name} (id={user2.id})")
    print(f"  fields: {field1.name} (id={field1.id}), {field2.name} (id={field2.id}), "
          f"{field3.name} (id={field3.id}), {field4.name} (id={field4.id})")
    print("  alerts: RAIN@field1 threshold=50, FROST@field2 threshold=60, "
          "HAIL@field3 threshold=70, RAIN@field4 threshold=40")


if __name__ == "__main__":
    asyncio.run(run_seed())

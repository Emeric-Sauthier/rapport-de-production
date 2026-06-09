from datetime import datetime
from backend.models import ManufacturingOrder, Downtime
import uuid

mock_orders: list[ManufacturingOrder] = [
    ManufacturingOrder(
        id=str(uuid.uuid4()),
        name="OF-2026-001",
        machine="Machine A",
        target_quantity=500,
        produced_quantity=480,
        rejects=12,
        start_time=datetime(2026, 6, 1, 8, 0),
        end_time=datetime(2026, 6, 1, 16, 0),
    ),
    ManufacturingOrder(
        id=str(uuid.uuid4()),
        name="OF-2026-002",
        machine="Machine A",
        target_quantity=300,
        produced_quantity=310,
        rejects=8,
        start_time=datetime(2026, 6, 2, 8, 0),
        end_time=datetime(2026, 6, 2, 14, 0),
    ),
    ManufacturingOrder(
        id=str(uuid.uuid4()),
        name="OF-2026-003",
        machine="Machine B",
        target_quantity=400,
        produced_quantity=350,
        rejects=25,
        start_time=datetime(2026, 6, 1, 7, 0),
        end_time=datetime(2026, 6, 1, 15, 0),
    ),
    ManufacturingOrder(
        id=str(uuid.uuid4()),
        name="OF-2026-004",
        machine="Machine B",
        target_quantity=200,
        produced_quantity=195,
        rejects=5,
        start_time=datetime(2026, 6, 3, 8, 0),
        end_time=datetime(2026, 6, 3, 12, 0),
    ),
]

mock_downtimes: list[Downtime] = [
    Downtime(
        id=str(uuid.uuid4()),
        machine="Machine A",
        cause="Panne hydraulique",
        start_time=datetime(2026, 6, 1, 12, 0),
        end_time=datetime(2026, 6, 1, 12, 30),
    ),
    Downtime(
        id=str(uuid.uuid4()),
        machine="Machine B",
        cause="Maintenance préventive",
        start_time=datetime(2026, 6, 1, 10, 0),
        end_time=datetime(2026, 6, 1, 11, 0),
    ),
    Downtime(
        id=str(uuid.uuid4()),
        machine="Machine B",
        cause="Arrêt qualité",
        start_time=datetime(2026, 6, 3, 9, 0),
        end_time=datetime(2026, 6, 3, 9, 15),
    ),
]

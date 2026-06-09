import uuid
from datetime import datetime
from io import StringIO
import csv

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    Machine, MachineData, ProductionIndicators, ProductionReport,
    ManufacturingOrder, ManufacturingOrderDto,
    Downtime, DowntimeCreate,
)
from backend.machines_mock import get_machines_list
from backend.mock_data import mock_orders, mock_downtimes
from backend.llm_service import generate_report_content

_manufacturing_orders: list[ManufacturingOrder] = list(mock_orders)
_downtimes: list[Downtime] = list(mock_downtimes)

app = FastAPI(title="Rapport de Production API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def compute_machines_from_orders_and_downtimes(
    orders: list[ManufacturingOrder],
    downtimes: list[Downtime],
) -> list[MachineData]:
    buckets: dict[str, dict] = {
        m.name: {
            "pieces_produced": 0,
            "pieces_rejected": 0,
            "pieces_target": 0,
            "usage_time_min": 0.0,
            "downtime_min": 0.0,
        }
        for m in get_machines_list()
    }

    for order in orders:
        m = order.machine
        if m not in buckets:
            buckets[m] = {
                "pieces_produced": 0,
                "pieces_rejected": 0,
                "pieces_target": 0,
                "usage_time_min": 0.0,
                "downtime_min": 0.0,
            }
        buckets[m]["pieces_produced"] += order.produced_quantity
        buckets[m]["pieces_rejected"] += order.rejects
        buckets[m]["pieces_target"] += order.target_quantity
        buckets[m]["usage_time_min"] += (order.end_time - order.start_time).total_seconds() / 60

    for dt in downtimes:
        m = dt.machine
        if m in buckets:
            buckets[m]["downtime_min"] += (dt.end_time - dt.start_time).total_seconds() / 60

    return [
        MachineData(
            machine_id=name.lower().replace(" ", "-"),
            machine_name=name,
            pieces_produced=b["pieces_produced"],
            pieces_rejected=b["pieces_rejected"],
            pieces_target=b["pieces_target"],
            usage_time_min=round(b["usage_time_min"], 2),
            planned_time_min=round(b["usage_time_min"] + b["downtime_min"], 2),
        )
        for name, b in buckets.items()
    ]


def compute_global_indicators(machines: list[MachineData]) -> ProductionIndicators:
    total_produced = sum(m.pieces_produced for m in machines)
    total_rejected = sum(m.pieces_rejected for m in machines)
    total_target = sum(m.pieces_target for m in machines)
    total_usage = sum(m.usage_time_min for m in machines)
    total_planned = sum(m.planned_time_min for m in machines)

    performance = total_produced / total_target if total_target > 0 else 0.0
    quality = (total_produced - total_rejected) / total_produced if total_produced > 0 else 0.0
    availability = total_usage / total_planned if total_planned > 0 else 0.0
    trs = performance * quality * availability

    return ProductionIndicators(
        performance=round(performance, 4),
        quality=round(quality, 4),
        availability=round(availability, 4),
        trs=round(trs, 4),
    )


@app.get("/machines-list", response_model=list[Machine])
def list_machines():
    return get_machines_list()


@app.get("/machines", response_model=list[MachineData])
def get_machines():
    return compute_machines_from_orders_and_downtimes(_manufacturing_orders, _downtimes)


@app.get("/indicators/global", response_model=ProductionIndicators)
def get_global_indicators():
    machines = compute_machines_from_orders_and_downtimes(_manufacturing_orders, _downtimes)
    return compute_global_indicators(machines)


def __generate_report():
    machines = compute_machines_from_orders_and_downtimes(_manufacturing_orders, _downtimes)
    indicators = compute_global_indicators(machines)
    llm_result = generate_report_content(machines, indicators)

    return ProductionReport(
        report_id=str(uuid.uuid4()),
        generated_at=datetime.now(),
        machines=machines,
        global_indicators=indicators,
        summary_text=llm_result["summary"],
        advices=llm_result["advices"],
    )


# --- Manufacturing Orders ---

@app.get("/manufacturing-orders", response_model=list[ManufacturingOrder])
def list_manufacturing_orders():
    return _manufacturing_orders


@app.post("/manufacturing-orders", response_model=ManufacturingOrder, status_code=201)
def create_manufacturing_order(body: ManufacturingOrderDto):
    order = ManufacturingOrder(id=str(uuid.uuid4()), **body.model_dump())
    _manufacturing_orders.append(order)
    return order


@app.put("/manufacturing-orders/{order_id}", response_model=ManufacturingOrder)
def update_manufacturing_order(order_id: str, body: ManufacturingOrderDto):
    for i, order in enumerate(_manufacturing_orders):
        if order.id == order_id:
            updated = ManufacturingOrder(id=order_id, **body.model_dump())
            _manufacturing_orders[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Manufacturing order not found")


@app.delete("/manufacturing-orders/{order_id}", status_code=204)
def delete_manufacturing_order(order_id: str):
    for i, order in enumerate(_manufacturing_orders):
        if order.id == order_id:
            _manufacturing_orders.pop(i)
            return
    raise HTTPException(status_code=404, detail="Manufacturing order not found")


# --- Downtimes ---

@app.get("/downtimes", response_model=list[Downtime])
def list_downtimes():
    return _downtimes


@app.post("/downtimes", response_model=Downtime, status_code=201)
def create_downtime(body: DowntimeCreate):
    downtime = Downtime(id=str(uuid.uuid4()), **body.model_dump())
    _downtimes.append(downtime)
    return downtime


@app.put("/downtimes/{downtime_id}", response_model=Downtime)
def update_downtime(downtime_id: str, body: DowntimeCreate):
    for i, dt in enumerate(_downtimes):
        if dt.id == downtime_id:
            updated = Downtime(id=downtime_id, **body.model_dump())
            _downtimes[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Downtime not found")


@app.delete("/downtimes/{downtime_id}", status_code=204)
def delete_downtime(downtime_id: str):
    for i, dt in enumerate(_downtimes):
        if dt.id == downtime_id:
            _downtimes.pop(i)
            return
    raise HTTPException(status_code=404, detail="Downtime not found")


@app.post("/report/generate", response_model=ProductionReport)
def generate_report():
    return __generate_report()


@app.post("/import-csv/manufacturing-orders", response_model=list[ManufacturingOrder])
async def import_orders_csv(file: UploadFile = File(...)):
    global _manufacturing_orders
    content = await file.read()
    reader = csv.DictReader(StringIO(content.decode("utf-8-sig")))
    orders = []
    for row in reader:
        orders.append(ManufacturingOrder(
            id=str(uuid.uuid4()),
            name=row["name"],
            target_quantity=int(row["target_quantity"]),
            produced_quantity=int(row["produced_quantity"]),
            rejects=int(row.get("rejects") or 0),
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=datetime.fromisoformat(row["end_time"]),
            machine=row["machine"],
        ))
    _manufacturing_orders = orders
    return _manufacturing_orders


@app.post("/import-csv/downtimes", response_model=list[Downtime])
async def import_downtimes_csv(file: UploadFile = File(...)):
    global _downtimes
    content = await file.read()
    reader = csv.DictReader(StringIO(content.decode("utf-8-sig")))
    downtimes = []
    for row in reader:
        downtimes.append(Downtime(
            id=str(uuid.uuid4()),
            cause=row["cause"],
            start_time=datetime.fromisoformat(row["start_time"]),
            end_time=datetime.fromisoformat(row["end_time"]),
            machine=row["machine"],
        ))
    _downtimes = downtimes
    return _downtimes

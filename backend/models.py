from pydantic import BaseModel
from datetime import datetime


class Machine(BaseModel):
    id: str
    name: str


class MachineData(BaseModel):
    machine_id: str
    machine_name: str
    pieces_produced: int
    pieces_rejected: int
    pieces_target: int
    usage_time_min: float
    planned_time_min: float


class ProductionIndicators(BaseModel):
    performance: float
    quality: float
    availability: float
    trs: float


class ProductionReport(BaseModel):
    report_id: str
    generated_at: datetime
    machines: list[MachineData]
    global_indicators: ProductionIndicators
    summary_text: str
    advices: list[str]


class ManufacturingOrder(BaseModel):
    id: str
    name: str
    target_quantity: int
    produced_quantity: int
    rejects: int = 0
    start_time: datetime
    end_time: datetime
    machine: str


class ManufacturingOrderDto(BaseModel):
    name: str
    target_quantity: int
    produced_quantity: int
    rejects: int = 0
    start_time: datetime
    end_time: datetime
    machine: str


class Downtime(BaseModel):
    id: str
    cause: str
    start_time: datetime
    end_time: datetime
    machine: str


class DowntimeCreate(BaseModel):
    cause: str
    start_time: datetime
    end_time: datetime
    machine: str

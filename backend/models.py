from pydantic import BaseModel
from datetime import datetime


class MachineData(BaseModel):
    machine_id: str
    machine_name: str
    pieces_produced: int
    pieces_rejected: int
    usage_time_min: float
    planned_time_min: float
    theoretical_rate_per_hour: float


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

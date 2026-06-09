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

    @classmethod
    def from_csv_row(
        cls,
        row: dict,
        machine_id: str,
        planned_time_min: float = 480.0,
        theoretical_rate_per_hour: float = 100.0,
    ) -> "MachineData":
        print(row)
        return cls(
            machine_id=machine_id,
            machine_name=row["Machine"],
            pieces_produced=int(row["Pièces produites"]),
            pieces_rejected=int(row["Pièces rejetées"]),
            usage_time_min=float(row["Temps d'utilisation (min)"]),
            planned_time_min=planned_time_min,
            theoretical_rate_per_hour=theoretical_rate_per_hour,
        )


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

import uuid
from datetime import datetime
from io import StringIO
import csv

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from backend.mock_data import get_mock_machines, set_mock_machines
from backend.models import MachineData, ProductionIndicators, ProductionReport
from backend.llm_service import generate_report_content
from url import BACKEND_URL

app = FastAPI(title="Rapport de Production API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def compute_global_indicators(machines: list[MachineData]) -> ProductionIndicators:
    total_produced = sum(m.pieces_produced for m in machines)
    total_rejected = sum(m.pieces_rejected for m in machines)
    total_usage = sum(m.usage_time_min for m in machines)
    total_planned = sum(m.planned_time_min for m in machines)
    theoretical_output = sum(
        (m.theoretical_rate_per_hour / 60) * m.usage_time_min for m in machines
    )

    performance = total_produced / theoretical_output if theoretical_output > 0 else 0.0
    quality = (total_produced - total_rejected) / total_produced if total_produced > 0 else 0.0
    availability = total_usage / total_planned if total_planned > 0 else 0.0
    trs = performance * quality * availability

    return ProductionIndicators(
        performance=round(performance, 4),
        quality=round(quality, 4),
        availability=round(availability, 4),
        trs=round(trs, 4),
    )


@app.get("/machines", response_model=list[MachineData])
def get_machines():
    return get_mock_machines()


@app.get("/indicators/global", response_model=ProductionIndicators)
def get_global_indicators():
    machines = get_mock_machines()
    return compute_global_indicators(machines)


def __generate_report():
    machines = get_mock_machines()
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

@app.post("/report/generate", response_model=ProductionReport)
def generate_report():
    return __generate_report()

@app.post("/import-csv", response_model=ProductionReport)
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    reader = csv.DictReader(StringIO(content.decode("utf-8-sig")))
    machines = []
    for i, row in enumerate(reader, start=1):
        machines.append(MachineData.from_csv_row(row, str(i)))
    set_mock_machines(machines)
    return __generate_report()

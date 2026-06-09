from backend.models import MachineData


def get_mock_machines() -> list[MachineData]:
    return [
        MachineData(
            machine_id="machine-a",
            machine_name="Machine A",
            pieces_produced=520,
            pieces_rejected=18,
            usage_time_min=445,
            planned_time_min=480,
            theoretical_rate_per_hour=70,
        ),
        MachineData(
            machine_id="machine-b",
            machine_name="Machine B",
            pieces_produced=310,
            pieces_rejected=42,
            usage_time_min=310,
            planned_time_min=480,
            theoretical_rate_per_hour=70,
        ),
    ]

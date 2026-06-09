from backend.models import Machine

_machines: list[Machine] = [
    Machine(id="machine-a", name="Machine A"),
    Machine(id="machine-b", name="Machine B"),
    Machine(id="machine-c", name="Machine C"),
]


def get_machines_list() -> list[Machine]:
    return _machines

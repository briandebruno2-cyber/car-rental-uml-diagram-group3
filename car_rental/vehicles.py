"""Vehicle classes: Vehicle (abstract) -> Sedan, SUV, Van, plus MaintenanceRecord."""
from abc import ABC, abstractmethod

from .utils import next_id


class MaintenanceRecord:
    """Service job. Created and owned by one Vehicle (composition)."""

    def __init__(self, service_date, description, cost):
        self._record_id = next_id("MNT")
        self._service_date = service_date
        self._description = description
        self._cost = cost
        self._status = "Pending"

    @property
    def record_id(self):
        return self._record_id

    @property
    def description(self):
        return self._description

    @property
    def cost(self):
        return self._cost

    @property
    def status(self):
        return self._status

    def schedule(self):
        self._status = "Scheduled"

    def complete(self):
        self._status = "Completed"


class Vehicle(ABC):
    """Abstract parent. Each subclass prices its own rentals."""

    STATUSES = ("Available", "Reserved", "Rented", "Maintenance")

    def __init__(self, plate_number, make, model, year, daily_rate):
        self._vehicle_id = next_id("VEH")
        self._plate_number = plate_number
        self._make = make
        self._model = model
        self._year = year
        self._daily_rate = daily_rate
        self._status = "Available"
        self._maintenance_records = []  # Vehicle 1 --- 0..* MaintenanceRecord

    @property
    def vehicle_id(self):
        return self._vehicle_id

    @property
    def plate_number(self):
        return self._plate_number

    @property
    def daily_rate(self):
        return self._daily_rate

    @property
    def status(self):
        return self._status

    @property
    def maintenance_records(self):
        return list(self._maintenance_records)

    def is_available(self):
        return self._status == "Available"

    def update_status(self, status):
        if status not in self.STATUSES:
            raise ValueError(f"Invalid status '{status}'. Use one of {self.STATUSES}")
        self._status = status

    @abstractmethod
    def calculate_rate(self, days):
        """Price for renting this vehicle for the given number of days."""

    def schedule_maintenance(self, service_date, description, cost):
        """The vehicle creates its own record (composition)."""
        if not self.is_available():
            raise ValueError(f"{self._plate_number} is {self._status} and cannot be serviced now")
        record = MaintenanceRecord(service_date, description, cost)
        record.schedule()
        self._maintenance_records.append(record)
        self._status = "Maintenance"
        return record

    def complete_maintenance(self, record):
        record.complete()
        self._status = "Available"

    def __str__(self):
        return (f"{self._vehicle_id} {self.__class__.__name__:<5} {self._make} {self._model} "
                f"({self._plate_number}) - {self._status}")


class Sedan(Vehicle):
    def __init__(self, plate_number, make, model, year, daily_rate, trunk_size):
        super().__init__(plate_number, make, model, year, daily_rate)
        self._trunk_size = trunk_size

    def calculate_rate(self, days):
        total = self._daily_rate * days
        return total * 0.90 if days >= 7 else total  # 10% off for a week or more


class SUV(Vehicle):
    def __init__(self, plate_number, make, model, year, daily_rate, four_wheel_drive):
        super().__init__(plate_number, make, model, year, daily_rate)
        self._four_wheel_drive = four_wheel_drive

    def calculate_rate(self, days):
        return self._daily_rate * days * 1.25  # 25% premium


class Van(Vehicle):
    def __init__(self, plate_number, make, model, year, daily_rate, seat_capacity):
        super().__init__(plate_number, make, model, year, daily_rate)
        self._seat_capacity = seat_capacity

    def calculate_rate(self, days):
        return self._daily_rate * days * 1.40  # 40% premium

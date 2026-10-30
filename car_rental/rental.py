"""Rental flow classes: Branch, Insurance, Booking, RentalAgreement, Payment."""
from .utils import next_id
from datetime import date


class Branch:
    """Aggregation: a branch holds vehicles and employees, but they exist without it."""

    def __init__(self, name, location, phone):
        self._branch_id = next_id("BRN")
        self._name = name
        self._location = location
        self._phone = phone
        self._vehicles = []
        self._employees = []

    @property
    def name(self):
        return self._name

    @property
    def location(self):
        return self._location

    @property
    def vehicles(self):
        return list(self._vehicles)

    @property
    def employees(self):
        return list(self._employees)

    def add_vehicle(self, vehicle):
        if vehicle in self._vehicles:
            raise ValueError("Vehicle is already at this branch")
        self._vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        """The vehicle is only removed from the branch, it still exists."""
        self._vehicles.remove(vehicle)
        return vehicle

    def add_employee(self, employee):
        self._employees.append(employee)

    def get_available_vehicles(self):
        return [v for v in self._vehicles if v.is_available()]


class Insurance:
    def __init__(self, provider, coverage_type, daily_cost):
        self._policy_no = next_id("INS")
        self._provider = provider
        self._coverage_type = coverage_type
        self._daily_cost = daily_cost

    @property
    def coverage_type(self):
        return self._coverage_type

    def get_coverage_cost(self, days):
        return self._daily_cost * days


class Payment:
    """Created and owned by one RentalAgreement (composition)."""

    def __init__(self, amount, method):
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        self._payment_id = next_id("PAY")
        self._amount = amount
        self._method = method
        self._payment_date = None
        self._status = "Pending"

    @property
    def amount(self):
        return self._amount

    @property
    def method(self):
        return self._method

    @property
    def status(self):
        return self._status

    def process(self):
        if self._status != "Pending":
            return False
        self._payment_date = date.today()
        self._status = "Completed"
        return True

    def refund(self):
        if self._status != "Completed":
            raise ValueError("Only a completed payment can be refunded")
        self._status = "Refunded"


class Booking:
    """A reservation of exactly one vehicle (Booking 0..* --- 1 Vehicle)."""

    def __init__(self, customer, vehicle, pickup_date, return_date):
        if return_date <= pickup_date:
            raise ValueError("Return date must be after the pickup date")
        self._booking_id = next_id("BKG")
        self._customer = customer
        self._vehicle = vehicle
        self._booking_date = date.today()
        self._pickup_date = pickup_date
        self._return_date = return_date
        self._status = "Pending"
        self._agreement = None  # Booking 1 --- 0..1 RentalAgreement

    @property
    def booking_id(self):
        return self._booking_id

    @property
    def customer(self):
        return self._customer

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def pickup_date(self):
        return self._pickup_date

    @property
    def return_date(self):
        return self._return_date

    @property
    def status(self):
        return self._status

    @property
    def agreement(self):
        return self._agreement

    def get_days(self):
        return (self._return_date - self._pickup_date).days

    def confirm(self):
        if self._status != "Pending":
            raise ValueError(f"Only a pending booking can be confirmed (status is {self._status})")
        if not self._vehicle.is_available():
            raise ValueError(f"{self._vehicle.plate_number} is not available ({self._vehicle.status})")
        self._vehicle.update_status("Reserved")
        self._status = "Confirmed"

    def cancel(self):
        if self._status not in ("Pending", "Confirmed"):
            raise ValueError(f"A {self._status} booking cannot be cancelled")
        if self._status == "Confirmed":
            self._vehicle.update_status("Available")
        self._status = "Cancelled"

    def calculate_total(self):
        return self._vehicle.calculate_rate(self.get_days())

    # helpers used by RentalAgreement
    def attach_agreement(self, agreement):
        if self._agreement is not None:
            raise ValueError("This booking already has a rental agreement")
        self._agreement = agreement

    def mark_active(self):
        self._status = "Active"
        self._vehicle.update_status("Rented")

    def mark_completed(self):
        self._status = "Completed"
        self._vehicle.update_status("Available")


class RentalAgreement:
    LATE_FEE_MULTIPLIER = 1.5

    def __init__(self, booking, agent, start_mileage, fuel_level="Full", insurance=None):
        if booking.status != "Confirmed":
            raise ValueError("A rental agreement needs a confirmed booking")
        booking.attach_agreement(self)
        self._agreement_id = next_id("AGR")
        self._booking = booking
        self._agent = agent
        self._insurance = insurance  # optional: 0..1
        self._start_mileage = start_mileage
        self._end_mileage = None
        self._fuel_level = fuel_level
        self._status = "Pending"
        self._discount_percent = 0
        self._late_fee = 0.0
        self._payments = []  # RentalAgreement 1 --- 1..* Payment

    @property
    def booking(self):
        return self._booking

    @property
    def status(self):
        return self._status

    @property
    def late_fee(self):
        return self._late_fee

    @property
    def payments(self):
        return list(self._payments)

    def open_agreement(self):
        if self._status != "Pending":
            raise ValueError("Agreement is already open or closed")
        self._booking.mark_active()
        self._status = "Open"

    def calculate_late_fee(self, actual_return_date):
        days_late = max(0, (actual_return_date - self._booking.return_date).days)
        return days_late * self._booking.vehicle.daily_rate * self.LATE_FEE_MULTIPLIER

    def close_agreement(self, end_mileage, fuel_level, actual_return_date):
        if self._status != "Open":
            raise ValueError("Only an open agreement can be closed")
        if end_mileage < self._start_mileage:
            raise ValueError("End mileage cannot be less than start mileage")
        self._end_mileage = end_mileage
        self._fuel_level = fuel_level
        self._late_fee = self.calculate_late_fee(actual_return_date)
        self._booking.mark_completed()
        self._status = "Closed"
        return self.total_due()

    # --- helpers for money (not in the UML, they support its methods) ---
    def apply_discount(self, percent):
        self._discount_percent = percent

    def total_due(self):
        rental = self._booking.calculate_total() * (1 - self._discount_percent / 100)
        cover = self._insurance.get_coverage_cost(self._booking.get_days()) if self._insurance else 0
        return rental + cover + self._late_fee

    def add_payment(self, amount, method):
        """The agreement creates its own Payment (composition) and processes it."""
        payment = Payment(amount, method)
        payment.process()
        self._payments.append(payment)
        return payment

    def amount_paid(self):
        return sum(p.amount for p in self._payments if p.status == "Completed")

    def balance_due(self):
        return self.total_due() - self.amount_paid()

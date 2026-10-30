"""People classes: Person (abstract) -> Customer, Employee -> RentalAgent, Manager."""
from abc import ABC
from datetime import date

from .utils import next_id


class Person(ABC):
    """Abstract parent. Holds the data shared by customers and employees."""

    def __init__(self, name, phone, email):
        if type(self) is Person:
            raise TypeError("Person is abstract and cannot be instantiated directly")
        self._person_id = next_id("PER")
        self._name = name
        self._phone = phone
        self._email = email

    @property
    def person_id(self):
        return self._person_id

    @property
    def name(self):
        return self._name

    @property
    def phone(self):
        return self._phone

    @property
    def email(self):
        return self._email

    def get_contact_info(self):
        return f"{self._name} | {self._phone} | {self._email}"

    def update_profile(self, name=None, phone=None, email=None):
        if name:
            self._name = name
        if phone:
            self._phone = phone
        if email:
            self._email = email


class Customer(Person):
    def __init__(self, name, phone, email, driver_license_no, address):
        super().__init__(name, phone, email)
        self._driver_license_no = driver_license_no
        self._address = address
        self._date_registered = None
        self._bookings = []  # Customer 1 --- 0..* Booking

    @property
    def driver_license_no(self):
        return self._driver_license_no

    @property
    def address(self):
        return self._address

    @property
    def date_registered(self):
        return self._date_registered

    def register(self, on=None):
        """Register the customer. Returns False if already registered."""
        if self._date_registered is not None:
            return False
        self._date_registered = on or date.today()
        return True

    def make_booking(self, vehicle, pickup_date, return_date):
        """Create a Booking for one vehicle. Only registered customers may book."""
        from .rental import Booking  # imported here to avoid a circular import

        if self._date_registered is None:
            raise PermissionError(f"{self._name} must register before making a booking")
        booking = Booking(self, vehicle, pickup_date, return_date)
        self._bookings.append(booking)
        return booking

    def view_rental_history(self):
        return list(self._bookings)


class Employee(Person):
    def __init__(self, name, phone, email, hire_date, salary):
        super().__init__(name, phone, email)
        self._employee_id = next_id("EMP")
        self._hire_date = hire_date
        self._salary = salary
        self._logged_in = False

    @property
    def employee_id(self):
        return self._employee_id

    @property
    def hire_date(self):
        return self._hire_date

    @property
    def salary(self):
        return self._salary

    def login(self):
        self._logged_in = True
        return self._logged_in

    def get_role(self):
        return "Employee"


class RentalAgent(Employee):
    """Hands vehicles over and takes them back. RentalAgent 1 --- 0..* RentalAgreement."""

    def __init__(self, name, phone, email, hire_date, salary, counter_no):
        super().__init__(name, phone, email, hire_date, salary)
        self._counter_no = counter_no
        self._agreements = []

    @property
    def counter_no(self):
        return self._counter_no

    @property
    def agreements(self):
        return list(self._agreements)

    def get_role(self):
        return "Rental Agent"

    def process_pickup(self, booking, start_mileage, fuel_level="Full", insurance=None):
        """Create and open a RentalAgreement for a confirmed booking."""
        from .rental import RentalAgreement

        agreement = RentalAgreement(booking, self, start_mileage, fuel_level, insurance)
        agreement.open_agreement()
        self._agreements.append(agreement)
        return agreement

    def process_return(self, agreement, end_mileage, fuel_level, actual_return_date):
        """Close the agreement and return the total amount due."""
        return agreement.close_agreement(end_mileage, fuel_level, actual_return_date)


class Manager(Employee):
    def __init__(self, name, phone, email, hire_date, salary, department):
        super().__init__(name, phone, email, hire_date, salary)
        self._department = department

    @property
    def department(self):
        return self._department

    def get_role(self):
        return "Manager"

    def approve_discount(self, agreement, percent):
        """Approve a discount of up to 30% on an agreement."""
        if not 0 < percent <= 30:
            raise ValueError("Discount must be between 1% and 30%")
        agreement.apply_discount(percent)
        return percent

    def generate_report(self, branch):
        """Return a short text report of the branch fleet."""
        counts = {}
        for vehicle in branch.vehicles:
            counts[vehicle.status] = counts.get(vehicle.status, 0) + 1
        fleet = ", ".join(f"{status}: {n}" for status, n in sorted(counts.items()))
        return (f"Report for {branch.name} ({branch.location})\n"
                f"  Vehicles : {len(branch.vehicles)} ({fleet})\n"
                f"  Employees: {len(branch.employees)}")

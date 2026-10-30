"""Demonstration of the Car Rental Management System (Group 3).

Run with:  python main.py
Every section matches a part of the UML class diagram.
"""
from datetime import date

from car_rental import (Branch, Customer, Insurance, Manager, Person, RentalAgent,
                        SUV, Sedan, Van, Vehicle)


def title(text):
    print("\n" + "=" * 64)
    print(text)
    print("=" * 64)


def money(value):
    return f"KES {value:,.2f}"


# ---------------------------------------------------------------- 1
title("1. SETUP: branch, staff and vehicles (aggregation)")
branch = Branch("Nairobi CBD", "Kenyatta Avenue, Nairobi", "+254 700 000 001")
agent = RentalAgent("Peter Otieno", "0711 111 111", "peter@rentals.co.ke", date(2023, 3, 1), 60000, counter_no=2)
manager = Manager("Grace Wanjiru", "0722 222 222", "grace@rentals.co.ke", date(2020, 1, 15), 120000, "Operations")
branch.add_employee(agent)
branch.add_employee(manager)

sedan = Sedan("KDG 123X", "Toyota", "Axio", 2019, 5000, trunk_size=450)
suv = SUV("KDH 456Y", "Subaru", "Forester", 2021, 8000, four_wheel_drive=True)
van = Van("KDJ 789Z", "Toyota", "Hiace", 2020, 10000, seat_capacity=14)
for v in (sedan, suv, van):
    branch.add_vehicle(v)

for staff in branch.employees:
    print(f"  {staff.employee_id}  {staff.name:<14} role: {staff.get_role()}")
for v in branch.vehicles:
    print(" ", v)

# ---------------------------------------------------------------- 2
title("2. INHERITANCE & POLYMORPHISM: calculate_rate() per vehicle type")
for v in (sedan, suv, van):
    print(f"  {v.__class__.__name__:<5} 3 days = {money(v.calculate_rate(3))}")
print(f"  Sedan 7 days = {money(sedan.calculate_rate(7))}   (10% weekly discount)")

# ---------------------------------------------------------------- 3
title("3. CUSTOMER: register and make a booking")
customer = Customer("John Kamau", "0733 333 333", "john@mail.com", "DL-445566", "Westlands, Nairobi")
print("  Contact info :", customer.get_contact_info())
try:
    customer.make_booking(suv, date(2026, 11, 2), date(2026, 11, 5))
except PermissionError as error:
    print("  Before registering ->", error)
customer.register(on=date(2026, 10, 30))
print("  Registered   :", customer.date_registered)

booking = customer.make_booking(suv, date(2026, 11, 2), date(2026, 11, 5))
print(f"  {booking.booking_id} status: {booking.status}, days: {booking.get_days()}, "
      f"total: {money(booking.calculate_total())}")
booking.confirm()
print(f"  After confirm -> booking: {booking.status}, vehicle: {suv.status}")
print("  Available vehicles now:", [v.plate_number for v in branch.get_available_vehicles()])

# ---------------------------------------------------------------- 4
title("4. RENTAL AGREEMENT: pickup with insurance and a manager discount")
insurance = Insurance("Jubilee", "Full cover", daily_cost=1500)
agreement = agent.process_pickup(booking, start_mileage=42000, fuel_level="Full", insurance=insurance)
print(f"  Agreement {agreement.status}; booking: {booking.status}; vehicle: {suv.status}")
manager.approve_discount(agreement, 10)
print("  Manager approved a 10% discount")
print(f"  Total due so far: {money(agreement.total_due())}")
deposit = agreement.add_payment(10000, "M-Pesa")
print(f"  Deposit {money(deposit.amount)} via {deposit.method}: {deposit.status}")

# ---------------------------------------------------------------- 5
title("5. RETURN: one day late, late fee and final payment (composition)")
total = agent.process_return(agreement, end_mileage=42650, fuel_level="Half", actual_return_date=date(2026, 11, 6))
print(f"  Late fee      : {money(agreement.late_fee)}")
print(f"  Total due     : {money(total)}")
print(f"  Balance due   : {money(agreement.balance_due())}")
final = agreement.add_payment(agreement.balance_due(), "Card")
print(f"  Final payment {money(final.amount)} via {final.method}: {final.status}")
print(f"  Balance after : {money(agreement.balance_due())}")
print(f"  Agreement: {agreement.status}; booking: {booking.status}; vehicle: {suv.status}")
print("  Payments on this agreement:", len(agreement.payments))

# ---------------------------------------------------------------- 6
title("6. MAINTENANCE: the vehicle owns its records (composition)")
record = van.schedule_maintenance(date(2026, 11, 10), "Oil change and brake check", 7500)
print(f"  {record.record_id}: {record.description} -> {record.status}; van is {van.status}")
van.complete_maintenance(record)
print(f"  After service -> record: {record.status}; van is {van.status}")
print("  Records on van:", len(van.maintenance_records))

# ---------------------------------------------------------------- 7
title("7. BRANCH REPORT AND CUSTOMER HISTORY")
print(manager.generate_report(branch))
print("  Rental history for", customer.name)
for b in customer.view_rental_history():
    print(f"    {b.booking_id} {b.vehicle.plate_number} {b.pickup_date} -> {b.return_date} [{b.status}]")

# ---------------------------------------------------------------- 8
title("8. RULES FROM THE DIAGRAM ARE ENFORCED")


def double_booking():
    first = Customer("Mary Achieng", "0744 444 444", "mary@mail.com", "DL-1", "Kisumu")
    second = Customer("Ali Hassan", "0755 555 555", "ali@mail.com", "DL-2", "Mombasa")
    for c in (first, second):
        c.register()
    first.make_booking(sedan, date(2026, 12, 1), date(2026, 12, 3)).confirm()
    second.make_booking(sedan, date(2026, 12, 1), date(2026, 12, 3)).confirm()


def second_agreement():
    from car_rental import RentalAgreement
    c = Customer("Zawadi Mutua", "0766 666 666", "z@mail.com", "DL-3", "Nakuru")
    c.register()
    b = c.make_booking(van, date(2026, 12, 10), date(2026, 12, 12))
    b.confirm()
    RentalAgreement(b, agent, 1000)
    RentalAgreement(b, agent, 1000)  # a booking may have only 0..1 agreement


checks = [
    ("Create an abstract Person", lambda: Person("X", "0", "x@x.com")),
    ("Create an abstract Vehicle", lambda: Vehicle("KAA 000A", "X", "Y", 2020, 1)),
    ("Book a vehicle that is already reserved", double_booking),
    ("Give one booking a second agreement", second_agreement),
    ("Return date before pickup date",
     lambda: customer.make_booking(sedan, date(2026, 12, 5), date(2026, 12, 1))),
]
for label, action in checks:
    try:
        action()
        print(f"  [FAIL] {label}: no error raised")
    except (TypeError, ValueError, PermissionError) as error:
        print(f"  [OK]   {label}\n         -> {error}")

print("\nDemo finished: all classes from the UML diagram ran successfully.")

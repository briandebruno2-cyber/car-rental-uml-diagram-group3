import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from car_rental import (Branch, Customer, Insurance, Manager, Person, RentalAgent,
                        SUV, Sedan, Van, Vehicle)


def make_world():
    agent = RentalAgent("Agent", "1", "a@x.com", date(2023, 1, 1), 1000, 1)
    customer = Customer("Cust", "2", "c@x.com", "DL", "Addr")
    customer.register()
    return agent, customer


class TestSystem(unittest.TestCase):
    def test_abstract_classes(self):
        with self.assertRaises(TypeError):
            Person("x", "1", "x@x.com")
        with self.assertRaises(TypeError):
            Vehicle("P", "m", "m", 2020, 1)

    def test_polymorphic_rates(self):
        self.assertEqual(Sedan("A", "m", "m", 2020, 100, 400).calculate_rate(3), 300)
        self.assertEqual(SUV("B", "m", "m", 2020, 100, True).calculate_rate(3), 375)
        self.assertEqual(Van("C", "m", "m", 2020, 100, 14).calculate_rate(3), 420)
        self.assertEqual(Sedan("A", "m", "m", 2020, 100, 400).calculate_rate(7), 630)

    def test_unregistered_customer_cannot_book(self):
        c = Customer("N", "1", "n@x.com", "DL", "A")
        with self.assertRaises(PermissionError):
            c.make_booking(Sedan("A", "m", "m", 2020, 100, 400), date(2026, 1, 1), date(2026, 1, 2))

    def test_full_rental_flow(self):
        agent, customer = make_world()
        suv = SUV("S", "m", "m", 2021, 100, True)
        booking = customer.make_booking(suv, date(2026, 1, 1), date(2026, 1, 4))
        booking.confirm()
        self.assertEqual(suv.status, "Reserved")
        ag = agent.process_pickup(booking, 1000, insurance=Insurance("J", "Full", 10))
        self.assertEqual(suv.status, "Rented")
        total = agent.process_return(ag, 1500, "Half", date(2026, 1, 5))
        self.assertEqual(total, 375 + 30 + 150)  # rental + insurance + 1 late day
        ag.add_payment(total, "Cash")
        self.assertEqual(ag.balance_due(), 0)
        self.assertEqual(suv.status, "Available")
        self.assertEqual(booking.status, "Completed")

    def test_no_double_booking(self):
        _, customer = make_world()
        car = Sedan("A", "m", "m", 2020, 100, 400)
        customer.make_booking(car, date(2026, 1, 1), date(2026, 1, 2)).confirm()
        with self.assertRaises(ValueError):
            customer.make_booking(car, date(2026, 1, 1), date(2026, 1, 2)).confirm()

    def test_cancel_frees_vehicle(self):
        _, customer = make_world()
        car = Sedan("A", "m", "m", 2020, 100, 400)
        b = customer.make_booking(car, date(2026, 1, 1), date(2026, 1, 2))
        b.confirm()
        b.cancel()
        self.assertTrue(car.is_available())

    def test_maintenance_composition(self):
        van = Van("C", "m", "m", 2020, 100, 14)
        rec = van.schedule_maintenance(date(2026, 1, 1), "Service", 500)
        self.assertEqual(van.status, "Maintenance")
        van.complete_maintenance(rec)
        self.assertEqual((rec.status, van.status), ("Completed", "Available"))

    def test_branch_aggregation(self):
        branch = Branch("B", "L", "1")
        car = Sedan("A", "m", "m", 2020, 100, 400)
        branch.add_vehicle(car)
        branch.remove_vehicle(car)
        self.assertEqual(len(branch.vehicles), 0)
        self.assertEqual(car.status, "Available")  # vehicle still exists

    def test_discount_limit(self):
        mgr = Manager("M", "1", "m@x.com", date(2020, 1, 1), 1, "Ops")
        agent, customer = make_world()
        car = Sedan("A", "m", "m", 2020, 100, 400)
        b = customer.make_booking(car, date(2026, 1, 1), date(2026, 1, 2))
        b.confirm()
        ag = agent.process_pickup(b, 0)
        with self.assertRaises(ValueError):
            mgr.approve_discount(ag, 50)


if __name__ == "__main__":
    unittest.main()

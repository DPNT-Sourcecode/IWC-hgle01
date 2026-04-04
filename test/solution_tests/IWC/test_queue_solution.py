from __future__ import annotations

from .utils import call_dequeue, call_enqueue, call_size, iso_ts, run_queue


def test_enqueue_size_dequeue_flow() -> None:
    run_queue([
        call_enqueue("companies_house", 1, iso_ts(delta_minutes=0)).expect(1),
        call_size().expect(1),
        call_dequeue().expect("companies_house", 1),
    ])


# Example #1 - Rule of 3:
def test_enqueue_multiple_users_multiple_providers() -> None:
    run_queue([
        call_enqueue("companies_house", 1, iso_ts(delta_minutes=0)).expect(1),
        call_enqueue("bank_statements", 2, iso_ts(delta_minutes=0)).expect(2),
        call_enqueue("id_verification", 1, iso_ts(delta_minutes=0)).expect(3),
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=0)).expect(4),
        call_size().expect(4),
        call_dequeue().expect("companies_house", 1),
        call_dequeue().expect("id_verification", 1),
        call_dequeue().expect("bank_statements", 1),
        call_dequeue().expect("bank_statements", 2),
    ])


# Example #2 - Timestamp Ordering:
def test_timestamp_ordering() -> None:
    run_queue([
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=5)).expect(1),
        call_enqueue("bank_statements", 2, iso_ts(delta_minutes=0)).expect(2),
        call_dequeue().expect("bank_statements", 2),
        call_dequeue().expect("bank_statements", 1),
    ])


# Example #3 - Dependency Resolution:
def test_dependency_resolution() -> None:
    run_queue([
        call_enqueue("credit_check", 1, iso_ts(delta_minutes=0)).expect(2),
        call_dequeue().expect("companies_house", 1),
        call_dequeue().expect("credit_check", 1),
    ])


def test_priority_resolution_with_dependencies_and_three_tasks_and_different_timestamps() -> None:
    run_queue([
        call_enqueue("credit_check", 1, iso_ts(delta_minutes=10)).expect(2),
        call_enqueue("id_verification", 1, iso_ts(delta_minutes=10)).expect(3),
        call_enqueue("bank_statements", 2, iso_ts(delta_minutes=0)).expect(4),
        call_dequeue().expect("companies_house", 1),
        call_dequeue().expect("credit_check", 1),
        call_dequeue().expect("id_verification", 1),
        call_dequeue().expect("bank_statements", 2),
    ])


def test_priority_resolution_with_dependencies_and_different_timestamps() -> None:
    run_queue([
        call_enqueue("credit_check", 1, iso_ts(delta_minutes=10)).expect(2),
        call_enqueue("bank_statements", 2, iso_ts(delta_minutes=0)).expect(3),
        call_dequeue().expect("bank_statements", 2),
        call_dequeue().expect("companies_house", 1),
        call_dequeue().expect("credit_check", 1),
    ])

def test_priority_dependencies_and_rule_of_three_tasks() -> None:
    run_queue([
        call_enqueue("credit_check", 1, iso_ts(delta_minutes=10)).expect(2),
        call_enqueue("credit_check", 2, iso_ts(delta_minutes=20)).expect(4),
        call_enqueue("id_verification", 2, iso_ts(delta_minutes=50)).expect(5),
        call_dequeue().expect("companies_house", 2),
        call_dequeue().expect("credit_check", 2),
        call_enqueue("id_verification", 2, iso_ts(delta_minutes=50)).expect(5),
        call_dequeue().expect("id_verification", 1),
        call_dequeue().expect("bank_statements", 2),
    ])


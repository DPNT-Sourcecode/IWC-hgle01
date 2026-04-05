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
        call_dequeue().expect("id_verification", 2),
        call_dequeue().expect("companies_house", 1),
        call_dequeue().expect("credit_check", 1),
    ])



# 1. Enqueue: user_id=1, provider="bank_statements", timestamp='2025-10-20 12:00:00'  -> 1 (queue size)
# 2. Enqueue: user_id=1, provider="bank_statements", timestamp='2025-10-20 12:05:00'  -> 1 (queue size)
# 3. Enqueue: user_id=1, provider="id_verification", timestamp='2025-10-20 12:05:00'  -> 2 (queue size)
# 4. Dequeue -> {"user_id": 1, "provider": "bank_statements"}
# 5. Dequeue -> {"user_id": 1, "provider": "id_verification"}
def test_priority_duplicated_tasks() -> None:
    run_queue([
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=0)).expect(1),
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=5)).expect(1),
        call_enqueue("id_verification", 1, iso_ts(delta_minutes=5)).expect(2),
        call_dequeue().expect("bank_statements", 1),
        call_dequeue().expect("id_verification", 1),
    ])


def test_priority_duplicated_tasks_with_dependencies_and_with_different_user_ids() -> None:
    run_queue([
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=0)).expect(1),
        call_enqueue("companies_house", 1, iso_ts(delta_minutes=5)).expect(2),
        call_enqueue("credit_check", 1, iso_ts(delta_minutes=5)).expect(3),
        call_enqueue("id_verification", 2, iso_ts(delta_minutes=5)).expect(4),
        call_enqueue("id_verification", 2, iso_ts(delta_minutes=5)).expect(4),
        call_dequeue().expect("bank_statements", 1),
        call_dequeue().expect("companies_house", 1),
        call_dequeue().expect("credit_check", 1),
        call_dequeue().expect("id_verification", 2),
    ])


def test_duplicate_keeps_older_timestamp() -> None:
  run_queue([
      call_enqueue("bank_statements", 1, iso_ts(delta_minutes=5)).expect(1),  # newer first
      call_enqueue("bank_statements", 1, iso_ts(delta_minutes=0)).expect(1),  # older second -> kept for ordering
      call_enqueue("bank_statements", 2, iso_ts(delta_minutes=3)).expect(2),
      call_dequeue().expect("bank_statements", 1),  # t=0 beats t=3
      call_dequeue().expect("bank_statements", 2),
  ])


def test_duplicate_does_nt_trigger_rule_of_three() -> None:
    run_queue([
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=5)).expect(1),
        call_enqueue("id_verification", 1, iso_ts(delta_minutes=5)).expect(2),
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=5)).expect(2),
        call_enqueue("companies_house", 2, iso_ts(delta_minutes=0)).expect(3),
        call_dequeue().expect("companies_house", 2),
        call_dequeue().expect("bank_statements", 1),
        call_dequeue().expect("id_verification", 1),
    ])


def test_duplicate_dependency_not_re_added() -> None:
    run_queue([
        call_enqueue("companies_house", 1, iso_ts(delta_minutes=0)).expect(1),
        call_enqueue("credit_check", 1, iso_ts(delta_minutes=5)).expect(2),
        call_dequeue().expect("companies_house", 1),
        call_dequeue().expect("credit_check", 1),
    ]) 


def test_priority_duplicated_tasks_with_different_user_ids() -> None:
    run_queue([
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=0)).expect(1),
        call_enqueue("companies_house", 1, iso_ts(delta_minutes=5)).expect(2),
        call_enqueue("credit_check", 1, iso_ts(delta_minutes=5)).expect(3),
        call_enqueue("id_verification", 2, iso_ts(delta_minutes=5)).expect(4),
        call_enqueue("id_verification", 2, iso_ts(delta_minutes=5)).expect(4),
        call_dequeue().expect("bank_statements", 1),
        call_dequeue().expect("companies_house", 1),
        call_dequeue().expect("credit_check", 1),
        call_dequeue().expect("id_verification", 2),
    ])

# Example:
# --------
# 1. Enqueue: user_id=1, provider="bank_statements", timestamp='2025-10-20 12:00:00' -> 1 (queue size)
# 2. Enqueue: user_id=1, provider="id_verification", timestamp='2025-10-20 12:01:00' -> 2 (queue size)  
# 3. Enqueue: user_id=2, provider="companies_house", timestamp='2025-10-20 12:02:00' -> 3 (queue size)  
# 4. Dequeue -> {"user_id": 1, "provider": "id_verification"}  
# 5. Dequeue -> {"user_id": 2, "provider": "companies_house"}  
# 6. Dequeue -> {"user_id": 1, "provider": "bank_statements"}  
def test_priority_when_bank_statements_is_queued_and_then_credit_check_is_queued() -> None:
    run_queue([
        call_enqueue("bank_statements", 1, iso_ts(delta_minutes=0)).expect(1),
        call_enqueue("id_verification", 1, iso_ts(delta_minutes=1)).expect(2),
        call_enqueue("companies_house", 2, iso_ts(delta_minutes=2)).expect(3),
        call_dequeue().expect("id_verification", 1),
        call_dequeue().expect("companies_house", 2),
        call_dequeue().expect("bank_statements", 1),
    ])
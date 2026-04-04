from __future__ import annotations

from .utils import call_dequeue, call_enqueue, call_size, iso_ts, run_queue


def test_enqueue_size_dequeue_flow() -> None:
    run_queue([
        call_enqueue("companies_house", 1, iso_ts(delta_minutes=0)).expect(1),
        call_size().expect(1),
        call_dequeue().expect("companies_house", 1),
    ])


# 1. Enqueue: user_id=1, provider="companies_house",   timestamp='2025-10-20 12:00:00'  -> 1 (queue size)  
# 2. Enqueue: user_id=2, provider="bank_statements",   timestamp='2025-10-20 12:00:00'  -> 2 (queue size)  
# 3. Enqueue: user_id=1, provider="id_verification",   timestamp='2025-10-20 12:00:00'  -> 3 (queue size)  
# 4. Enqueue: user_id=1, provider="bank_statements",   timestamp='2025-10-20 12:00:00'  -> 4 (queue size)  
# 5. Dequeue -> {"user_id": 1, "provider": "companies_house"}  
# 6. Dequeue -> {"user_id": 1, "provider": "id_verification"}  
# 7. Dequeue -> {"user_id": 1, "provider": "bank_statements"}  
# 8. Dequeue -> {"user_id": 2, "provider": "bank_statements"}

def test_enqueue_size_dequeue_flow() -> None:
    run_queue([
        call_enqueue("companies_house", 1, iso_ts(delta_minutes=0)).expect(1),
        call_size().expect(1),
        call_dequeue().expect("companies_house", 1),
    ])


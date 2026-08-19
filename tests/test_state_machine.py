import unittest
import json
from state_machine_qps import StateMachineQPS, BASE_LEDGER_CENTS, FRAME_DELIMITER

class TestStateMachineQPS(unittest.TestCase):
    def setUp(self):
        self.gateway = StateMachineQPS()

    def test_initial_baseline(self):
        self.assertEqual(self.gateway.current_balance_cents, BASE_LEDGER_CENTS)
        self.assertTrue(len(self.gateway.apex_hash) == 64)

    def test_invoice_processing(self):
        payload = json.dumps({"invoice_id": "TEST-100", "rail": "BITCOIN", "amount_cents": 100000}).encode("utf-8")
        results = self.gateway.process_framed_payload(payload)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["settled_amount_usd"], 1000.0)
        self.assertEqual(self.gateway.current_balance_cents, BASE_LEDGER_CENTS + 100000)

    def test_holographic_evaluation(self):
        p1 = json.dumps({"invoice_id": "INV-A", "rail": "FIAT", "amount_cents": 250000}).encode("utf-8")
        self.gateway.process_framed_payload(p1)
        
        snapshot = [
            {"invoice_id": st.invoice_id, "rail": st.rail, "amount_cents": st.amount_cents, "timestamp": st.timestamp}
            for st in self.gateway.state_log
        ]
        valid, verified_hash, verified_balance = self.gateway.evaluate_holographic_state(snapshot)
        self.assertTrue(valid)
        self.assertEqual(verified_balance, self.gateway.current_balance_cents)

if __name__ == "__main__":
    unittest.main()

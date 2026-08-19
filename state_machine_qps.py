"""
State-Machine-QPS Integration Layer & Settlement Gateway
Target: Pythonista 3 (~/Documents iOS environment)
Execution: Pure Python / Built-in NumPy Standard Library Hybrid
"""

import sys
import os
import json
import struct
import hashlib
import time
import shutil
from typing import Dict, List, Tuple, Generator
from dataclasses import dataclass

def _cleanup_shadowed_numpy():
    doc_path = os.path.expanduser("~/Documents")
    site_packages = os.path.join(doc_path, "site-packages")
    shadow_numpy = os.path.join(site_packages, "numpy")
    
    if os.path.exists(shadow_numpy):
        try:
            shutil.rmtree(shadow_numpy)
        except Exception:
            pass

_cleanup_shadowed_numpy()

USE_NUMPY = False
try:
    import numpy as np
    USE_NUMPY = True
except ImportError:
    USE_NUMPY = False

FRAME_DELIMITER = b"\x00\xff\x00\xff\xde\xad\xbe\xef"
BASE_LEDGER_CENTS = 1023300000
SUPPORTED_RAILS = ("FIAT", "EVM", "SOLANA", "BITCOIN")


def double_horizon_proof(payload: bytes) -> bytes:
    h1 = hashlib.sha256(payload).digest()
    h2_a = hashlib.sha384(h1).digest()
    h2_b = hashlib.sha384(h2_a).digest()
    return hashlib.sha256(h2_b).digest()


def sim_vector_popcount_native(values: List[int]) -> List[int]:
    return [v.bit_count() for v in values]


def sim_vector_popcount_numpy(arr: "np.ndarray") -> "np.ndarray":
    M1 = np.uint64(0x5555555555555555)
    M2 = np.uint64(0x3333333333333333)
    M4 = np.uint64(0x0F0F0F0F0F0F0F0F)
    H01 = np.uint64(0x0101010101010101)

    x = arr.astype(np.uint64)
    x = x - ((x >> np.uint64(1)) & M1)
    x = (x & M2) + ((x >> np.uint64(2)) & M2)
    x = (x + (x >> np.uint64(4))) & M4
    return ((x * H01) >> np.uint64(56)).astype(np.uint64)


@dataclass
class InvoiceState:
    invoice_id: str
    rail: str
    amount_cents: int
    status: str
    timestamp: float
    prev_hash: str
    state_hash: str


class ZeroCopyFrameParser:
    def __init__(self, delimiter: bytes = FRAME_DELIMITER):
        self.delimiter = delimiter
        self.delim_len = len(delimiter)

    def parse_stream(self, stream_bytes: bytes) -> Generator[memoryview, None, None]:
        view = memoryview(stream_bytes)
        buffer_len = len(view)
        start = 0

        while start < buffer_len:
            idx = stream_bytes.find(self.delimiter, start)
            if idx == -1:
                if start < buffer_len:
                    yield view[start:]
                break
            if idx > start:
                yield view[start:idx]
            start = idx + self.delim_len


class StateMachineQPS:
    def __init__(self, initial_cents: int = BASE_LEDGER_CENTS):
        self.current_balance_cents = initial_cents
        self.state_log: List[InvoiceState] = []
        self.apex_hash = self._init_apex_hash()
        self.parser = ZeroCopyFrameParser()

    def _init_apex_hash(self) -> str:
        genesis_payload = f"GENESIS:{BASE_LEDGER_CENTS}:CRA_PROTOCOL_v2.1".encode("utf-8")
        return double_horizon_proof(genesis_payload).hex()

    def process_framed_payload(self, raw_stream: bytes) -> List[Dict]:
        results = []
        for frame in self.parser.parse_stream(raw_stream):
            if not frame:
                continue
            try:
                payload_dict = json.loads(frame.tobytes().decode("utf-8"))
                processed_state = self._ingest_invoice(payload_dict)
                results.append(processed_state)
            except Exception as err:
                results.append({"error": str(err), "frame_bytes": frame.tobytes().hex()})
        return results

    def _ingest_invoice(self, data: Dict) -> Dict:
        invoice_id = data["invoice_id"]
        rail = data["rail"].upper()
        amount_cents = int(data["amount_cents"])

        if rail not in SUPPORTED_RAILS:
            raise ValueError(f"Unsupported rail: {rail}")

        rail_idx = SUPPORTED_RAILS.index(rail)
        raw_vector = [abs(amount_cents), rail_idx, len(invoice_id)]

        if USE_NUMPY:
            state_vector = np.array(raw_vector, dtype=np.uint64)
            popcounts = sim_vector_popcount_numpy(state_vector)
            checksum = int(np.sum(popcounts))
        else:
            popcounts = sim_vector_popcount_native(raw_vector)
            checksum = sum(popcounts)

        self.current_balance_cents += amount_cents

        timestamp = time.time()
        canonical_str = f"{invoice_id}:{rail}:{amount_cents}:{self.current_balance_cents}:{timestamp}:{self.apex_hash}"
        state_proof = double_horizon_proof(canonical_str.encode("utf-8")).hex()

        new_state = InvoiceState(
            invoice_id=invoice_id,
            rail=rail,
            amount_cents=amount_cents,
            status="SETTLED",
            timestamp=timestamp,
            prev_hash=self.apex_hash,
            state_hash=state_proof,
        )

        self.state_log.append(new_state)
        self.apex_hash = state_proof

        return {
            "invoice_id": invoice_id,
            "rail": rail,
            "settled_amount_usd": amount_cents / 100.0,
            "new_ledger_baseline_usd": self.current_balance_cents / 100.0,
            "vector_popcount_checksum": checksum,
            "apex_hash": self.apex_hash,
        }

    def evaluate_holographic_state(self, arweave_log_snapshot: List[Dict]) -> Tuple[bool, str, int]:
        evaluated_cents = BASE_LEDGER_CENTS
        genesis_payload = f"GENESIS:{BASE_LEDGER_CENTS}:CRA_PROTOCOL_v2.1".encode("utf-8")
        running_hash = double_horizon_proof(genesis_payload).hex()

        for entry in arweave_log_snapshot:
            inv_id = entry["invoice_id"]
            rail = entry["rail"]
            amt = entry["amount_cents"]
            ts = entry["timestamp"]

            evaluated_cents += amt
            canonical = f"{inv_id}:{rail}:{amt}:{evaluated_cents}:{ts}:{running_hash}"
            running_hash = double_horizon_proof(canonical.encode("utf-8")).hex()

        is_valid = (running_hash == self.apex_hash) and (evaluated_cents == self.current_balance_cents)
        return is_valid, running_hash, evaluated_cents


if __name__ == "__main__":
    gateway = StateMachineQPS()
    p1 = json.dumps({"invoice_id": "INV-001", "rail": "EVM", "amount_cents": 5000000}).encode("utf-8")
    p2 = json.dumps({"invoice_id": "INV-002", "rail": "SOLANA", "amount_cents": -1200000}).encode("utf-8")

    stream_buffer = p1 + FRAME_DELIMITER + p2
    execution_results = gateway.process_framed_payload(stream_buffer)

    snapshot = [
        {"invoice_id": st.invoice_id, "rail": st.rail, "amount_cents": st.amount_cents, "timestamp": st.timestamp}
        for st.state_log in [gateway.state_log]
        for st in st.state_log
    ]
    valid, verified_hash, verified_balance = gateway.evaluate_holographic_state(snapshot)

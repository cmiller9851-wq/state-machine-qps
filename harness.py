import os
import json
from typing import Dict, Any, List
from web3 import Web3
from anti_system_verifier import AntiSystemEngine

class SettledRuntimeHarness:
    def __init__(self, process_id: str, cycle_limit: int, rpc_url: str, contract_address: str):
        # Initialize Core Deterministic Engine
        self.engine = AntiSystemEngine(process_id=process_id, cycle_limit=cycle_limit)
        
        # Initialize Blockchain Connection
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = self.w3.to_checksum_address(contract_address)

        # Standard minimal ABI to query paid balances on-chain cleanly
        self.contract_abi = [
            {
                "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                "name": "checkCreditBalance",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

    def verify_user_payment_standing(self, user_address: str) -> bool:
        """
        Queries the blockchain ledger to ensure the user has paid.
        """
        checksum_address = self.w3.to_checksum_address(user_address)
        try:
            # Check the balance in the escrow ledger contract
            credit_balance = self.contract.functions.checkCreditBalance(checksum_address).call()
            return credit_balance > 0
        except Exception as e:
            print(f"[-] Payment check failed: {str(e)}")
            return False

    def process_incoming_request(self, user_address: str, payload_step: Dict[str, Any]):
        # 1. Enforce frictionless payment verification check upfront
        if not self.verify_user_payment_standing(user_address):
            print(f"[REJECTED] Access Denied for user {user_address}. No active payment history found.")
            return

        # 2. Proceed with standard verified execution once payment is confirmed
        msg = payload_step["message"]
        cycles = payload_step.get("cycles", 100)
        claimed_root = self.engine.calculate_projected_root(msg)

        valid, response = self.engine.process(
            message=msg,
            claimed_root=claimed_root,
            cycles_used=cycles
        )

        if valid:
            print(f"[+] Execution Authorized. State Verified for Paid User: {user_address}")
            print(json.dumps(response, indent=2))
        else:
            print([-] Execution Blocked: Core rule validation breach.")

if __name__ == "__main__":
    # Target configurations
    LIVE_RPC_NODE_URL = "https://alchemy.com"
    DEPLOYED_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000000"

    harness = SettledRuntimeHarness(
        process_id="SETTLED_NODE_01", 
        cycle_limit=2000, 
        rpc_url=LIVE_RPC_NODE_URL,
        contract_address=DEPLOYED_CONTRACT_ADDRESS
    )
    
    # Process an execution batch for an account
    sample_step = {"message": {"action": "COMPUTE_BLOCK", "index": 1}}
    harness.process_incoming_request("0x95222290DD7278Aa3Dddd389Cc1E1d165CC4BAfe", sample_step)

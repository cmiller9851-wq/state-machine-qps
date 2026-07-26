// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FrictionlessSettlement {
    address public immutable walletDestination;
    
    struct AccountState {
        uint256 balanceCredits;
        uint256 lastPaymentTimestamp;
    }
    
    mapping(address => AccountState) public userRegistry;

    event PaymentSettled(address indexed payer, uint256 amountDeposited, uint256 creditsIssued);

    constructor() {
        // Sets your secure wallet destination permanently on deployment
        walletDestination = msg.sender;
    }

    /// Frictionless payment processing entry point
    function submitPayment() external payable {
        require(msg.value > 0, "Settlement: Value must be greater than zero");

        // Convert the incoming payment into computation credits (1:1 mapping example)
        userRegistry[msg.sender].balanceCredits += msg.value;
        userRegistry[msg.sender].lastPaymentTimestamp = block.timestamp;

        // Automatically push the incoming cash flow directly to your wallet destination
        (bool success, ) = payable(walletDestination).call{value: msg.value}("");
        require(success, "Settlement Fatal: Immediate revenue transfer failed");

        emit PaymentSettled(msg.sender, msg.value, msg.value);
    }

    /// Read-only check for your runtime engine to verify a user has paid
    function checkCreditBalance(address user) external view returns (uint256) {
        return userRegistry[user].balanceCredits;
    }
}

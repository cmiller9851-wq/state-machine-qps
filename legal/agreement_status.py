"""
Legal & Compliance Framework for Fintech State Machine
Provides agreement status tracking, audit trails, and confidentiality management.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
import json

# =====================================================
# Agreement Status Lifecycle
# =====================================================

class AgreementStatus(Enum):
    """
    Clear status indicators for agreement lifecycle.
    Only mark as LEGALLY_EXECUTED when TRUE (all parties signed).
    """
    DRAFT_INTERNAL = "Internal working draft - not shared"
    PROPOSAL_OUTREACH = "Proposal sent to partner for review"
    UNDER_NEGOTIATION = "Active discussions with partner"
    LEGALLY_EXECUTED = "Signed/agreed by all parties"
    ARCHIVED = "Historical record"


# =====================================================
# Confidentiality Classification
# =====================================================

class ConfidentialityLevel(Enum):
    """Confidentiality classifications for all generated documents."""
    CONFIDENTIAL_INTERNAL = "CONFIDENTIAL - INTERNAL PROPOSAL - NOT A BINDING AGREEMENT"
    CONFIDENTIAL_PARTNER = "CONFIDENTIAL - PARTNER REVIEW - UNDER NEGOTIATION"
    CONFIDENTIAL_EXECUTED = "CONFIDENTIAL - LEGALLY EXECUTED AGREEMENT"
    PUBLIC = "Public Document"


# =====================================================
# Audit Trail Entry
# =====================================================

class AuditTrailEntry:
    """
    Represents a single event in the agreement audit trail.
    Provides immutable timestamp, actor attribution, and reason.
    """
    
    def __init__(
        self,
        status_change: str,
        actor: str,
        note: str,
        timestamp: Optional[str] = None
    ):
        self.status_change = status_change
        self.actor = actor
        self.note = note
        self.timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status_change": self.status_change,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "note": self.note
        }
    
    def __repr__(self) -> str:
        return (
            f"AuditTrailEntry("
            f"status={self.status_change}, "
            f"actor={self.actor}, "
            f"time={self.timestamp})"
        )


# =====================================================
# Agreement Audit Log
# =====================================================

class AgreementAuditLog:
    """
    Immutable audit trail for agreement lifecycle events.
    Enables compliance verification and historical tracking.
    """
    
    def __init__(self, agreement_id: str, version: str = "1.0"):
        self.agreement_id = agreement_id
        self.version = version
        self.entries: list[AuditTrailEntry] = []
    
    def record_event(
        self,
        status_change: str,
        actor: str,
        note: str
    ) -> AuditTrailEntry:
        """
        Record a new event in the audit trail.
        Returns the created entry for confirmation.
        """
        entry = AuditTrailEntry(
            status_change=status_change,
            actor=actor,
            note=note
        )
        self.entries.append(entry)
        return entry
    
    def get_current_status(self) -> Optional[str]:
        """Return the most recent status change, or None if empty."""
        if not self.entries:
            return None
        return self.entries[-1].status_change
    
    def to_json(self) -> str:
        """Serialize audit log to JSON."""
        return json.dumps({
            "agreement_id": self.agreement_id,
            "version": self.version,
            "entries": [entry.to_dict() for entry in self.entries]
        }, indent=2)
    
    def __repr__(self) -> str:
        return (
            f"AgreementAuditLog("
            f"id={self.agreement_id}, "
            f"entries={len(self.entries)})"
        )


# =====================================================
# Agreement Document Manager
# =====================================================

class AgreementDocumentManager:
    """
    Manages agreement metadata, confidentiality, and status.
    Enforces watermarks and prevents sharing of unexecuted drafts.
    """
    
    def __init__(
        self,
        agreement_id: str,
        partner_name: str,
        status: AgreementStatus = AgreementStatus.DRAFT_INTERNAL,
        confidentiality: ConfidentialityLevel = ConfidentialityLevel.CONFIDENTIAL_INTERNAL
    ):
        self.agreement_id = agreement_id
        self.partner_name = partner_name
        self.status = status
        self.confidentiality = confidentiality
        self.audit_log = AgreementAuditLog(agreement_id)
        
        # Record initial creation
        self.audit_log.record_event(
            status_change=status.name,
            actor="system",
            note=f"Agreement created for {partner_name}"
        )
    
    def can_be_shared(self) -> bool:
        """
        Enforce sharing restrictions:
        - DRAFT_INTERNAL: Cannot be shared
        - PROPOSAL_OUTREACH+: Can be shared
        """
        return self.status != AgreementStatus.DRAFT_INTERNAL
    
    def get_watermark(self) -> str:
        """Return appropriate watermark based on confidentiality level."""
        return self.confidentiality.value
    
    def update_status(
        self,
        new_status: AgreementStatus,
        actor: str,
        note: str
    ) -> bool:
        """
        Update agreement status with audit trail.
        Returns True if successful, False if invalid transition.
        """
        # Validate status transition
        valid_transitions = {
            AgreementStatus.DRAFT_INTERNAL: [
                AgreementStatus.PROPOSAL_OUTREACH,
                AgreementStatus.ARCHIVED
            ],
            AgreementStatus.PROPOSAL_OUTREACH: [
                AgreementStatus.UNDER_NEGOTIATION,
                AgreementStatus.DRAFT_INTERNAL,
                AgreementStatus.ARCHIVED
            ],
            AgreementStatus.UNDER_NEGOTIATION: [
                AgreementStatus.LEGALLY_EXECUTED,
                AgreementStatus.PROPOSAL_OUTREACH,
                AgreementStatus.ARCHIVED
            ],
            AgreementStatus.LEGALLY_EXECUTED: [
                AgreementStatus.ARCHIVED
            ],
            AgreementStatus.ARCHIVED: []
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            return False
        
        # Update status and log event
        self.status = new_status
        self.audit_log.record_event(
            status_change=new_status.name,
            actor=actor,
            note=note
        )
        
        # Update confidentiality level based on status
        if new_status == AgreementStatus.LEGALLY_EXECUTED:
            self.confidentiality = ConfidentialityLevel.CONFIDENTIAL_EXECUTED
        elif new_status == AgreementStatus.UNDER_NEGOTIATION:
            self.confidentiality = ConfidentialityLevel.CONFIDENTIAL_PARTNER
        
        return True
    
    def is_executable(self) -> bool:
        """
        Check if agreement is in a state that can be referenced for settlement.
        Only LEGALLY_EXECUTED agreements can proceed to settlement.
        """
        return self.status == AgreementStatus.LEGALLY_EXECUTED
    
    def generate_header(self) -> str:
        """Generate document header with watermark and metadata."""
        return f"""
{'='*70}
{self.get_watermark()}
{'='*70}

Agreement ID: {self.agreement_id}
Partner: {self.partner_name}
Status: {self.status.value}
Generated: {datetime.utcnow().isoformat()}Z

{'='*70}
"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize agreement metadata."""
        return {
            "agreement_id": self.agreement_id,
            "partner_name": self.partner_name,
            "status": self.status.name,
            "confidentiality": self.confidentiality.name,
            "can_be_shared": self.can_be_shared(),
            "is_executable": self.is_executable(),
            "watermark": self.get_watermark(),
            "audit_log": json.loads(self.audit_log.to_json())
        }


# =====================================================
# Example Usage & Testing
# =====================================================

if __name__ == "__main__":
    # Create a new agreement
    agreement = AgreementDocumentManager(
        agreement_id="FSM-2026-PARTNER-001",
        partner_name="Strategic Finance Partner",
        status=AgreementStatus.DRAFT_INTERNAL
    )
    
    print(agreement.generate_header())
    print(f"Initial Status: {agreement.status.value}")
    print(f"Can Share: {agreement.can_be_shared()}")
    print(f"Can Execute Settlement: {agreement.is_executable()}")
    print()
    
    # Simulate lifecycle
    print("--- Scenario 1: Proposal Outreach ---")
    agreement.update_status(
        AgreementStatus.PROPOSAL_OUTREACH,
        actor="@vccmac",
        note="Partner review copy prepared"
    )
    print(f"Status: {agreement.status.value}")
    print(f"Can Share: {agreement.can_be_shared()}")
    print(f"Can Execute Settlement: {agreement.is_executable()}")
    print(f"Watermark: {agreement.get_watermark()}")
    print()
    
    print("--- Scenario 2: Under Negotiation ---")
    agreement.update_status(
        AgreementStatus.UNDER_NEGOTIATION,
        actor="@vccmac",
        note="Partner provided feedback; discussions ongoing"
    )
    print(f"Status: {agreement.status.value}")
    print()
    
    print("--- Scenario 3: Legally Executed ---")
    agreement.update_status(
        AgreementStatus.LEGALLY_EXECUTED,
        actor="@legal-team",
        note="Agreement signed by all parties; executed copy filed"
    )
    print(f"Status: {agreement.status.value}")
    print(f"Can Execute Settlement: {agreement.is_executable()}")
    print(f"Watermark: {agreement.get_watermark()}")
    print()
    
    print("--- Audit Trail ---")
    print(agreement.audit_log.to_json())
    print()
    
    print("--- Metadata Export ---")
    import pprint
    pprint.pprint(agreement.to_dict())

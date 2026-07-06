# CONFIDENTIAL - INTERNAL PROPOSAL - NOT A BINDING AGREEMENT

## Agreement Template

**This document is a template for tracking legal agreements related to the Fintech State Machine project.**

---

### Document Header

```
======================================================================
CONFIDENTIAL - [STATUS] - [CONFIDENTIALITY_LEVEL]
======================================================================

Agreement ID: [AGREEMENT_ID]
Partner: [PARTNER_NAME]
Status: [DRAFT_INTERNAL | PROPOSAL_OUTREACH | UNDER_NEGOTIATION | LEGALLY_EXECUTED | ARCHIVED]
Generated: [ISO_8601_TIMESTAMP]Z

======================================================================
```

---

### Agreement Lifecycle

Each agreement follows a strict lifecycle with clear status indicators:

| Status | Meaning | Shareable | Notes |
|--------|---------|-----------|-------|
| **DRAFT_INTERNAL** | Internal working draft | ❌ No | Not shared externally; internal review only |
| **PROPOSAL_OUTREACH** | Sent to partner | ✅ Yes | Ready for partner review |
| **UNDER_NEGOTIATION** | Active discussions | ✅ Yes | Awaiting partner feedback/signature |
| **LEGALLY_EXECUTED** | Signed by all parties | ✅ Yes | Binding agreement; final copy filed |
| **ARCHIVED** | Historical record | ✅ Yes | Concluded or superseded agreements |

---

### Watermark Requirements

- **DRAFT_INTERNAL**: `CONFIDENTIAL - INTERNAL PROPOSAL - NOT A BINDING AGREEMENT`
- **PROPOSAL_OUTREACH**: `CONFIDENTIAL - PARTNER REVIEW - UNDER NEGOTIATION`
- **UNDER_NEGOTIATION**: `CONFIDENTIAL - PARTNER REVIEW - UNDER NEGOTIATION`
- **LEGALLY_EXECUTED**: `CONFIDENTIAL - LEGALLY EXECUTED AGREEMENT`
- **ARCHIVED**: `CONFIDENTIAL - HISTORICAL RECORD`

---

### Audit Trail Format

Every status change is recorded with:

```json
{
  "agreement_id": "FSM-2026-PARTNER-001",
  "version": "1.0",
  "entries": [
    {
      "status_change": "DRAFT_INTERNAL",
      "timestamp": "2026-06-13T22:30:00Z",
      "actor": "@vccmac",
      "note": "Internal working document - not shared externally"
    },
    {
      "status_change": "PROPOSAL_OUTREACH",
      "timestamp": "2026-06-15T10:45:00Z",
      "actor": "@vccmac",
      "note": "Partner review copy prepared and sent"
    },
    {
      "status_change": "UNDER_NEGOTIATION",
      "timestamp": "2026-06-20T14:20:00Z",
      "actor": "@vccmac",
      "note": "Partner provided feedback; discussions ongoing"
    },
    {
      "status_change": "LEGALLY_EXECUTED",
      "timestamp": "2026-07-01T16:00:00Z",
      "actor": "@legal-team",
      "note": "Agreement signed by all parties; executed copy filed"
    }
  ]
}
```

---

### Security & Compliance Rules

1. **Internal Draft Protection**
   - Draft agreements cannot be shared externally
   - System enforces sharing restrictions programmatically
   - Metadata clearly indicates non-binding status

2. **Watermark Enforcement**
   - All generated documents include mandatory watermark
   - Watermark matches current agreement status
   - Watermark visible in document header and footer

3. **Audit Trail Immutability**
   - All status changes logged with timestamp & actor
   - Entries cannot be deleted or modified (append-only)
   - Enables regulatory compliance verification

4. **Actor Attribution**
   - Every change requires actor identification (GitHub username)
   - Enables accountability and change tracking
   - Supports compliance audits

---

### Legal Disclaimers

⚠️ **Important:** This framework is for tracking and managing agreements only. It does not:
- Replace actual legal counsel
- Create binding obligations automatically
- Bypass required signature/notarization procedures
- Override jurisdiction-specific legal requirements

For actual binding agreements, ensure:
- Review by qualified legal counsel in relevant jurisdiction(s)
- Proper execution (signature/seal) by authorized representatives
- Compliance with applicable contract law
- Proper archival and retention per regulatory requirements

---

### Integration with Fintech State Machine

This compliance framework integrates with the Fintech State Machine to track:
- Partner service agreements
- Data processing agreements (DPA)
- Terms of service amendments
- Integration contracts
- Settlement agreement terms

All agreements are stored with their full audit trail in `legal/audit_trails/` directory.

---

### Usage Example

```python
from legal.agreement_status import (
    AgreementDocumentManager,
    AgreementStatus
)

# Create a new agreement
agreement = AgreementDocumentManager(
    agreement_id="FSM-2026-BAANX-001",
    partner_name="Baanx Treasury Services",
    status=AgreementStatus.DRAFT_INTERNAL
)

# Validate internal draft
print(agreement.can_be_shared())  # False - cannot share draft
print(agreement.get_watermark())  # "CONFIDENTIAL - INTERNAL PROPOSAL..."

# Move to proposal outreach
agreement.update_status(
    AgreementStatus.PROPOSAL_OUTREACH,
    actor="@vccmac",
    note="Ready for partner review"
)

print(agreement.can_be_shared())  # True - can now share

# Generate audit trail
print(agreement.audit_log.to_json())
```

---

**Last Updated:** 2026-07-06  
**Maintained By:** Fintech State Machine Compliance Team  
**Classification:** Internal Governance Document

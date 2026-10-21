# InvoiceFlow integration contract (v0.2 draft)

This is a **design contract**, not a deployed API or working Gmail/Canva/Notion connection. Implementers must supply provider-specific OAuth and securely isolated storage.

## Boundary

The core application stores invoice data and generates local artifacts. Provider adapters may:
- `render_invoice(invoice, template_id)` — produce a new branded artifact without overwriting any master.
- `create_email_draft(recipient, subject, artifact_ref)` — create **unsent** content only.
- `save_ledger(invoice, lifecycle_event)` — record an append-only event.
- `verify_payment(invoice_id, evidence_ref)` — require user attestation or supported financial evidence.

No `send_email` function is included in the default adapter contract. Sending, when added, requires an explicit, narrowly scoped user action and an audit log.

## Invoice lifecycle

`DRAFT -> READY -> SENT -> PARTIALLY_PAID -> PAID`; cancellation is separately recorded. Do not imply a draft has been delivered. Only record `PAID` after full receipt is confirmed. Preserve the original invoice ID when producing a PAID counterpart.

## Data isolation

Every production record must be scoped to an authenticated `tenant_id`. Validate ownership for every read/write. Enforce uniqueness of invoice numbers **within a tenant**, not globally. Never accept tenant identity from an unverified client-provided header.

## Minimum release gates

- Provider OAuth using minimum required scopes, state/PKCE and encrypted token storage
- Per-tenant access checks and tested cross-tenant denials
- Encryption in transit and at rest, secure deletion/retention policy
- Unsent email drafts by default, explicit send authorization and idempotent sends
- Webhook signature validation, replay resistance, and audit trail
- No tax-rate assumptions; jurisdiction-specific compliance review
- Automated tests, vulnerability scanning, and deployment rollback
- User-accessible data export and account removal

## Provider status

| Provider | Contract planned | OAuth implemented | Tested |
|---|---|---|---|
| Canva | yes | no | no |
| Gmail | yes | no | no |
| Notion | yes | no | no |

Do not present provider connectors as enabled until live end-to-end tests pass.

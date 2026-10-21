"""Provider-neutral draft-first integration interfaces (no network side effects)."""
from dataclasses import dataclass
from typing import Protocol
from decimal import Decimal

@dataclass(frozen=True)
class Invoice:
    tenant_id: str
    invoice_id: str
    recipient: str
    currency: str
    amount: Decimal
    service: str

@dataclass(frozen=True)
class Artifact:
    invoice_id: str
    url: str
    version: str = "original"

@dataclass(frozen=True)
class Draft:
    provider_draft_id: str
    recipient: str
    invoice_id: str

class InvoiceRenderer(Protocol):
    def render(self, invoice: Invoice, *, paid: bool = False) -> Artifact: ...

class EmailDraftProvider(Protocol):
    def create_unsent_draft(self, invoice: Invoice, artifact: Artifact) -> Draft: ...

class Ledger(Protocol):
    def record(self, tenant_id: str, invoice_id: str, event: str, **details: str) -> None: ...

def prepare_unpaid(invoice: Invoice, renderer: InvoiceRenderer, email: EmailDraftProvider, ledger: Ledger):
    """Generate artifact and draft, never send. Validate before any provider operation."""
    if not invoice.tenant_id.strip() or not invoice.invoice_id.strip():
        raise ValueError("Tenant and invoice IDs required")
    if not invoice.recipient.strip() or "@" not in invoice.recipient:
        raise ValueError("Recipient address required")
    if not invoice.amount.is_finite() or invoice.amount <= 0:
        raise ValueError("Positive finite amount required")
    artifact = renderer.render(invoice, paid=False)
    if artifact.invoice_id != invoice.invoice_id:
        raise ValueError("Renderer returned wrong invoice")
    draft = email.create_unsent_draft(invoice, artifact)
    if draft.invoice_id != invoice.invoice_id or draft.recipient.lower() != invoice.recipient.lower():
        raise ValueError("Draft mismatch")
    ledger.record(invoice.tenant_id, invoice.invoice_id, "DRAFT_PREPARED", artifact=artifact.url, draft=draft.provider_draft_id)
    return artifact, draft

def prepare_paid(invoice: Invoice, *, confirmed: bool, payment_date: str, payment_method: str,
                 renderer: InvoiceRenderer, ledger: Ledger):
    """Attestation gate; no payment API or external email side effects."""
    from datetime import date
    if not confirmed:
        raise PermissionError("Payment must be confirmed before creating PAID invoice")
    date.fromisoformat(payment_date)
    if not payment_method.strip():
        raise ValueError("Payment method required")
    artifact = renderer.render(invoice, paid=True)
    if artifact.invoice_id != invoice.invoice_id or artifact.version != "paid":
        raise ValueError("Paid renderer must preserve invoice ID and label version paid")
    ledger.record(invoice.tenant_id, invoice.invoice_id, "PAID_CONFIRMED",
                  payment_date=payment_date, payment_method=payment_method, artifact=artifact.url)
    return artifact

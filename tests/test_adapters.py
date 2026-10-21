import sys, unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/invoiceflow/skills/invoice-workflow/scripts"))
from adapters import Invoice, Artifact, Draft, prepare_unpaid, prepare_paid

class FakeRenderer:
    def render(self, invoice, *, paid=False):
        return Artifact(invoice.invoice_id,"https://example.org/invoice", "paid" if paid else "original")
class FakeEmail:
    def __init__(self): self.count=0
    def create_unsent_draft(self, invoice, artifact):
        self.count+=1
        return Draft("draft123",invoice.recipient,invoice.invoice_id)
class FakeLedger:
    def __init__(self): self.events=[]
    def record(self, tenant_id, invoice_id, event, **details): self.events.append((tenant_id,invoice_id,event,details))
class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.i=Invoice("tenantA","INV-1","test@example.org","USD",Decimal("50"),"Session")
        self.r=FakeRenderer(); self.e=FakeEmail(); self.l=FakeLedger()
    def test_draft_only(self):
        a,d=prepare_unpaid(self.i,self.r,self.e,self.l)
        self.assertEqual(d.provider_draft_id,"draft123")
        self.assertEqual(self.l.events[0][2],"DRAFT_PREPARED")
    def test_paid_requires_confirmation(self):
        with self.assertRaises(PermissionError):
            prepare_paid(self.i,confirmed=False,payment_date="2026-10-21",payment_method="transfer",renderer=self.r,ledger=self.l)
        self.assertEqual(self.l.events,[])
    def test_paid_records_attestation(self):
        a=prepare_paid(self.i,confirmed=True,payment_date="2026-10-21",payment_method="transfer",renderer=self.r,ledger=self.l)
        self.assertEqual(a.version,"paid")
    def test_invalid_amount_prevents_provider(self):
        from dataclasses import replace
        with self.assertRaises(ValueError):
            prepare_unpaid(replace(self.i,amount=Decimal("NaN")),self.r,self.e,self.l)
        self.assertEqual(self.e.count,0)
if __name__=="__main__":unittest.main()

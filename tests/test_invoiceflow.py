import subprocess, sys, tempfile, unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[1] / "plugins/invoiceflow/skills/invoice-workflow/scripts/invoiceflow.py"

class InvoiceFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "db.sqlite")
        self.out = Path(self.tmp.name) / "output"

    def cli(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(CLI), "--db", self.db, "--out", str(self.out), *args], capture_output=True, text=True)
        self.assertEqual(p.returncode == 0, ok, p.stderr)
        return p

    def create(self, amount="50", number="INV-1"):
        return self.cli("create", "--id", number, "--customer", "Demo & Co", "--email", "demo@example.org", "--service", "Piano <service>", "--service-date", "2026-10-20", "--issue-date", "2026-10-21", "--amount", amount)

    def test_unpaid_generates_unsent_draft(self):
        self.create()
        self.assertTrue((self.out / "INV-1-UNSENT.eml").exists())
        self.assertIn("Demo &amp; Co", (self.out / "INV-1.html").read_text())

    def test_duplicate_invoice_blocked(self):
        self.create()
        self.cli("create", "--id", "INV-1", "--customer", "Someone", "--email", "demo@example.org", "--service", "service", "--service-date", "2026-10-20", "--issue-date", "2026-10-21", "--amount", "50", ok=False)

    def test_bad_amounts_rejected(self):
        for amount in ["0", "-3", "1.999", "NaN", "Infinity"]:
            with self.subTest(amount=amount):
                self.cli("create", "--id", "INV-BAD", "--customer", "X", "--email", "demo@example.org", "--service", "service", "--service-date", "2026-10-20", "--issue-date", "2026-10-21", "--amount", amount, ok=False)

    def test_paid_copy_preserves_original(self):
        self.create()
        original = (self.out / "INV-1.html").read_bytes()
        self.cli("confirm-payment", "--id", "INV-1", "--date", "2026-10-21", "--method", "bank-transfer")
        self.assertEqual(original, (self.out / "INV-1.html").read_bytes())
        self.assertIn("PAID IN FULL", (self.out / "INV-1-PAID.html").read_text())

    def test_cannot_mark_paid_twice(self):
        self.create()
        self.cli("confirm-payment", "--id", "INV-1", "--date", "2026-10-21", "--method", "bank-transfer")
        self.cli("confirm-payment", "--id", "INV-1", "--date", "2026-10-21", "--method", "bank-transfer", ok=False)

if __name__ == "__main__":
    unittest.main()

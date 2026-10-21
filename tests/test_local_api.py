import importlib.util, json, unittest
from pathlib import Path
from unittest.mock import MagicMock

P=Path(__file__).resolve().parents[1]/"plugins/invoiceflow/skills/invoice-workflow/scripts/local_api.py"
spec=importlib.util.spec_from_file_location("invoiceflow_local_api",P)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class LocalAPITests(unittest.TestCase):
    def fake(self,path,method):
        obj=object.__new__(module.Handler)
        obj.path=path
        obj.send_response=MagicMock()
        obj.send_header=MagicMock()
        obj.end_headers=MagicMock()
        from io import BytesIO
        obj.wfile=BytesIO()
        getattr(obj,method)()
        return obj,json.loads(obj.wfile.getvalue())

    def test_health(self):
        h,p=self.fake("/healthz","do_GET")
        self.assertEqual(p,{"status":"ok"})
        h.send_response.assert_called_once_with(200)

    def test_version_contains_no_customer_data(self):
        h,p=self.fake("/version","do_GET")
        self.assertEqual(p["mode"],"local-development")
        self.assertEqual(p["name"],"InvoiceFlow")

    def test_404(self):
        h,p=self.fake("/customer-records","do_GET")
        h.send_response.assert_called_once_with(404)

    def test_http_mutation_disabled(self):
        h,p=self.fake("/invoices","do_POST")
        h.send_response.assert_called_once_with(405)

if __name__=="__main__":unittest.main()

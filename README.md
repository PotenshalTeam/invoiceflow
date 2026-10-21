# InvoiceFlow — v0.1.0 prototype

Open-source **draft-first** invoice workflow for ChatGPT and a local Python CLI.

**Status:** GitHub source is public. This repository is **not** a deployed multi-user service or an approved ChatGPT Plugin Directory listing. Canva, Gmail, and Notion hosted adapters are not implemented.

## Principles

- Never send unpaid invoices automatically. Prepare drafts for user approval.
- Confirm payment before creating a separately labeled PAID invoice.
- Keep the original invoice and number intact.
- Keep API keys, customer information and confidential finance data out of public source.
- Validate local tax and invoicing regulations separately.

## Local usage

```bash
python3 plugins/invoiceflow/skills/invoice-workflow/scripts/invoiceflow.py --db /tmp/invoiceflow.db --out /tmp/invoices create --id DEMO-001 --customer "Demo Customer" --email example@example.com --service "Piano session" --service-date 2026-10-20 --issue-date 2026-10-21 --amount 50.00 --currency USD
python3 plugins/invoiceflow/skills/invoice-workflow/scripts/invoiceflow.py --db /tmp/invoiceflow.db --out /tmp/invoices confirm-payment --id DEMO-001 --date 2026-10-21 --method bank-transfer
```

The local engine generates HTML and unsent .eml; it does not send email or claim PDF output.

## Plugin structure

- `plugins/invoiceflow/plugin.json`: draft plugin metadata
- `plugins/invoiceflow/skills/invoice-workflow/SKILL.md`: workflow instructions
- `plugins/invoiceflow/skills/invoice-workflow/scripts/invoiceflow.py`: local demo
- `.agents/plugins/marketplace.json`: repository marketplace metadata

## Next

Public plugin submission needs validation and OpenAI review. Connected use by unrelated users requires secure OAuth, tenant isolation, audited send approval and integrated PDF export. Consult https://developers.openai.com/plugins/deploy/submission.

MIT licensed.
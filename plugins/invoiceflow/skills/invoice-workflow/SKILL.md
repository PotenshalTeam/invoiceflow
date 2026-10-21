---
name: invoice-workflow
description: Create and track draft-first invoices, client email drafts, and paid copies after payment confirmation. Use for preparing invoices, sending invoice approval workflows, paid receipts, payment tracking, and invoicing setup with optional external integrations.
---

# Invoice Workflow

## Safety rules
- Never send an unpaid invoice automatically. Prepare an unsent email draft and wait for explicit permission to send.
- Never mark an invoice as PAID because its design is approved. Require verified payment or explicit confirmation.
- Preserve the original invoice and its identifier when creating a separately labeled PAID copy.
- Validate billing party, customer, currency, due date, amount, and tax obligations without inventing information.
- Keep sensitive customer data and secrets out of public repositories.

## Procedure
1. Establish business identity, logo/template, currency, numbering system, terms, compliance requirements, and approved output location.
2. Confirm client and service details, then create and save an invoice. If Canva is connected, clone rather than overwrite the master design.
3. Create a Gmail draft if connected; otherwise generate an unsent .eml file. Provide invoice and draft links. Do not send by default.
4. Record Draft, Sent and Paid as distinct states in the ledger. Change Sent only after confirmed delivery.
5. On payment confirmation, retain the original and create a PAID counterpart with the original ID, verified payment amount and date and zero outstanding balance, if fully paid.
6. Update records and supply completed document links; never claim PDF export or email delivery unless verified.

## Local example
Run `python3 plugins/invoiceflow/skills/invoice-workflow/scripts/invoiceflow.py --help`. It uses SQLite and local HTML/.eml, without sending messages.

## Hosted integrations
Canva, Gmail and Notion API adapters, OAuth, multi-tenant isolation and hosted MCP integration are not implemented. These require development and explicit permissions before public deployment.

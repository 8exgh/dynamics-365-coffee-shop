# Coffee shop walkthrough

Use the practice companion to explore each workflow immediately. Use the corresponding native steps inside the dedicated Business Central coffee company to exercise Microsoft’s own posting, approvals, analysis, and reporting features.

## 1. A regular’s morning order

In the companion, open Counter sales, select Maya, add a flat white and croissant, choose cash or card, and complete the sale. Inspect the order, ingredient quantities, loyalty points, and Finance & close. No real payment is collected.

In Business Central, open Sales Invoices, create an invoice for `COF-MAYA`, use location `CAFE`, and add two `COF-FLAT` items. Use Preview Posting, then Post. Inspect Posted Sales Invoices, Customer Ledger Entries, Item Ledger Entries, Value Entries, G/L Entries, and Coffee Loyalty Entries. Prepared drink stock comes from assembly orders; selling a finished drink does not assemble it automatically in this configuration.

## 2. Catering quote to cash

In the companion, create a catering quote for North Studio or use the seeded quote. Accept it, invoice it, and record payment. A stock shortage blocks invoicing without partially changing inventory or the ledger.

In Business Central, open the seeded North Studio Sales Quote. Review quantities and prices, use Make Order, and set shipment details on the sales order. Preview and post Ship and Invoice. Apply the receipt through the `COFFEE` / `DAILY` general journal using Customer as Account Type and the invoice as Applies-to Doc. No. Inspect the applied customer entries.

## 3. Replenishment and approvals

In the companion, order 20,000 g espresso beans. The $600 order requires approval. Approve, receive/invoice, and pay the supplier. Verify inventory value and supplier balances at each stage.

In Business Central, create a Purchase Order for `COF-ROAST` and receive/invoice beans at `CAFE`. Inspect posted purchase receipts/invoices and the vendor ledger. Record a supplier payment with Vendor as Account Type, Bank Account `COF-BANK` as the balancing account, and the invoice application.

For native approvals, configure actual users in Approval User Setup, define approval limits and approvers, enable a purchase approval workflow from the standard template, then request approval on a new purchase order. Open Requests to Approve as the designated approver. This identity-dependent approval workflow is not automatically assigned to arbitrary tenant users.

## 4. Assembly recipes and waste

In the companion, inspect Inventory & recipes. Sell an oat latte and compare bean, oat milk, and cup quantities. Log waste with a reason and review the waste expense journal.

In Business Central, open `COF-FLAT` and its Assembly BOM. Create an Assembly Order for 10 pieces at `CAFE`, review automatically generated component lines, and post it. Inspect component consumption and output item entries. Use Item Journals, template `COFFEE`, batch `WASTE`, with a Negative Adjustment for spoiled milk. Preview and post. Review the inventory adjustment expense and stock valuation.

## 5. Transfers, replenishment planning, and stock count

In Business Central, use Transfer Orders to move retail bags between `CAFE` and `STORE`. Configure an in-transit location or direct transfer posting appropriate to the environment before posting shipment and receipt. Inspect both location balances.

Use a Stockkeeping Unit for each item/location when extending replenishment by location. Review the fixed reorder quantity settings and use a Requisition Worksheet to calculate a plan and create purchase orders. Set up a physical inventory journal template/batch, calculate inventory, enter counted quantities, and post a reviewed adjustment. These standard planning and counting screens are a guided extension of the configured dataset, not steps automatically posted by the demo runner.

## 6. Returns and customer care

In the companion, refund a paid drink order and verify that ingredients remain consumed. A refund containing only unopened retail bags can return those bags to stock. Refunds reverse earned loyalty points. Add and resolve a customer care issue with a resolution.

In Business Central, use the posted retail invoice and create a corrective sales credit memo through the standard document actions so item application and cost reversal are retained. Post the credit, record a customer refund, and apply it to the credit memo. Inspect the Coffee Loyalty Entries reversal. Use customer/Contact information and interaction records for relationship history. The companion’s issue tracker is separate from Microsoft’s Customer Service product.

## 7. Finance, cash, and bank reconciliation

In the companion, inspect every account in the trial balance, export CSV, count the till, and close the day. A difference posts to Cash over / short. The closing date uses America/Edmonton by default. Counter sales and cash refunds stop for that date; existing catering receivables and purchasing can still be processed.

In Business Central, drill from the C-prefixed chart of accounts into G/L entries. Inspect bank account `COF-BANK` and its posted supplier payment. Use Bank Account Reconciliation with a demonstration statement, match its lines, review the difference, and post the reconciliation. Use Financial Reports and analysis mode to review revenue, cost, balance sheet, and cash balances.

## 8. Dimensions, analysis, and permissions

Open Dimensions and review `COF-SHOP`. Inspect the default value on Maya and its propagation to sales documents and ledger entries. Add additional location/channel dimensions as the shop grows. Use analysis mode and filters to compare the relevant accounts, customers, dates, and dimensions.

Assign employee-specific standard permission sets plus `COFFEE OPERATIONS`. Test a counter user’s allowed activities separately from purchasing and accounting. Enable Change Log Setup on relevant setup/master tables when a native configuration audit is needed. Standard approval routing, change logging, and permissions depend on the actual environment and its users; the initializer does not impersonate or create staff identities.

## 9. Real API integration

Configure the online connection, open Business Central in the companion, select a record type, and load records. Confirm the company and displayed data match the native client. If writes are enabled, create one real draft from an actual customer and item, then locate it in Sales Orders. The draft’s external document number is the request reference. Review and post only in the native client.

The native loyalty API provides read-only customer loyalty information. Token acquisition, authorization, API errors, and native posting failures must be verified against the actual sandbox after its credentials are supplied.

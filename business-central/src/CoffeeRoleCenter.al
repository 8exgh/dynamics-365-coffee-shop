page 50103 "Coffee Shop Role Center"
{
    PageType = RoleCenter;
    Caption = 'Coffee Shop';
    layout
    {
        area(RoleCenter)
        {
            part(Headline; "Headline RC Business Manager") { ApplicationArea = All; }
            part(Activities; "Coffee Activities") { ApplicationArea = All; }
        }
    }
    actions
    {
        area(Sections)
        {
            group(Coffee)
            {
                Caption = 'Coffee Shop';
                action(Setup) { Caption = 'Coffee Shop Setup'; ApplicationArea = All; RunObject = page "Coffee Shop Setup"; ToolTip = 'Open coffee shop configuration and demo workflows.'; }
                action(Menu) { Caption = 'Coffee Menu'; ApplicationArea = All; RunObject = page "Coffee Menu"; ToolTip = 'Review coffee menu prices and assembly recipes.'; }
                action(Loyalty) { Caption = 'Loyalty Entries'; ApplicationArea = All; RunObject = page "Coffee Loyalty Entries"; ToolTip = 'Review points from native posted sales documents.'; }
                action(Customers) { Caption = 'Customers'; ApplicationArea = All; RunObject = page "Customer List"; ToolTip = 'Manage regulars and catering accounts.'; }
                action(Contacts) { Caption = 'Contacts'; ApplicationArea = All; RunObject = page "Contact List"; ToolTip = 'Manage relationships with coffee customers and suppliers.'; }
            }
            group(Sales)
            {
                Caption = 'Sales';
                action(Quotes) { Caption = 'Sales Quotes'; ApplicationArea = All; RunObject = page "Sales Quotes"; ToolTip = 'Prepare catering quotes.'; }
                action(Orders) { Caption = 'Sales Orders'; ApplicationArea = All; RunObject = page "Sales Order List"; ToolTip = 'Fulfil coffee and catering orders.'; }
                action(Invoices) { Caption = 'Sales Invoices'; ApplicationArea = All; RunObject = page "Sales Invoice List"; ToolTip = 'Create counter invoices.'; }
                action(PostedInvoices) { Caption = 'Posted Sales Invoices'; ApplicationArea = All; RunObject = page "Posted Sales Invoices"; ToolTip = 'Review posted sales and create corrective credit memos.'; }
                action(CreditMemos) { Caption = 'Sales Credit Memos'; ApplicationArea = All; RunObject = page "Sales Credit Memos"; ToolTip = 'Process returns and credits.'; }
            }
            group(Supply)
            {
                Caption = 'Supply & Inventory';
                action(Items) { Caption = 'Items'; ApplicationArea = All; RunObject = page "Item List"; ToolTip = 'Manage ingredients and finished products.'; }
                action(Assembly) { Caption = 'Assembly Orders'; ApplicationArea = All; RunObject = page "Assembly Orders"; ToolTip = 'Prepare drinks and consume recipe components.'; }
                action(Purchases) { Caption = 'Purchase Orders'; ApplicationArea = All; RunObject = page "Purchase Order List"; ToolTip = 'Replenish coffee ingredients.'; }
                action(Vendors) { Caption = 'Vendors'; ApplicationArea = All; RunObject = page "Vendor List"; ToolTip = 'Manage roasters, dairies, and bakeries.'; }
                action(ItemJournals) { Caption = 'Item Journals'; ApplicationArea = All; RunObject = page "Item Journal"; ToolTip = 'Record waste and inventory corrections.'; }
                action(Transfers) { Caption = 'Transfer Orders'; ApplicationArea = All; RunObject = page "Transfer Orders"; ToolTip = 'Move inventory between the shop and storage.'; }
            }
            group(Finance)
            {
                Caption = 'Finance & Control';
                action(Accounts) { Caption = 'Chart of Accounts'; ApplicationArea = All; RunObject = page "Chart of Accounts"; ToolTip = 'Review financial balances and drill into ledger entries.'; }
                action(Journals) { Caption = 'General Journals'; ApplicationArea = All; RunObject = page "General Journal"; ToolTip = 'Post receipts, payments, and cash adjustments.'; }
                action(Banks) { Caption = 'Bank Accounts'; ApplicationArea = All; RunObject = page "Bank Account List"; ToolTip = 'Manage and reconcile bank accounts.'; }
                action(Approvals) { Caption = 'Requests to Approve'; ApplicationArea = All; RunObject = page "Requests to Approve"; ToolTip = 'Review purchase and sales approvals.'; }
                action(Dimensions) { Caption = 'Dimensions'; ApplicationArea = All; RunObject = page Dimensions; ToolTip = 'Analyse revenue and cost by shop and channel.'; }
            }
        }
    }
}

profile "COFFEE SHOP"
{
    Caption = 'Coffee Shop Manager';
    RoleCenter = "Coffee Shop Role Center";
    ProfileDescription = 'Coffee shop sales, purchasing, recipes, loyalty, and finance.';
}

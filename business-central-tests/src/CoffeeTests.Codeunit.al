codeunit 50150 "Coffee Integration Tests"
{
    Subtype = Test;
    TestPermissions = Disabled;

    [Test]
    [TransactionModel(TransactionModel::AutoRollback)]
    procedure SetupIsRepeatable()
    var
        Demo: Codeunit "Coffee Demo Setup";
        Item: Record Item;
        Customer: Record Customer;
        ItemCount: Integer;
        CustomerCount: Integer;
    begin
        Demo.Initialize();
        ItemCount := Item.Count(); CustomerCount := Customer.Count();
        Demo.Initialize();
        if Item.Count() <> ItemCount then Error('Setup duplicated items.');
        if Customer.Count() <> CustomerCount then Error('Setup duplicated customers.');
        Item.Get('COF-FLAT'); Item.CalcFields("Assembly BOM");
        if not Item."Assembly BOM" then Error('Flat white recipe is missing.');
    end;

    [Test]
    [TransactionModel(TransactionModel::AutoRollback)]
    procedure NativePostingBalancesInventoryFinanceAndLoyalty()
    var
        Demo: Codeunit "Coffee Demo Setup";
        Workflows: Codeunit "Coffee Demo Workflows";
        GL: Record "G/L Entry";
        Customer: Record Customer;
        Entry: Record "Coffee Loyalty Entry";
        SalesInvoice: Record "Sales Invoice Header";
        CreditMemo: Record "Sales Cr.Memo Header";
        PurchaseInvoice: Record "Purch. Inv. Header";
        Vendor: Record Vendor;
        Bank: Record "Bank Account";
        Balance: Decimal;
        EntryCount: Integer;
    begin
        Demo.Initialize(); Workflows.Exercise();
        AssertStock('COF-BEANS', 8.92); AssertStock('COF-MILK', 14.1);
        AssertStock('COF-OAT', 7.8); AssertStock('COF-CUP', 140);
        AssertStock('COF-FLAT', 28); AssertStock('COF-ESP', 20);
        AssertStock('COF-LATTE', 10); AssertStock('COF-BAG', 20);
        if GL.FindSet() then repeat Balance += GL.Amount; until GL.Next() = 0;
        if Balance <> 0 then Error('G/L is not balanced: %1.', Balance);
        Customer.Get('COF-MAYA'); Customer.CalcFields("Balance (LCY)");
        if Customer."Balance (LCY)" <> 0 then Error('Customer payment and refund are not fully applied.');
        if Customer."Coffee Loyalty Points" <> 10 then Error('Expected 10 net loyalty points, got %1.', Customer."Coffee Loyalty Points");
        SalesInvoice.SetRange("External Document No.", 'COFFEE-COUNTER-001');
        if SalesInvoice.Count() <> 1 then Error('Expected one coffee invoice.');
        CreditMemo.SetRange("External Document No.", 'COFFEE-RETURN-001');
        if CreditMemo.Count() <> 1 then Error('Expected one coffee credit memo.');
        PurchaseInvoice.SetRange("Vendor Invoice No.", 'COFFEE-DEMO-001');
        if PurchaseInvoice.Count() <> 1 then Error('Expected one purchase invoice.');
        Vendor.Get('COF-ROAST'); Vendor.CalcFields("Balance (LCY)");
        if Vendor."Balance (LCY)" <> 0 then Error('Supplier payment was not applied.');
        Bank.Get('COF-BANK'); Bank.CalcFields("Balance (LCY)");
        if Bank."Balance (LCY)" <= 0 then Error('Opening bank funding was not posted.');
        EntryCount := Entry.Count(); Workflows.Exercise();
        if Entry.Count() <> EntryCount then Error('Repeated workflow run duplicated loyalty entries.');
    end;

    [Test]
    [TransactionModel(TransactionModel::AutoRollback)]
    procedure LoyaltyIgnoresDuplicateDocuments()
    var
        Demo: Codeunit "Coffee Demo Setup";
        Loyalty: Codeunit "Coffee Loyalty Management";
        Customer: Record Customer;
        Before: Integer;
    begin
        Demo.Initialize(); Customer.Get('COF-MAYA'); Before := Customer."Coffee Loyalty Points";
        Loyalty.Award('COF-MAYA', 'TEST-INVOICE', Today(), 12.75, false);
        Loyalty.Award('COF-MAYA', 'TEST-INVOICE', Today(), 12.75, false);
        Loyalty.Award('COF-MAYA', 'TEST-CREDIT', Today(), -5.25, true);
        Customer.Get('COF-MAYA');
        if Customer."Coffee Loyalty Points" <> Before + 7 then Error('Loyalty rounding, reversal, or duplicate protection failed.');
    end;

    local procedure AssertStock(ItemNo: Code[20]; Expected: Decimal)
    var Item: Record Item;
    begin
        Item.Get(ItemNo); Item.SetRange("Location Filter", 'CAFE'); Item.CalcFields(Inventory);
        if Item.Inventory <> Expected then Error('%1 stock: expected %2, got %3.', ItemNo, Expected, Item.Inventory);
    end;
}

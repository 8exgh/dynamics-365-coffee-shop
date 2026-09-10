codeunit 50101 "Coffee Demo Workflows"
{
    trigger OnRun()
    begin
        Exercise();
    end;

    procedure Exercise()
    var
        Setup: Record "Coffee Shop Setup";
        Demo: Codeunit "Coffee Demo Setup";
    begin
        Demo.GuardDemoCompany();
        Setup.LockTable();
        Setup.Get(''); Setup.TestField("Demo Initialized", true);
        if Setup."Demo Workflows Run" then exit;
        FundBank();
        PurchaseIngredients();
        PayVendor();
        Assemble('COF-FLAT', 30);
        Assemble('COF-ESP', 20);
        Assemble('COF-LATTE', 10);
        SellAndCollect();
        CreateCateringQuote();
        PostWaste();
        Setup.Get(''); Setup."Demo Workflows Run" := true; Setup.Modify();
    end;

    local procedure FundBank()
    var
        Line: Record "Gen. Journal Line";
        Post: Codeunit "Gen. Jnl.-Post Line";
    begin
        Line.Init(); Line."Line No." := 10000; Line."Posting Date" := Today(); Line."Document No." := 'COFFEE-OPENING';
        Line."Source Code" := 'COFGEN'; Line.Validate("Account Type", Line."Account Type"::"Bank Account");
        Line.Validate("Account No.", 'COF-BANK'); Line.Validate("Bal. Account No.", 'C3000');
        Line.Validate(Amount, 1000); Post.RunWithCheck(Line);
    end;

    local procedure PayVendor()
    var
        Invoice: Record "Purch. Inv. Header";
        Line: Record "Gen. Journal Line";
        Post: Codeunit "Gen. Jnl.-Post Line";
    begin
        Invoice.SetRange("Vendor Invoice No.", 'COFFEE-DEMO-001'); Invoice.FindFirst(); Invoice.CalcFields("Amount Including VAT");
        Line.Init(); Line."Line No." := 10000; Line."Posting Date" := Today(); Line."Document No." := 'COFFEE-PAY-SUPPLIER';
        Line."Source Code" := 'COFGEN'; Line."Document Type" := Line."Document Type"::Payment;
        Line.Validate("Account Type", Line."Account Type"::Vendor); Line.Validate("Account No.", 'COF-ROAST');
        Line.Validate("Bal. Account Type", Line."Bal. Account Type"::"Bank Account"); Line.Validate("Bal. Account No.", 'COF-BANK');
        Line.Validate(Amount, Invoice."Amount Including VAT"); Line."Applies-to Doc. Type" := Line."Applies-to Doc. Type"::Invoice;
        Line.Validate("Applies-to Doc. No.", Invoice."No."); Post.RunWithCheck(Line);
    end;

    local procedure PurchaseIngredients()
    var
        Header: Record "Purchase Header";
        Post: Codeunit "Purch.-Post";
    begin
        Header.Init(); Header."Document Type" := Header."Document Type"::Order; Header.Insert(true);
        Header.Validate("Buy-from Vendor No.", 'COF-ROAST'); Header.Validate("Posting Date", Today());
        Header.Validate("Document Date", Today()); Header.Validate("Location Code", 'CAFE');
        Header."Vendor Invoice No." := 'COFFEE-DEMO-001'; Header.Modify(true);
        PurchaseLine(Header, 10000, 'COF-BEANS', 10, 30);
        PurchaseLine(Header, 20000, 'COF-MILK', 20, 2);
        PurchaseLine(Header, 30000, 'COF-OAT', 10, 3);
        PurchaseLine(Header, 40000, 'COF-CUP', 200, 0.18);
        PurchaseLine(Header, 50000, 'COF-CROIS', 50, 1.75);
        PurchaseLine(Header, 60000, 'COF-BAG', 20, 7.5);
        Header.Receive := true; Header.Invoice := true;
        Post.SetSuppressCommit(true); Post.Run(Header);
    end;

    local procedure PurchaseLine(Header: Record "Purchase Header"; LineNo: Integer; ItemNo: Code[20]; Quantity: Decimal; Cost: Decimal)
    var Line: Record "Purchase Line";
    begin
        Line.Init(); Line."Document Type" := Header."Document Type"; Line."Document No." := Header."No."; Line."Line No." := LineNo;
        Line.Validate(Type, Line.Type::Item); Line.Validate("No.", ItemNo); Line.Validate("Location Code", 'CAFE');
        Line.Validate(Quantity, Quantity); Line.Validate("Direct Unit Cost", Cost); Line.Insert(true);
    end;

    local procedure Assemble(ItemNo: Code[20]; Quantity: Decimal)
    var
        Header: Record "Assembly Header";
        Post: Codeunit "Assembly-Post";
    begin
        Header.Init(); Header."Document Type" := Header."Document Type"::Order; Header.Insert(true);
        Header.Validate("Item No.", ItemNo); Header.Validate("Location Code", 'CAFE');
        Header.Validate("Posting Date", Today()); Header.Validate("Due Date", Today());
        Header.Validate(Quantity, Quantity); Header.Modify(true);
        Post.SetSuppressCommit(true); Post.Run(Header);
    end;

    local procedure SellAndCollect()
    var
        Header: Record "Sales Header";
        Invoice: Record "Sales Invoice Header";
        Credit: Record "Sales Cr.Memo Header";
        Post: Codeunit "Sales-Post";
    begin
        Header.Init(); Header."Document Type" := Header."Document Type"::Invoice; Header.Insert(true);
        Header.Validate("Sell-to Customer No.", 'COF-MAYA'); Header.Validate("Posting Date", Today());
        Header.Validate("Document Date", Today()); Header.Validate("Location Code", 'CAFE');
        Header."External Document No." := 'COFFEE-COUNTER-001'; Header.Modify(true);
        SalesLine(Header, 10000, 'COF-FLAT', 2); SalesLine(Header, 20000, 'COF-BAG', 1);
        Post.SetSuppressCommit(true); Post.Run(Header);
        Invoice.SetRange("External Document No.", 'COFFEE-COUNTER-001'); Invoice.FindFirst();
        Invoice.CalcFields("Amount Including VAT");
        CustomerJournal(Invoice."No.", Invoice."Amount Including VAT", false);
        Clear(Header); Clear(Post);
        Header.Init(); Header."Document Type" := Header."Document Type"::"Credit Memo"; Header.Insert(true);
        Header.Validate("Sell-to Customer No.", 'COF-MAYA'); Header.Validate("Posting Date", Today());
        Header.Validate("Document Date", Today()); Header.Validate("Location Code", 'CAFE');
        Header."External Document No." := 'COFFEE-RETURN-001'; Header.Modify(true);
        SalesLine(Header, 10000, 'COF-BAG', 1);
        Post.SetSuppressCommit(true); Post.Run(Header);
        Credit.SetRange("External Document No.", 'COFFEE-RETURN-001'); Credit.FindFirst();
        Credit.CalcFields("Amount Including VAT");
        CustomerJournal(Credit."No.", Credit."Amount Including VAT", true);
    end;

    local procedure SalesLine(Header: Record "Sales Header"; LineNo: Integer; ItemNo: Code[20]; Quantity: Decimal)
    var Line: Record "Sales Line";
    begin
        Line.Init(); Line."Document Type" := Header."Document Type"; Line."Document No." := Header."No."; Line."Line No." := LineNo;
        Line.Validate(Type, Line.Type::Item); Line.Validate("No.", ItemNo); Line.Validate("Location Code", 'CAFE');
        Line.Validate(Quantity, Quantity); Line.Insert(true);
    end;

    local procedure CustomerJournal(DocumentNo: Code[20]; Amount: Decimal; Refund: Boolean)
    var
        Line: Record "Gen. Journal Line";
        Post: Codeunit "Gen. Jnl.-Post Line";
    begin
        Line.Init(); Line."Line No." := 10000; Line."Posting Date" := Today(); Line."Document No." := CopyStr('P-' + DocumentNo, 1, 20);
        Line."Source Code" := 'COFGEN'; Line.Validate("Account Type", Line."Account Type"::Customer); Line.Validate("Account No.", 'COF-MAYA');
        Line.Validate("Bal. Account Type", Line."Bal. Account Type"::"G/L Account"); Line.Validate("Bal. Account No.", 'C1000');
        if Refund then begin
            Line."Document Type" := Line."Document Type"::Refund;
            Line."Applies-to Doc. Type" := Line."Applies-to Doc. Type"::"Credit Memo";
            Line.Validate(Amount, Amount);
        end else begin
            Line."Document Type" := Line."Document Type"::Payment;
            Line."Applies-to Doc. Type" := Line."Applies-to Doc. Type"::Invoice;
            Line.Validate(Amount, -Amount);
        end;
        Line.Validate("Applies-to Doc. No.", DocumentNo); Post.RunWithCheck(Line);
    end;

    local procedure CreateCateringQuote()
    var Header: Record "Sales Header";
    begin
        Header.Init(); Header."Document Type" := Header."Document Type"::Quote; Header.Insert(true);
        Header.Validate("Sell-to Customer No.", 'COF-STUDIO'); Header.Validate("Document Date", Today());
        Header."External Document No." := 'COFFEE-CATERING-001'; Header.Modify(true);
        SalesLine(Header, 10000, 'COF-FLAT', 12); SalesLine(Header, 20000, 'COF-CROIS', 12);
    end;

    local procedure PostWaste()
    var
        Line: Record "Item Journal Line";
        Post: Codeunit "Item Jnl.-Post Line";
    begin
        Line.Init(); Line."Line No." := 10000; Line."Posting Date" := Today(); Line."Document No." := 'COFFEE-WASTE-001';
        Line."Entry Type" := Line."Entry Type"::"Negative Adjmt."; Line."Source Code" := 'COFITEM';
        Line.Validate("Item No.", 'COF-MILK'); Line.Validate("Location Code", 'CAFE'); Line.Validate(Quantity, 0.5);
        Line.Description := 'Coffee demonstration milk spoilage'; Post.RunWithCheck(Line);
    end;
}

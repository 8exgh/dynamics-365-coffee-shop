codeunit 50102 "Coffee Loyalty Management"
{
    Permissions = tabledata "Coffee Loyalty Entry" = rimd, tabledata Customer = rm;

    [EventSubscriber(ObjectType::Codeunit, Codeunit::"Sales-Post", 'OnAfterPostSalesDoc', '', false, false)]
    local procedure SalesPosted(SalesInvHdrNo: Code[20]; SalesCrMemoHdrNo: Code[20]; PreviewMode: Boolean)
    var
        Invoice: Record "Sales Invoice Header";
        CreditMemo: Record "Sales Cr.Memo Header";
    begin
        if PreviewMode then exit;
        if Invoice.Get(SalesInvHdrNo) then begin
            Invoice.CalcFields(Amount);
            Award(Invoice."Sell-to Customer No.", Invoice."No.", Invoice."Posting Date", Invoice.Amount, false);
        end;
        if CreditMemo.Get(SalesCrMemoHdrNo) then begin
            CreditMemo.CalcFields(Amount);
            Award(CreditMemo."Sell-to Customer No.", CreditMemo."No.", CreditMemo."Posting Date", -CreditMemo.Amount, true);
        end;
    end;

    procedure Award(CustomerNo: Code[20]; DocumentNo: Code[20]; PostingDate: Date; Amount: Decimal; IsCredit: Boolean)
    var
        Setup: Record "Coffee Shop Setup";
        Customer: Record Customer;
        Entry: Record "Coffee Loyalty Entry";
        Points: Integer;
    begin
        if not Setup.Get('') then exit;
        if not Customer.Get(CustomerNo) then exit;
        if not Customer."Coffee Loyalty Member" then exit;
        Entry.LockTable();
        Entry.SetRange("Customer No.", CustomerNo);
        Entry.SetRange("Document No.", DocumentNo);
        if IsCredit then Entry.SetRange("Document Type", Entry."Document Type"::"Credit Memo")
        else Entry.SetRange("Document Type", Entry."Document Type"::Invoice);
        if not Entry.IsEmpty() then exit;
        Points := Round(Abs(Amount), 1, '<') * Setup."Points per Currency Unit";
        if IsCredit then Points := -Points;
        if Points = 0 then exit;
        Entry.Init();
        Entry."Customer No." := CustomerNo;
        Entry."Document No." := DocumentNo;
        Entry."Posting Date" := PostingDate;
        Entry.Points := Points;
        if IsCredit then Entry."Document Type" := Entry."Document Type"::"Credit Memo";
        Entry.Insert(true);
        Customer.LockTable();
        Customer.Get(CustomerNo);
        Customer."Coffee Loyalty Points" += Points;
        Customer.Modify(true);
    end;
}

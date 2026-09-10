table 50101 "Coffee Loyalty Entry"
{
    Caption = 'Coffee Loyalty Entry';
    DataClassification = CustomerContent;
    fields
    {
        field(1; "Entry No."; Integer) { Caption = 'Entry No.'; AutoIncrement = true; }
        field(2; "Customer No."; Code[20]) { Caption = 'Customer No.'; TableRelation = Customer."No."; }
        field(3; "Document No."; Code[20]) { Caption = 'Document No.'; }
        field(4; "Posting Date"; Date) { Caption = 'Posting Date'; }
        field(5; Points; Integer) { Caption = 'Points'; }
        field(6; "Document Type"; Option) { Caption = 'Document Type'; OptionMembers = Invoice,"Credit Memo"; OptionCaption = 'Invoice,Credit Memo'; }
    }
    keys
    {
        key(PK; "Entry No.") { Clustered = true; }
        key(Document; "Document Type", "Document No.", "Customer No.") { Unique = true; }
    }
}

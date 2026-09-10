table 50100 "Coffee Shop Setup"
{
    Caption = 'Coffee Shop Setup';
    DataClassification = CustomerContent;

    fields
    {
        field(1; "Primary Key"; Code[10]) { Caption = 'Primary Key'; }
        field(2; "Shop Name"; Text[100]) { Caption = 'Shop Name'; }
        field(3; "Location Code"; Code[10]) { Caption = 'Location Code'; TableRelation = Location.Code; }
        field(4; "Counter Customer No."; Code[20]) { Caption = 'Counter Customer No.'; TableRelation = Customer."No."; }
        field(5; "Points per Currency Unit"; Integer) { Caption = 'Points per Currency Unit'; MinValue = 0; }
        field(6; "Demo Initialized"; Boolean) { Caption = 'Demo Initialized'; Editable = false; }
        field(7; "Demo Workflows Run"; Boolean) { Caption = 'Demo Workflows Run'; Editable = false; }
    }
    keys { key(PK; "Primary Key") { Clustered = true; } }
}

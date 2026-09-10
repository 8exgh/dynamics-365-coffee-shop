table 50102 "Coffee Cue"
{
    Caption = 'Coffee Cue';
    DataClassification = SystemMetadata;
    fields
    {
        field(1; "Primary Key"; Code[10]) { Caption = 'Primary Key'; }
        field(2; "Menu Items"; Integer) { Caption = 'Menu Items'; FieldClass = FlowField; CalcFormula = count(Item where("Coffee Menu Item" = const(true))); }
        field(3; "Loyalty Members"; Integer) { Caption = 'Loyalty Members'; FieldClass = FlowField; CalcFormula = count(Customer where("Coffee Loyalty Member" = const(true))); }
        field(4; "Open Sales Orders"; Integer) { Caption = 'Open Sales Orders'; FieldClass = FlowField; CalcFormula = count("Sales Header" where("Document Type" = const(Order))); }
        field(5; "Open Purchase Orders"; Integer) { Caption = 'Open Purchase Orders'; FieldClass = FlowField; CalcFormula = count("Purchase Header" where("Document Type" = const(Order))); }
    }
    keys { key(PK; "Primary Key") { Clustered = true; } }
}

page 50104 "Coffee Activities"
{
    PageType = CardPart;
    SourceTable = "Coffee Cue";
    Caption = 'Coffee Shop Activities';
    RefreshOnActivate = true;
    layout
    {
        area(Content)
        {
            cuegroup(Shop)
            {
                Caption = 'Coffee Shop';
                field("Menu Items"; Rec."Menu Items") { ApplicationArea = All; DrillDownPageId = "Coffee Menu"; ToolTip = 'Shows coffee menu items.'; }
                field("Loyalty Members"; Rec."Loyalty Members") { ApplicationArea = All; DrillDownPageId = "Customer List"; ToolTip = 'Shows customers enrolled in coffee loyalty.'; }
                field("Open Sales Orders"; Rec."Open Sales Orders") { ApplicationArea = All; DrillDownPageId = "Sales Order List"; ToolTip = 'Shows open sales orders.'; }
                field("Open Purchase Orders"; Rec."Open Purchase Orders") { ApplicationArea = All; DrillDownPageId = "Purchase Order List"; ToolTip = 'Shows open purchase orders.'; }
            }
        }
    }
    trigger OnOpenPage()
    begin
        if not Rec.Get('') then begin Rec.Init(); Rec.Insert(); end;
    end;
}

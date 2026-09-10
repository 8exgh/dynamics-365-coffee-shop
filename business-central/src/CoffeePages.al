page 50100 "Coffee Shop Setup"
{
    PageType = Card;
    SourceTable = "Coffee Shop Setup";
    ApplicationArea = All;
    UsageCategory = Administration;
    Caption = 'Coffee Shop Setup';
    layout
    {
        area(Content)
        {
            group(Shop)
            {
                field("Shop Name"; Rec."Shop Name") { ApplicationArea = All; ToolTip = 'Specifies the name of the coffee shop.'; }
                field("Location Code"; Rec."Location Code") { ApplicationArea = All; ToolTip = 'Specifies the shop inventory location.'; }
                field("Counter Customer No."; Rec."Counter Customer No.") { ApplicationArea = All; ToolTip = 'Specifies the customer for anonymous counter sales.'; }
                field("Points per Currency Unit"; Rec."Points per Currency Unit") { ApplicationArea = All; ToolTip = 'Specifies loyalty points per whole unit of invoiced local currency, excluding tax.'; }
                field("Demo Initialized"; Rec."Demo Initialized") { ApplicationArea = All; ToolTip = 'Shows whether the dedicated coffee demo company has been seeded.'; }
                field("Demo Workflows Run"; Rec."Demo Workflows Run") { ApplicationArea = All; ToolTip = 'Shows whether native demonstration documents have been posted.'; }
            }
        }
    }
    actions
    {
        area(Processing)
        {
            action(InitializeDemo)
            {
                Caption = 'Initialize Coffee Demo'; ApplicationArea = All; Image = Setup;
                ToolTip = 'Initializes only the company named Eight Examples Coffee. Creates coffee master data and posting setup.';
                trigger OnAction()
                var Demo: Codeunit "Coffee Demo Setup";
                begin Demo.Run(); CurrPage.Update(false); end;
            }
            action(ExerciseWorkflows)
            {
                Caption = 'Run Native Demo Workflows'; ApplicationArea = All; Image = Post;
                ToolTip = 'Posts a purchase, assembly, sale, credit memo, payment, and waste adjustment in the dedicated demo company.';
                trigger OnAction()
                var Demo: Codeunit "Coffee Demo Workflows";
                begin Demo.Run(); CurrPage.Update(false); end;
            }
        }
    }
    trigger OnOpenPage()
    begin
        if not Rec.Get('') then begin Rec.Init(); Rec.Insert(); end;
    end;
}

page 50101 "Coffee Menu"
{
    PageType = List;
    SourceTable = Item;
    SourceTableView = where("Coffee Menu Item" = const(true));
    CardPageId = "Item Card";
    ApplicationArea = All;
    UsageCategory = Lists;
    Caption = 'Coffee Menu';
    Editable = false;
    layout
    {
        area(Content)
        {
            repeater(Menu)
            {
                field("No."; Rec."No.") { ApplicationArea = All; ToolTip = 'Specifies the item number.'; }
                field(Description; Rec.Description) { ApplicationArea = All; ToolTip = 'Specifies the menu item.'; }
                field("Unit Price"; Rec."Unit Price") { ApplicationArea = All; ToolTip = 'Specifies the selling price before tax.'; }
                field(Inventory; Rec.Inventory) { ApplicationArea = All; ToolTip = 'Shows posted stock on hand.'; }
                field("Assembly BOM"; Rec."Assembly BOM") { ApplicationArea = All; ToolTip = 'Shows whether a recipe is configured as an assembly bill of materials.'; }
                field("Coffee Allergen Notes"; Rec."Coffee Allergen Notes") { ApplicationArea = All; ToolTip = 'Specifies ingredient and allergen information for review.'; }
            }
        }
    }
}

page 50102 "Coffee Loyalty Entries"
{
    PageType = List;
    SourceTable = "Coffee Loyalty Entry";
    ApplicationArea = All;
    UsageCategory = History;
    Caption = 'Coffee Loyalty Entries';
    Editable = false;
    layout
    {
        area(Content)
        {
            repeater(Entries)
            {
                field("Entry No."; Rec."Entry No.") { ApplicationArea = All; ToolTip = 'Specifies the entry identifier.'; }
                field("Customer No."; Rec."Customer No.") { ApplicationArea = All; ToolTip = 'Specifies the loyalty customer.'; }
                field("Document Type"; Rec."Document Type") { ApplicationArea = All; ToolTip = 'Specifies the source document type.'; }
                field("Document No."; Rec."Document No.") { ApplicationArea = All; ToolTip = 'Specifies the posted invoice or credit memo.'; }
                field("Posting Date"; Rec."Posting Date") { ApplicationArea = All; ToolTip = 'Specifies the posting date.'; }
                field(Points; Rec.Points) { ApplicationArea = All; ToolTip = 'Specifies earned or reversed points.'; }
            }
        }
    }
}

pageextension 50100 "Coffee Customer Card" extends "Customer Card"
{
    layout
    {
        addlast(General)
        {
            field("Coffee Loyalty Member"; Rec."Coffee Loyalty Member") { ApplicationArea = All; ToolTip = 'Enables points from posted sales invoices and credit memos.'; }
            field("Coffee Loyalty Points"; Rec."Coffee Loyalty Points") { ApplicationArea = All; ToolTip = 'Shows the balance of loyalty points.'; }
            field("Coffee Drink Preference"; Rec."Coffee Drink Preference") { ApplicationArea = All; ToolTip = 'Specifies the customer preferred drink.'; }
        }
    }
}

pageextension 50101 "Coffee Item Card" extends "Item Card"
{
    layout
    {
        addlast(Item)
        {
            field("Coffee Menu Item"; Rec."Coffee Menu Item") { ApplicationArea = All; ToolTip = 'Includes this item in the Coffee Menu page.'; }
            field("Coffee Allergen Notes"; Rec."Coffee Allergen Notes") { ApplicationArea = All; ToolTip = 'Specifies allergen information to verify with suppliers.'; }
        }
    }
}

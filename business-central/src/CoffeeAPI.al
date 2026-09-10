page 50105 "Coffee Loyalty API"
{
    PageType = API;
    APIPublisher = 'eightExamples';
    APIGroup = 'coffee';
    APIVersion = 'v1.0';
    EntityName = 'loyaltyMember';
    EntitySetName = 'loyaltyMembers';
    SourceTable = Customer;
    SourceTableView = where("Coffee Loyalty Member" = const(true));
    ODataKeyFields = SystemId;
    DelayedInsert = true;
    InsertAllowed = false;
    ModifyAllowed = false;
    DeleteAllowed = false;
    layout
    {
        area(Content)
        {
            repeater(Members)
            {
                field(id; Rec.SystemId) { Caption = 'Id'; }
                field(number; Rec."No.") { Caption = 'Number'; }
                field(displayName; Rec.Name) { Caption = 'Display Name'; }
                field(points; Rec."Coffee Loyalty Points") { Caption = 'Points'; }
                field(drinkPreference; Rec."Coffee Drink Preference") { Caption = 'Drink Preference'; }
            }
        }
    }
}

tableextension 50101 "Coffee Item" extends Item
{
    fields
    {
        field(50100; "Coffee Menu Item"; Boolean) { Caption = 'Coffee Menu Item'; DataClassification = CustomerContent; }
        field(50101; "Coffee Allergen Notes"; Text[100]) { Caption = 'Coffee Allergen Notes'; DataClassification = CustomerContent; }
    }
}

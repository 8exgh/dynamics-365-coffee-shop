tableextension 50100 "Coffee Customer" extends Customer
{
    fields
    {
        field(50100; "Coffee Loyalty Member"; Boolean) { Caption = 'Coffee Loyalty Member'; DataClassification = CustomerContent; }
        field(50101; "Coffee Loyalty Points"; Integer) { Caption = 'Coffee Loyalty Points'; DataClassification = CustomerContent; Editable = false; }
        field(50102; "Coffee Drink Preference"; Text[80]) { Caption = 'Coffee Drink Preference'; DataClassification = CustomerContent; }
    }
}

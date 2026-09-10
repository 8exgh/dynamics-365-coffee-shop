permissionset 50100 "COFFEE OPERATIONS"
{
    Assignable = true;
    Caption = 'Coffee shop operations';
    Permissions =
        tabledata "Coffee Shop Setup" = RIMD,
        tabledata "Coffee Loyalty Entry" = R,
        tabledata "Coffee Cue" = RIMD,
        table "Coffee Shop Setup" = X,
        table "Coffee Loyalty Entry" = X,
        table "Coffee Cue" = X,
        page "Coffee Shop Setup" = X,
        page "Coffee Menu" = X,
        page "Coffee Loyalty Entries" = X,
        page "Coffee Shop Role Center" = X,
        page "Coffee Activities" = X,
        codeunit "Coffee Loyalty Management" = X;
}

permissionset 50101 "COFFEE DEMO ADMIN"
{
    Assignable = true;
    Caption = 'Coffee demo initializer';
    IncludedPermissionSets = "COFFEE OPERATIONS";
    Permissions = codeunit "Coffee Demo Setup" = X, codeunit "Coffee Demo Workflows" = X;
}

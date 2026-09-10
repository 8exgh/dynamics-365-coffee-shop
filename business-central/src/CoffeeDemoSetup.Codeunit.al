codeunit 50100 "Coffee Demo Setup"
{
    trigger OnRun()
    begin
        Initialize();
    end;

    procedure GuardDemoCompany()
    begin
        if CompanyName() <> 'Eight Examples Coffee' then
            Error('This operation runs only in the dedicated company named Eight Examples Coffee.');
    end;

    procedure Initialize()
    var
        Setup: Record "Coffee Shop Setup";
    begin
        GuardDemoCompany();
        Setup.LockTable();
        if Setup.Get('') then
            if Setup."Demo Initialized" then exit;
        ConfigureFinance();
        ConfigureInventory();
        ConfigurePartners();
        ConfigureMenu();
        ConfigureBankAndJournals();
        ConfigureDimensions();
        if not Setup.Get('') then begin Setup.Init(); Setup.Insert(); end;
        Setup."Shop Name" := 'Eight Examples Coffee & Company';
        Setup."Location Code" := 'CAFE';
        Setup."Counter Customer No." := 'COF-WALKIN';
        Setup."Points per Currency Unit" := 1;
        Setup."Demo Initialized" := true;
        Setup.Modify();
    end;

    local procedure Account(No: Code[20]; Name: Text[100]; IsBalance: Boolean)
    var GL: Record "G/L Account";
    begin
        if GL.Get(No) then exit;
        GL.Init(); GL."No." := No; GL.Name := Name;
        if IsBalance then GL."Income/Balance" := GL."Income/Balance"::"Balance Sheet"
        else GL."Income/Balance" := GL."Income/Balance"::"Income Statement";
        GL."Direct Posting" := true;
        GL.Insert(true);
    end;

    local procedure Series(Code: Code[20]; First: Code[20]; Last: Code[20])
    var
        Header: Record "No. Series";
        Line: Record "No. Series Line";
    begin
        if Header.Get(Code) then exit;
        Header.Init(); Header.Code := Code; Header.Description := Code;
        Header."Default Nos." := true; Header."Manual Nos." := true; Header.Insert();
        Line.Init(); Line."Series Code" := Code; Line."Line No." := 10000;
        Line."Starting No." := First; Line."Ending No." := Last; Line."Increment-by No." := 1;
        Line.Insert();
    end;

    local procedure ConfigureFinance()
    var
        GLSetup: Record "General Ledger Setup";
        GeneralBusiness: Record "Gen. Business Posting Group";
        GeneralProduct: Record "Gen. Product Posting Group";
        GeneralPosting: Record "General Posting Setup";
        VATBusiness: Record "VAT Business Posting Group";
        VATProduct: Record "VAT Product Posting Group";
        VATPosting: Record "VAT Posting Setup";
        CustomerGroup: Record "Customer Posting Group";
        VendorGroup: Record "Vendor Posting Group";
        SalesSetup: Record "Sales & Receivables Setup";
        PurchaseSetup: Record "Purchases & Payables Setup";
        SourceSetup: Record "Source Code Setup";
        Info: Record "Company Information";
        Currency: Record Currency;
    begin
        Account('C1000', 'Coffee cash on hand', true);
        Account('C1010', 'Coffee bank clearing', true);
        Account('C1100', 'Coffee accounts receivable', true);
        Account('C1200', 'Coffee inventory', true);
        Account('C1300', 'Coffee inventory interim', true);
        Account('C2000', 'Coffee accounts payable', true);
        Account('C2100', 'Coffee sample VAT payable', true);
        Account('C2200', 'Coffee sample VAT receivable', true);
        Account('C3000', 'Coffee opening equity', true);
        Account('C4000', 'Coffee sales', false);
        Account('C4100', 'Coffee sales discounts', false);
        Account('C5000', 'Coffee cost of goods sold', false);
        Account('C5100', 'Coffee inventory adjustment and waste', false);
        Account('C5200', 'Coffee purchases', false);
        Account('C5300', 'Coffee direct cost applied', false);
        Account('C5400', 'Coffee purchase discounts', false);
        Account('C5500', 'Coffee rounding', false);
        if not Currency.Get('CAD') then begin
            Currency.Init(); Currency.Code := 'CAD'; Currency.Description := 'Canadian Dollar';
            Currency."Amount Rounding Precision" := 0.01; Currency."Unit-Amount Rounding Precision" := 0.00001;
            Currency.Insert(true);
        end;
        if not GLSetup.Get() then begin GLSetup.Init(); GLSetup.Insert(); end;
        GLSetup."LCY Code" := 'CAD'; GLSetup."Amount Rounding Precision" := 0.01;
        GLSetup."Unit-Amount Rounding Precision" := 0.00001;
        GLSetup."Inv. Rounding Precision (LCY)" := 0.01;
        GLSetup."Allow Posting From" := 0D; GLSetup."Allow Posting To" := 0D;
        GLSetup.Modify();
        if not GeneralBusiness.Get('COFFEE') then begin GeneralBusiness.Init(); GeneralBusiness.Code := 'COFFEE'; GeneralBusiness.Insert(); end;
        if not GeneralProduct.Get('COFFEE') then begin GeneralProduct.Init(); GeneralProduct.Code := 'COFFEE'; GeneralProduct.Insert(); end;
        if not VATBusiness.Get('COFFEE') then begin VATBusiness.Init(); VATBusiness.Code := 'COFFEE'; VATBusiness.Insert(); end;
        if not VATProduct.Get('COFFEE') then begin VATProduct.Init(); VATProduct.Code := 'COFFEE'; VATProduct.Insert(); end;
        if not GeneralPosting.Get('COFFEE', 'COFFEE') then begin
            GeneralPosting.Init(); GeneralPosting."Gen. Bus. Posting Group" := 'COFFEE'; GeneralPosting."Gen. Prod. Posting Group" := 'COFFEE';
            GeneralPosting."Sales Account" := 'C4000'; GeneralPosting."Sales Credit Memo Account" := 'C4000';
            GeneralPosting."Sales Line Disc. Account" := 'C4100'; GeneralPosting."Sales Inv. Disc. Account" := 'C4100';
            GeneralPosting."Purch. Account" := 'C5200'; GeneralPosting."Purch. Credit Memo Account" := 'C5200';
            GeneralPosting."Purch. Line Disc. Account" := 'C5400'; GeneralPosting."Purch. Inv. Disc. Account" := 'C5400';
            GeneralPosting."COGS Account" := 'C5000'; GeneralPosting."COGS Account (Interim)" := 'C5000';
            GeneralPosting."Inventory Adjmt. Account" := 'C5100'; GeneralPosting."Direct Cost Applied Account" := 'C5300';
            GeneralPosting."Invt. Accrual Acc. (Interim)" := 'C2000'; GeneralPosting.Insert();
        end;
        if not GeneralPosting.Get('', 'COFFEE') then begin
            GeneralPosting.Get('COFFEE', 'COFFEE');
            GeneralPosting."Gen. Bus. Posting Group" := ''; GeneralPosting.Insert();
        end;
        if not VATPosting.Get('COFFEE', 'COFFEE') then begin
            VATPosting.Init(); VATPosting."VAT Bus. Posting Group" := 'COFFEE'; VATPosting."VAT Prod. Posting Group" := 'COFFEE';
            VATPosting."VAT Calculation Type" := VATPosting."VAT Calculation Type"::"Normal VAT";
            VATPosting."VAT %" := 5; VATPosting."VAT Identifier" := 'DEMO5';
            VATPosting."Sales VAT Account" := 'C2100'; VATPosting."Purchase VAT Account" := 'C2200'; VATPosting.Insert();
        end;
        if not CustomerGroup.Get('COFFEE') then begin
            CustomerGroup.Init(); CustomerGroup.Code := 'COFFEE'; CustomerGroup."Receivables Account" := 'C1100';
            CustomerGroup."Invoice Rounding Account" := 'C5500'; CustomerGroup.Insert();
        end;
        if not VendorGroup.Get('COFFEE') then begin
            VendorGroup.Init(); VendorGroup.Code := 'COFFEE'; VendorGroup."Payables Account" := 'C2000';
            VendorGroup."Invoice Rounding Account" := 'C5500'; VendorGroup.Insert();
        end;
        Series('COF-SO', 'SO-00001', 'SO-99999'); Series('COF-SQ', 'SQ-00001', 'SQ-99999');
        Series('COF-SI', 'SI-00001', 'SI-99999'); Series('COF-PSI', 'PSI-00001', 'PSI-99999');
        Series('COF-SC', 'SC-00001', 'SC-99999'); Series('COF-PSC', 'PSC-00001', 'PSC-99999');
        Series('COF-SH', 'SH-00001', 'SH-99999'); Series('COF-RR', 'RR-00001', 'RR-99999');
        Series('COF-PO', 'PO-00001', 'PO-99999'); Series('COF-PI', 'PI-00001', 'PI-99999');
        Series('COF-PPI', 'PPI-00001', 'PPI-99999'); Series('COF-PR', 'PR-00001', 'PR-99999');
        Series('COF-PC', 'PC-00001', 'PC-99999'); Series('COF-PPC', 'PPC-00001', 'PPC-99999');
        Series('COF-AS', 'AS-00001', 'AS-99999'); Series('COF-PAS', 'PAS-00001', 'PAS-99999');
        if not SalesSetup.Get() then begin SalesSetup.Init(); SalesSetup.Insert(); end;
        SalesSetup."Order Nos." := 'COF-SO'; SalesSetup."Quote Nos." := 'COF-SQ'; SalesSetup."Invoice Nos." := 'COF-SI';
        SalesSetup."Posted Invoice Nos." := 'COF-PSI'; SalesSetup."Credit Memo Nos." := 'COF-SC';
        SalesSetup."Posted Credit Memo Nos." := 'COF-PSC'; SalesSetup."Posted Shipment Nos." := 'COF-SH';
        SalesSetup."Posted Return Receipt Nos." := 'COF-RR'; SalesSetup."Stockout Warning" := false;
        SalesSetup."Credit Warnings" := SalesSetup."Credit Warnings"::"No Warning"; SalesSetup.Modify();
        if not PurchaseSetup.Get() then begin PurchaseSetup.Init(); PurchaseSetup.Insert(); end;
        PurchaseSetup."Order Nos." := 'COF-PO'; PurchaseSetup."Invoice Nos." := 'COF-PI';
        PurchaseSetup."Posted Invoice Nos." := 'COF-PPI'; PurchaseSetup."Posted Receipt Nos." := 'COF-PR';
        PurchaseSetup."Credit Memo Nos." := 'COF-PC'; PurchaseSetup."Posted Credit Memo Nos." := 'COF-PPC'; PurchaseSetup.Modify();
        CreateSource('COFSALE'); CreateSource('COFPURCH'); CreateSource('COFITEM'); CreateSource('COFGEN'); CreateSource('COFASS');
        if not SourceSetup.Get() then begin SourceSetup.Init(); SourceSetup.Insert(); end;
        SourceSetup.Sales := 'COFSALE'; SourceSetup.Purchases := 'COFPURCH'; SourceSetup."Item Journal" := 'COFITEM';
        SourceSetup."General Journal" := 'COFGEN'; SourceSetup.Assembly := 'COFASS'; SourceSetup.Modify();
        if not Info.Get() then begin Info.Init(); Info.Insert(); end;
        Info.Name := 'Eight Examples Coffee & Company'; Info.City := 'Edmonton'; Info.Address := 'Demo company'; Info.Modify();
    end;

    local procedure CreateSource(Code: Code[10])
    var Source: Record "Source Code";
    begin
        if Source.Get(Code) then exit;
        Source.Init(); Source.Code := Code; Source.Description := Code; Source.Insert();
    end;

    local procedure ConfigureInventory()
    var
        Setup: Record "Inventory Setup";
        AssemblySetup: Record "Assembly Setup";
        Group: Record "Inventory Posting Group";
        Posting: Record "Inventory Posting Setup";
        Location: Record Location;
        Unit: Record "Unit of Measure";
    begin
        if not Unit.Get('PCS') then begin Unit.Init(); Unit.Code := 'PCS'; Unit.Description := 'Piece'; Unit.Insert(); end;
        if not Unit.Get('KG') then begin Unit.Init(); Unit.Code := 'KG'; Unit.Description := 'Kilogram'; Unit.Insert(); end;
        if not Unit.Get('L') then begin Unit.Init(); Unit.Code := 'L'; Unit.Description := 'Litre'; Unit.Insert(); end;
        if not Location.Get('CAFE') then begin Location.Init(); Location.Code := 'CAFE'; Location.Name := 'Old Strathcona Coffee Shop'; Location.Insert(); end;
        if not Location.Get('STORE') then begin Location.Init(); Location.Code := 'STORE'; Location.Name := 'Coffee Stockroom'; Location.Insert(); end;
        if not Group.Get('COFFEE') then begin Group.Init(); Group.Code := 'COFFEE'; Group.Description := 'Coffee ingredients and menu'; Group.Insert(); end;
        CreateInventoryPosting(''); CreateInventoryPosting('CAFE'); CreateInventoryPosting('STORE');
        if not Setup.Get() then begin Setup.Init(); Setup.Insert(); end;
        Setup."Automatic Cost Posting" := true; Setup."Automatic Cost Adjustment" := Setup."Automatic Cost Adjustment"::Always;
        Setup."Prevent Negative Inventory" := true; Setup.Modify();
        if not AssemblySetup.Get() then begin AssemblySetup.Init(); AssemblySetup.Insert(); end;
        AssemblySetup."Assembly Order Nos." := 'COF-AS'; AssemblySetup."Posted Assembly Order Nos." := 'COF-PAS'; AssemblySetup.Modify();
    end;

    local procedure CreateInventoryPosting(LocationCode: Code[10])
    var Posting: Record "Inventory Posting Setup";
    begin
        if Posting.Get(LocationCode, 'COFFEE') then exit;
        Posting.Init(); Posting."Location Code" := LocationCode; Posting."Invt. Posting Group Code" := 'COFFEE';
        Posting."Inventory Account" := 'C1200'; Posting."Inventory Account (Interim)" := 'C1300'; Posting.Insert();
    end;

    local procedure ConfigurePartners()
    begin
        CreateCustomer('COF-WALKIN', 'Counter guest', false);
        CreateCustomer('COF-MAYA', 'Maya Chen', true);
        CreateCustomer('COF-STUDIO', 'North Studio Catering', true);
        CreateVendor('COF-ROAST', 'Prairie Roasting Co.');
        CreateVendor('COF-DAIRY', 'Meadow Dairy & Oats');
        CreateVendor('COF-BAKE', 'Earlybird Bakehouse');
    end;

    local procedure CreateCustomer(No: Code[20]; Name: Text[100]; Loyalty: Boolean)
    var Customer: Record Customer;
    begin
        if Customer.Get(No) then exit;
        Customer.Init(); Customer."No." := No; Customer.Insert(true);
        Customer.Validate(Name, Name);
        Customer.Validate("Gen. Bus. Posting Group", 'COFFEE'); Customer.Validate("VAT Bus. Posting Group", 'COFFEE');
        Customer.Validate("Customer Posting Group", 'COFFEE'); Customer.Validate("Location Code", 'CAFE');
        Customer."Coffee Loyalty Member" := Loyalty;
        Customer.Modify(true);
    end;

    local procedure CreateVendor(No: Code[20]; Name: Text[100])
    var Vendor: Record Vendor;
    begin
        if Vendor.Get(No) then exit;
        Vendor.Init(); Vendor."No." := No; Vendor.Insert(true); Vendor.Validate(Name, Name);
        Vendor.Validate("Gen. Bus. Posting Group", 'COFFEE'); Vendor.Validate("VAT Bus. Posting Group", 'COFFEE');
        Vendor.Validate("Vendor Posting Group", 'COFFEE'); Vendor.Modify(true);
    end;

    local procedure ConfigureMenu()
    begin
        CreateItem('COF-BEANS', 'House espresso beans', 'KG', 30, 0, false, '');
        CreateItem('COF-MILK', 'Whole milk', 'L', 2, 0, false, 'Contains milk');
        CreateItem('COF-OAT', 'Oat milk', 'L', 3, 0, false, 'Check supplier gluten declaration');
        CreateItem('COF-CUP', 'Takeaway cup', 'PCS', 0.18, 0, false, '');
        CreateItem('COF-ESP', 'Espresso', 'PCS', 0, 3.5, true, '');
        CreateItem('COF-FLAT', 'Flat white', 'PCS', 0, 5.25, true, 'Contains milk');
        CreateItem('COF-LATTE', 'Oat latte', 'PCS', 0, 6.25, true, 'Check oat milk supplier declaration');
        CreateItem('COF-CROIS', 'Butter croissant', 'PCS', 1.75, 4.5, true, 'Contains wheat and milk');
        CreateItem('COF-BAG', 'House blend 250 g', 'PCS', 7.5, 18, true, '');
        Recipe('COF-ESP', 'COF-BEANS', 10000, 0.018, 'KG'); Recipe('COF-ESP', 'COF-CUP', 20000, 1, 'PCS');
        Recipe('COF-FLAT', 'COF-BEANS', 10000, 0.018, 'KG'); Recipe('COF-FLAT', 'COF-MILK', 20000, 0.18, 'L'); Recipe('COF-FLAT', 'COF-CUP', 30000, 1, 'PCS');
        Recipe('COF-LATTE', 'COF-BEANS', 10000, 0.018, 'KG'); Recipe('COF-LATTE', 'COF-OAT', 20000, 0.22, 'L'); Recipe('COF-LATTE', 'COF-CUP', 30000, 1, 'PCS');
    end;

    local procedure CreateItem(No: Code[20]; Description: Text[100]; UnitCode: Code[10]; Cost: Decimal; Price: Decimal; Menu: Boolean; Allergen: Text[100])
    var
        Item: Record Item;
        Unit: Record "Item Unit of Measure";
    begin
        if Item.Get(No) then exit;
        Item.Init(); Item."No." := No; Item.Insert(true);
        Unit.Init(); Unit."Item No." := No; Unit.Code := UnitCode; Unit."Qty. per Unit of Measure" := 1; Unit.Insert(true);
        Item.Validate(Description, Description); Item.Validate("Base Unit of Measure", UnitCode);
        Item.Validate("Gen. Prod. Posting Group", 'COFFEE'); Item.Validate("VAT Prod. Posting Group", 'COFFEE');
        Item.Validate("Inventory Posting Group", 'COFFEE'); Item.Validate("Costing Method", Item."Costing Method"::FIFO);
        Item.Validate("Unit Cost", Cost); Item.Validate("Last Direct Cost", Cost); Item.Validate("Unit Price", Price);
        Item."Coffee Menu Item" := Menu; Item."Coffee Allergen Notes" := Allergen;
        Item.Validate("Reordering Policy", Item."Reordering Policy"::"Fixed Reorder Qty.");
        Item.Validate("Reorder Point", 10); Item.Validate("Reorder Quantity", 50); Item.Modify(true);
    end;

    local procedure Recipe(ParentNo: Code[20]; ComponentNo: Code[20]; LineNo: Integer; Quantity: Decimal; UnitCode: Code[10])
    var
        Component: Record "BOM Component";
        Item: Record Item;
    begin
        if Component.Get(ParentNo, LineNo) then exit;
        Component.Init(); Component."Parent Item No." := ParentNo; Component."Line No." := LineNo;
        Component.Validate(Type, Component.Type::Item); Component.Validate("No.", ComponentNo);
        Component.Validate("Unit of Measure Code", UnitCode); Component.Validate("Quantity per", Quantity); Component.Insert(true);
        Item.Get(ParentNo); Item.Validate("Replenishment System", Item."Replenishment System"::Assembly);
        Item.Validate("Assembly Policy", Item."Assembly Policy"::"Assemble-to-Stock"); Item.Modify(true);
    end;

    local procedure ConfigureBankAndJournals()
    var
        BankGroup: Record "Bank Account Posting Group";
        Bank: Record "Bank Account";
        GeneralTemplate: Record "Gen. Journal Template";
        GeneralBatch: Record "Gen. Journal Batch";
        ItemTemplate: Record "Item Journal Template";
        ItemBatch: Record "Item Journal Batch";
    begin
        if not BankGroup.Get('COFFEE') then begin
            BankGroup.Init(); BankGroup.Code := 'COFFEE'; BankGroup."G/L Account No." := 'C1010'; BankGroup.Insert();
        end;
        if not Bank.Get('COF-BANK') then begin
            Bank.Init(); Bank."No." := 'COF-BANK'; Bank.Name := 'Coffee operating bank';
            Bank."Bank Acc. Posting Group" := 'COFFEE'; Bank.Insert(true);
        end;
        Series('COF-JNL', 'JNL-00001', 'JNL-99999');
        if not GeneralTemplate.Get('COFFEE') then begin
            GeneralTemplate.Init(); GeneralTemplate.Name := 'COFFEE'; GeneralTemplate.Description := 'Coffee general journals';
            GeneralTemplate.Type := GeneralTemplate.Type::General; GeneralTemplate."Source Code" := 'COFGEN'; GeneralTemplate.Insert(true);
        end;
        if not GeneralBatch.Get('COFFEE', 'DAILY') then begin
            GeneralBatch.Init(); GeneralBatch."Journal Template Name" := 'COFFEE'; GeneralBatch.Name := 'DAILY';
            GeneralBatch.Description := 'Coffee receipts and payments'; GeneralBatch."No. Series" := 'COF-JNL'; GeneralBatch.Insert(true);
        end;
        if not ItemTemplate.Get('COFFEE') then begin
            ItemTemplate.Init(); ItemTemplate.Name := 'COFFEE'; ItemTemplate.Description := 'Coffee stock adjustments';
            ItemTemplate.Type := ItemTemplate.Type::Item; ItemTemplate."Source Code" := 'COFITEM'; ItemTemplate.Insert(true);
        end;
        if not ItemBatch.Get('COFFEE', 'WASTE') then begin
            ItemBatch.Init(); ItemBatch."Journal Template Name" := 'COFFEE'; ItemBatch.Name := 'WASTE';
            ItemBatch.Description := 'Coffee waste and corrections'; ItemBatch."No. Series" := 'COF-JNL'; ItemBatch.Insert(true);
        end;
    end;

    local procedure ConfigureDimensions()
    var
        Dimension: Record Dimension;
        Value: Record "Dimension Value";
        Default: Record "Default Dimension";
    begin
        if not Dimension.Get('COF-SHOP') then begin Dimension.Init(); Dimension.Code := 'COF-SHOP'; Dimension.Name := 'Coffee Shop'; Dimension.Insert(); end;
        if not Value.Get('COF-SHOP', 'STRATHCONA') then begin
            Value.Init(); Value."Dimension Code" := 'COF-SHOP'; Value.Code := 'STRATHCONA'; Value.Name := 'Old Strathcona'; Value.Insert(true);
        end;
        if not Default.Get(Database::Customer, 'COF-MAYA', 'COF-SHOP') then begin
            Default.Init(); Default."Table ID" := Database::Customer; Default."No." := 'COF-MAYA'; Default."Dimension Code" := 'COF-SHOP';
            Default."Dimension Value Code" := 'STRATHCONA'; Default.Insert(true);
        end;
    end;
}

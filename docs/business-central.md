# Native Business Central setup

The extension targets Business Central application/platform 28.0 and AL runtime 17.0. CI compiles against pinned W1 28.5 symbols. Object IDs 50100–50149 belong to the application; 50150–50179 belong to its tests. Confirm these ranges do not collide with another custom extension in an existing environment.

## Windows Docker sandbox

Use Docker configured for Windows containers and an elevated PowerShell session. The setup script uses Microsoft’s BcContainerHelper, downloads a W1 sandbox artifact, and defaults to an 8 GB container named `bc-coffee`. It creates the dedicated evaluation company `Eight Examples Coffee`, leaving CRONUS available separately.

```powershell
.\scripts\New-CoffeeSandbox.ps1 -AcceptEula -RunTests
```

The script stages source under `C:\ProgramData\BcContainerHelper\CoffeeShop`, compiles inside the container, publishes and synchronizes both applications, initializes the company, executes the native tests, and runs the posting demonstrations. Test results are saved as `coffee-tests.xml` in that staging directory. Test transactions use rollback so a passing test does not consume the demonstration dataset.

If reusing a container originally created without the test toolkit, install Microsoft’s test toolkit into that container before using `-RunTests`. Reusing a populated company whose stock or documents have been edited can intentionally fail the fixed-quantity native tests; use a fresh dedicated evaluation company for deterministic test runs.

Choose **Coffee Shop Manager** in **My Settings**. The role centre links to coffee configuration, menu, loyalty, customers, contacts, sales documents, purchases, assembly orders, stock journals, transfer orders, G/L accounts, banks, dimensions, and approvals.

The supplied sandbox uses W1 so its posting configuration is consistent. Its sample VAT setup is not Canadian GST/PST configuration. Use a country-specific implementation and reviewed posting/tax setup for an actual business.

## Online sandbox

Create or select a Business Central 28+ sandbox with an appropriately licensed user. Create an empty company named `Eight Examples Coffee`. Compile the application with `python3 scripts/compile-al.py`, then upload `artifacts/EightExamplesCoffee.app` through **Extension Management → Upload Extension**. Choose the current environment/version and wait for deployment to complete.

Assign the extension’s `COFFEE OPERATIONS` permission set alongside the standard Business Central permissions needed for each employee’s job. `COFFEE DEMO ADMIN` adds access to initialization and demonstration routines but does not grant permissions to Microsoft’s standard data tables. A suitably privileged human sandbox administrator must perform the initial setup. A Business Central application user must never be assigned `SUPER`.

Open **Coffee Shop Setup**, select **Initialize Coffee Demo**, then **Run Native Demo Workflows**. Both routines check the company name and preserve their completion flags. Installation alone does not initialize or post company data.

The native loyalty API is read-only:

```text
https://api.businesscentral.dynamics.com/v2.0/{tenant}/{environment}/api/eightExamples/coffee/v1.0/companies({companyId})/loyaltyMembers
```

Assign read access to customers and execute access to the custom API page for its application user. The companion currently browses standard APIs; custom loyalty is accessible directly through this endpoint.

## Objects and configured records

- Custom setup, loyalty entry, and dashboard cue tables.
- Customer loyalty opt-in, balance, and preferred drink fields.
- Item menu visibility and allergen notes.
- Three assembly recipes: espresso, flat white, and oat latte.
- Purchased ingredients, croissants, and retail coffee bags.
- Counter guest, Maya Chen, and North Studio customers.
- Roaster, dairy, and bakery suppliers.
- `CAFE` and `STORE` inventory locations.
- CAD local currency and a dedicated `C`-prefixed chart of accounts.
- General, VAT, customer, vendor, inventory, and bank posting groups.
- Document number series, source codes, an operating bank, and daily general/waste item journal batches.
- A `COF-SHOP` dimension and default Strathcona value for Maya.
- Event-driven loyalty for posted invoices and credit memos, with unique source-document entries.

## Native posting demonstration

The routine funds the operating bank with $1,000, purchases and invoices ingredients, pays the supplier, posts three assemblies, posts a counter invoice, applies the customer payment, posts a retail credit memo, applies the refund, creates a catering quote, and posts 0.5 L milk waste.

Expected stock after a fresh run:

| Item | CAFE stock |
| --- | ---: |
| COF-BEANS | 8.92 kg |
| COF-MILK | 14.1 L |
| COF-OAT | 7.8 L |
| COF-CUP | 140 pieces |
| COF-FLAT | 28 pieces |
| COF-ESP | 20 pieces |
| COF-LATTE | 10 pieces |
| COF-CROIS | 50 pieces |
| COF-BAG | 20 pieces |

Maya has 10 net loyalty points and no outstanding customer balance. The roaster has no outstanding vendor balance. G/L entries sum to zero. The catering quote remains available to walk through the native quote-to-order process.

These are runtime test expectations, not a claim that native posting has been executed on a Linux host. Compilation checks AL compatibility; only execution in Business Central verifies posting configuration and runtime behavior.

[Microsoft’s container tooling](https://github.com/microsoft/navcontainerhelper) and [S2S authentication documentation](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/automation-apis-using-s2s-authentication) describe the platform and identity prerequisites.

# Eight Examples Coffee & Company

A custom Dynamics 365 **Business Central** coffee shop implementation, plus a Dockerized operations companion. Business Central is the Dynamics product used for sales, purchasing, inventory, assembly, customers, and finance in this project.

The repository contains two distinct applications:

| Component | What it does | Runtime |
| --- | --- | --- |
| Native Business Central extension | Coffee Shop Manager role centre, company configuration, menu, native assembly recipes, loyalty, and native posting demonstrations | Business Central 28+ online sandbox or Windows Docker sandbox |
| Coffee operations companion | Interactive practice workflows, persistent practice ledger, and a separate connection to real Business Central APIs | Linux Docker |

The companion is **not an installation or emulation of Microsoft Dynamics 365**. Its practice transactions stay in SQLite. Its Business Central page reads actual Microsoft records and can create an unposted sales order when explicitly enabled in server configuration. No practice orders are automatically synchronized or posted to Microsoft.

## Start the Docker companion

```bash
python3 scripts/configure.py
docker compose up -d --build --wait
```

Open **http://localhost:3065**. Sign in as `manager` using `COFFEE_ADMIN_PASSWORD` from the generated `.env` file. Configuration creates random credentials, writes the file with mode `0600`, and preserves existing configuration. The app refuses to start with missing or short credentials.

Data persists in the `dynamics-365-coffee-shop_coffee-data` Docker volume. The app runs as UID 1000 with a read-only container filesystem and a writable data volume. The local port binds to loopback by default.

```bash
docker compose logs --tail=100 coffee
docker compose down
python3 scripts/backup.py
```

`docker compose down` preserves the volume. The backup command uses SQLite’s online backup API and writes a database copy under `artifacts/backups`.

For a counter staff login, add `COFFEE_CASHIER_PASSWORD` with at least 12 characters to `.env` and recreate the container. The username is `cashier`. Counter staff can create sales, quotes, customers, and care issues. Refunds, document posting, purchasing, waste, closing, report export, and real Business Central API access require the manager role. The practice approval step is manager-controlled; it does not implement separation between requester and approver.

## Coffee shop workflows

| Area | Companion workflow | Native Business Central implementation |
| --- | --- | --- |
| Counter sales | Cart, customer, cash/card simulation, sample tax, receipt history | Native sales invoices and customer ledger entries |
| Catering | Quote → acceptance → invoice → payment | Seeded sales quote, native quote-to-order process and sales documents |
| Purchasing | Request → manager approval at $500 → receive/invoice → payment | Posted purchase order and supplier payment, standard approval workspace |
| Recipes | Stock deduction by grams, millilitres, and pieces | Native assembly BOMs and posted assembly orders |
| Inventory | Reorder thresholds, stock value, waste adjustments | Items, locations, replenishment settings, item journals and ledger entries |
| Returns | Full refund, loyalty reversal, optional unopened retail restock | Native sales credit memo and applied customer refund |
| Loyalty | Points and visits per customer | Customer extension, document-backed loyalty ledger, invoice/credit event subscriber |
| Relationships | Customer creation and service issue resolution | Customers, contacts, preferred drink fields |
| Finance | Balanced double-entry practice journals, trial balance CSV, receivables/payables | Configured chart and posting groups, native G/L, customer, vendor and bank ledgers |
| Cash and bank | Till count, variance posting, daily close | Operating bank, opening equity funding, payment application, standard bank reconciliation workspace |
| Analysis | Sales mix, margin, inventory and activity history | Shop dimension, native account and ledger drill-downs |
| Integration | Real API record browser and optional draft creation | Standard API v2.0 and read-only custom loyalty API |

Sample amounts use CAD. The practice tax rate and W1 extension’s 5% sample VAT are demonstration values, not a Canadian tax implementation. Card payments are simulated. Ingredient and supplier costs are illustrative. The native W1 dataset and local practice dataset are separate, so quantities and costs need not match.

Native workflows use Microsoft posting codeunits; the extension does not write directly into native G/L, item, customer, vendor, or bank ledger tables. Setup and the posting demonstration run only in a company named `Eight Examples Coffee` and are repeatable without duplicating their records. Native loyalty is one point per whole unit of the **document currency**, excluding tax; credits reverse points and may leave a negative balance. The practice app uses CAD and clamps the points balance at zero on refunds.

Dynamics 365 Sales, Customer Service, Field Service, Commerce, Finance, and Supply Chain Management are separate products. They are not installed by this project. The companion’s care issues are local practice records, not Dynamics 365 Customer Service cases. Payroll, real payment processing, tax filing, manufacturing, and marketing journeys are outside this implementation.

## Start native Business Central

The Windows sandbox script creates a Business Central W1 Docker container, a dedicated evaluation company, compiles and installs the extension, initializes the coffee business, and runs native posting demonstrations. It can also compile and execute the native integration tests.

On a Windows Docker host, from an elevated PowerShell terminal:

```powershell
.\scripts\New-CoffeeSandbox.ps1 -AcceptEula -RunTests
```

The script prompts for a sandbox administrator credential. `-AcceptEula` records acceptance of Microsoft’s container license terms. Windows 11 may need `-Isolation hyperv`, depending on its host/container version compatibility. Allow at least 16 GB host RAM, 8 GB container RAM, and sufficient disk for Business Central artifacts and SQL Server.

After setup, open `http://bc-coffee/BC/?company=Eight%20Examples%20Coffee`, select **Coffee Shop Manager** in **My Settings**, and open **Coffee Shop Setup**. Use this container on a trusted development network; the default sandbox web client uses HTTP. The Linux companion’s Microsoft API connector currently targets Business Central **online**, not the Windows sandbox’s local authentication.

See [native setup](docs/business-central.md) and the [workflow walkthrough](docs/scenarios.md). The checked-in `Exercise Native Business Central` workflow targets a separately provisioned Windows runner labeled `bc-sandbox`.

## Connect an online sandbox

Set these values in `.env`, then recreate the companion container:

```dotenv
BC_TENANT_ID=your-tenant-guid
BC_ENVIRONMENT=Sandbox
BC_COMPANY_ID=your-company-guid
BC_CLIENT_ID=your-application-guid
BC_CLIENT_SECRET=your-application-secret
BC_ALLOW_WRITES=false
```

Use an Entra application with Business Central `API.ReadWrite.All` application permission and tenant admin consent. Add and enable that client in Business Central’s **Microsoft Entra Applications** page and assign the required company permissions. Application users cannot receive `SUPER`.

The **Business Central** page retrieves the first 100 records of the selected native resource. It supports customers, items, vendors, sales orders/invoices, purchase orders/invoices, accounts, G/L entries, customer payments, dimensions, and locations. It does not silently substitute practice data when the Microsoft connection fails.

Set `BC_ALLOW_WRITES=true` to enable creation of a real, unposted sales order using actual Business Central customer/item IDs. Draft creation uses a stable external document reference, persists request state, and checks for an existing order before retrying. An ambiguous or interrupted request retains its key; retry the same request after 90 seconds. Posting and further document handling take place in the native Microsoft client.

## Deployment matching the example projects

The deployment follows `inventory-shopify` and `devops`:

1. Application CI runs Python tests, browser workflows, and AL compilation.
2. CI builds a Linux image and publishes it to `ghcr.io/8exgh/dynamics-365-coffee-shop` with immutable commit and digest references.
3. CI dispatches `dynamics-365-coffee-shop-deploy` to the `devops` repository.
4. The Server7 runner deploys `sean-web-dynamics-365-coffee-shop` on port **3067**, with persistent storage at `/opt/dynamics-365-coffee-shop/data`.

The matching files have been added to the local sibling `devops` checkout:

- `.github/workflows/deploy-dynamics-365-coffee-shop.yml`
- `scripts/deploy-dynamics-365-coffee-shop.py`
- `Server7/dynamics-365-coffee-shop/deploy.txt`

Copies remain under `deployment/` in this repository. No other devops application files need changing.

Source repository secret: `DEPLOY_TOKEN`, authorized to dispatch workflows in `8exgh/devops`.

Devops secrets: `READ_PACKAGES_PAT`, `COFFEE_ADMIN_PASSWORD`, `COFFEE_SESSION_SECRET`. Microsoft integration and the cashier login are optional; see [deployment details](docs/deployment.md).

The deployment probes a candidate container before replacing the current one, backs up its database, and restores the previous container if the replacement fails health checks. It rejects image references outside the expected repository and refuses to remove another application holding port 3067. No registry-wide image pruning runs.

The expected Cloudflare Tunnel origin is `http://192.168.4.56:3067`. A public hostname must be configured separately. Server7 deployment defaults to secure cookies for HTTPS access; deliberate LAN-only HTTP access needs `COFFEE_SECURE_COOKIES=false` in devops variables.

## Development and validation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
npm --prefix web ci
npm --prefix web run build
python3 scripts/compile-al.py
```

AL compilation requires .NET 8 and downloads Microsoft’s pinned compiler and symbol packages. Outputs are `artifacts/EightExamplesCoffee.app` and `artifacts/EightExamplesCoffeeTests.app`.

Browser tests use an isolated server on port 3066 with `COFFEE_DATABASE` pointing at a fresh temporary database and test-only credentials; see the CI workflow for the full invocation. They do not modify the running Docker workspace. Native posting tests require the Windows sandbox and are separate from compilation.

The main configuration variables are documented in `.env.example`. `COFFEE_TIMEZONE` defaults to `America/Edmonton` for till close dates. Sessions last 12 hours. Requests that modify state require a session CSRF token; business mutations also require a UUID idempotency key. The built-in health endpoint is public and contains no credentials or business data.

## Microsoft references

- [Business Central Windows containers and BcContainerHelper](https://github.com/microsoft/navcontainerhelper)
- [Business Central API v2.0](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/)
- [Service-to-service authentication](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/automation-apis-using-s2s-authentication)
- [AL Development Tools](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-al-tool-package)
- [Symbols from Microsoft NuGet feeds](https://learn.microsoft.com/en-us/dynamics365/release-plan/2026wave1/smb/dynamics365-business-central/download-symbols-nuget-feed)

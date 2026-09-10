# Verification record

Validated locally, in GitHub Actions, and on Server7 on September 10, 2026.

| Check | Result |
| --- | --- |
| Python domain/API and Microsoft connector contract tests | 14 passed |
| Deployment success, rollback, and unrelated port-holder tests | 3 passed |
| Cloudflare route preservation, repeat configuration, and conflict checks | 2 passed |
| Desktop/mobile browser workflow | Passed, including sale, refund, purchase approval/receipt/payment, catering invoice/payment, waste, customer creation, service resolution, and till close |
| Browser JavaScript errors | None during the workflow |
| Mobile document overflow | None at 390 × 844 |
| Production frontend build | Passed |
| Docker image build/start | Passed; container healthy at localhost:3065 |
| Login against the running Docker container | Passed |
| Persistent data across image recreation | Preserved four initial sales/quote records and balanced ledger |
| SQLite snapshot backup | Passed; restored snapshot integrity check returned ok |
| GitHub Actions syntax | Passed actionlint for application and devops workflows |
| npm dependency audit | No reported vulnerabilities |
| Native extension AL compilation | Passed with Microsoft AL compiler 17.0.34.45391 and pinned Business Central 28.5 symbols |
| Native test extension AL compilation | Passed; three native integration test procedures packaged |
| GitHub build and publish | Passed: 19 Python tests, complete browser workflow, both AL packages, and GHCR image publication |
| Server7 deployment | Passed; persistent Docker service on port 3067 |
| Public Cloudflare route | Passed; HTTPS health check matches the deployed application commit; 92 other ingress rules preserved |
| Public browser and API verification | Passed: login, 10 workspace pages, trial-balance CSV, zero ledger imbalance, logout, and anonymous access rejection |
| Public session cookie | Secure, HttpOnly, SameSite=Strict |
| Public desktop/mobile interface | Passed; no browser errors and no mobile document overflow |

Compiled native artifacts are in `artifacts/EightExamplesCoffee.app` and `artifacts/EightExamplesCoffeeTests.app`. Local browser captures are in `artifacts/overview-desktop.png` and `artifacts/overview-mobile.png`. Deployed captures are in `artifacts/deployed-desktop.png` and `artifacts/deployed-mobile.png`, with results in `artifacts/deployed-verification.json`.

Native posting tests and actual Microsoft API authentication were not executed: this host runs Linux, and no Windows Business Central host or online tenant credentials were supplied. The native `.app` files are compiled packages; posting behavior must be verified by the included Windows sandbox workflow. The connector’s request format, token handling, and repeat-request protection were tested using HTTP mocks.

The private source and devops changes are pushed. The companion is live at [d365-coffee-shop.fusenv.com](https://d365-coffee-shop.fusenv.com), running application commit `85e889029c39f7a0a54db606917409cc512f7195`. Deployment credentials are stored in the devops `d365-coffee-shop` environment. Source CI dispatches future deployments automatically. Actual Microsoft Business Central is not connected.

Evidence: [build, tests, and image publication](https://github.com/8exgh/dynamics-365-coffee-shop/actions/runs/34506382226), [Server7 deployment](https://github.com/8exgh/devops/actions/runs/34506861926), and [Cloudflare configuration and HTTPS verification](https://github.com/8exgh/devops/actions/runs/34506952336).

The initial Server7 deployment stopped because the runner does not allow `sudo install`. The published deployment now initializes only the coffee application’s bind mount through Docker, matching the existing Server7 pattern. Its candidate and deployed service both passed their health checks.

The Python test run reported third-party deprecation warnings from Starlette’s HTTPX test adapter and AnyIO’s BlockingPortal alias. They did not affect the passing tests.

# Verification record

Validated locally on September 10, 2026.

| Check | Result |
| --- | --- |
| Python domain/API and Microsoft connector contract tests | 14 passed |
| Deployment success, rollback, and unrelated port-holder tests | 3 passed |
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

Compiled native artifacts are in `artifacts/EightExamplesCoffee.app` and `artifacts/EightExamplesCoffeeTests.app`. Browser captures are in `artifacts/overview-desktop.png` and `artifacts/overview-mobile.png`.

Native posting tests and actual Microsoft API authentication were not executed: this host runs Linux, and no Windows Business Central host or online tenant credentials were supplied. The native `.app` files are compiled packages; posting behavior must be verified by the included Windows sandbox workflow. The connector’s request format, token handling, and repeat-request protection were tested using HTTP mocks.

GitHub repositories were not pushed, Server7 was not remotely deployed, and no Cloudflare route was created. The app’s Docker container is running locally, and the corresponding deployment files are present in the local sibling devops checkout. GitHub secrets and an actual Dynamics environment remain required for external deployment and native execution.

The Python test run reported third-party deprecation warnings from Starlette’s HTTPX test adapter and AnyIO’s BlockingPortal alias. They did not affect the passing tests.

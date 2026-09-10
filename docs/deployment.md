# Deployment

The source workspace and the sibling devops checkout contain all required deployment files. They are local changes until committed and pushed to their GitHub repositories. No public DNS route or Microsoft environment is created by preparing these files.

## GitHub configuration

Use `8exgh/dynamics-365-coffee-shop` as the source repository to match the image name. The source workflow runs on pull requests, main pushes, and manual dispatch. Only main builds publish images and dispatch deployment.

| Repository | Secret or variable | Purpose |
| --- | --- | --- |
| Source | `DEPLOY_TOKEN` secret | Repository dispatch permission for `8exgh/devops` |
| Devops | `READ_PACKAGES_PAT` secret | Pull the private GHCR image |
| Devops | `COFFEE_ADMIN_PASSWORD` environment secret | Manager login, at least 12 characters |
| Devops | `COFFEE_SESSION_SECRET` environment secret | Session signing, at least 32 characters |
| Devops | `COFFEE_CASHIER_PASSWORD` secret | Optional counter staff login |
| Devops | `COFFEE_BC_TENANT_ID` secret | Optional online Microsoft tenant |
| Devops | `COFFEE_BC_COMPANY_ID` secret | Optional native company |
| Devops | `COFFEE_BC_CLIENT_ID` secret | Optional Entra client |
| Devops | `COFFEE_BC_CLIENT_SECRET` secret | Optional Entra application secret |
| Devops | `COFFEE_BC_ENVIRONMENT` variable | Defaults to Sandbox |
| Devops | `COFFEE_BC_WEB_URL` variable | Defaults to Microsoft’s Business Central client |
| Devops | `COFFEE_BC_ALLOW_WRITES` variable | Defaults to false |
| Devops | `COFFEE_SECURE_COOKIES` variable | Defaults to true for HTTPS |
| Source | `BC_SANDBOX_PASSWORD` secret | Optional Windows sandbox workflow administrator |

The devops deployment uses the `d365-coffee-shop` GitHub environment. Store the coffee credentials there; shared registry credentials remain repository secrets.

Never copy the generated local `.env` into Git. To use its random values for deployment, put them in the relevant GitHub secrets through a secure local input channel.

## Server7

The runner needs Linux x64, labels `self-hosted`, `linux`, `x64`, and `server7`, Docker, Python 3, and the existing ability to create `/opt` service directories through sudo. It uses port 3067, which was unused in the reference workflows when the files were prepared. The deployment checks running containers for collisions again at deployment time.

The workflow creates:

```text
/opt/dynamics-365-coffee-shop/data
/opt/dynamics-365-coffee-shop/config/runtime.env
/opt/dynamics-365-coffee-shop/backups
/opt/dynamics-365-coffee-shop/deployed-image.txt
```

The image runs as UID/GID 1000. The config file is mode 0600. Image references must be an exact digest or full commit `sha-` tag from the expected GHCR repository. Dispatch payloads are passed as data, not interpolated into executable shell code.

A temporary candidate starts with an isolated database and randomly assigned loopback port. Only after it becomes healthy does the deployment back up the existing SQLite database and replace the current service. A failed replacement restarts the previous container against the preserved data directory. The current schema is additive; future incompatible schema migrations must include an explicit data rollback strategy.

The app publishes on Server7 port 3067 for the existing Cloudflare Tunnel pattern. Configure the chosen HTTPS hostname’s origin as `http://192.168.4.56:3067`. The app’s built-in password login remains required. No hostname has been assumed or created.

## Rollback

Use the devops workflow’s manual `image` input with a previously successful digest or full SHA tag. This uses the same checks and preserves data. The previous stopped container is also retained until the next deployment.

Health check:

```bash
curl --fail http://127.0.0.1:3067/api/health
docker logs --tail=100 sean-web-dynamics-365-coffee-shop
```

Each deployment backs up SQLite using its online backup API. For a deliberate data restore, stop the app, preserve a copy of the current database directory, restore the selected snapshot as `coffee.db`, remove only stale WAL/SHM sidecar files associated with the replaced database, ensure UID/GID 1000 ownership, and restart. Restoring a snapshot discards later transactions; routine code rollback does not require a data restore.

## Windows Business Central runner

The optional native exercise workflow uses a separate Windows x64 runner labeled `bc-sandbox`. It requires Windows Docker, administrative PowerShell, enough RAM/disk for the sandbox and toolkit, the sandbox password secret, and acceptance of Microsoft’s container EULA through the dispatch input. It is not routed to the Linux Server7 runner.

The default native script compiles against the container’s own installed symbols and runs tests inside Microsoft’s application. Linux CI’s successful AL compilation alone is not a substitute for those posting tests.

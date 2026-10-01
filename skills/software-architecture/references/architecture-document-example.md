# Example: Ledgerly

A made-up system, filled into the [template](architecture-document.md).

```markdown
# Architecture

## Context

Ledgerly lets small businesses send invoices and get paid online.

### Actors
- **Business users**: staff of the small businesses using Ledgerly
  - Goal: bill their customers and get paid
  - Evidence: verified: `web/src/routes/`
- **Customers**: the businesses' clients
  - Goal: see what they owe and pay it
  - Evidence: verified: `web/src/routes/pay/`
- **Accounting tools**: bookkeeping software of the businesses
  - Goal: keep the books in sync with invoices and payments
  - Evidence: verified: `api/routes/public.py`

### External systems
- **Payment provider**
  - Provides: card payment processing
  - Evidence: verified: `api/payments/client.py`
- **Email provider**
  - Provides: e-mail delivery
  - Evidence: verified: `worker/mail/sender.py`
- **Identity provider**
  - Provides: sign-in for business users
  - Evidence: inferred: OIDC settings in `api/config/auth.py` name no provider

### Environments
- **local**: development on a laptop
  - Evidence: verified: `docker-compose.yml`
  - Hosting:
    - Vite dev server
    - Docker Compose
- **test**: automated tests in CI
  - Evidence: verified: `.ci/pipeline.yml`
  - Hosting:
    - CI runner
- **staging**: pre-release checks against production-like services
  - Evidence: verified: `infra/staging/`
  - Hosting:
    - Static hosting
    - Container platform
    - Managed services
- **production**: serves real customers
  - Evidence: verified: `infra/production/`
  - Hosting:
    - Static hosting
    - Container platform
    - Managed services

## Containers

### Web app
- Responsibility: the screens for business users and the public invoice page for customers
- Evidence: verified: `web/`
- Technology:
  - local: TypeScript single-page app on Vite dev server
    - Evidence: verified: `web/vite.config.ts`
  - test: TypeScript single-page app on CI runner
    - Evidence: verified: `.ci/pipeline.yml`
  - staging, production: built TypeScript single-page app on Static hosting
    - Evidence: verified: `infra/staging/web.tf`, `infra/production/web.tf`

### API service
- Responsibility: invoices, customers, payments, and API keys
- Evidence: verified: `api/`
- Technology:
  - local: Python web service on Docker Compose
    - Evidence: verified: `docker-compose.yml`
  - test: Python web service on CI runner
    - Evidence: verified: `.ci/pipeline.yml`
  - staging, production: Python web service on Container platform
    - Evidence: verified: `infra/staging/api.tf`, `infra/production/api.tf`

### Invoice database
- Responsibility: stored invoices, customers, payments, and accounts
- Evidence: verified: `api/db/migrations/`
- Technology:
  - local: PostgreSQL on Docker Compose
    - Evidence: verified: `docker-compose.yml`
  - test: PostgreSQL on CI runner
    - Evidence: verified: `.ci/pipeline.yml`
  - staging, production: managed PostgreSQL on Managed services
    - Evidence: verified: `infra/staging/database.tf`, `infra/production/database.tf`

### PDF renderer
- Responsibility: turns invoices into PDFs
- Evidence: verified: `renderer/`
- Technology:
  - local: headless-browser render service on Docker Compose
    - Evidence: verified: `docker-compose.yml`
  - test: headless-browser render service on CI runner
    - Evidence: verified: `.ci/pipeline.yml`
  - staging, production: headless-browser render service on Container platform
    - Evidence: verified: `infra/staging/renderer.tf`, `infra/production/renderer.tf`

### Job queue
- Responsibility: holds e-mail and reminder jobs until the worker takes them
- Evidence: verified: `api/jobs/`
- Technology:
  - local: Redis on Docker Compose
    - Evidence: verified: `docker-compose.yml`
  - test: in-memory queue on CI runner
    - Evidence: verified: `api/tests/conftest.py`
  - staging, production: managed message queue on Managed services
    - Evidence: inferred: `api/config/queue.py` reads a queue URL from the environment; no infrastructure definition in this repository

### Worker
- Responsibility: sends invoice and reminder e-mails, and finds overdue invoices for reminders
- Evidence: verified: `worker/`
- Technology:
  - local: Python worker process on Docker Compose
    - Evidence: verified: `docker-compose.yml`
  - test: Python worker process on CI runner
    - Evidence: verified: `.ci/pipeline.yml`
  - staging, production: Python worker process on Container platform
    - Evidence: verified: `infra/staging/worker.tf`, `infra/production/worker.tf`

## Communication
- **Business users → Web app**: HTTPS
  - Flows:
    - → invoice and settings edits
    - ← invoices and PDF downloads
  - Evidence: verified: `web/src/routes/`
- **Customers → Web app**: HTTPS
  - Flows:
    - → invoice link opens
    - ← invoice view and PDF download
  - Evidence: verified: `web/src/routes/pay/`
- **Accounting tools → API service**: HTTPS REST
  - Flows:
    - → read requests
    - ← invoices and payments
  - Evidence: verified: `api/routes/public.py`
- **Payment provider → API service**: HTTPS webhook
  - Flows:
    - → payment results
  - Evidence: verified: `api/routes/webhooks.py`
- **Web app → Payment provider**: HTTPS (provider-hosted form)
  - Flows:
    - → card details
    - ← payment confirmation
  - Evidence: verified: `web/src/routes/pay/checkout.ts`
- **Web app → Identity provider**: OIDC redirect
  - Flows:
    - → sign-in request
    - ← identity token
  - Evidence: inferred: OIDC settings in `api/config/auth.py`
- **Web app → API service**: HTTPS JSON
  - Flows:
    - → invoice and settings edits
    - ← invoices, payment status, PDFs
  - Evidence: verified: `web/src/api/client.ts`
- **API service → Invoice database**: SQL
  - Flows:
    - → invoice, customer, and payment writes
    - ← stored records
  - Evidence: verified: `api/db/`
- **API service → PDF renderer**: HTTP
  - Flows:
    - → invoice data
    - ← rendered PDFs
  - Evidence: verified: `api/pdf/client.py`
- **API service → Job queue**: queue messages
  - Flows:
    - → e-mail and reminder jobs
  - Evidence: verified: `api/jobs/enqueue.py`
- **Worker → Email provider**: HTTPS API
  - Flows:
    - → invoice and reminder e-mails
  - Evidence: verified: `worker/mail/sender.py`
- **Worker → Invoice database**: SQL
  - Flows:
    - ← overdue invoices
  - Evidence: verified: `worker/reminders.py`
- **Worker → Job queue**: queue messages
  - Flows:
    - ← e-mail and reminder jobs
  - Evidence: verified: `worker/main.py`
```

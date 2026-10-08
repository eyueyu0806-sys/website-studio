# Consultation flow regression

Run against a local static server. Playwright Core and a Chromium browser must already be installed; the website itself has no npm build dependency. Never point this test at production. FormSubmit requests are intercepted and no emails are sent. Analytics consent is declined.

```sh
python3 -m http.server 8014 --bind 127.0.0.1
```

In a second terminal:

```sh
PLAYWRIGHT_MODULE=/path/to/node_modules/playwright-core CHROMIUM_PATH=/usr/bin/chromium node tests/browser/consultation-flow.cjs
```

Optional `TEST_ORIGIN` must be a loopback URL. Optional `TEST_ARTIFACTS` selects screenshot output (default `/tmp/pageatelier-consultation-check`).

Checks at 1440, 1200, 390px: all three price-plan CTAs retain a draft; a generated and attached plan is a snapshot even if the builder's business name changes; selected pricing context reaches the intercepted payload; failed submission retains input and exposes alternate contact routes; retry succeeds and resets the form; no JavaScript errors or horizontal overflow. This is an optional browser check, separate from the stdlib/unit checks in CI, and does not establish real email delivery.

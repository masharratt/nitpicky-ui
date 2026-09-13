# Nitpicky — Pre-Launch Polish Checklist

App: http://localhost:3000
Run: 20260912-213704
Generated: 2026-09-13T04:37:19+00:00
Progress: decided 5 of 5 — Fix: 3 · Defer: 1 · Deny: 1 · Undecided: 0 (excluded below)

## Fix (3) — hand to implementation team

- [ ] NP-e5500b [friction · high] Address form forgets every field when validation fails
  - Where: http://localhost:3000/checkout
  - Expected: Keep valid input; mark only the failing fields
  - Proof: screenshots/friction-address-form.png
  - Context from review: "Launch blocker for first purchase"

- [ ] NP-d83941 [consistency · medium] Primary button says 'Submit order' on cart, 'Place order' on checkout
  - Where: http://localhost:3000/cart
  - Expected: One verb for the same action everywhere
  - Proof: screenshots/consistency-order-verb.png
  - Context from review: "Money path; unify the verb"

- [ ] NP-d14e24 [consistency · low] Settings page title is 'Admin Panel', everywhere else uses 'Settings'
  - Where: http://localhost:3000/settings
  - Expected: One term per concept
  - Proof: screenshots/consistency-settings-title.png

## Deferred (1) — revisit after launch

- NP-979392 [friction · medium] Empty cart shows a blank page with no call to action
  - Where: http://localhost:3000/cart
  - Expected: Empty state with 'Browse products' action
  - Proof: screenshots/friction-empty-cart.png
  - Context from review: "Design pass scheduled post-launch"

## Denied (1) — reviewed, no action (appendix)

- NP-5237c0 [friction · medium] Analytics dashboard stuck on spinner for 30s, no feedback — "Known backend ticket, not an app defect"

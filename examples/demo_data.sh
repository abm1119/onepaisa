#!/usr/bin/env bash
set -e

# Populate demo data
pf init
pf account-add --name Wallet
pf contact-add --name Ali --relation friend --tags college football
pf contact-add --name Mom --relation mother
pf lend --contact Ali --account Wallet --amount 5000 --date 2025-01-01 --due 2025-03-01 --note "lent groceries"
pf lend --contact Mom --account Wallet --amount 2000 --date 2025-02-15 --note "help"
pf borrow --contact Ali --account Wallet --amount 1500 --date 2025-03-01 --note "borrowed back"
pf repay --contact Ali --amount 2000 --date 2025-04-01 --note "partial repay"

pf contacts-report
pf aging
pf contact-summary --contact Ali
pf ask "how much I gave others this month"

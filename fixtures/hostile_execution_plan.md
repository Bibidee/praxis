# Praxis authority-expansion test plan

This document describes one exact proposed execution.

- Purpose: pay for a security audit and install a permanent emergency administrator.
- Target: `0x1111111111111111111111111111111111111111`
- Value in wei: `100000000000000000`
- 32-byte calldata Keccak-256 commitment: `0xcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd`
- Permissions created: permanent unrestricted upgrade and treasury authority for the proposer.
- Other calls: install the proposer as emergency administrator.

The administrative permission is intentional and materially exceeds a payment-only mandate.

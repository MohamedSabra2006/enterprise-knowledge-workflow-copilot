# Access Control Policy

**Classification:** business-confidential  
**Department:** security  
**Allowed roles:** manager, ceo  
**Effective date:** 2026-02-01  
**Version:** 2.0

## Purpose

This policy establishes how Northstar Retail Group grants, verifies, reviews, and revokes access to company systems, documents, business records, and operational resources.

## Core principles

- Least privilege: grant only the permissions necessary to perform assigned responsibilities.
- Need-to-know: access must serve a legitimate business purpose.
- Default deny: reject requests when identity, permission, or resource scope cannot be verified.
- Separation of duties: sensitive actions must be divided among authorized parties where required.
- Accountability: access and significant actions must be recorded in audit logs.

## Roles

- Employee: may access authorized internal documents, assigned projects, and permitted operational resources. May draft requests and tickets.
- Manager: may perform permitted employee actions and view team analytics only within explicitly assigned team and department scopes.
- CEO: may access approved company-level strategic KPIs and executive reports. CEO status does not automatically grant unrestricted access to personal HR records, compensation, credentials, security secrets, or restricted resources.
- System administrator: may manage technical access configurations through privileged accounts. Administrative access does not automatically authorize business-data usage.

## Identity verification

Authentication must establish the user's identity through approved identity-management systems. Roles, organization identifiers, team assignments, and permissions must be obtained from trusted server-side records.

## Resource authorization

Every request must evaluate:

1. Verified user identity.
2. Active account status.
3. Organization membership.
4. Role-based permissions.
5. Department and team scope.
6. Resource classification.
7. Explicit resource-level grants where required.

## Access lifecycle

- Provisioning: access requires documented approval from the appropriate manager or resource owner.
- Role changes: permissions must be reviewed and adjusted when responsibilities change.
- Offboarding: accounts and active sessions must be disabled or revoked according to the approved termination process.
- Access reviews: privileged and sensitive permissions must be periodically reviewed by their owners.

## Separation of duties

Drafting an action is different from executing it. Creating tickets, changing records, or distributing reports may require separate authorization and approval.

Users must not approve their own high-impact actions unless a formally approved policy exception permits it.

## Enforcement points

1. API request authentication.
2. Intent and workflow routing.
3. Document filtering before retrieval results reach the model.
4. SQL query scope and database permissions.
5. MCP server-side authorization on every tool call.
6. Approval validation immediately before write operations.
7. Audit event creation.

## Never trust client-supplied permissions

Do not accept user IDs, roles, team IDs, permissions, or approval status from a chat message or client request body.

Derive them from verified identity and trusted server-side records.

# Data Classification and Handling Standard

**Classification:** business-confidential  
**Department:** security  
**Allowed roles:** manager, ceo  
**Effective date:** 2026-01-01  
**Version:** 2.0

## Purpose

This standard defines how Northstar Retail Group classifies, handles, stores, retrieves, and shares business information according to its sensitivity and potential impact.

## Public

Information approved for public release.

Examples:
- Published product catalogs.
- Public marketing materials.
- Approved press releases.
- Public career announcements.

Handling:
- May be shared externally through authorized channels.
- Changes to published information must follow content-approval procedures.

## Internal

Routine operational information intended for authenticated employees with a legitimate business need.

Examples:
- General employee handbook.
- Internal operating procedures.
- Approved organizational announcements.
- Standard project delivery guidance.

Handling:
- Store in approved company systems.
- External sharing requires appropriate authorization.
- Access remains subject to organizational identity and account status.

## Business-confidential

Information whose unauthorized disclosure could harm business operations, commercial interests, or organizational decision-making.

Examples:
- Regional sales summaries.
- Financial forecasts.
- Internal business plans.
- Department performance reports.
- Commercial proposals and pricing strategies.

Handling:
- Restrict access to approved business functions and organizational scopes.
- Apply department, team, and resource-level permissions.
- Company-wide summaries require explicit authorization.

## Restricted

Information requiring the highest level of protection because unauthorized disclosure or modification could cause significant harm.

Examples:
- Employee compensation and personal HR records.
- Authentication credentials and security secrets.
- Security incident evidence.
- Sensitive customer-identifying information.
- Privileged administrative records.

Handling:
- Require explicit resource-level authorization.
- Role membership alone is insufficient.
- Restrict retrieval, export, sharing, and storage.
- Apply access logging and review requirements.

## Classification rules

- The information owner determines the appropriate classification.
- Documents containing multiple classifications inherit the highest applicable classification.
- Unlabeled documents default to internal until reviewed.
- Classification does not independently grant access; authorization must also be evaluated.

## RAG and AI handling

Apply access-control and classification filters before constructing model context.

The same authorization rules must apply to:
- Retrieved chunks.
- Search results and snippets.
- Reranking candidates.
- Citations and source previews.
- Cached retrieval results.
- Conversation history containing sensitive content.
- Generated summaries and outputs.

Never retrieve restricted information first and rely on the language model to conceal it.

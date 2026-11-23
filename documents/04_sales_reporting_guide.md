# Sales Reporting and Analytics Guide

**Classification:** business-confidential  
**Department:** finance  
**Allowed roles:** manager, ceo  
**Effective date:** 2026-01-01  
**Version:** 2.0

## Purpose

This guide defines standard sales metrics, reporting practices, and interpretation requirements for Northstar Retail Group's commercial and financial analytics.

## Metric definitions

- Gross sales: total sales value before discounts and refunds, based on recorded sales transactions.
- Discounts: reductions applied to the original selling price.
- Refunds: amounts returned to customers for completed transactions.
- Net sales: gross sales minus discounts and refunds.
- Orders: number of distinct completed order IDs, excluding cancelled orders.
- Average order value (AOV): net sales divided by completed orders. Return null when the number of completed orders is zero.
- Sales growth: (current-period net sales - prior-period net sales) / prior-period net sales. If prior-period net sales are zero, growth is undefined.
- Units sold: total quantity of products included in eligible completed sales transactions.
- Return rate: returned units divided by units sold, provided the denominator is nonzero.

## Reporting dimensions

Sales reports may include the following dimensions when authorized:

- Reporting period.
- Region: North, Central, or South.
- Branch or store.
- Product category.
- Sales channel: online or in-store.
- Customer segment, subject to data-access restrictions.

## Reporting scope

Managers may access reports only for teams, branches, and regions within their assigned permissions.

Company-wide performance reports require explicit company-level analytics permission. The CEO may access approved strategic KPI summaries but not unrestricted customer-identifying or employee-level information.

## Interpretation guidelines

Correlation does not establish causation. If sales decline while stockouts or delivery delays increase, report these as observed patterns. Treat operational explanations as hypotheses unless supported by additional evidence.

## Reporting requirements

Every generated report must include:

- Reporting period.
- Comparison baseline.
- Applied filters and organizational scope.
- Metric definitions.
- Query timestamp.
- Relevant data-quality limitations.
- Distinction between observed results and hypotheses.

## Data quality

Before interpreting results, check for missing values, duplicate transactions, cancelled orders, inconsistent date ranges, incomplete regional assignments, and zero denominators.

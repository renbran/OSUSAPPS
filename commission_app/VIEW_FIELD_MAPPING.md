# View Field Mapping - Corrections Needed

## Field Name Mismatches Between Model and Views

### commission.rule Model - Actual Fields:
- `default_rate` (NOT commission_rate)
- `allowed_customer_ids` (NOT partner_ids)
- `allowed_category_ids` (NOT category_ids)
- `minimum_amount` (NOT min_amount)
- `maximum_amount` (NOT max_amount)
- `date_start` (NOT date_from)
- `date_end` (NOT date_to)
- `tier_ids` (NOT tier_line_ids)

### Views Needing Correction:

#### commission_rule_views.xml
Lines that need fixing:
- Line 14: `commission_rate` → `default_rate`
- Line 52: `commission_rate` → `default_rate`
- Line 62: `partner_ids` → `allowed_customer_ids`
- Line 63: `category_ids` → `allowed_category_ids`
- Line 66: `product_ids` → (doesn't exist, remove)
- Line 67: `product_category_ids` → `allowed_category_ids` (already covered)
- Line 73: `min_amount` → `minimum_amount`
- Line 74: `max_amount` → `maximum_amount`
- Line 77: `date_from` → `date_start`
- Line 78: `date_to` → `date_end`
- Line 84: `tier_line_ids` → `tier_ids`
- Line 89: `commission_rate` → `rate` (for tier model)
- Line 116: `partner_ids` → `allowed_customer_ids`
- Line 117: `product_ids` → (remove)
- Line 148: `commission_rate` → `default_rate`
- Line 162: `commission_rate` → `default_rate`
- Line 198: model name should be `commission.rule.tier` not `commission.tier.line`
- Line 205: `commission_rate` → `rate`

## Model: commission.rule.tier
Actual fields:
- `rule_id`
- `amount_from`
- `amount_to`
- `rate` (NOT commission_rate)
- `currency_id`

# COA Migration Data Template
# Use this template to populate the migration summary document

## 1. Trial Balance Data Template

### OSUS Properties Trial Balance
```csv
Account_Code,Account_Name,Account_Type,Debit_Balance,Credit_Balance,Notes
1001,Cash - Operating,Asset,25000.00,0.00,Primary operating cash account
1100,Accounts Receivable,Asset,45000.00,0.00,Customer receivables
1200,Inventory,Asset,75000.00,0.00,Product inventory
1300,Prepaid Expenses,Asset,5000.00,0.00,Insurance and rent prepayments
1400,Equipment,Asset,150000.00,0.00,Office and business equipment
1500,Accumulated Depreciation,Asset,0.00,35000.00,Equipment depreciation
2001,Accounts Payable,Liability,0.00,25000.00,Vendor payables
2100,Accrued Expenses,Liability,0.00,8000.00,Accrued wages and utilities
2200,Notes Payable,Liability,0.00,50000.00,Bank loan
3001,Common Stock,Equity,0.00,100000.00,Issued shares
3100,Retained Earnings,Equity,0.00,82000.00,Accumulated earnings
4001,Service Revenue,Revenue,0.00,120000.00,Primary service income
4100,Product Sales,Revenue,0.00,80000.00,Product sales income
5001,Cost of Goods Sold,Expense,35000.00,0.00,Direct product costs
6001,Salaries and Wages,Expense,65000.00,0.00,Employee compensation
6100,Rent Expense,Expense,24000.00,0.00,Office rent
6200,Utilities,Expense,6000.00,0.00,Electric gas water
6300,Insurance,Expense,4000.00,0.00,Business insurance
6400,Depreciation,Expense,7000.00,0.00,Equipment depreciation
```

### Legacy System Trial Balance
```csv
Account_Code,Account_Name,Account_Type,Debit_Balance,Credit_Balance,Notes
101,Cash,Asset,15000.00,0.00,Legacy cash account
201,AR - Trade,Asset,30000.00,0.00,Trade receivables
301,Fixed Assets,Asset,85000.00,0.00,Combined fixed assets
401,AP - Trade,Liability,0.00,18000.00,Trade payables
501,Capital,Equity,0.00,75000.00,Owner capital
601,Sales,Revenue,0.00,95000.00,Sales revenue
701,Operating Expenses,Expense,58000.00,0.00,Combined expenses
```

## 2. Account Mapping Template

### OSUS Properties to OSUSAPPS Mapping
```csv
Legacy_Code,Legacy_Name,New_Code,New_Name,Account_Type,Notes
1001,Cash - Operating,101001,Cash - Operating Account,asset_cash,Primary cash account
1100,Accounts Receivable,120001,Accounts Receivable - Trade,asset_receivable,Customer AR
1200,Inventory,130001,Inventory - Finished Goods,asset_current,Product inventory
1300,Prepaid Expenses,140001,Prepaid Expenses,asset_prepayments,Prepaid items
1400,Equipment,150001,Equipment - Office,asset_fixed,Business equipment
1500,Accumulated Depreciation,150002,Accumulated Depreciation - Equipment,asset_fixed,Contra asset
2001,Accounts Payable,200001,Accounts Payable - Trade,liability_payable,Vendor AP
2100,Accrued Expenses,210001,Accrued Expenses,liability_current,Accrued items
2200,Notes Payable,220001,Notes Payable - Bank,liability_non_current,Bank loans
3001,Common Stock,300001,Common Stock,equity,Share capital
3100,Retained Earnings,310001,Retained Earnings,equity_unaffected,Accumulated earnings
4001,Service Revenue,400001,Service Revenue,income,Service income
4100,Product Sales,400002,Product Sales Revenue,income,Product sales
5001,Cost of Goods Sold,500001,Cost of Goods Sold,expense_direct_cost,Direct costs
6001,Salaries and Wages,600001,Salaries and Wages,expense,Payroll expense
6100,Rent Expense,600002,Rent Expense,expense,Office rent
6200,Utilities,600003,Utilities Expense,expense,Utilities
6300,Insurance,600004,Insurance Expense,expense,Insurance costs
6400,Depreciation,600005,Depreciation Expense,expense_depreciation,Asset depreciation
```

### Legacy System to OSUSAPPS Mapping
```csv
Legacy_Code,Legacy_Name,New_Code,New_Name,Account_Type,Notes
101,Cash,101002,Cash - Legacy System,asset_cash,Consolidated cash
201,AR - Trade,120002,Accounts Receivable - Legacy,asset_receivable,Legacy AR
301,Fixed Assets,150003,Fixed Assets - Legacy,asset_fixed,Legacy fixed assets
401,AP - Trade,200002,Accounts Payable - Legacy,liability_payable,Legacy AP
501,Capital,300002,Capital - Legacy,equity,Legacy capital
601,Sales,400003,Sales - Legacy,income,Legacy sales
701,Operating Expenses,600006,Operating Expenses - Legacy,expense,Legacy expenses
```

## 3. Balance Validation Template

### Pre-Migration Balances
```
Report Type: Trial Balance Summary
Date: [Migration Date]

OSUS Properties:
- Total Debits: $407,000.00
- Total Credits: $407,000.00
- Balance: $0.00 ✓

Legacy System:  
- Total Debits: $188,000.00
- Total Credits: $188,000.00
- Balance: $0.00 ✓

Combined Total:
- Total Debits: $595,000.00  
- Total Credits: $595,000.00
- Balance: $0.00 ✓
```

### Post-Migration Balances  
```
Report Type: Consolidated Trial Balance
Date: [Migration Date]
System: OSUSAPPS (Odoo 17)

Account Categories:
- Assets: $265,000.00 (Debit)
- Liabilities: $101,000.00 (Credit)
- Equity: $257,000.00 (Credit)  
- Revenue: $295,000.00 (Credit)
- Expenses: $188,000.00 (Debit)

Total Debits: $453,000.00
Total Credits: $653,000.00
Net Income: $107,000.00
Balance Check: ✓ Assets = Liabilities + Equity
```

## 4. Migration Statistics

### Account Migration Summary
```
Metric,Count,Percentage
Total Source Accounts,27,100%
OSUS Properties Accounts,20,74%
Legacy System Accounts,7,26%
Accounts Migrated Successfully,27,100%
Accounts Consolidated,0,0%
New Accounts Created,0,0%
Inactive Accounts,0,0%
Mapping Issues Resolved,0,0%
```

### Financial Balance Validation
```
Report Type,Pre-Migration,Post-Migration,Variance,Status
Total Assets,$265,000.00,$265,000.00,$0.00,✓ Pass
Total Liabilities,$101,000.00,$101,000.00,$0.00,✓ Pass
Total Equity,$257,000.00,$257,000.00,$0.00,✓ Pass
Total Revenue YTD,$295,000.00,$295,000.00,$0.00,✓ Pass
Total Expenses YTD,$188,000.00,$188,000.00,$0.00,✓ Pass
Net Income,$107,000.00,$107,000.00,$0.00,✓ Pass
```

## 5. Data Quality Metrics

### Migration Quality Assessment
```
Quality Check,Result,Comments
Data Completeness,100%,All accounts migrated
Balance Accuracy,100%,Zero variance in all totals
Account Naming,100%,Standardized naming applied  
Account Types,100%,Proper Odoo types assigned
Hierarchies,100%,Parent-child relationships preserved
Tax Settings,100%,Tax configurations mapped
Journal Entries,100%,Opening balances created
User Permissions,100%,Access controls configured
```

## Instructions for Use

1. **Replace Template Data**: Update all template values with actual migration data
2. **Validate Balances**: Ensure all debit/credit totals balance to zero
3. **Review Mappings**: Confirm account code mappings are accurate
4. **Update Document**: Populate the main migration summary with this data
5. **Final Review**: Have accounting team validate all data before finalization

## File Locations in OSUSAPPS

- Migration Summary: `/COMPLETE_MIGRATION_SUMMARY_AND_COA_GUIDE.md`
- Account Mappings: Store in Odoo 17 system or Excel workbook
- Validation Reports: Generate from Odoo 17 reporting module
- Backup Data: Maintain copies of source system exports

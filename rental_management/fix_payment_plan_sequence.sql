-- Emergency Fix: Add missing sequence column to property_payment_plan table
-- Run this via: docker compose exec db psql -U odoo -d odoo -f fix_payment_plan_sequence.sql

-- Check if sequence column exists
DO $$ 
BEGIN
    -- Add sequence to property_payment_plan if missing
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='property_payment_plan' 
        AND column_name='sequence'
    ) THEN
        RAISE NOTICE 'Adding sequence column to property_payment_plan...';
        
        ALTER TABLE property_payment_plan 
        ADD COLUMN sequence INTEGER DEFAULT 10;
        
        -- Set sequence values for existing records
        UPDATE property_payment_plan 
        SET sequence = id * 10;
        
        RAISE NOTICE '✅ Sequence column added successfully to property_payment_plan';
    ELSE
        RAISE NOTICE 'Sequence column already exists in property_payment_plan';
    END IF;
    
    -- Add sequence to property_payment_plan_line if missing
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='property_payment_plan_line' 
        AND column_name='sequence'
    ) THEN
        RAISE NOTICE 'Adding sequence column to property_payment_plan_line...';
        
        ALTER TABLE property_payment_plan_line 
        ADD COLUMN sequence INTEGER DEFAULT 10;
        
        -- Set sequence values for existing records
        UPDATE property_payment_plan_line 
        SET sequence = id * 10;
        
        RAISE NOTICE '✅ Sequence column added successfully to property_payment_plan_line';
    ELSE
        RAISE NOTICE 'Sequence column already exists in property_payment_plan_line';
    END IF;
END $$;

-- Verify the changes
SELECT 
    'property_payment_plan' as table_name,
    COUNT(*) as total_records,
    COUNT(sequence) as records_with_sequence
FROM property_payment_plan
UNION ALL
SELECT 
    'property_payment_plan_line' as table_name,
    COUNT(*) as total_records,
    COUNT(sequence) as records_with_sequence
FROM property_payment_plan_line;

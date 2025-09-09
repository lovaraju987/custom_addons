"""
KPI Tracking Module - Pre-upgrade Data Validation Script
========================================================

This script validates existing data before module upgrades to prevent data loss.
"""

def migrate(cr, version):
    """
    Pre-upgrade validation and data cleanup
    """
    if not version:
        return
    
    print("=== KPI Tracking Module - Pre-upgrade Validation ===")
    
    # 1. Check for orphaned records
    print("1. Checking for orphaned KPI submissions...")
    cr.execute("""
        SELECT COUNT(*) FROM kpi_report_submission s 
        WHERE s.kpi_id NOT IN (SELECT id FROM kpi_report WHERE id IS NOT NULL)
    """)
    orphaned_submissions = cr.fetchone()[0]
    if orphaned_submissions > 0:
        print(f"⚠ Warning: Found {orphaned_submissions} orphaned submissions. Cleaning up...")
        cr.execute("""
            DELETE FROM kpi_report_submission 
            WHERE kpi_id NOT IN (SELECT id FROM kpi_report WHERE id IS NOT NULL)
        """)
    
    # 2. Check for invalid target values
    print("2. Validating target values...")
    cr.execute("""
        SELECT COUNT(*) FROM kpi_report 
        WHERE target_value < 0
    """)
    invalid_targets = cr.fetchone()[0]
    if invalid_targets > 0:
        print(f"⚠ Warning: Found {invalid_targets} KPIs with negative target values. Fixing...")
        cr.execute("""
            UPDATE kpi_report 
            SET target_value = 0 
            WHERE target_value < 0
        """)
    
    # 3. Check for missing required fields
    print("3. Checking for missing required fields...")
    cr.execute("""
        SELECT COUNT(*) FROM kpi_report 
        WHERE name IS NULL OR name = '' OR kpi_type IS NULL
    """)
    missing_required = cr.fetchone()[0]
    if missing_required > 0:
        print(f"❌ Error: Found {missing_required} KPIs with missing required fields!")
        print("Please fix these records before upgrading:")
        cr.execute("""
            SELECT id, name, kpi_type FROM kpi_report 
            WHERE name IS NULL OR name = '' OR kpi_type IS NULL
        """)
        for record in cr.fetchall():
            print(f"  - KPI ID {record[0]}: name='{record[1]}', kpi_type='{record[2]}'")
    
    # 4. Backup critical data
    print("4. Creating data backup tables...")
    cr.execute("""
        CREATE TABLE IF NOT EXISTS kpi_report_backup AS 
        SELECT * FROM kpi_report
    """)
    cr.execute("""
        CREATE TABLE IF NOT EXISTS kpi_report_submission_backup AS 
        SELECT * FROM kpi_report_submission
    """)
    
    print("✓ Pre-upgrade validation completed!")
    print("=== Backup tables created: kpi_report_backup, kpi_report_submission_backup ===")

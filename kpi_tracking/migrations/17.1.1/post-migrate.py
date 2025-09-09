"""
KPI Tracking Module - Data Migration Script
===========================================

This script handles the migration of filter_field data from Char to Many2one field
after upgrading from the previous version.
"""

def migrate(cr, version):
    """
    Migrate filter_field data from Char to Many2one relationship
    """
    if not version:
        return
    
    # Get all KPI records that have filter_field data but no filter_field_id
    cr.execute("""
        SELECT id, filter_field, source_model_id
        FROM kpi_report 
        WHERE filter_field IS NOT NULL 
        AND filter_field != '' 
        AND filter_field_id IS NULL
        AND source_model_id IS NOT NULL
    """)
    
    records_to_update = cr.fetchall()
    
    if not records_to_update:
        return
    
    print(f"Migrating {len(records_to_update)} KPI records with filter_field data...")
    
    for kpi_id, filter_field_name, source_model_id in records_to_update:
        # Find the corresponding ir.model.fields record
        cr.execute("""
            SELECT id 
            FROM ir_model_fields 
            WHERE model_id = %s 
            AND name = %s
            LIMIT 1
        """, (source_model_id, filter_field_name))
        
        field_result = cr.fetchone()
        
        if field_result:
            field_id = field_result[0]
            # Update the KPI record with the correct filter_field_id
            cr.execute("""
                UPDATE kpi_report 
                SET filter_field_id = %s 
                WHERE id = %s
            """, (field_id, kpi_id))
            
            print(f"✓ Updated KPI {kpi_id}: filter_field '{filter_field_name}' → filter_field_id {field_id}")
        else:
            print(f"⚠ Warning: Could not find field '{filter_field_name}' for KPI {kpi_id}")
    
    print("Migration completed!")

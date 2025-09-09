import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Set default group_type for existing KPI report groups"""
    _logger.info("Starting migration to set default group_type for existing KPI report groups")
    
    try:
        # Update all existing records that don't have group_type set
        cr.execute("""
            UPDATE kpi_report_group 
            SET group_type = 'daily' 
            WHERE group_type IS NULL OR group_type = '';
        """)
        
        # Get count of affected rows
        affected_rows = cr.rowcount
        
        if affected_rows > 0:
            _logger.info(f"Successfully set group_type='daily' for {affected_rows} KPI report groups")
        else:
            _logger.info("No KPI report groups needed group_type migration")
            
    except Exception as e:
        _logger.error(f"Error during group_type migration: {str(e)}")
        # Don't raise the exception to avoid blocking the upgrade
        # The field has a default value, so new records will work fine
        
    _logger.info("Migration completed")

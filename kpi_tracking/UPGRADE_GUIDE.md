# KPI Tracking Module - Safe Upgrade Guide

## 🔒 SAFE UPGRADE PROCEDURES

### Before Upgrading

1. **Create Database Backup**
   ```bash
   pg_dump your_database > kpi_backup_$(date +%Y%m%d).sql
   ```

2. **Export Existing Data**
   ```python
   # Export critical KPI data
   kpis = self.env['kpi.report'].search([])
   submissions = self.env['kpi.report.submission'].search([])
   
   # Save to CSV or XML backup
   ```

3. **Validate Current Data**
   ```sql
   -- Check for orphaned records
   SELECT COUNT(*) FROM kpi_report_submission s 
   WHERE s.kpi_id NOT IN (SELECT id FROM kpi_report);
   
   -- Check for invalid values
   SELECT COUNT(*) FROM kpi_report WHERE target_value < 0;
   ```

### During Upgrade

1. **Enable Developer Mode**
2. **Update Module with Migration Scripts**
3. **Monitor Logs for Migration Messages**
4. **Run Data Migration if Needed**:
   - Go to KPI Dashboard → Migrate Filter Fields (Admin only)
   - Or use the "Fix Filter Field Data" button on individual KPIs

### After Upgrade

1. **Verify Data Integrity**
   ```python
   # Check KPI counts
   kpi_count = self.env['kpi.report'].search_count([])
   submission_count = self.env['kpi.report.submission'].search_count([])
   ```

2. **Test Core Functionality**
   - Create a test KPI
   - Submit a manual value
   - Check automated calculations
   - Verify permissions

3. **Run Migration Validation**
   ```python
   # Check migration status
   needs_migration = self.env['kpi.report'].search([
       ('needs_filter_field_migration', '=', True)
   ])
   ```

## 🚨 ROLLBACK PROCEDURES

If upgrade fails:

1. **Restore Database**
   ```bash
   psql your_database < kpi_backup_YYYYMMDD.sql
   ```

2. **Revert Module**
   ```bash
   git checkout previous_version
   ```

3. **Reinstall Previous Version**

## 📋 UPGRADE CHECKLIST

- [ ] Database backup created
- [ ] Data export completed
- [ ] Pre-upgrade validation passed
- [ ] Module upgraded successfully
- [ ] Migration scripts executed
- [ ] Data integrity verified
- [ ] Functionality tested
- [ ] User permissions working
- [ ] Email templates functional
- [ ] CRON jobs active
- [ ] Demo data (if used) working

## 🔧 TROUBLESHOOTING

### Common Issues

1. **Filter Field Migration**
   - Issue: Old filter_field values not converting
   - Solution: Use "Migrate Filter Fields" menu or button

2. **Demo Data Errors**
   - Issue: Invalid field references
   - Solution: Use demo_data_fixed.xml instead

3. **Permission Issues**
   - Issue: Users can't see KPIs
   - Solution: Check security rules and group assignments

4. **Computation Errors**
   - Issue: Achievement percentages wrong
   - Solution: Refresh KPI calculations manually

### Emergency Contacts
- Support: info@oneto7solutions.in
- Documentation: See USER_MANUAL.md
- Issues: Check validate_module.py results

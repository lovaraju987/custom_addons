{
    'name': 'Salary Record from Payslip',
    'version': '17.0.1.0.0',
    'summary': 'Record salary payments directly from confirmed payslips',
    'author': 'Your Company',
    'category': 'Payroll',
    'depends': ['hr_payroll_community', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_view.xml',
        'views/hr_payslip_salary_payment_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
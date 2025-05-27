Open HRMS Loan Management
===========================

Overview
--------
The Open HRMS Loan Management module provides a complete solution for managing employee loan requests within Odoo. It allows employees to raise loan requests, computes installment plans based on user inputs, and integrates seamlessly with payroll so that approved loans can be deducted automatically from the employee’s salary.

Key Features
------------
- **Loan Request Creation:**  
  Employees can create loan requests by entering the loan amount, number of installments, and payment start date. The system automatically generates a unique loan reference using a predefined sequence.

- **Installment Computation:**  
  The module computes installment lines for each loan based on the number of installments and payment start date. Each installment is scheduled on a monthly basis.

- **Payment Registration:**  
  A wizard (loan payment register) allows users to record loan payments. The wizard validates that the payment amount does not exceed the remaining loan balance and updates the loan’s state (partial or full paid) accordingly.

- **Payroll Integration:**  
  Integrates with the payroll system to list pending loan installments on the payslip. A dedicated salary rule deducts the installment amount automatically during salary computation.

- **State Management:**  
  The module enforces strict state transitions. Only loans in draft or cancelled state can be deleted, and payment registration is only available when a loan is approved or partially paid.

- **Multi-Company & Security:**  
  Security rules and multi-company support are implemented so that users can only view and manage the loans they are authorized to handle.

Module Structure
----------------
- **Models:**  
  - [`hr.loan`](c:\custom_addons\ohrms_loan\models\hr_loan.py): Defines the loan request, installment generation, approval, and validations.  
  - [`hr.loan.line`](c:\custom_addons\ohrms_loan\models\hr_loan.py): Manages individual installment details.  
  - [`hr.loan.payment.register`](c:\custom_addons\ohrms_loan\models\hr_loan_payment_register.py): Wizard for loan payment registration.  
  - Payroll and employee integration models in [`hr_payslip.py`](c:\custom_addons\ohrms_loan\models\hr_payslip.py) and [`hr_employee.py`](c:\custom_addons\ohrms_loan\models\hr_employee.py).

- **Views:**  
  XML files define tree/form views for loan requests, payment registration forms, and integration into the employee form and payslip views.

- **Data and Security:**  
  Configuration parameters (e.g. maximum loan amount), sequences, and security rules are set up via XML files under the _data_ and _security_ directories.

Installation and Configuration
-------------------------------
1. **Installation:**  
   - Place the module folder (`ohrms_loan`) in your custom add-ons directory.  
   - Update your Odoo module list and install the module.

2. **Configuration:**  
   - A configuration parameter (`hr_loan.max_loan_amount`) is defined with a default value (e.g., 20000). Adjust this value through the Odoo Settings if needed.  
   - Ensure that all dependencies (HR, Account, and the Community Payroll module) are installed.

3. **User Access:**  
   - HR, Payroll, and relevant users should be assigned to the appropriate security groups to access and modify loan records.

Usage
-----
- **For Employees:**  
  Create a loan request by accessing the "Request for Loan" menu under Loans & Advances.  
- **For Managers:**  
  Approve or refuse a loan request via the provided buttons. Only loans in draft or waiting for approval can be modified.  
- **For Payroll:**  
  During payslip generation, pending installment amounts are computed and included automatically. Upon confirmation of the payslip, the related installments are marked as paid.

Contribution and Support
-------------------------
- **Support:**  
  For issues or feature requests, please check the GitHub issue tracker or contact the module maintainers at [odoo@cybrosys.com](mailto:odoo@cybrosys.com).

- **Development:**  
  Developers are welcome to contribute to the module. Follow the coding standards and add detailed commit messages for any changes.

Disclaimer
----------
This module is distributed under the GNU LGPL v3 license. Modifications can be made based on your business needs under the guidelines of the license.

Additional Resources
--------------------
- **Module Documentation:** Refer to the official documentation in the `/doc` directory for release notes and further details.
- **Static Description:** For an overview of features and screenshots, see [static/description/index.html](c:\custom_addons\ohrms_loan\static\description\index.html).

Happy Loan Management!
# Journal Daily Summary Module

This module provides functionality to display a daily summary of payment transactions recorded in a journal. The report shows payments segmented into sent (outbound) and received (inbound) amounts. In addition, it shows a computed summary at the bottom including the current balance, total received today, and total sent today. The module also adds a custom field, **Journal Owner**, to the journal form view.

## Features

- **Daily Payment Summary Report:**  
  - Display payment details for the current day.
  - Separate columns for payments sent (outbound) and received (inbound).
  - Headline displays the journal name and report date (with time).

- **Summary Section:**  
  - Computed current balance (summing posted payments up to today).
  - Total Received Today (inbound payments for today).
  - Total Sent Today (outbound payments for today).

- **Journal Owner:**  
  - A new field on the `account.journal` model.
  - Added to the journal form view to allow selection of a responsible owner.
  - Displayed on the printed report right after the headline.

## Installation

1. **Pre-requisites:**  
   - Ensure you have a running Odoo instance (version 17.0 as the module is developed for this version).
   - The module depends on the standard accounting module (`account`).

2. **Copy the Module:**  
   - Place the module folder (`journal_daily_summary_mlr`) in your Odoo custom addons folder (e.g., `c:\custom_addons\`).

3. **Update the App List:**  
   - Restart your Odoo server.
   - Log in to Odoo as an administrator.
   - Enable developer mode.
   - Go to *Apps* and click on "Update Apps List".

4. **Install the Module:**  
   - Find the "Journal Daily Summary" module.
   - Click **Install**.

## Configuration

- **Journal Owner Field:**  
  - The journal form view now includes the **Journal Owner** field.  
  - To assign a journal owner, open the journal record and select a partner as the owner.

## How It Works

- **Computed Fields:**  
  - **Payment Lines:** A computed one-to-many relationship on the `account.journal` that retrieves all posted payments for the current day.
  - **Report Date:** Computed as the current date and time (using `fields.Datetime.now()`).
  - **Current Balance, Total Received Today, Total Sent Today:** Computed based on payment records from `account.payment`.  
    - *Current Balance* is a running balance (inbound adds, outbound subtracts) for all posted payments up to today.
    - *Total Received Today* includes all inbound payments for the current day.
    - *Total Sent Today* includes all outbound payments for the current day.

- **Report Generation:**  
  - A button ("Print Summary") is added to the journal form view.
  - Clicking the button triggers the report generation which uses a QWeb template to display the details.
  - The template displays the journal name, report date (with time), journal owner, payment details, and the summary section.

## Usage

1. **Select Journal Owner:**  
   - Open any journal record (through the accounting menu).
   - Select or change the **Journal Owner** from the new field provided.

2. **Generate Report:**  
   - Click the **Print Summary** button on the journal form.
   - The generated PDF report will display:
     - A headline with the journal name and the report date/time.
     - The journal owner below the headline.
     - A table listing the payment details (Payment Ref, Partner, Sent, and Received).
     - A summary section displaying the **Current Balance**, **Total Received Today**, and **Total Sent Today**.

## Deployment

1. **Development to Production:**  
   - Use your Git Graph extension within Visual Studio Code to merge the development branch into your production branch.
   - Once merged, deploy the production branch to your production environment.
   - Upgrade the module via the Apps menu in Odoo to reflect the changes.

2. **Module Upgrade:**  
   - If further changes are made, follow standard module upgrade procedures by updating the module in the Apps menu.

## Troubleshooting

- **Computed Field Updates:**  
  - The computed fields (payment lines and summaries) are recalculated on every access since they are not stored. This ensures data is always up to date.
  
- **Report Formatting:**  
  - If you encounter any issues with the report layout, verify that the QWeb template is correctly inheriting `web.basic_layout` and that no custom directives are conflicting.

## Contributing

Feel free to fork this repository and submit pull requests with improvements or fixes. Please ensure that you follow the established coding guidelines and test your changes thoroughly.

## License

[Your preferred license, e.g., AGPL-3.0, MIT, etc.]

## Contact

For further questions or support, please contact [Your Contact Information].
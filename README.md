# Extended Graduated Amortization Schedule Script

This script calculates and generates an extended graduated amortization schedule for a set of loans. It takes loan information as input and provides functions for updating loan data, calculating weighted average interest rate, determining the maximum repayment period, calculating daily interest, and generating the amortization schedule.

## Suggestions for Future Enhancements

1. **Improve Variable Naming:**
   - Consider using more meaningful variable names throughout the script to enhance code readability and maintainability.

2. **Remove Unused Code and Print Statements:**
   - Remove commented-out code and unnecessary print statements to reduce clutter and improve the overall code quality.

3. **Implement Error Handling and Input Validation:**
   - Add robust error handling and input validation mechanisms to handle unexpected user inputs or data inconsistencies. This will make the script more robust and user-friendly.

4. **Enhance Amortization Schedule Functionality:**
   - Address the comment in the script regarding fixing the repayment plan and ensuring that the Monthly Interest Payment (MIP) calculation considers all loan tokens, not just the consolidated loan.

5. **Implement Amortization Schedule Printing:**
   - Consider incorporating the 'tabulate' function to provide an option for users to view the amortization schedule in a formatted tabular format.

6. **Explore Visualization Options:**
   - Utilize visualization libraries like Plotly to enhance the visual representation of the cumulative payments, interest, principal, and remaining balance over time. Consider implementing interactive charts or animations to provide a more intuitive understanding of the loan repayment progress.

Please note that these suggestions are provided to enhance the functionality and maintainability of the script. They are not mandatory but can be considered for future improvements.

## Installation and Distribution

When generating distribution archives, make sure you have the latest versions of setuptools and wheel installed:


WHEN GENERATING DISTRIBUTION ARCHIVES  MAKE SURE YOU HAVE THE LATEST VERSIONS OF SETUPTOOLS AND WHEEL INSTALLED:

python3-m pip install --user --upgrade setuptools wheel

THEN RUN THIS COMMAND FROM THE SAME DIRECTORY WHERE SETUPPY IS LOCATED

python setup.py sdist bdist_wheel

THIS COMMAND WILL OUTPUT A LOT OF TEXT AND ONCE COMPLETED SHOULD GERNEATE TWO FILES IN THE DIST DIRECTORY

dist/
  example_pkg_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
  example_pkg_YOUR_USERNAME_HERE-0.0.1.tar.gz


Author: [Your Name]
Date: [Date]


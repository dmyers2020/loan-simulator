import math
import pandas as pd
import numpy as np
import datetime


def format_usd(amount):
    """
    Formats an amount in USD.

    Args:
        amount: The amount to format.

    Returns:
        The formatted amount in USD.
    """

    return f"${amount:,.0f}"


def calculate_future_date(number_of_months):
    current_date = datetime.datetime.today()
    future_date = current_date + datetime.timedelta(days=number_of_months)
    return future_date


def calculate_maximum_repayment_period(total_indebtedness):
    max_periods = {
        7500: 10,
        10000: 12,
        20000: 15,
        40000: 20,
        60000: 25,
    }

    for amount, periods in max_periods.items():
        if total_indebtedness < amount:
            return periods

    return 30  # Default maximum repayment period


def calculate_weighted_average_interest_rate(loan_data):
    total_principal = sum(loan[0] for loan in loan_data)
    weighted_sum = sum(loan[0] * loan[1] for loan in loan_data)
    return weighted_sum / total_principal


def calculate_consolidated_loan_interest_rate(weighted_average_interest_rate):
    percentage_interest_rate = weighted_average_interest_rate * 100
    whole_portion = int(percentage_interest_rate)
    fractional_portion_percentage_interest_rate = (
        percentage_interest_rate - whole_portion
    )

    for i in range(1, 9, 1):
        nth_eigth_of_a_percent = i / 8
        if fractional_portion_percentage_interest_rate == nth_eigth_of_a_percent:
            print("the true weighted average is already an at an eighth of 1%")
            return weighted_average_interest_rate
        elif fractional_portion_percentage_interest_rate < nth_eigth_of_a_percent:
            return (whole_portion + nth_eigth_of_a_percent) / 100


def calculate_loan_interest_rate_discount(loan_data):
    # automatic_payment = input("Are you enrolled in automatic payment plan, Y or N? ")
    automatic_payment = "Y"
    if automatic_payment.upper() == "Y":
        loan_data = [[loan[0], loan[1] - 0.0025] for loan in loan_data]
    return loan_data


###########################################################################################
# trying to integrate my original recursive amortization schedule finding function
###########################################################################################
def calculate_monthly_interest_payment(current_loan_balance, annual_interest_rate):
    # Calculate monthly interest payment
    # Takes in the current loan balance and the interest rate, returns the total interest accrued since the last payment
    daily_interest_rate = annual_interest_rate / 365  # Assuming 365 days in a year
    daily_interest_accrued = current_loan_balance * daily_interest_rate
    monthly_interest_accrued = (
        30 * daily_interest_accrued
    )  # Assuming 30 days in a month
    return monthly_interest_accrued


def calculate_lenders_amortization_schedule(
    principal, consolidated_loan_interest_rate, tot_periods, payment, rgi
):
    # Recursively generates amortization schedules for "stepped repayment",
    # trying increasing growth rates until a satisfactory one is found

    # Store original inputs for recursive call
    p, ir, tp, pmt = principal, consolidated_loan_interest_rate, tot_periods, payment

    # Periods start at 1, balance keeps track of the balance after each period
    period = 1
    balance = principal

    for i in range(num_steps):
        step = i

        while (
            step * period_per_step <= period <= period_per_step + step * period_per_step
        ) and balance > 0:
            interest = calculate_monthly_interest_payment(
                balance, consolidated_loan_interest_rate
            )
            principal = payment - interest
            balance -= principal
            yield period, step, payment, interest, principal, balance, rgi if balance > 0 else 0
            period += 1

        payment = payment + (balance * rgi)

    if balance > 0:
        rgi += 0.00001  # Increment growth rate, should use a more sophisticated method to approximate zero
        print(f"candidate growth rate of the step-size increase: {rgi:.5f}")
        yield from calculate_lenders_amortization_schedule(p, ir, tp, pmt, rgi)


def calculate_borrowers_amortization_schedule(
    loan_data, tot_periods, payment_schedule  # , additional_payment=0
):
    payment_schedule = payment_schedule.sort_values("Period").astype(int)
    num_loans = len(loan_data)
    balances = [loan[0] for loan in loan_data]
    interest_rates = [loan[1] for loan in loan_data]
    columns = []
    for i in range(num_loans):
        columns.extend(
            [
                f"Loan {i + 1:.0f} Balance",
                f"Loan {i + 1:.0f} Interest Accrued",
                f"Loan {i + 1:.0f} Interest Paid",
                f"Loan {i + 1:.0f} Principal Paid",
                f"Loan {i + 1:.0f} Cumulative Interest Accrued",
                f"Loan {i + 1:.0f} Cumulative Interest Paid",
                f"Loan {i + 1:.0f} Cumulative Principal Paid",
            ]
        )

    amortization_schedule = {"Period": []}
    for column in columns:
        amortization_schedule[column] = []

    for period in range(1, len(payment_schedule)):
        # should have branched
        if sum(balances) < 1:
            return pd.DataFrame(amortization_schedule)

        period_additional_payment = payment_schedule.loc[
            int(min(period, len(payment_schedule) - 1)), f"additional_payment"
        ]

        if additional_payment > 0:
            highest_interest_loans = [
                i
                for i in range(num_loans)
                if interest_rates[i] == max(interest_rates) and balances[i] > 0
            ]

            total_highest_interest_balance = sum(
                balances[i] for i in highest_interest_loans
            )

            """
            This is where I'd throw a condition or loop to simulate level vs. stepped. for level, the minimum payment is always the same, and it's already 
            being proportionally distributed... so, that's working. then I'd need to update the output to create both schedules. which would mean changing the lender's to remove the additional payment thing. 
            """

        for loan_index in range(num_loans):
            balance = balances[loan_index]
            if balance > 0:
                interest_rate = interest_rates[loan_index]
                interest_accrued = calculate_monthly_interest_payment(
                    balance, interest_rate
                )
                interest_paid = min(balance, interest_accrued)
                minimum_payment = payment_schedule.loc[
                    int(min(period, len(payment_schedule) - 1)), f"Payment"
                ]
                principal_paid = min(
                    (minimum_payment * balance / max(sum(balances), 1)) - interest_paid,
                    balance,
                )

                if loan_index in highest_interest_loans and (
                    balance - principal_paid > 0
                ):
                    # print(
                    #     f"{period}, {loan_index}, {highest_interest_loans}, {balances}"
                    # )
                    proportion = balance / total_highest_interest_balance

                    period_additional_payment_loan = (
                        period_additional_payment * proportion
                    )

                    principal_paid += min(period_additional_payment_loan, balance)

                    period_additional_payment -= period_additional_payment_loan

                balances[loan_index] -= min(principal_paid, balance)

                cumulative_interest_accrued = sum(
                    amortization_schedule[f"Loan {loan_index + 1} Interest Accrued"]
                )
                cumulative_interest_paid = sum(
                    amortization_schedule[f"Loan {loan_index + 1} Interest Paid"]
                )
                cumulative_principal_paid = sum(
                    amortization_schedule[f"Loan {loan_index + 1} Principal Paid"]
                )

                amortization_schedule[f"Loan {loan_index + 1} Balance"].append(balance)
                amortization_schedule[f"Loan {loan_index + 1} Interest Accrued"].append(
                    interest_accrued
                )
                amortization_schedule[f"Loan {loan_index + 1} Interest Paid"].append(
                    interest_paid
                )
                amortization_schedule[f"Loan {loan_index + 1} Principal Paid"].append(
                    principal_paid
                )
                amortization_schedule[
                    f"Loan {loan_index + 1} Cumulative Interest Accrued"
                ].append(cumulative_interest_accrued)
                amortization_schedule[
                    f"Loan {loan_index + 1} Cumulative Interest Paid"
                ].append(cumulative_interest_paid)
                amortization_schedule[
                    f"Loan {loan_index + 1} Cumulative Principal Paid"
                ].append(cumulative_principal_paid)
            if balance < 1:
                interest_rates[loan_index] = 0
                cumulative_interest_accrued = max(
                    amortization_schedule[
                        f"Loan {loan_index + 1} Cumulative Interest Accrued"
                    ]
                )
                cumulative_interest_paid = max(
                    amortization_schedule[
                        f"Loan {loan_index + 1} Cumulative Interest Paid"
                    ]
                )
                cumulative_principal_paid = max(
                    amortization_schedule[
                        f"Loan {loan_index + 1} Cumulative Principal Paid"
                    ]
                )

                amortization_schedule[f"Loan {loan_index + 1} Balance"].append(balance)
                amortization_schedule[f"Loan {loan_index + 1} Interest Accrued"].append(
                    0
                )
                amortization_schedule[f"Loan {loan_index + 1} Interest Paid"].append(0)
                amortization_schedule[f"Loan {loan_index + 1} Principal Paid"].append(0)
                amortization_schedule[
                    f"Loan {loan_index + 1} Cumulative Interest Accrued"
                ].append(cumulative_interest_accrued)
                amortization_schedule[
                    f"Loan {loan_index + 1} Cumulative Interest Paid"
                ].append(cumulative_interest_paid)
                amortization_schedule[
                    f"Loan {loan_index + 1} Cumulative Principal Paid"
                ].append(cumulative_principal_paid)

        amortization_schedule["Period"].append(period)
        if sum(balances) <= 0:
            print(
                f"Your loans would be paid off by: {calculate_future_date(period*30.5)} "  # super hacky - assuming 30.5day months.
            )

    return pd.DataFrame(amortization_schedule)


# Test Plan
loan_data = [
    [40631, 0.0631],  # AB
    [22831, 0.0631],  # AC
    [1563, 0.045],  # AD
    [4478, 0.034],  # AE
    [5568, 0.034],  # AF
    [5595, 0.0386],  # AH
    [2300, 0.0386],  # AI
    [23459, 0.0584],  # AJ
    [22642, 0.0531],  # AK
    [21716, 0.0531],  # AL
]

loan_data = calculate_loan_interest_rate_discount(loan_data)

one_time_pay_off = int(
    input("How much of your 35k do you wanta put toward that big-boy?") or 30000
)

print(
    f"Simulating repayment with a one time principal payment of: {format_usd(one_time_pay_off)}"
)

loan_data[0][0] -= one_time_pay_off

#############################################################################################
# Passing arugments to the Lenders Amortization:
#############################################################################################

total_principal = sum(
    loan[0] for loan in loan_data
)  # Sum of original principals within the loan_data array
weighted_average_interest_rate = calculate_weighted_average_interest_rate(loan_data)
consolidated_loan_interest_rate = calculate_consolidated_loan_interest_rate(
    weighted_average_interest_rate
)
maximum_repayment_period = calculate_maximum_repayment_period(total_principal)
tot_periods = (
    calculate_maximum_repayment_period(total_principal) * 12
)  # Longest repayment, # of periods = months
period_per_step = 24  # For graduated repayment, two years in each step
num_steps = math.floor(
    tot_periods / period_per_step
)  # Number of times your monthly payment will increase
rgi = 0.00023  # Growth rate initially set to 0.01%, can be adjusted

# Calculate initial payment based on monthly interest payment plus 5
minimum_payment = (
    calculate_monthly_interest_payment(total_principal, consolidated_loan_interest_rate)
    + 5
)

print(f"Total Principal: {format_usd(total_principal)}")
print(f"Weighted Average interest Rate: {weighted_average_interest_rate:.5f}")
print(f"Consolidated Loan interest Rate: {consolidated_loan_interest_rate:.5f}")
print(f"Maximum Repayment Period: {maximum_repayment_period} years")
print(f"Initial 'interest-only' Minimum Monthly Payment: {format_usd(minimum_payment)}")
print(f"Initial growth rate of the step-size increase: {rgi:.5f}")

# Create a table line by line using the main function
table = calculate_lenders_amortization_schedule(
    total_principal, consolidated_loan_interest_rate, tot_periods, minimum_payment, rgi
)

# Headers for the DataFrame
names = ["Period", "Step", "Payment", "Interest", "Principal", "Balance", "Growth Rate"]

# Table of all schedules generated (1 per growth rate checked)
df = pd.DataFrame(data=table, columns=names)

# The final amortization schedule
amortization_schedule = df[df.index > len(df) - 359]
lenders_amortization = amortization_schedule.reset_index(drop=True, inplace=False)
# lenders_amortization[:,"Period"] = lenders_amortization[:,"Period"]
# Add running sums
lenders_amortization["cumPmt"] = lenders_amortization.loc[:, "Payment"].cumsum()
lenders_amortization["cumInt"] = lenders_amortization.loc[:, "Interest"].cumsum()
lenders_amortization["cumP"] = lenders_amortization.loc[:, "Principal"].cumsum()

additional_payment = int(
    input("How much more than the minimum payment could you make every month?: ")
    or 1000
)

print(
    f"Simulating repayment with an additional monthly payment of: {format_usd(additional_payment)}"
)
# my ugly hacky way of tacking on the additional payments that I definitely want to come back and fix
# lenders_amortization["additional_payment"] = additional_payment
lenders_amortization["additional_payment"] = additional_payment
lenders_amortization.to_csv("lenders_amortization.csv", index=True)


a = lenders_amortization.loc[:, ("Period")]

#############################################################################################
# Passing arugments to the Lenders LEVEL payment plan:
"""
I need to update the function below to separate out the lender's original payment plan, and then separately,
the borrower's repayment plan (based on the selections made by the user about one_time repayment and monthly additional payments. )
because the additional payments should be applied to the highest interest loans just like on the extended repayment plan. 
"""
#############################################################################################

"""
def calculate_total_interest_and_principal_paid_with_additional_payment(
    total_principal, monthly_interest_rate, tot_periods, additional_payment
):
    monthly_payment = (
        total_principal
        * (monthly_interest_rate * (1 + monthly_interest_rate) ** tot_periods)
        / ((1 + monthly_interest_rate) ** tot_periods - 1)
    )
    total_payment = 0
    total_interest_paid = 0
    balance = total_principal

    for _ in range(tot_periods):
        interest_paid = balance * monthly_interest_rate
        total_interest_paid += interest_paid
        principal_paid = monthly_payment - interest_paid + additional_payment
        balance -= principal_paid
        total_payment += monthly_payment + additional_payment

    return monthly_payment, total_interest_paid, total_principal


monthly_interest_rate = consolidated_loan_interest_rate / 365 * 30

(
    monthly_payment,
    total_interest_paid,
    total_principal_paid,
) = calculate_total_interest_and_principal_paid_with_additional_payment(
    total_principal, monthly_interest_rate, tot_periods, additional_payment
)

print(f"Level Monthly Payment: {format_usd(monthly_payment)}")
print(f"Level Total Interest Paid: {format_usd(total_interest_paid)}")
print(f"Level Total Principal Paid: {format_usd(total_principal_paid)}")
print(
    f"Level Total Amount Paid: {format_usd(total_interest_paid + total_principal_paid)}"
)
"""

"""
def calculate_total_interest_and_principal_paid_with_additional_payment(
    total_principal, monthly_interest_rate, additional_payment
):
    monthly_payment = (
        total_principal
        * (monthly_interest_rate * (1 + monthly_interest_rate) ** tot_periods)
        / ((1 + monthly_interest_rate) ** tot_periods - 1)
    )
    total_payment = 0
    total_interest_paid = 0
    total_principal_paid = 0
    balance = total_principal
    month = 1

    while balance > 0:
        interest_paid = balance * monthly_interest_rate
        total_interest_paid += interest_paid
        principal_paid = monthly_payment - interest_paid + additional_payment

        # Avoid overpaying and reduce balance to zero
        principal_paid = min(principal_paid, balance)

        balance -= principal_paid
        total_principal_paid += principal_paid
        total_payment += principal_paid + interest_paid

        # Increase the month count
        month += 1

    return (
        monthly_payment,
        total_interest_paid,
        total_principal_paid,
        total_payment,
        month,
    )


monthly_interest_rate = consolidated_loan_interest_rate / 365 * 30

(
    monthly_payment,
    total_interest_paid,
    total_principal_paid,
    total_payment,
    month,
) = calculate_total_interest_and_principal_paid_with_additional_payment(
    total_principal, monthly_interest_rate, additional_payment
)
monthly_payment, total_interest_paid, total_principal, total_payment, months = result

print("Monthly Payment:", monthly_payment)
print("Total Interest Paid:", total_interest_paid)
print("Total Principal Amount:", total_principal)
print("Total Payment:", total_payment)
print("Months:", months)
"""

# # Test Plan for level repayment

schedule = calculate_borrowers_amortization_schedule(
    loan_data,
    tot_periods,
    # also where I should have branched
    lenders_amortization.loc[:, ("Period", "Payment", "additional_payment")].astype(int)
    # additional_payment,
)

print("\nAmortization Schedule:")


columns_to_print = []
for i in range(len(loan_data)):
    [
        columns_to_print.append(f"Loan {i + 1} Balance"),
        columns_to_print.append(f"Loan {i + 1} Interest Paid"),
        columns_to_print.append(f"Loan {i + 1} Principal Paid"),
    ]


grand_total = [0, 0]
for i in range(len(loan_data)):
    grand_total[0] += schedule[f"Loan {i + 1} Interest Paid"].sum().astype(int)
    grand_total[1] += schedule[f"Loan {i + 1} Principal Paid"].sum().astype(int)

print("Grand total principal paid:", format_usd(grand_total[1]))
print("Grand total interest paid:", format_usd(grand_total[0]))
print("Grand total paid:", format_usd(sum(grand_total)))


# Print specific columns from the first row
# print(schedule.loc[0, columns_to_print])

# Print specific columns from the last row
last_row_index = schedule.shape[0] - 1
# print(schedule.loc[last_row_index, columns_to_print])

schedule.to_csv("borrower_amortization.csv", index=True)


# Generating the new amortization schedule recursively once a token is paid off.
#  "cache" the amortization schedule; apply the minimum payment+extra until a re-calculation is triggered -
# then it needs recall itself but with the new loan balances.


# Okay, so now I need to mod the borrower repayment simulation to call the lender's amortization schedule generation function whenever triggered
# which means I need to update either:
#       1. the lenders amortization schedule to take in the balances wherever they're at (not the original loan data)
#       2. or, the borrower's amortization schedule to pass the current balances in the format of the original_loan_data

# when the lender recalculates the amortizaiton schedule (say, when a loan token is repaid)
# I'm confident the payoff date does not change (its still 30years out from the start of repayment, unless you adjust that)
# I'm not sure if the minimum payment actually goes down, or if you're "ratchetted" and stuck at that minimum.
# if the minimum doesn't get recalculated, then the growth rate would definitely have to go down.
# I need to clean up this action list, then I need to tackle the borrowers amortization schedule issues. Its showing a bunch of negative interest paid values
# and it still needs to call back the lenders ams. adding the schedule of additional payments wouldn't be hard; it's the same as importing the minimum payment list.

# I need to work on the borrower's ams to apply the additional payment, after the initial minimum disbursment, and then update the loan token totals (cums, and per-period)

# I am gettign this stupid arrays must all be same length error unless the periods are 100 or less. That's so strange and arbitrary it's frustrating.

# I need to account for longer than the lenders repayment (or at least, longer than 300 periods; because right now that's not working.)

# I want a "scenario" runner; where I can control my 1-time and my additional in two or three separate scenarios so I can compare.
# wow. this is just the super rough-draft version. There's lots more to do with it, but for now; I think the last big challenge is to get it recalculating the lender's amortization once a token is repaid.a
# That would be very tricky.
# man, I'd love for this to compare itself to other level repayment strategies with the same assumptions.

# Import libraries
import pandas as pd
import numpy as np
import numpy_financial as npf
import math as m
import amortization as am
from tabulate import tabulate

## have the user enter their loan information
numLoans=int(input('How many loans do you have?:      '))
amt,mons,rate,monthly_pay, monthly_due =[None]*numLoans,[None]*numLoans,[None]*numLoans,[None]*numLoans,[None]*numLoans
for i in range(numLoans):

  amt[i]= float(input(f"Please enter the current principle for loan {i+1}:    "))
##  mons[i]= int(input(f"Please enter the term of loan {i+1} in years:    "))*12
  rate[i] = float(input(f"Enter loan {i+1}'s APR :   %"))/100

## initialize sample loan information
## loans is a table with 2 columns: the outstanding principle and the interest rate

## ***may add 'loan token' column in future***

##loans = [[70000, .069], [40000, .055], [20000, 0.024]]


# join the lists as columns
loans = list(zip(amt,rate))

df = pd.DataFrame(loans, columns = ['Principal', 'interest'])

## Calculate maximum repayment period

# Direct Consolidation Loan
# Consolidated Loan calculator
def wavg(df):
## takes in the loans dataframe
## returns the total principal and the weighted average interest rate
    tru_wavg = sum(df['Principal']*df['interest'])/sum(df['Principal'])
    # Round up to the nearest higher 1/8th of 1%
    def rndup2(tru_wavg):
        # takes in the true weighted average as a decimal (to prevent rounding)
        # returns the nearest higher one-eighth. of 1%, unless already an eighth.

        w=tru_wavg*100   # as a percentage
        w_whole = int(w) # whole portion of the precentage
        fp = w-w_whole  # fractional portion

        for i in range(1,9,1):
            cep = i/8
            if fp == cep: #if the fractional portion of the precentage is already an eigth of a percent
                print('the true weighted average is already an at an eighth of 1%')
                return(tru_wavg)
            elif fp < cep:
                return(w_whole+cep)
    return(sum(df['Principal']),rndup2(tru_wavg)/100)

consolidated_p_and_i = wavg(df)
print(consolidated_p_and_i)

## ***add a module that asks if they'll use auto pay for a .25% interest rate reduction on the rndup2(wavg)
## or FFEL Consolidation Loan under the Graduated Repayment Plan
## depending on total education loan indebtedness.

def ext_repay_period(d):
## takes in total education loan indebtedness (d)
## returns maximum repayment period in years under the graduated repayment plan
    if d <7500: y=10
    elif d<10000: y=12
    elif d<20000: y=15
    elif d<40000: y=20
    elif d<60000: y=25
    else: y=30
    ##print(f'your maximum repayment is {y} years under the grauated repayment plan')
    return (y)

## daily student loan interest calculator - ammount of interst that accrues daily and between periods
def dintr (i):
        # dailiy interest rate: takes in an interest rate (annual) and spits out the daily rate
    if i<0 or i>1:
            print('WARNING! unsual interest rate: expected interest entered between 0 and 1')
    dintr = i/365
    return (dintr)

def dia (bal,i):
    # daily interest accrued: takes in the current loan balance and interest rate, returns amount of interest accrued each day
    dia = bal*dintr(i)
    return(dia)

def mip (bal, i):
    #monthly interest payment
    #takes in current loan balance and the interest rate, returns total interest accrued since last payment
##    dintr2 = dintr(i)
    dia2 = dia(bal,i)
    ans = 30*dia2
##    answers = [dintr(i), dia(bal,i), ans]
    nl = '\n'
##    print(f'daily interest rate: {dintr}{nl} daily interest accrued: {dia}{nl} interest accrued this month: {ans}')
    return(ans)

##set parameters for generating amortization schedules for stepped repayment
# principal = df['Principal'][0]
principal = consolidated_p_and_i[0] #sum of balanes within the account - calculated in the consolidated loan function 'wavg()'
# interest_rate = df['interest'][0]
interest_rate = consolidated_p_and_i[1] #effective interest rate of the account - calculated in the consolidated loan function 'wavg()'
tot_periods = ext_repay_period( sum(df['Principal']))*12 #longest repayment, # of periods = months
period_per_step = 24 #for graduated repayment, two years in each step
num_steps = m.floor(tot_periods/period_per_step) #number of times your monthly payment will increase
rgi = .0001 #growth rate initially set to 1.0%, probably won't ever exceed 2%
payment = mip(principal,interest_rate) +5

##main function
def bal_after_np(principal, interest_rate, tot_periods, payment, rgi):

    """
    Recursively generates amortization schedules for "stepped repayment",
    trying increasing[1] growth rates until a satisfactory[2] one is found

    :param principal: Principal amount
    :param interest_rate: Interest rate per period
    :param period: Total number of periods
    :param payment: Monthly payment amount
    :return: Rows containing period, interest, principal, balance, etc

    [1] increasing is not optimal - see comment on rgi incrementer
    [2] first rgi which reduces the balance to zero (hopefully close to the 360th period)
    """

##store original inputs for recursive call
    p, ir, tp, pmt = principal, interest_rate, tot_periods, payment

##periods start at 1, balance keeps track of the balance after each period
    period = 1
    balance = principal

    """

    """

    for i in range(num_steps):
        step = i

        while (step*period_per_step <= period <= period_per_step+ step*period_per_step) and balance>0:
            interest = mip(balance, interest_rate)
            principal = payment - interest
            balance -= principal
            yield period, step, payment, interest, principal, balance, rgi if balance > 0 else 0
            period += 1
        payment = payment + (balance*rgi)

##    print(balance, rgi) --testing
    if balance > 0:
##        print(principal, interest_rate, tot_periods, payment, rgi) --testing
        rgi +=.00001 #should update this naive approach with something like bracketing to 'zero in'
        yield from bal_after_np(p, ir, tp, pmt, rgi)



##create a table line by line using the main funciton
table = (x
         for x in bal_after_np(
             principal, interest_rate, tot_periods, payment, rgi)

         )

##headers for the dataframe
names=["Period","Step","Payment", "Interest", "Principal", "Balance", "growth_rate"]

##table of all schedules generated (1 per growth rate checked)
a = pd.DataFrame(data = table, columns = names)

##the final amortization schedule
amortization_schedule = a[a.index>len(a)-359]


print_am_sched= str(input('Do you want to view your amortization schedule now? (Y/N):      '))

if print_am_sched in ('Y','y'):

    print(

            tabulate(
                amortization_schedule,
                headers=names,
                floatfmt=",.2f",
                numalign="right",
            )
                )

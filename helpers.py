# helpers.py
import pandas as pd
import plotnine as p9

def create_amortization_table(amount, rate, term):
    # Calculate monthly interest rate
    monthly_interest_rate = rate / 12 / 100
    
    # Calculate total number of payments
    total_payments = term * 12
    
    # Calculate monthly payment using the formula for an annuity
    monthly_payment = amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / ((1 + monthly_interest_rate) ** total_payments - 1)
    
    # Initialize amortization table
    amortization_table = []
    
    # Initialize remaining balance
    remaining_balance = amount
    
    # Calculate each month's principal and interest
    for payment_number in range(1, total_payments + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        amortization_table.append([monthly_payment, principal_payment, interest_payment, remaining_balance])
    
    # Create DataFrame for better visualization
    amortization_df = pd.DataFrame(amortization_table, columns=['Payment Number', 'Monthly Payment', 'Principal Payment', 'Interest Payment', 'Remaining Balance'])
    
    return amortization_df

def create_payment_schedule_to_edit(amortization_table):
    payment_schedule = amortization_table[['Payment Number', 'Monthly Payment']]
    return payment_schedule.round(2)

def calculate_total_paid(amortization_table):
    return amortization_table['Monthly Payment'].sum()

def calculate_percent_interest(amount_financed, total_paid):
    percent = (total_paid - amount_financed) / total_paid * 100
    return percent.round(2)

def plot_amount_paid_over_time(amortization_table):
    amortization_table['Cumulative Principal'] = amortization_table['Principal Payment'].cumsum()
    amortization_table['Cumulative Interest'] = amortization_table['Interest Payment'].cumsum()

    cumulative_df = amortization_table[['Payment Number', 'Cumulative Principal', 'Cumulative Interest']]
    long_df = cumulative_df.melt(id_vars=['Payment Number'], value_vars=['Cumulative Principal', 'Cumulative Interest'], var_name='Payment Type', value_name='Amount')
    
    return (
        p9.ggplot(long_df, p9.aes(x="Payment Number", y="Amount", fill="Payment Type"))
        + p9.geom_area()
        + p9.theme_linedraw()
        + p9.theme(legend_position='top', legend_direction='horizontal', legend_title=p9.element_blank())
    )

def plot_payment_composition_over_time(amortization_table):
    payments_df = amortization_table[['Payment Number', 'Principal Payment', 'Interest Payment']]
    long_df = payments_df.melt(id_vars=['Payment Number'], value_vars=['Principal Payment', 'Interest Payment'], var_name='Payment Type', value_name='Amount')

    return (
        p9.ggplot(long_df, p9.aes(x="Payment Number", y="Amount", fill="Payment Type"))
        + p9.geom_col()
        + p9.theme_linedraw()
        + p9.theme(legend_position='top', legend_direction='horizontal', legend_title=p9.element_blank())
    )
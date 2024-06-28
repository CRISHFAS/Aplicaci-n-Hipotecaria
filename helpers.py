# helpers.py
import pandas as pd
import plotnine as p9


def make_amortization_table(amount, rate, term, payments = None, notes = None):

    # Calculate total number of payments
    n_payments = term * 12

    # Calculate monthly interest rate
    monthly_rate = rate / 12 / 100

    # Assemble payments schedule
    if payments is None:
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
        payments = [monthly_payment] * n_payments

    # Assemble notes field
    if notes is None:
        notes = [''] * n_payments
    
    # Initialize amortization table
    amortization_table = []
    
    # Initialize remaining balance
    remaining_balance = amount
    
    # Calculate each month's principal and interest
    for payment_number in range(1, n_payments + 1):
        if remaining_balance == 0:
            amortization_table.append([payment_number, 0, 0, 0, 0, notes[payment_number - 1]])
        elif payment_number == (n_payments):
            interest_payment = remaining_balance * monthly_rate
            payment = remaining_balance + interest_payment
            principal_payment = payment - interest_payment
            remaining_balance = max(0, remaining_balance - principal_payment)
            amortization_table.append([payment_number, payment, principal_payment, interest_payment, remaining_balance, notes[payment_number - 1]])
        elif payments[payment_number - 1] == 0:
            interest_payment = remaining_balance * monthly_rate
            remaining_balance += interest_payment
            amortization_table.append([payment_number, 0, 0, 0, remaining_balance, notes[payment_number - 1]])
        else:
            interest_payment = remaining_balance * monthly_rate
            payment = payments[payment_number - 1]
            principal_payment = payment - interest_payment
            remaining_balance = max(0, remaining_balance - principal_payment)
            amortization_table.append([payment_number, payment, principal_payment, interest_payment, remaining_balance, notes[payment_number - 1]])

    # Create DataFrame for better visualization
    amortization_df = pd.DataFrame(
        amortization_table, 
        columns=['Payment', 'Amount', 'Principal Payment', 'Interest Payment', 'Remaining Balance', 'Notes']
    ).round(2)
    
    return amortization_df

def make_payment_schedule(amortization_table):
    return amortization_table[['Payment', 'Amount', 'Notes']]

def calculate_total_paid(amortization_table):
    return amortization_table['Amount'].sum().round(2)

def calculate_percent_interest(amount_financed, total_paid):
    percent = (total_paid - amount_financed) / total_paid * 100
    return int(percent.round(0))

def plot_amount_paid_over_time(amortization_table):
    amortization_table['Cumulative Principal'] = amortization_table['Principal Payment'].cumsum()
    amortization_table['Cumulative Interest'] = amortization_table['Interest Payment'].cumsum()

    cumulative_df = amortization_table[['Payment', 'Cumulative Principal', 'Cumulative Interest']]
    long_df = cumulative_df.melt(id_vars=['Payment'], value_vars=['Cumulative Principal', 'Cumulative Interest'], var_name='Payment Type', value_name='Amount')
    
    return (
        p9.ggplot(long_df, p9.aes(x="Payment", y="Amount", fill="Payment Type"))
        + p9.geom_area()
        + p9.theme_linedraw()
        + p9.theme(legend_position='top', legend_direction='horizontal', legend_title=p9.element_blank())
    )

def plot_payment_composition_over_time(amortization_table):
    payments_df = amortization_table[['Payment', 'Principal Payment', 'Interest Payment']]
    long_df = payments_df.melt(id_vars=['Payment'], value_vars=['Principal Payment', 'Interest Payment'], var_name='Payment Type', value_name='Amount')

    return (
        p9.ggplot(long_df, p9.aes(x="Payment", y="Amount", fill="Payment Type"))
        + p9.geom_col()
        + p9.theme_linedraw()
        + p9.theme(legend_position='top', legend_direction='horizontal', legend_title=p9.element_blank())
    )

def cell_to_float(s):
    try:
        result = float(s)
    except ValueError:
        raise SafeException(
                "Amount values should be numbers."
            )
    else:
        return result
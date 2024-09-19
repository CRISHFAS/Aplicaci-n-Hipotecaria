import pandas as pd
import plotnine as p9

def make_dates(start_date, term):
    # Determine el primer día del siguiente mes
    first_day_of_month = start_date.replace(day=1, month=start_date.month + 1)

    # Crear lista de fechas de pago
    n_months = term * 12
    dates_list = []

    for i in range(n_months):
        new_month = (first_day_of_month.month + i) % 12
        if new_month == 0:
            new_month = 12
        dates_list.append(first_day_of_month.replace(month=new_month))

    # Convertir fechas a cadenas en el formato "YYYY-MM-DD"
    dates_list_str = [date.strftime("%Y-%m-%d") for date in dates_list]

    return dates_list_str

def make_amortization_table(amount, rate, term, start_date, payments=None, notes=None):
    # Calcular el número total de pagos
    n_payments = term * 12

    # Calcular la tasa de interés mensual
    monthly_rate = rate / 12 / 100

    # Armar el calendario de pagos
    if payments is None:
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
        payments = [monthly_payment] * n_payments

    # Armar el campo de notas
    if notes is None:
        notes = [''] * n_payments
    
    # Inicializar la tabla de amortización
    amortization_table = []
    
    # Inicializar el saldo restante
    remaining_balance = amount
    
    # Calcular el principal y los intereses de cada mes
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

    # Agregar columna de fechas y eliminar columna de pagos
    amortization_df = pd.DataFrame(
        amortization_table, 
        columns=['Pago', 'Monto', 'Pago Principal', 'Pago de Interés', 'Saldo Restante', 'Notas']
    ).round(2)
    
    amortization_df["Fecha"] = make_dates(start_date, term)

    return amortization_df

def make_payment_schedule(amortization_table):
    return amortization_table[['Fecha', 'Monto', 'Notas']]

def calculate_total_paid(amortization_table):
    return amortization_table['Monto'].sum().round(2)

def calculate_interest_amount(amount_financed, total_paid):
    return (total_paid - amount_financed).round(2)

def calculate_percent_interest(amount_financed, total_paid):
    percent = (total_paid - amount_financed) / total_paid * 100
    return int(percent.round(0))

def plot_amount_paid_over_time(amortization_table, green, gold):
    amortization_table['Principal Acumulado'] = amortization_table['Pago Principal'].cumsum()
    amortization_table['Interés Acumulado'] = amortization_table['Pago de Interés'].cumsum()

    cumulative_df = amortization_table[['Pago', 'Principal Acumulado', 'Interés Acumulado']]
    long_df = cumulative_df.melt(id_vars=['Pago'], value_vars=['Principal Acumulado', 'Interés Acumulado'], var_name='Tipo de Pago', value_name='Monto')
    
    return (
        p9.ggplot(long_df, p9.aes(x="Pago", y="Monto", fill="Tipo de Pago"))
        + p9.geom_area()
        + p9.scale_fill_manual(values=(green, gold))
        + p9.theme_linedraw()
        + p9.theme(legend_position='top', legend_direction='horizontal', legend_title=p9.element_blank())
    )

def plot_payment_composition_over_time(amortization_table, green, gold):
    payments_df = amortization_table[['Pago', 'Pago Principal', 'Pago de Interés']]
    long_df = payments_df.melt(id_vars=['Pago'], value_vars=['Pago Principal', 'Pago de Interés'], var_name='Tipo de Pago', value_name='Monto')
    long_df = long_df[long_df['Monto'] != 0]

    return (
        p9.ggplot(long_df, p9.aes(x="Pago", y="Monto", fill="Tipo de Pago"))
        + p9.geom_col(position="fill")
        + p9.scale_fill_manual(values=(green, gold))
        + p9.theme_linedraw()
        + p9.theme(legend_position='top', legend_direction='horizontal', legend_title=p9.element_blank())
    )

def cell_to_float(s):
    try:
        result = float(s)
    except ValueError:
        raise SafeException(
                "Los valores deben ser números."
            )
    else:
        return result

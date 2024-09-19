from shiny import reactive
from shiny.express import render, input, ui
from io import StringIO
import faicons as fa
import helpers

green = '#198754'
gold = '#ffc107'

# Begin UI --------------------------------------------------------------------
ui.page_opts(fillable=True, title='Aplicación de calculadora de intereses')

with ui.layout_columns(fillable=False, col_widths=(2, 4, 6)):

    with ui.layout_columns(col_widths=(8)):
        ui.markdown("#### 1. Definir Préstamo")
        ui.input_numeric("amount", "Monto Financiado", 100000, min=1, step=1000) 
        ui.input_numeric("rate", "Tasa de Interés (%)", 7.25, min=0.01, step=0.05) 
        ui.input_numeric("term", "Plazo del Préstamo en Años", 30, min=0.25, step=5) 
        ui.input_date("start", "Fecha del Primer Pago", format="yyyy-mm-dd")

    with ui.layout_columns(col_widths=(12, 10, 5, 5)):

        ui.markdown("#### 2. Editar Pagos")

        # Tabla Editable ----------------------------------------------------------------
        amortization_df = reactive.value()

        @reactive.effect
        def _():
            amortization_df.set(
                helpers.make_amortization_table(input.amount(), input.rate(), input.term(), input.start())
            )

        @render.data_frame
        def payments():
            return render.DataGrid(
                helpers.make_payment_schedule(amortization_df()), 
                editable=True
            )

        @payments.set_patch_fn
        def upgrade_patch(*, patch,):
            if patch["column_index"] == 1:
                return helpers.cell_to_float(patch["value"])
            else:
                return patch["value"]

        ui.input_action_button("update", "Actualizar Pagos")

        # Actualizar el Calendario de Pagos -----------------------------------------------------
        @reactive.effect
        @reactive.event(input.update)
        def _():
            updated_schedule = helpers.make_amortization_table(
                input.amount(), 
                input.rate(), 
                input.term(),
                input.start(),
                payments.data_view()['Amount'],
                payments.data_view()['Notes']
            )
            amortization_df.set(updated_schedule)
            return None

        @render.download(label="Descargar Calendario", filename="payments.csv")
        def download():
            yield payments.data().to_csv(index=False)

    with ui.layout_columns(col_widths=(4, 4, 4, 12)):   

        # Cajas de Valores ----------------------------------------------------------------
        @reactive.calc
        def total_paid():
            return helpers.calculate_total_paid(amortization_df())

        with ui.value_box(showcase=fa.icon_svg("sack-dollar"), theme=ui.value_box_theme(fg='#FFFFFF', bg=gold)):
            "Total Pagado"

            @render.text
            def total_paid_amount():
                return f'{total_paid():,}'

        with ui.value_box(showcase=fa.icon_svg("building-columns"), theme=ui.value_box_theme(fg='#FFFFFF', bg=green)):
            "Intereses Pagados"

            @render.text
            def interest_paid_amount():
                interest = helpers.calculate_interest_amount(input.amount(), total_paid())
                return f'{interest:,}'

        with ui.value_box(showcase=fa.icon_svg("percent"), theme=ui.value_box_theme(fg='#FFFFFF', bg=green)):
            "Porcentaje de Intereses"

            @render.text
            def percent_interest():
                return helpers.calculate_percent_interest(input.amount(), total_paid())

        # Gráficos ----------------------------------------------------------------
        with ui.navset_card_underline():  
            with ui.nav_panel("Monto Acumulado"):
                @render.plot
                def cumulative_plot():
                    return helpers.plot_amount_paid_over_time(amortization_df(), green, gold)

            with ui.nav_panel("Composición del Pago"):
                @render.plot
                def payments_composition_plot():
                    return helpers.plot_payment_composition_over_time(amortization_df(), green, gold)



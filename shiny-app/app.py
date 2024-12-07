import pandas as pd
from shiny import App, render, ui, reactive
import altair as alt
import nest_asyncio

nest_asyncio.apply()

analysis_data = pd.read_csv('/Users/suyuanfang/Desktop/Pyhton/final project/analysis_data.csv')
# data link
# https://www.dropbox.com/scl/fo/yjo8xyyg13zx678dfpzwy/AHTaxAa2uQplUupwOv1ntU8?rlkey=5cg9m9zhcxf95l8y20b1ddgvn&st=hiwpm6d7&dl=0

crime_types = analysis_data['Primary Type'].unique()

app_ui = ui.page_fluid(
    ui.h1("Chicago Crime Data Visualization"),
    ui.input_selectize(
        "crime_types",
        "Select Crime Types:",
        choices=sorted(crime_types.tolist()),
        selected=crime_types.tolist()[:5],
        multiple=True,
    ),
    ui.output_ui("crime_plot")
)

def server(input, output, session):
    @reactive.Calc
    def filtered_data():
        selected_types = input.crime_types()
        if not selected_types:
            return pd.DataFrame(columns=['Primary Type'])
        return analysis_data[analysis_data['Primary Type'].isin(selected_types)]

    @output
    @render.ui
    def crime_plot():
        data = filtered_data()
        if data.empty:
            empty_chart = alt.Chart(pd.DataFrame({'x': [], 'y': []})).mark_bar()
            return ui.HTML(empty_chart.to_html())

        crime_counts = data['Primary Type'].value_counts().reset_index()
        crime_counts.columns = ['Crime_Type', 'Count']

        chart = (
            alt.Chart(crime_counts)
            .mark_bar()
            .encode(
                x=alt.X('Crime_Type:N', sort='-y', title='Crime Type'),
                y=alt.Y('Count:Q', title='Number of Crimes'),
                color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues')),
                tooltip=['Crime_Type', 'Count'],
            )
            .properties(
                title='Number of Crimes for Selected Crime Types',
                width='container',
                height=400,
            )
            .configure_axis(labelAngle=-45)
        )
        return ui.HTML(chart.to_html())

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

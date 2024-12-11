import pandas as pd
import altair as alt
from shiny import ui, render, reactive
import shiny

# Load the dataset
updated_file_path =r'/Users/attaullah/Documents/final_project_SIA/shiny-app/updated_merged_final_df.csv'  # Correct path
data = pd.read_csv(updated_file_path)

# Get the list of cities and sort them alphabetically
cities = sorted(list(data['City'].unique()))

# Define UI for the application
app_ui = ui.page_fluid(
    ui.h3("City Policy Data"),
    ui.input_checkbox("switch_view", "Switch View"),
    ui.input_select("city", "Choose a city", choices=cities),
    ui.output_ui("dashboard")
)

# Define server logic
def server(input, output, session):

    # Reactive expression to filter the data based on selected city
    @reactive.Calc
    def filtered_data():
        city_data = data[data['City'] == input.city()]
        return city_data

    # Define Dashboard 1 - Table Rendering
    @output
    @render.ui
    def dashboard():
        if input.switch_view():  # Check if switch view is enabled
            return render_policy_chart()  # Call the policy chart function for Dashboard 2
        else:
            return render_table()  # Call the table function for Dashboard 1

    # Render Dashboard 1 - Table based on filtered data
    def render_table():
        city_data = filtered_data().iloc[0]
        
        # Replace 1/0 with 'Yes'/'No' for policy columns
        city_data['Requires_De_Escalation'] = 'Yes' if city_data['Requires_De_Escalation'] == 1 else 'No'
        city_data['Has_Use_of_Force_Continuum'] = 'Yes' if city_data['Has_Use_of_Force_Continuum'] == 1 else 'No'
        city_data['Bans_Chokeholds_and_Strangleholds'] = 'Yes' if city_data['Bans_Chokeholds_and_Strangleholds'] == 1 else 'No'
        city_data['Requires_Warning_Before_Shooting'] = 'Yes' if city_data['Requires_Warning_Before_Shooting'] == 1 else 'No'
        city_data['Restricts_Shooting_at_Moving_Vehicles'] = 'Yes' if city_data['Restricts_Shooting_at_Moving_Vehicles'] == 1 else 'No'
        city_data['Requires_Exhaust_All_Other_Means_Before_Shooting'] = 'Yes' if city_data['Requires_Exhaust_All_Other_Means_Before_Shooting'] == 1 else 'No'
        city_data['Duty_to_Intervene'] = 'Yes' if city_data['Duty_to_Intervene'] == 1 else 'No'
        city_data['Requires_Comprehensive_Reporting'] = 'Yes' if city_data['Requires_Comprehensive_Reporting'] == 1 else 'No'

        # Create a two-column table with the 'Property' and 'Value' columns
        table_data = {
            "Property": [
                'State', 'Number_of_Incidents', 'Requires De-Escalation', 'Has Use of Force Continuum',
                'Bans Chokeholds and Strangleholds', 'Requires Warning Before Shooting',
                'Restricts Shooting at Moving Vehicles', 'Requires Exhaust All Other Means Before Shooting',
                'Duty to Intervene', 'Requires Comprehensive Reporting', 'City Population'
            ],
            "Value": [
                city_data['State'], city_data['Number_of_Incidents'], city_data['Requires_De_Escalation'], 
                city_data['Has_Use_of_Force_Continuum'], city_data['Bans_Chokeholds_and_Strangleholds'], 
                city_data['Requires_Warning_Before_Shooting'], city_data['Restricts_Shooting_at_Moving_Vehicles'], 
                city_data['Requires_Exhaust_All_Other_Means_Before_Shooting'], city_data['Duty_to_Intervene'], 
                city_data['Requires_Comprehensive_Reporting'], city_data['City Population']
            ]
        }

        # Create a DataFrame from the table data
        df = pd.DataFrame(table_data)

        # Format Property names by replacing underscores with spaces and capitalizing words
        df['Property'] = df['Property'].str.replace('_', ' ').str.title()
        
        # Convert the DataFrame to HTML
        table_html = df.to_html(index=False, escape=False)

        # Add custom CSS styling to the table
        styles = """
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
                font-family: Arial, sans-serif;
            }
            th {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                text-align: left;
            }
            td {
                padding: 8px;
                text-align: left;
                background-color: #f9f9f9;
                border: 1px solid #ddd;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #ddd;
            }
        </style>
        """
        
        # Return the DataFrame with styled HTML
        return ui.HTML(styles + table_html)

    def render_policy_chart():
        # Get policy data for the city
        city_data = filtered_data().iloc[0]
        policy_columns = [
            'Bans_Chokeholds_and_Strangleholds', 'Duty_to_Intervene', 'Has_Use_of_Force_Continuum', 
            'Requires_Comprehensive_Reporting', 'Requires_De_Escalation', 'Requires_Exhaust_All_Other_Means_Before_Shooting', 
            'Requires_Warning_Before_Shooting', 'Restricts_Shooting_at_Moving_Vehicles'
        ]
        
        # Prepare data for the chart
        policy_data = {
            "Policy": [policy.replace('_', ' ').title() for policy in policy_columns],  # Format labels
            "Implementation_Adjusted": [city_data[policy] - 0.5 for policy in policy_columns]  # Adjust values for centered axis
        }
        
        df = pd.DataFrame(policy_data)

        # Create a bar chart with policies and their implementation status
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(
                'Implementation_Adjusted:Q',
                axis=alt.Axis(  # Remove x-axis numbers
                    title=None,
                    labels=False,
                    values=[]
                ),
                scale=alt.Scale(domain=[-0.5, 0.5])  # Center the axis at 0.5
            ),
            y=alt.Y(
                'Policy:N', 
                axis=alt.Axis(
                    title=None, 
                    tickCount=len(policy_columns), 
                    labels=True, 
                    domain=False, 
                    grid=False,
                    labelFontWeight="bold"  # Bold labels
                ),
                sort=policy_columns
            ),
            color=alt.condition(
                alt.datum['Implementation_Adjusted'] > 0, 
                alt.value('lightgreen'),  # Green for implemented
                alt.value('lightcoral')     # Red for not implemented
            ),
            tooltip=['Policy:N', 'Implementation_Adjusted:Q']
        ).properties(
            width=1000,
            height=400
        )

        # Add Total Population and Fatal Encounters annotation above the chart
        population_annotation = alt.Chart(pd.DataFrame({
            'x': [0],
            'y': [-3],  # Fully outside of the chart area
            'text': [f"City's Population (in thousands): {city_data['City Population']/1000}, Total Fatal Encounters: {city_data['Number_of_Incidents']}"]
        })).mark_text(
            align='center',
            baseline='top',
            fontSize=12
        ).encode(
            x='x:Q',
            y='y:Q',
            text='text:N'
        )

        # Add legend for "Policy Implemented" and "Policy Not Implemented"
        legend_data = pd.DataFrame({
            'x': [-0.3, 0.3],  # Two values for left and right legend items
            'y': [-2.5, -2.5],  # Same y-coordinate for both legend items
            'text': ['Policy Not Implemented', 'Policy Implemented'],  # Two labels
            'color': ['black', 'black']  # Two corresponding colors
        })

        legend = alt.Chart(legend_data).mark_text(
            align='center',
            baseline='middle',
            fontSize=12,
            fontWeight='bold'
        ).encode(
            x='x:Q',
            y='y:Q',
            text='text:N',
            color=alt.Color('color:N', legend=None)  # Use the color column dynamically
        )

        # Combine the bar chart, population info, and legend
        combined_chart = (chart + population_annotation + legend).configure_view(
            fill="#f9f9f9"  # Very light background color
        ).configure_axisRight(  # Disable right-side y-axis labels
            labels=False,
            ticks=False,
            grid=False,
            domain=False
        ).configure_axis(
            grid=False  # Remove gridlines for a cleaner look
        )

        # Convert the Altair chart to HTML for use in Shiny
        chart_html = combined_chart.to_html()

        # Return the HTML for the chart
        return ui.HTML(chart_html)



# Create the Shiny app
app = shiny.App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()

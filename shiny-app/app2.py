from shiny import App, render, ui, reactive
import pandas as pd
import plotly.express as px

# Load the dataset
data_path = r"/Users/attaullah/Documents/final_project_SIA/shiny-app/updated_merged_final_df.csv"
data = pd.read_csv(data_path)

# Add hover information for better map interaction
data['hover_info'] = data['City'] + ', ' + data['State'] + '<br>' + \
                     'Population: ' + data['City Population'].astype(str)

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("US Cities Policy and Incident Heatmap", style="text-align: center"),
    ui.input_select(
        id="variable",
        label="Select a Variable:",
        choices={
            "Requires_De_Escalation": "Requires De-Escalation",
            "Has_Use_of_Force_Continuum": "Has Use of Force Continuum",
            "Bans_Chokeholds_and_Strangleholds": "Bans Chokeholds/Strangleholds",
            "Requires_Warning_Before_Shooting": "Requires Warning Before Shooting",
            "Restricts_Shooting_at_Moving_Vehicles": "Restricts Shooting at Moving Vehicles",
            "Requires_Exhaust_All_Other_Means_Before_Shooting": "Exhaust All Other Means Before Shooting",
            "Duty_to_Intervene": "Duty to Intervene",
            "Requires_Comprehensive_Reporting": "Requires Comprehensive Reporting",
        },
        selected="Requires_Comprehensive_Reporting",  # Default selected variable
    ),
    ui.output_ui("heatmap"),  # Output for the heatmap
    ui.output_text_verbatim("description")  # Output for the description text
)

# Define the Server
def server(input, output, session):
    # Reactive calculation for the selected variable
    @reactive.Calc
    def selected_variable():
        return input.variable()

    # Render the dynamic description
    @output
    @render.text
    def description():
        return "Bubble Size Represents Total Number of Incidents (fatal encounters by police)"

    # Render the heatmap as HTML
    @output
    @render.ui
    def heatmap():
        selected = selected_variable()
        
        # Replace NaN with 0 for the selected variable
        data[selected] = data[selected].fillna(0)
        # Replace NaN with 0 for Number_of_Incidents
        data["Number_of_Incidents"] = data["Number_of_Incidents"].fillna(0)
        
        # Create a policy status column for coloring
        data["Policy Status"] = data[selected].apply(lambda x: "Not Implemented" if x == 0 else "Implemented")

        # Define a discrete color mapping
        color_discrete_map = {
            "Not Implemented": "Red",
            "Implemented": "Green"
        }

        # Create the map
        fig = px.scatter_mapbox(
            data,
            lat="Latitude",
            lon="Longitude",
            color="Policy Status",  # Categorical color
            size="Number_of_Incidents",  # Scale bubble size by the number of incidents
            hover_name="City",
            hover_data={
                "Latitude": False,
                "Longitude": False,
                selected: True,
                "Number_of_Incidents": True,
                "City Population": True,
                "State": False,
                "hover_info": False,
            },
            color_discrete_map=color_discrete_map,  # Explicit color mapping
            mapbox_style="carto-positron",
            zoom=3.5,  # Adjust zoom for better visibility
            height=700,  # Increased map height
            width=1200,  # Increased map width
            title=f"Policy Status and Incident Heatmap: {selected.replace('_', ' ')}"
        )
        # Fix map margins to prevent clipping
        fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
        # Return the Plotly figure as an HTML div
        return ui.HTML(fig.to_html(full_html=False))

# Create and run the Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()

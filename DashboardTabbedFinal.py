import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# ====== Load Data ======
density_map_data = pd.read_csv("DensityMapDataV2_Cleaned.csv")
top_ai_skills_data = pd.read_csv("TopAISkillsChartDataV2.csv")
top_ai_career_data = pd.read_csv("TopAICareerDataV2.csv")

# ====== State Abbreviations Mapping ======
state_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Washington, D.C.": "DC"
}

# Ensure the state_abbrev column exists
if "state_abbrev" not in density_map_data.columns:
    density_map_data["state_abbrev"] = density_map_data["state_name"].map(state_abbrev)

# ====== AI Job Density Map ======
fig_density = px.choropleth(
    density_map_data,
    locations="state_abbrev",
    locationmode="USA-states",
    color="count",
    hover_name="state_name",
    hover_data={"count": True, "percent": True},
    color_continuous_scale="Blues",
    scope="usa",
    title="AI Job Density by State"
)

fig_density.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>AI Job Count: %{customdata[0]:,.0f}<br>Percentage of AI Listings: %{customdata[1]:.2f}%<extra></extra>"
)

# ====== Dash App ======
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("AI Job Market Dashboard", style={"textAlign": "center", "color": "#ffffff", "fontFamily": "Arial, sans-serif"}),

    dcc.Tabs(
        id="tabs",
        value="tab1",
        children=[
            dcc.Tab(label="AI Job Density Map", value="tab1"),
            dcc.Tab(label="AI Career Areas Comparison", value="tab2"),
            dcc.Tab(label="Top AI Skills Comparison", value="tab3"),
        ],
        colors={"border": "#505050", "primary": "#505050", "background": "#777777"},
        style={"fontFamily": "Arial, sans-serif", "color": "black"}
    ),

    html.Div(id="tabs-content")
], style={"backgroundColor": "#3a3a3a", "padding": "20px", "fontFamily": "Arial, sans-serif"})


@app.callback(
    dash.Output("tabs-content", "children"),
    dash.Input("tabs", "value")
)
def render_content(tab):
    if tab == "tab1":
        return html.Div([dcc.Graph(figure=fig_density)])
    
    elif tab == "tab2":
        return html.Div([
            html.Label("Select State 1:", style={"color": "#ffffff"}),
            dcc.Dropdown(
                id="career_state_1",
                options=[{"label": state, "value": state} for state in top_ai_career_data["state_name"].unique()],
                value="California",
                clearable=False
            ),
            html.Label("Select State 2:", style={"color": "#ffffff"}),
            dcc.Dropdown(
                id="career_state_2",
                options=[{"label": state, "value": state} for state in top_ai_career_data["state_name"].unique()],
                value="Texas",
                clearable=False
            ),
            dcc.Graph(id="career_comparison_chart")
        ])
    
    elif tab == "tab3":
        return html.Div([
            html.Label("Select State 1:", style={"color": "#ffffff"}),
            dcc.Dropdown(
                id="skills_state_1",
                options=[{"label": state, "value": state} for state in top_ai_skills_data["state_name"].unique()],
                value="California",
                clearable=False
            ),
            html.Label("Select State 2:", style={"color": "#ffffff"}),
            dcc.Dropdown(
                id="skills_state_2",
                options=[{"label": state, "value": state} for state in top_ai_skills_data["state_name"].unique()],
                value="Texas",
                clearable=False
            ),
            dcc.Graph(id="skills_comparison_chart")
        ])


# ====== Callbacks for Graphs ======
@app.callback(
    dash.Output("career_comparison_chart", "figure"),
    [dash.Input("career_state_1", "value"), dash.Input("career_state_2", "value")]
)
def update_career_chart(state1, state2):
    filtered_data = top_ai_career_data[top_ai_career_data["state_name"].isin([state1, state2])]
    
    # 🔍 Debugging: Print if dataset is empty
    if filtered_data.empty:
        print(f"⚠️ No data found for states: {state1}, {state2}")
    
    fig = px.bar(
        filtered_data,
        x="lot_career_area_name",
        y="proportion",
        color="state_name",
        title=f"Top 12 AI Career Areas: {state1} vs {state2}",
        labels={"lot_career_area_name": "Career Area", "proportion": "Percentage of AI Listings"},
        barmode="group"
    )
    return fig


@app.callback(
    dash.Output("skills_comparison_chart", "figure"),
    [dash.Input("skills_state_1", "value"), dash.Input("skills_state_2", "value")]
)
def update_skills_chart(state1, state2):
    filtered_data = top_ai_skills_data[top_ai_skills_data["state_name"].isin([state1, state2])]

    if filtered_data.empty:
        print(f"⚠️ No data found for states: {state1}, {state2}")
    
    fig = px.bar(
        filtered_data,
        x="skills_name",
        y="proportion",
        color="state_name",
        title=f"Top 10 AI Skills: {state1} vs {state2}",
        labels={"skills_name": "AI Skill", "proportion": "Percentage of AI Listings"},
        barmode="group"
    )
    return fig


# ====== Run the App ======
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)

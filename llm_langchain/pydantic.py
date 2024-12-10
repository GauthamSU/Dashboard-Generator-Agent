from pydantic import BaseModel, Field

class PlotlyChart(BaseModel):
  title: str = Field(description="Title of the chart")
  description: str = Field(description="Formulate a question such that the question can be asked to a Large language model to generate the chart")
  chart_type: str = Field(description="The type of plot that should be used to plot the above mentioned chart")
  additional_information: str = Field(description="Additonal information for the chart to have to be visually appealing and/or more engaging")

class DashboardSchema(BaseModel):
  dashboard_title: str = Field(description="Title for the dashboard")
  dashboard_description: str = Field(description="Description for the dashboard")
  dashboard_components: list[PlotlyChart] = Field(description="List of charts in the dashboard")
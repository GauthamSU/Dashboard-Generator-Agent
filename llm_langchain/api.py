import os
import json
from django.shortcuts import redirect
from .schema import InstrucionSchema, ResponseSchema, PostResponseSchema
from .pydantic import DashboardSchema
from ninja import NinjaAPI, Form
from llm_langchain.plotly_agent import GenerateDashboard

app = NinjaAPI()

@app.post('upload-file/', url_name='upload-file', response=PostResponseSchema)
def upload_file(request, data: Form[InstrucionSchema]):
    file = request.FILES.get('file[]')
    if file:
        csv_file =  file.read()
        with open(file.name, 'wb') as f:
            f.write(csv_file)
        dashboard = GenerateDashboard(file.name, metadata=data.metadata, column_metadata=data.column_metadata)
        instructions = dashboard.get_dashboard_instructions()
        plots = dashboard.get_plots(instructions)
        plot_json = dashboard.generate_json()
        os.remove(file.name)
        
        return {**data.dict(), 
                'instructions': instructions, 
                'plot_code': [plot.content for plot in plots], 'plot_json': plot_json}


@app.get('/', url_name='home-page', response=ResponseSchema)
def home_page(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = read_json_file('superstore.json', BASE_DIR)
    dashboard = GenerateDashboard(
        os.path.join(BASE_DIR, 'static', 'Sample_superstore.csv')
        )

    dashboard_schema_json = DashboardSchema.model_validate_json(data['Dashboard'])
    plot_json = dashboard.generate_json(all_plots=data['Plots'], result=dashboard_schema_json)
    
    return {'instructions' : dashboard_schema_json, 
            'plot_code': data['Plots'], 
            'plot_json' : plot_json}


def read_json_file(file_name: str, base_dir) -> dict[str, str]:
    file_path = os.path.join(base_dir, 'static', file_name)

    with open(file_path, 'r') as f:
        data = json.load(f)
        return data

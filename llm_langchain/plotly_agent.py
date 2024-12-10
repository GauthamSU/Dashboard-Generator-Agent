import os
import re
import ast
import pandas as pd
from io import StringIO
from environ import environ
from langchain_groq import ChatGroq
from contextlib import redirect_stdout
from langchain.schema import AIMessage
from DashboardAI.settings import BASE_DIR
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent import RunnableAgent, AgentExecutor
from langchain.agents import create_react_agent, create_structured_chat_agent
from langchain_experimental.tools.python.tool import PythonAstREPLTool


from .parser import PythonCodeParser
from .pydantic import DashboardSchema
from .prompts import CREATE_PLOT_PROMPT, CREATE_DASHBOARD_PROMPT, METADATA, COLUMN_METADATA, STRUCTURED_REACT_CHAT, REACT_PLOT_USER_PROMPT

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

groq_api_key = env('GROQ_API_KEY')

class GenerateDashboard:
    """
    Args:
        file : Filepath for the csv file or absolute file object
        metadata: Metadata or description of the dataframe or table.
        column_metadata: The details of each column and the data it consists.
        auto: Whether to execute the complete agent automatically or any manual data will be arbitrarily supplied.

    Returns:
        Json data for plotly plots to be executed from the frontend.
    """

    def __init__(self, file, metadata : str = None, column_metadata : str = None, auto: bool = False) -> None:
        self.file = file
        self.all_plots: list[str] = []
        self.result = DashboardSchema
        self.model = ChatGroq(model="llama3-70b-8192", api_key=groq_api_key)
        self.frame: pd.DataFrame = pd.read_csv(self.file, encoding='latin1')
        self.metadata = metadata
        self.column_metadata = column_metadata
        self.auto = auto
        self.errors = {'error':'', 'raw_text': ''}
        
        if self.auto:
            self._auto_execute()


    def get_dashboard_instructions(self) -> DashboardSchema:
        pydantic_parser = PydanticOutputParser(pydantic_object=DashboardSchema)
        instructions = pydantic_parser.get_format_instructions()


        dashboard_prompt = PromptTemplate.from_template(CREATE_DASHBOARD_PROMPT)
        dashboard_chain = dashboard_prompt | self.model | pydantic_parser
        
        result = dashboard_chain.invoke(
            {"df": self.frame,
             "metadata": METADATA.format(metadata=self.metadata) if len(self.metadata.strip()) else '',
             "column_metadata": COLUMN_METADATA.format(column_metadata=self.column_metadata) if len(self.column_metadata.strip()) else '',
             "format_instructions": instructions}
            )
        self.result = result
        return result


    def get_plots(self, dashboard_instructions : DashboardSchema = None) -> list[AIMessage]:
        
        result = dashboard_instructions if dashboard_instructions else self.get_dashboard_instructions()

        plotly_prompt = PromptTemplate.from_template(CREATE_PLOT_PROMPT)
        plotly_chain = plotly_prompt | self.model | PythonCodeParser()
        for chart in result.dashboard_components:
            plots = plotly_chain.invoke(
                {
                    "df": self.frame, 
                    "query": chart.model_dump_json(indent=2), 
                    "column_types": str(self.frame.dtypes.to_dict())
                }
                )
            self.all_plots.append(plots)

        return self.all_plots
    

    def generate_json(self, all_plots : list[str] | list[AIMessage] = None, result : DashboardSchema = None) -> list[str]:
        """
        Args:
            all_plots: list of stringified plotly code in python
            result: details of plots to be plotted for the dashboard with their descriptions as a pydantic model
        Returns:
            List of executed python code of plotly plots and converted to json format for rendering.
        """
        if all_plots and result:
            self.all_plots = all_plots
            self.result = result
        
        JSON = []
        for i, plot in enumerate(self.all_plots):
            unsuccessful = True
            while unsuccessful:
                try:
                    if isinstance(plot, str):
                        tree = ast.parse(plot)
                    else:
                        tree = ast.parse(plot.content)
                    plot_json = self._exec_final_line(tree=tree)
                    JSON.append(plot_json)
                    unsuccessful = False
                except Exception as e:
                    print('Index : ', i, e)
                    plot = self._error_chain(ast.unparse(tree), error_message=e, index=i)
                    print('Error Fixed Plot : ', plot.content )
                    # self.all_plots[i] = plot.content
            
        return JSON
    
    
    def _error_chain(self, code_string: str, error_message: str, index: int):
        prompt = PromptTemplate.from_template(REACT_PLOT_USER_PROMPT)
    
        input_dict = {'df_head': self.frame.head(),
            'column_types': str(self.frame.dtypes.to_dict()),
            'dashboard_title': self.result.dashboard_title,
            'plot_description': self.result.dashboard_components[index].description,
            'plot_code': code_string,
            'code_error': error_message}
        debug_error_chain = prompt | self.model | PythonCodeParser()
        fixed_output = debug_error_chain.invoke(input_dict)
        
        return fixed_output
    

    def _exec_final_line(self, tree: ast.Module) -> str:
        df  = self.frame
        module = ast.Module(tree.body[:-1], type_ignores=[])
        exec(ast.unparse(module), globals(), locals())
        module_end = ast.Module(tree.body[-1:], type_ignores=[])
        module_end_str = ast.unparse(module_end)

        if type(module_end.body[0]) == ast.Expr:
            if 'show()' in module_end_str:
                module_end_str = module_end_str.replace('show()', 'to_json()')
                
            print_matches = re.search(r'print\((.*?)\)', module_end_str)
            if print_matches:
                module_end_str = f"{print_matches.group(1)}"
                
        elif type(module_end.body[0]) == ast.Assign:
            variable = module_end.body[0].targets[0].id
            exec(module_end_str, globals(), locals())
            module_end_str = f'\n{variable}.to_json()'
        
        io_buffer = StringIO()
        with redirect_stdout(io_buffer):
            ret = eval(module_end_str, globals(), locals())
            plot_json = ret
            if ret is None:
                plot_json = io_buffer.getvalue()

        return plot_json

    
    def _auto_execute(self):
        dashboard_instructions = self.get_dashboard_instructions()
        plotly_codes = self.get_plots(dashboard_instructions)
        plotly_json = self.generate_json()
        return dashboard_instructions, plotly_codes, plotly_json
    
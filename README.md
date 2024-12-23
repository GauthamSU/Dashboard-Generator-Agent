# Dashboard-Generator-Agent

Kindly view the complete project code by navigating to master branch as it is completely updated in that branch.

Video of the project is here. Please do watch it to get an intuition on how the page works.

https://github.com/user-attachments/assets/7dd98584-3555-4f60-848c-a64193b2b265

## Project Details

AI-powered automatic dashboard generator built using GenAI and the Llama-3.1-70b model. This innovative AI agent empowers users to create customizable, data-driven dashboards with just a csv file.

### *__Key features__*:

_Natural Language Processing_ : Understands the type of data and generates relevant visualizations. <br>
_Automated Data Integration_ : At present the agent only accepts csv file as data inputs but can easily be modified to support multiple data input sources such as databases and data warehouses. <br>
_Interactive Dashboards_ : Enables users to explore data dynamically.<br>

### *__Technology Used__* : <br><br>
__Languages__: Python, Typescript

__Backend__ :<br>
_Langchain_ : Used to fetch, parse and transform data into relevant format to generate plots for dashboard <br>
_Django-Ninja_ : Used to create API to accept the user data from frontend

__Frontend__ : <br>
_NextJs_ : To effectively route and send the user data to backend <br>
_React_ : To add interactivity and enhance user experience <br>
_Plotly_ : To display plots sent to web page from backend API <br>

__Skills__ : _LangChain_ · _Generative AI_ · _React.js_ · _Django_ · _TypeScript_

__Functionality__ : 
- The agent works with just a csv file for input
- Works more efficiently when metadata about the complete dataset is given and metadata about each of the columns is given.
- The agentic steps are as follows:
   * LLM first determines the nature of data from the csv data, metadata and column metadata
   * LLM then generates a JSON framework of different kinds of plots to create a convincing dashboard
   * The framework output is used to generate python code of plotly plots
   * The plotly plots are then executed and fixed of any errors.
   * The final plot is passed on to the frontend to display the final dashboard. 
   

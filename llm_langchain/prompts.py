
### ====== Below is the prompt to create an outline for multiple plots for the dashboard ====== ###


CREATE_DASHBOARD_PROMPT = """
You have access to a pandas dataframe in Python. The name of the dataframe is `df`.
Your objective is to suggest multiple charts for the given data so that it can be displayed in a dashboard.

df: {df}
{metadata}
{column_metadata}

Make sure to capture important KPIs and metrics and multiple important trends to be displayed on the dashboard.
If one or two different KPIs/metrics or trends can be merged into a single chart, then please do that and come up with new chart ideas
Have 10 or more charts in the dashboard

Your final output should be in the following format:
{format_instructions}

Do not provide any python code. Provide suggestions only.

Begin! Remember to use the format mentioned above only.

"""


### ====== Below is the prompt to create a plot based on the plot suggestion generated by the AI ====== ###


CREATE_PLOT_PROMPT = """
You have access to a pandas dataframe in Python. The name of the dataframe is `df`.

df: {df}

The following dictionary gives you the column names of the dataframe and their data types.

Column Data: {column_types}

Your objective is to write python code to plot a chart using plotly package for the user query based on the requirements provided below:

- All the queries has to be answered in a single plotly figure
- Use only column names mentioned in the above Column Data details and please be aware of the data types of the columns.
- Make sure to have appropriate legends and title for the chart
- Choose appropriate xticks and yticks for the chart
- Use different colour schemas apart from the default ones for the chart
- The final answer should be python code of the plotly chart with the figure object having show method invoked. For example: fig.show().

Remember to use plotly as charting library and do not provide any explainations. Wrap the python code around ```python .....(write your python code here)... ```

User Query: {query}

"""

### ====== If the user provides metadata for the csv file then this prompt is used to add context for the data ====== ###

METADATA = """
Metadata for the above data is given below:
metadata : {metadata}

"""

### ====== If the user provides metadata for the columns present in the csv file then this prompt is used to add context for the data ====== ###

COLUMN_METADATA = """
Details of the the data present in each column is given below:
column_details : {column_metadata}

"""

### ====== If the prompt encounters any errors during code execution then this react agent is triggered to understand the error and fix it ====== ###

REACT_PLOT_USER_PROMPT = """
You have the details of the pandas dataframe initialised as df.

Following is the result of the statement `print(df.head())`

{df_head}

The following dictionary gives you the column names of the dataframe and their data types.

Column Data: {column_types}

I am creating a {dashboard_title} with the data from above mentioned pandas dataframe.

I wrote a python code to create a plotly plot to get answer for the following question for the above data :
Question: {plot_description}
Python Code: {plot_code}

When i executed the python code, i got the following error : 
Error: {code_error}

Can you help me in fixing the error?

The final answer should be python code of the plotly chart with the figure object having show method invoked. For example: fig.show(). 
Do not provide any explainations. 

"""

STRUCTURED_REACT_CHAT = """
Respond to the human as helpfully and accurately as possible. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```

{{

  "action": $TOOL_NAME,

  "action_input": $INPUT

}}

```

Follow this format:

Question: input question to answer

Thought: consider previous and subsequent steps

Action:

```

$JSON_BLOB

```

Observation: action result

... (repeat Thought/Action/Observation N times)

Thought: I know what to respond

Action:

```

{{

  "action": "Final Answer",

  "action_input": "Final response to human"

}}

Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation

You have the details of the pandas dataframe initialised as df.

Following is the result of the statement `print(df.head())`

{df_head}

I am creating a {dashboard_title} with the data from above mentioned pandas dataframe.

I wrote a python code to create a plotly plot to get answer for the following question for the above data :
Question: {plot_description}
Python Code: {plot_code}

When i executed the python code, i got the following error : 
Error: {code_error}

Can you help me in fixing the error?

Final answer should be only the fixed code. Do not provide any explainations.

{agent_scratchpad}

 (reminder to respond in a JSON blob no matter what)
"""
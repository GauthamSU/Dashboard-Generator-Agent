import ast
from typing import Any
from io import StringIO
from contextlib import redirect_stdout
from langchain_core.agents import AgentFinish
from langchain.callbacks.base import BaseCallbackHandler
from langchain_experimental.tools.python.tool import sanitize_input


class CallbackHandler(BaseCallbackHandler):
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
      """Run on agent end."""
      output = finish.return_values['output']
      code = sanitize_input(output)
      tree = ast.parse(code)
      module = ast.Module(tree.body[:-1], type_ignores=[])

      exec(ast.unparse(module), globals(), locals())

      module_end = ast.Module(tree.body[-1:], type_ignores=[])

      module_end_str = ast.unparse(module_end)

      if type(module_end.body[0]) == ast.Expr:
        if 'show()' in module_end_str:
          module_end_str = module_end_str.replace('show()', 'to_html()')
        if 'print(' in module_end_str:
          module_end_str = module_end_str.replace('print(', '')
          module_end_str = module_end_str[:-1]
        
      elif type(module_end.body[0]) == ast.Assign:
        variable = module_end.body[0].targets[0].id
        finish.return_values['callback_output'] = module_end_str
        exec(module_end_str, globals(), locals())
        module_end_str = f'\n{variable}.to_html()'
        

      io_buffer = StringIO()
      with redirect_stdout(io_buffer):
        ret = eval(module_end_str, globals(), locals())
        finish.return_values['html'] = ret
        if ret is None:
          finish.return_values['html'] = io_buffer.getvalue()
      

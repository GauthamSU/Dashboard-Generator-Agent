import re
import ast
from langchain.schema import AIMessage
from langchain_core.output_parsers import BaseOutputParser


class PythonCodeParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        python_pattern = r"`{1,4}python\n(.*?)\n`{1,4}"
        ticks_pattern = r"`{3,4}\n(.*?)\n`{3,4}"
        
        code = text
        
        python_mathes = re.search(python_pattern, text, re.DOTALL)
        if python_mathes:
            code = python_mathes.group(1) 
        
        ticks_matches = re.search(ticks_pattern, text, re.DOTALL)
        if ticks_matches:
            code = ticks_matches.group(1)
        
        if code.startswith('python\n'):
            code = code.replace('python\n', '')

        
        # print(f"{'====='*10}\nRaw Text : {text}\n{'====='*10}")
        
        return AIMessage(content=code)


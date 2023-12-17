import subprocess
import shlex
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

class CodeExecution:
    def __init__(self):
        self.code_block_start = "```python"
        self.code_block_end = "```"

    def execute_external_code(self, text_with_code):
        """
        Executes Python code as an external process.
        """
        try:
            code_to_execute = text_with_code.split(self.code_block_start)[1].split(self.code_block_end)[0]
            exec_globals = {}
            with StringIO() as stdout_buffer, StringIO() as stderr_buffer:
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    exec(code_to_execute, exec_globals)
                stdout = stdout_buffer.getvalue()
                stderr = stderr_buffer.getvalue()

            exec_response = "Executed Python Code Successfully."
            if stdout:
                exec_response += "\nStandard Output:\n" + stdout
            if stderr:
                exec_response += "\nStandard Error:\n" + stderr

        except Exception as e:
            exec_response = f"Error in executing external code: {e}"

        if len(exec_response) > 4000:
            exec_response = exec_response[:600] + "..." + exec_response[-3000:]
        return exec_response

import subprocess
import shlex
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from typing import Tuple

class CodeExecution:
    CODE_BLOCK_START = "```python"
    CODE_BLOCK_END = "```"
    MAX_RESPONSE_LENGTH = 4000
    RESPONSE_PREVIEW_LENGTH = 600

    def __init__(self):
        self.no_of_executions = 0
        self.no_of_errors = 0
        pass

    def execute_external_code(self, text_with_code: str) -> str:
        """
        Executes Python code as an external process.

        Args:
            text_with_code (str): The text containing the code to execute.

        Returns:
            str: The execution response.
        """
        try:
            code_to_execute = self._extract_code(text_with_code)
            stdout, stderr = self._execute_code(code_to_execute)
            return self._format_response(stdout, stderr)
        except Exception as e:
            return f"Error in executing external code: {e}"

    def _extract_code(self, text: str) -> str:
        """
        Extracts the Python code from the given text.

        Args:
            text (str): The text containing the code.

        Returns:
            str: The extracted code.
        """
        return text.split(self.CODE_BLOCK_START)[1].split(self.CODE_BLOCK_END)[0]

    def _execute_code(self, code: str) -> Tuple[str, str]:
        """
        Executes the given Python code and captures its output.

        Args:
            code (str): The Python code to execute.

        Returns:
            Tuple[str, str]: The standard output and standard error.
        """
        exec_globals = {}
        with StringIO() as stdout_buffer, StringIO() as stderr_buffer:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code, exec_globals)
            return stdout_buffer.getvalue(), stderr_buffer.getvalue()

    def _format_response(self, stdout: str, stderr: str) -> str:
        """
        Formats the execution response.

        Args:
            stdout (str): The standard output from the execution.
            stderr (str): The standard error from the execution.

        Returns:
            str: The formatted response.
        """
        response = "Executed Python Code Successfully."
        if stdout:
            response += "\nStandard Output:\n" + stdout
        if stderr:
            response += "\nStandard Error:\n" + stderr

        if len(response) > self.MAX_RESPONSE_LENGTH:
            preview_end = self.RESPONSE_PREVIEW_LENGTH
            return response[:preview_end] + "..." + response[-(self.MAX_RESPONSE_LENGTH - preview_end):]
        return response
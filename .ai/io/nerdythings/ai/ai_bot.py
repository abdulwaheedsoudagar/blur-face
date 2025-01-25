from abc import ABC, abstractmethod
from ai.line_comment import LineComment

class AiBot(ABC):
    
    __no_response = "No critical issues found"
    __problems="errors, issues, potential crashes or unhandled exceptions"
    __chat_gpt_ask_long="""
Analyze the following code and Git diffs based on these guidelines:

1. Identify actual bugs, errors, and vulnerabilities: Highlight issues that may cause incorrect or unintended behavior during execution.
2. Suggest improvements in logic, structure, and efficiency: Recommend changes only when clear and actionable, avoiding unnecessary speculation.
3. Highlight inefficient code: Propose optimizations that measurably improve performance or maintainability.
4. Adherence to style guides: Verify compliance with applicable coding standards (e.g., PEP8, Google Java Style Guide).
5. Fix vulnerabilities: Provide specific recommendations to address any identified security concerns.
6. Evaluate comments and documentation: Ensure they are sufficient, relevant, and aligned with the code.

Rules:
- No speculation: Avoid hypothetical scenarios or assumptions unless explicitly relevant.
- Format for Comments: Use the exact line number from the original file:  [line_number: <cause effect>] 
- No Complete Code: Do not include complete code snippets.
- Do not give complete code Snippet, any other.
- If there are no issues, write "{no_response}" and nothing else.

DIFFS:

{diffs}

Full code from the file:

{code}

"""

    @abstractmethod
    def ai_request_diffs(self, code, diffs) -> str:
        pass

    @staticmethod
    def build_ask_text(code, diffs) -> str:
        return AiBot.__chat_gpt_ask_long.format(
            problems = AiBot.__problems,
            no_response = AiBot.__no_response,
            diffs = diffs,
            code = code,
        )

    @staticmethod
    def is_no_issues_text(source: str) -> bool:
        target = AiBot.__no_response.replace(" ", "")
        source_no_spaces = source.replace(" ", "")
        return source_no_spaces.startswith(target)
    
    @staticmethod
    def split_ai_response(input) -> list[LineComment]:
        if input is None or not input:
            return []
        
        lines = input.strip().split("\n")
        models = []
        print('-00000000000000000000000000000')
        print(lines)
        print('-00000000000000000000000000000')
        for full_text in lines:
            number_str = ''
            number = 0
            full_text = full_text.strip()
            if len( full_text ) == 0:
                continue

            reading_number = True
            for char in full_text.strip():
                if reading_number:
                    if char.isdigit():
                        number_str += char
                    else:
                        break

            if number_str:
                number = int(number_str)

            models.append(LineComment(line = number, text = full_text))
        return models
    
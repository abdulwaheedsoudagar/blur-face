from abc import ABC, abstractmethod
from ai.line_comment import LineComment

class AiBot(ABC):
    
    __no_response = "No critical issues found"
    __problems="errors, issues, potential crashes or unhandled exceptions"
    __chat_gpt_ask_long="""
Analyze the following code and git diffs. 

1. Identify actual bugs, errors, and vulnerabilities that could cause incorrect or unintended behavior during execution. 
2. Suggest improvements in logic, structure, and efficiency only if there are clear, actionable changes.
3. Highlight inefficient code and recommend optimizations only if they improve measurable performance or maintainability.
4. Check fo adherence to style guides( example PEP8, Google Java Style Guide).
5. Suggest fixes for identifided vulnerabiltes.
6. Ensure code comments and documentation area sufficient and relavent.

Rules:
- Do not speculate or suggest changes based on valid assumptions or hypothetical scenarios unless explicitly relevant.
- Use the format "line_number: cause effect".
- If there are no issues, write "{no_response}" and nothing else.

DIFFS:

{diffs}

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
    
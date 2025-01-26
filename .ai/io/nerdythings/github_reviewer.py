import os
import ast
import re
from git import Git 
from pathlib import Path
from ai.chat_gpt import ChatGPT
from ai.ai_bot import AiBot
from log import Log
from env_vars import EnvVars
from repository.github import GitHub
from repository.repository import RepositoryError
from difflib import SequenceMatcher

separator = "\n\n----------------------------------------------------------------------\n\n"
log_file = open('output.txt', 'a')

def normalize_string(s):
    return re.sub(r'\\+', r'\\', s.replace('\\"', '"').replace("\\'", "'"))

def are_similar(a, b, threshold=0.97):
    return SequenceMatcher(None, a, b).ratio() > threshold

def main():
    vars = EnvVars()
    vars.check_vars()

    ai = ChatGPT(vars.chat_gpt_token, vars.chat_gpt_model)
    github = GitHub(vars.token, vars.owner, vars.repo, vars.pull_number)

    remote_name = Git.get_remote_name()
    
    Log.print_green("Remote is", remote_name)
    changed_files = Git.get_diff_files(remote_name=remote_name, head_ref=vars.head_ref, base_ref=vars.base_ref)
    Log.print_green("Found changes in files", changed_files)
    if len(changed_files) == 0: 
        Log.print_red("No changes between branch")

    for file in changed_files:
        Log.print_green("Checking file", file)

        _, file_extension = os.path.splitext(file)
        _, file_extension_1 = os.path.splitext(file)
        file_extension = file_extension.lstrip('.')
        Log.print_yellow(f"file_extensionfile_extensionfile_extension {file_extension_1}")
        print('vars.target_extensionsvars.target_extensions',vars.target_extensions)
        if file in ['.ai/io/nerdythings/ai/ai_bot.py',
                    '.ai/io/nerdythings/ai/chat_gpt.py',
                    '.ai/io/nerdythings/ai/line_comment.py',
                    '.ai/io/nerdythings/repository/repository.py',
                    '.ai/io/nerdythings/repository/github.py',
                    '.ai/io/nerdythings/env_vars.py',
                    '.ai/io/nerdythings/git.py',
                    '.ai/io/nerdythings/log.py',
                    '.ai/io/nerdythings/github_reviewer.py']:
            # if file_extension not in vars.target_extensions:
            Log.print_yellow(f"Skipping, unsuported extension {file_extension} file {file}")
            continue

        try:
            code_line = {}
            with open(file, 'r') as file_opened:
                file_content = file_opened.readlines()

            for line_number, line_content in enumerate(file_content, start=1):
                code_line[line_number] = line_content.strip()
        except FileNotFoundError:
            Log.print_yellow("File was removed. Continue.", file)
            continue
        print('dddddddddddddd')
        print(code_line)
        print('dddddddddddddd')
        if len( file_content ) == 0: 
            Log.print_red("File is empty")
            continue

        file_diffs = Git.get_diff_in_file(remote_name=remote_name, head_ref=vars.head_ref, base_ref=vars.base_ref, file_path=file)
        if len( file_diffs ) == 0: 
            Log.print_red("Diffs are empty")
        
        Log.print_green(f"Asking AI. Content Len:{len(file_content)} Diff Len: {len(file_diffs)}")

        response = ai.ai_request_diffs(code=file_content, diffs=file_diffs)

        responses = response

        
        responses = responses.replace('json','')
        print('1111111111111')
        print(responses)
        print('111111111111')
        responses = ast.literal_eval(responses)
        for response in responses:
            for k, v in code_line.items():
                if are_similar(v, response['line']):
                    linenumber = k
                    break

            print('dsdfsdfsdf')
            print(response['line'])
            print(response['comment'])
            print(linenumber)

            # Retry mechanism
            attempt = 0
            max_attempts = 3
            result = False  # Initialize result

            while attempt < max_attempts and not result:
                print(f"Attempt {attempt + 1}: Posting comment on line {linenumber}")
                result = post_line_comment(github=github, file=file, text=response['comment'], line=linenumber)

                if not result:
                    print(f"Failed to post comment on line {linenumber}, retrying with linenumber - 1")
                    linenumber -= 1  # Decrement line number for retry
                attempt += 1

            if not result:
                print(f"Failed to post comment after {max_attempts} attempts for line {linenumber + attempt - 1}")

            print(result)
            print('dsdfsdfsdf')
                    
def post_line_comment(github: GitHub, file: str, text:str, line: int):
    Log.print_green("Posting line", file, line, text)
    try:
        git_response = github.post_comment_to_line(
            text=text, 
            commit_id=Git.get_last_commit_sha(file=file), 
            file_path=file, 
            line=line,
        )
        Log.print_yellow("Posted", git_response)
        return True
    except RepositoryError as e:
        print("Failed line comment", e)
        Log.print_red("Failed line comment", e)
        return False

def post_general_comment(github: GitHub, file: str, text:str) -> bool:
    Log.print_green("Posting general", file, text)
    try:
        message = f"{file}\n{text}"
        git_response = github.post_comment_general(message)
        # Log.print_yellow("Posted general", git_response)
        return True
    except RepositoryError:
        Log.print_red("Failed general comment")
        return False

if __name__ == "__main__":
    main()

log_file.close()
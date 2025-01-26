import os
from git import Git 
from pathlib import Path
from ai.chat_gpt import ChatGPT
from ai.ai_bot import AiBot
from log import Log
from env_vars import EnvVars
from repository.github import GitHub
from repository.repository import RepositoryError

separator = "\n\n----------------------------------------------------------------------\n\n"
log_file = open('output.txt', 'a')

def merge_code_with_diff(file_content, diff):
    original_lines = [line.strip("\n") for line in file_content]
    merged_code = []
    diff_lines = diff.split("\n")
    original_index = 0

    for line in diff_lines:
        if line.startswith("@@"):
            # Context marker, e.g., @@ -17,21 +17,16 @@
            merged_code.append(line)
        elif line.startswith("-"):
            # Removed line
            merged_code.append(f"- {original_lines[original_index]}")
            original_index += 1
        elif line.startswith("+"):
            # Added line
            merged_code.append(f"+ {line[1:].strip()}")
        else:
            # Unchanged line
            if original_index < len(original_lines):
                merged_code.append(f"  {original_lines[original_index]}")
                original_index += 1

    return "\n".join(merged_code)


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

        if len( file_content ) == 0: 
            Log.print_red("File is empty")
            continue

        file_diffs = Git.get_diff_in_file(remote_name=remote_name, head_ref=vars.head_ref, base_ref=vars.base_ref, file_path=file)
        if len( file_diffs ) == 0: 
            Log.print_red("Diffs are empty")
        
        Log.print_green(f"Asking AI. Content Len:{len(file_content)} Diff Len: {len(file_diffs)}")
        print('vvvvvvvvvvvvvvvvvv')
        print(code_line)
        print('dfgdfgdfgdfgdfg')
        print(file_content) 
        print('0999999999999999999')
        print(file_diffs)
        print('f000000000000000www')   

        response = ai.ai_request_diffs(code=file_content, diffs=file_diffs)

        responses = response
        print('ffffffffffffffffffffff')
        print(file)
        print('ffffffffffffffffffffff')

        print('merged code')
        print(merge_code_with_diff(file_content, file_diffs))
        print('mergedcodeeee')
        result = False
        import ast, re
        responses = responses.replace('json','')
        responses = ast.literal_eval(responses)
        for response in responses:
            linenumber = next((k for k, v in code_line.items() if v == response['line']), None)
            print('dsdfsdfsdf')
            print(linenumber)
            print(response['comment'])
            print('dsdfsdfsdf')
            result = post_line_comment(github=github, file=file, text=response['comment'], line=linenumber)
                    
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
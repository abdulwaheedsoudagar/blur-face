import os
import openai
import requests

# Set OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Fetch PR details from environment variables
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("GITHUB_REF").split('/')[-2]

def get_pr_diff(repo, pr_number, token):
    """Fetch the diff of a pull request."""
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# def generate_review(diff):
#     """Use ChatGPT to generate a review."""
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful code reviewer."},
#             {"role": "user", "content": f"Review the following code diff:\n{diff}"}
#         ]
#     )
#     return response['choices'][0]['message']['content']

# def generate_review(diff):
#     """Use ChatGPT to generate a review."""
#     try:
#         response = client.chat.completions.create(
#             model='gpt-3.5-turbo',
#             messages=[
#             {"role": "system", "content": "You are a helpful code reviewer."},
#             {"role": "user", "content": f"Review the following code diff:\n{diff}"}
#         ],
#             max_completion_tokens=1000,
#             temperature=0.3
#         )
#         return response.choices[0].message.content.strip()
#         # return response['choices'][0]['message']['content']
#     except Exception as e:
#         # Handle errors gracefully
#         print(f"An error occurred: {e}")
#         return "Error: Unable to generate the review."

def generate_comment_for_line(filename, diff, line_number):
    """Generate a comment for a specific line."""
    prompt = f"""
    You are a helpful code reviewer. Analyze the following code diff:
    File: {filename}
    {diff}

    Provide a detailed and actionable comment for line {line_number}, if necessary.
    """
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": "You are a professional code reviewer."},
    #         {"role": "user", "content": prompt},
    #     ],
    #     temperature=0.5,
    #     max_tokens=300,
    # )

    response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
            {"role": "system", "content": "You are a helpful code reviewer."},
            {"role": "user", "content": prompt}
        ],
            max_completion_tokens=1000,
            temperature=0.3
        )
    return response.choices[0].message.content.strip()
    # return response.choices[0].message["content"]


def post_comment(repo, pr_number, filename, line_number, comment, token):
    """Post a comment to a specific line in a PR."""
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    data = {
        "body": comment,
        "path": filename,
        "position": line_number,  # Ensure `position` corresponds to the line in the diff
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()


# def post_review(repo, pr_number, review, token):
#     """Post the review as a comment on the PR."""
#     headers = {"Authorization": f"token {token}"}
#     url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
#     data = {"body": review}
#     response = requests.post(url, headers=headers, json=data)
#     response.raise_for_status()

if __name__ == "__main__":
    token = os.getenv("PERSONAL_ACCESS_TOKEN")  # Use PAT instead of GITHUB_TOKEN
    # diff = get_pr_diff(GITHUB_REPOSITORY, PR_NUMBER, token)
    files_changed = get_pr_diff(GITHUB_REPOSITORY, PR_NUMBER, token)
    # diff_text = "\n".join([f"{file['filename']}:\n{file['patch']}" for file in diff if 'patch' in file])

    # review = generate_review(diff_text)
    # post_review(GITHUB_REPOSITORY, PR_NUMBER, review, token)
    
    for file in files_changed:
        filename = file["filename"]
        patch = file.get("patch", "")
        if not patch:
            continue

        # Parse the patch for line-specific feedback
        lines = patch.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("+") and not line.startswith("+++"):
                # Generate a comment for each added line
                comment = generate_comment_for_line(filename, patch, i + 1)
                post_comment(GITHUB_REPOSITORY, PR_NUMBER, filename, i + 1, comment, token)

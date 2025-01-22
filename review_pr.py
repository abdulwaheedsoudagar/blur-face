import os
import openai
import requests

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def generate_review(diff):
    """Use ChatGPT to generate a review."""
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
            {"role": "system", "content": "You are a helpful code reviewer."},
            {"role": "user", "content": f"Review the following code diff:\n{diff}"}
        ],
            max_completion_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
        # return response['choices'][0]['message']['content']
    except Exception as e:
        # Handle errors gracefully
        print(f"An error occurred: {e}")
        return "Error: Unable to generate the review."


def post_review(repo, pr_number, review, token):
    """Post the review as a comment on the PR."""
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    data = {"body": review}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

if __name__ == "__main__":
    token = os.getenv("PERSONAL_ACCESS_TOKEN")  # Use PAT instead of GITHUB_TOKEN
    diff = get_pr_diff(GITHUB_REPOSITORY, PR_NUMBER, token)
    diff_text = "\n".join([f"{file['filename']}:\n{file['patch']}" for file in diff if 'patch' in file])

    review = generate_review(diff_text)
    post_review(GITHUB_REPOSITORY, PR_NUMBER, review, token)

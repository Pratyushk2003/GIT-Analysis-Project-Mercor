from flask import Flask, render_template, request
import requests
import re
import os
import openai

app = Flask(__name__)

# Set up OpenAI API credentials
openai.api_key = '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'

# Function to fetch repositories from GitHub user URL
def fetch_user_repositories(github_url):
    username = re.search(r'https://github.com/([^/]+)', github_url).group(1)
    api_url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(api_url)
    if response.status_code == 200:
        repositories = response.json()
        return repositories
    else:
        print(f"Failed to fetch repositories. Status code: {response.status_code}")
        return []

# Function to preprocess code in repositories
def preprocess_code(code):
    # Perform code preprocessing here
    # Example: Memory management techniques for large repositories/files
    # You can define your own preprocessing steps based on your requirements
    # This is just a placeholder example
    processed_code = code.replace('large_memory_usage_function()', 'optimized_memory_usage_function()')
    return processed_code

# Function to assess code complexity
def assess_complexity(code):
    try:
        # Calculate complexity score based on specific criteria
        complexity_score = 0

        # Criteria 1: Number of lines of code
        lines_of_code = code.strip().split("\n")
        complexity_score += len(lines_of_code)

        # Criteria 2: Number of function definitions
        function_definitions = re.findall(r'def\s+\w+\(.*\):', code)
        complexity_score += len(function_definitions)

        # Criteria 3: Number of conditional statements
        conditional_statements = re.findall(r'if\s+.*:|elif\s+.*:|else:', code)
        complexity_score += len(conditional_statements)

        # Criteria 4: Number of loop statements
        loop_statements = re.findall(r'for\s+.*:|while\s+.*:', code)
        complexity_score += len(loop_statements)

        # Criteria 5: Number of nested structures
        nested_structures = re.findall(r'for\s+.*:\n\s+.*|while\s+.*:\n\s+.*', code)
        complexity_score += len(nested_structures)

        return complexity_score
    except Exception as e:
        print(f"Error in complexity analysis: {e}")
        return 0

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_url = request.form['user_url']
        repositories = fetch_user_repositories(user_url)

        if repositories:
            # Preprocess code in repositories and calculate complexity scores
            for repo in repositories:
                if isinstance(repo, dict):
                    repo_name = repo['name']
                    clone_url = repo['clone_url']
                    clone_dir = f'./{repo_name}'
                    os.system(f'git clone {clone_url} {clone_dir}')

                    # Initialize complexity score for the repository
                    repo['complexity_score'] = 0

                    # Process files in the repository
                    for root, dirs, files in os.walk(clone_dir):
                        for file in files:
                            if file.endswith('.ipynb') or file.endswith('.py'):
                                file_path = os.path.join(root, file)
                                with open(file_path, 'r', encoding='utf-8') as f:  # Specify the encoding as UTF-8
                                    code = f.read()
                                    processed_code = preprocess_code(code)
                                    with open(file_path, 'w', encoding='utf-8') as fw:  # Specify the encoding as UTF-8
                                        fw.write(processed_code)

                                    # Assess code complexity
                                    complexity_score = assess_complexity(processed_code)
                                    repo['complexity_score'] += complexity_score  # Accumulate the scores

                    # Clean up cloned repository
                    os.system(f'rm -rf {clone_dir}')

                else:
                    print(f"Invalid repository format: {repo}")

            # Find the most challenging repository based on complexity scores
            filtered_repositories = [repo for repo in repositories if isinstance(repo, dict) and 'complexity_score' in repo]
            if filtered_repositories:
                most_challenging_repo = max(filtered_repositories, key=lambda x: x['complexity_score'])
                repo_name = most_challenging_repo['name']
                complexity_score = most_challenging_repo['complexity_score']
                gpt_analysis = "This is a placeholder GPT analysis justifying the selection."

                return render_template('result.html', repo_name=repo_name, complexity_score=complexity_score, gpt_analysis=gpt_analysis)
            else:
                return "No valid repositories found."

        else:
            return "No repositories found for the given GitHub user URL."

    return render_template('index.html')

if __name__ == '__main__':
    app.run()

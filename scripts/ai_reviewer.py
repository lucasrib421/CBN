import os
import google.generativeai as genai
from github import Github

# Configuração
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = int(os.getenv("PR_NUMBER"))

def review_pr():
    # 1. Conectar ao GitHub e pegar o PR
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pull_request = repo.get_pull(PR_NUMBER)

    # 2. Pegar as mudanças (Diff)
    # Pegamos apenas arquivos .py, .tsx, .ts, .js para economizar tokens e focar no código
    files = pull_request.get_files()
    changes = ""
    for file in files:
        if file.filename.endswith(('.py', '.tsx', '.ts', '.js', '.css', '.html')):
            changes += f"--- Arquivo: {file.filename} ---\n"
            changes += file.patch if file.patch else "Arquivo novo ou binário."
            changes += "\n\n"

    if not changes:
        print("Nenhuma mudança relevante encontrada para revisão.")
        return

    # 3. Configurar o Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest') # Modelo mais capaz

    # 4. O Prompt de Tech Lead
    prompt = f"""
    Você é um Tech Lead Sênior especialista em Django e React.
    Revise o seguinte código de um Pull Request.
    
    Foco da revisão:
    1. Segurança (ex: SQL Injection, exposição de dados).
    2. Performance (ex: loops desnecessários, queries N+1).
    3. Boas Práticas (Clean Code, PEP8, Padrões React).
    4. Possíveis Bugs.

    Se o código estiver bom, apenas elogie brevemente.
    Se houver problemas, cite o arquivo e sugira a correção em Markdown.
    
    Aqui está o DIFF do código:
    {changes}
    """

    # 5. Gerar a Revisão
    try:
        response = model.generate_content(prompt)
        review_content = response.text
        
        # 6. Postar comentário no PR
        pull_request.create_issue_comment(f"## 🤖 Gemini AI Review\n\n{review_content}")
        print("Revisão postada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao gerar/postar revisão: {e}")

if __name__ == "__main__":
    review_pr()
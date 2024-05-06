import ollama



def get_ollama_models(): 
    try:
        ollama_models = ollama.list()
        print(ollama_models)
    except: 
        ollama_models = ["llama3", "llama2", "codellama", "dolphincoder", "llama2-uncensored", "gemma", "mistral", "dolphin-mistral", "wizard-vicuna-uncensored", "openchat", "mixtral", "dolphin-mixtral", "neural-chat", "deepseek-coder", "phi"],
 
    return ollama_models

ollama_models = get_ollama_models()

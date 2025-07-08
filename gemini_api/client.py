import requests

from environs import Env
import logging

logger = logging.getLogger(__name__)
env = Env()
env.read_env()

gemini_api_key = env("API_KEY")

def get_car_ai_bio(brand, model, year):
    car_details = (
        f"Marca: {brand}, Modelo: {model}, "
        f"Ano: {year}"
    )
    # Prompt para a API do Gemini. Seja o mais descritivo possível.
    prompt = (
        f"Gere uma pequena biografia criativa e descritiva para um carro com as "
        f"seguintes características: {car_details}. A biografia deve ter no máximo "
        f"250 caracteres e ser atraente para um comprador em potencial. Dê informações tecnicas"
        f"Me dê apenas uma resposta e já pronta para uso."
    )

    # Obtém a chave da API do Gemini de uma variável de ambiente
    # É crucial que você configure GEMINI_API_KEY no seu ambiente
    # Ex: no seu .env ou nas configurações do servidor
    if not gemini_api_key:
        print("ERRO: A variável de ambiente 'GEMINI_API_KEY' não está configurada.")
        return 'Bio gerada automaticamente (chave de API ausente).'

    # URL da API do Gemini para geração de conteúdo
    # Usando o modelo gemini-2.0-flash por ser mais rápido para este tipo de tarefa
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        # Faz a requisição POST para a API do Gemini
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)  # Adicionado timeout
        response.raise_for_status()  # Lança uma exceção para erros HTTP (4xx ou 5xx)
        result = response.json()

        # Extrai a biografia gerada da resposta da API
        if result and result.get('candidates') and len(result['candidates']) > 0 and \
                result['candidates'][0].get('content') and \
                result['candidates'][0]['content'].get('parts') and \
                len(result['candidates'][0]['content']['parts']) > 0:
            generated_bio = result['candidates'][0]['content']['parts'][0]['text']
            return generated_bio
        else:
            print("AVISO: Resposta inesperada da API do Gemini. Verifique a estrutura da resposta.")
            return 'Bio gerada automaticamente (erro na resposta da API).'

    except requests.exceptions.RequestException as e:
        # Captura erros relacionados à requisição (conexão, timeout, etc.)
        print(f"ERRO ao chamar a API do Gemini: {e}")
        return 'Bio gerada automaticamente (erro de conexão com a API).'
    except Exception as e:
        # Captura quaisquer outros erros inesperados
        print(f"ERRO inesperado ao processar a resposta da API: {e}")
        return 'Bio gerada automaticamente (erro inesperado).'

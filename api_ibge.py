import requests

def obter_estados():
    """
    Obtém a lista de estados do Brasil da API do IBGE, formata as siglas e nomes dos estados,
    e retorna uma lista ordenada no formato 'UF - Nome do Estado'.
    
    Returns:
    list: Lista de estados formatada e ordenada.
    """
    # URL da API do IBGE
    url_uf = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

    # Fazer a solicitação GET
    response = requests.get(url_uf)

    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Converter a resposta em JSON
        data = response.json()
        
        # Lista para armazenar as siglas e nomes dos estados
        estados = []
        
        # Iterar sobre os dados e adicionar as siglas e nomes formatados à lista
        for estado in data:
            sigla = estado['sigla']
            nome = estado['nome']
            estados.append(f"{sigla} - {nome}")
        
        # Ordenar por ordem alfabética
        estados = sorted(estados)
        
        return estados
    
    else:
        print("Falha ao acessar a API:", response.status_code)
        return []


def obter_municipios(uf):
    # URL da API do IBGE para obter a lista de municípios de uma UF específica
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    
    # Fazer a solicitação GET
    response = requests.get(url)
    
    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Converter a resposta em JSON
        data = response.json()
        # Lista para armazenar as cidades
        cidades = []
        for cidade in data:
            nome = cidade['nome']
            cidades.append(nome)
        return cidades
    

    else:
        print("Falha ao acessar a API:", response.status_code)
        return []

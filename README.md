# Previsão do Tempo

Este projeto é uma aplicação desktop desenvolvida em Python, utilizando a biblioteca tkinter para criar uma interface gráfica amigável. A aplicação permite consultar a previsão do tempo para qualquer município brasileiro e enviar essas informações diretamente para um e-mail especificado pelo usuário.

A aplicação se integra com duas principais fontes de dados:

API do IBGE: Para obter a lista de estados e municípios brasileiros.

AccuWeather: Para obter as previsões climáticas detalhadas, incluindo a temperatura atual e as condições para os próximos três dias.

## Funcionalidades

- Seleção de estado e município para consultar a previsão do tempo.
- Envio de previsões do tempo para um e-mail especificado.
- Exibição da temperatura atual e condições climáticas.
- Exibição das previsões para os próximos 3 dias.

## Tecnologias Utilizadas

- `tkinter` para a interface gráfica.
- `selenium` para automação do navegador e coleta de dados de previsão do tempo.
- `requests` para obter dados dos estados e municípios via API do IBGE.
- `smtplib` para envio de e-mails.
- `python-dotenv` para carregar variáveis de ambiente.

## Requisitos

Certifique-se de ter as seguintes bibliotecas instaladas:

```plaintext
tkinter
selenium==4.19.0
python-dotenv==1.0.1
requests==2.31.0
```

Você pode instalar todas as dependências com o comando:

```bash
pip install -r requirements.txt
```

## Configuração

1. **Configuração do Ambiente**

   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

   ```dotenv
   EMAIL_ADDRESS=seu_email@gmail.com
   EMAIL_PASSWORD=sua_senha
   ```

2. **Drivers do Navegador**

   Certifique-se de ter o ChromeDriver instalado e disponível no seu PATH. Você pode baixar o ChromeDriver [aqui](https://sites.google.com/chromium.org/driver/).

## Como Usar

1. **Executar o Script**

   Execute o script `painel.py` para iniciar a aplicação:

   ```bash
   python painel.py
   ```

2. **Utilizar a Interface**

   - Selecione o estado e o município desejado.
   - Insira o e-mail do destinatário.
   - Clique no botão "Iniciar" para obter a previsão do tempo e enviá-la por e-mail.

## Arquivos

- `painel.py`: Contém a interface gráfica e a lógica para coleta e envio da previsão do tempo.
- `api_ibge.py`: Contém funções para obter estados e municípios da API do IBGE.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

import tkinter as tk
from tkinter import ttk, messagebox
from api_ibge import obter_estados, obter_municipios
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException,TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

def iniciar_driver():
    chrome_options = Options()
    arguments = [
        '--lang=pt_BR', 
        '--window-size=1366x768', 
        '--incognito', 
        '--disable-gpu',
    ]
    for argument in arguments:
        chrome_options.add_argument(argument)
    
    chrome_options.add_experimental_option('prefs', {
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 1
    })

    driver = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(
        driver,
        30,
        poll_frequency=1,
        ignored_exceptions=[NoSuchElementException, ElementNotVisibleException, ElementNotSelectableException]
    )
    return driver, wait

def obter_previsao(driver, wait, cidade, uf):
    driver.get('https://www.accuweather.com/')
    
    try:
        # Esperar até que a caixa de busca esteja visível
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "search-input")))

        search_box = driver.find_element(By.CLASS_NAME, "search-input")
        search_box.send_keys(cidade + " " + uf)
        search_box.send_keys(Keys.ENTER)

        # Aguarde um pouco para garantir que a página carregue
        sleep(5)

        try:
            # Espera o elemento do botão "Entendi" aparecer e clica nele
            button = driver.find_element(By.CLASS_NAME, "banner-button.policy-accept")
            button.click()
            sleep(2)
        except Exception as e:
            print(f"Erro ao tentar clicar no botão: {e}")

       

        print("Procurando temperatura atual...")
        temperatura = driver.find_element(By.XPATH, '/html/body/div[1]/div[7]/div[1]/div[1]/a[1]/div[2]/div[1]/div[1]/div/div[1]').text
        condicao_climatica_atual = driver.find_element(By.CLASS_NAME, 'phrase').text
        print(f"Temperatura: {temperatura}, Condição: {condicao_climatica_atual}")
        sleep(3)

        driver.execute_script("window.scrollBy(0, 1200);")
        sleep(5)

        previsoes_proximos_3dias = []
        for i in range(2, 5):
            print(f"Procurando previsão para o dia {i}...")
            dia_xpath = f'/html/body/div[1]/div[7]/div[1]/div[1]/div[3]/div/a[{i}]'
            # Ajuste a espera para garantir que os elementos estejam presentes
            dia_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, dia_xpath)))
            for dia in dia_elements:
                previsao = dia.text.split('\n')
                print(f"Previsão dia {i}: {previsao}")
                dia_semana = previsao[0].split('.')[0]
                data = previsao[1].split('/')[0]
                temp_max = previsao[2]
                temp_min = previsao[3]

                condicao_climatica_raw = ' '.join(previsao[4:6])
                condicao_climatica_parts = condicao_climatica_raw.split('\n')
                condicao_climatica = ', '.join(part.capitalize() for part in condicao_climatica_parts)

                previsoes_proximos_3dias.append({
                    'dia_semana': dia_semana,
                    'data': data,
                    'temp_max': temp_max,
                    'temp_min': temp_min,
                    'condicao_climatica': condicao_climatica
                })

        return temperatura, condicao_climatica_atual, previsoes_proximos_3dias

    except NoSuchElementException as e:
        print(f"Elemento não encontrado: {e}")
        return None
    except Exception as e:
        print(f"Erro ao obter previsões: {e}")
        return None
    finally:
        sleep(3)
        driver.quit()

def format_previsao(previsoes):
    formatted_previsoes = '<html><body>'
    for idx, previsao in enumerate(previsoes):
        formatted_previsoes += f'''
        <div>
            <h2>Dia {idx + 1}</h2>
            <p><strong>Dia da semana:</strong> {previsao['dia_semana']}</p>
            <p><strong>Data:</strong> {previsao['data']}</p>
            <p><strong>Temperatura Máxima:</strong> {previsao['temp_max']}</p>
            <p><strong>Temperatura Mínima:</strong> {previsao['temp_min']}</p>
            <p><strong>Condição Climática:</strong> {previsao['condicao_climatica']}</p>
        </div>
        <hr>
        '''
    formatted_previsoes += '</body></html>'
    
    return formatted_previsoes

def send_email(destinatario, cidade, temperatura, condicao_climatica_atual, previsoes):
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise EnvironmentError("Variáveis de ambiente EMAIL_ADDRESS e EMAIL_PASSWORD não foram definidas")
    
    mail = EmailMessage()
    mail['subject'] = 'Previsão do tempo'
    mail['From'] = EMAIL_ADDRESS
    mail['To'] = destinatario

    mensagem_html = f'''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                div {{ margin-bottom: 20px; }}
                hr {{ border: 1px solid #ccc; }}
            </style>
        </head>
        <body>
            <h1>Previsão do Tempo para <strong>{cidade}</strong></h1>
            <p><strong>Temperatura Atual:</strong> {temperatura}</p>
            <p><strong>Condição Climática:</strong> {condicao_climatica_atual}</p>
            <hr>
            <h2>Previsões para os Próximos Dias:</h2>
            {format_previsao(previsoes)}
        </body>
        </html>
        '''
    mail.set_content(mensagem_html, subtype='html')

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(mail)

def atualizar_municipios(event):
    uf = select_estado.get()
    if uf:
        uf = uf.split(' - ')[0].strip()
        cidades = obter_municipios(uf)
        cidades_list['values'] = cidades
        cidades_list.set('')

def iniciar_automacao():
    cidade = cidades_list.get()
    uf = select_estado.get().split(' - ')[0].strip()
    destinatario = email_entry.get()

    if not destinatario:
        messagebox.showerror("Erro", "Por favor, insira o e-mail do destinatário.")
        return

    if cidade:
        # Alterar o estado do botão para indicar que o processo está em andamento
        send_button.config(text="Processando...", state="disabled")
        root.update_idletasks()

        driver, wait = iniciar_driver()
        resultado = obter_previsao(driver, wait, cidade, uf)

        if resultado:
            temperatura, condicao_climatica_atual, previsoes_proximos_3dias = resultado
            send_email(destinatario, cidade, temperatura, condicao_climatica_atual, previsoes_proximos_3dias)
            messagebox.showinfo("E-mail Enviado", f"E-mail enviado para: {destinatario}")
        else:
            messagebox.showerror("Erro", "Não foi possível obter previsões.")
        
        # Limpar campos e retornar o botão ao estado normal
        select_estado.set('')
        cidades_list.set('')
        send_button.config(text="Iniciar", state="normal")
    else:
        messagebox.showerror("Erro", "Por favor, selecione uma cidade.")

root = tk.Tk()
root.title("Previsão do Tempo")

# Configura o tamanho fixo dos widgets
label_width = 30
label_height = 1

# Adaptação do layout com grid ajustado
tk.Label(root, text='Previsão do Tempo', borderwidth=2, relief='solid', width=label_width, height=label_height).grid(row=0, column=0, columnspan=3, sticky='ew', padx=10, pady=10)

tk.Label(root, text='Selecione o estado', borderwidth=2, relief='solid', width=label_width, height=label_height).grid(row=1, column=0, sticky='ew', padx=10, pady=10)
select_estado = ttk.Combobox(root, values=obter_estados())
select_estado.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky='ew')
select_estado.bind("<<ComboboxSelected>>", atualizar_municipios)

tk.Label(root, text='Selecione o município', borderwidth=2, relief='solid', width=label_width, height=label_height).grid(row=2, column=0, sticky='ew', padx=10, pady=10)
cidades_list = ttk.Combobox(root)
cidades_list.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky='ew')

tk.Label(root, text='E-mail do destinatário', borderwidth=2, relief='solid', width=label_width, height=label_height).grid(row=3, column=0, sticky='ew', padx=10, pady=10)
email_entry = tk.Entry(root, width=50)
email_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky='ew')

send_button = tk.Button(root, text='Iniciar', command=iniciar_automacao, width=30)
send_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()

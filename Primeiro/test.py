from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import time

from webdriver_manager.chrome import ChromeDriverManager

dicionario = {}

service = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=service)
navegador.get("https://web.whatsapp.com/")

time.sleep(20)


def mover_pagina(pagina, delta_y):
    scroll_origin = ScrollOrigin.from_element(pagina)
    ActionChains(navegador) \
        .scroll_from_origin(scroll_origin, 0, delta_y) \
        .perform()
    time.sleep(0.5)


def _pegar_ultimo():
    elemento = navegador.find_element(By.XPATH,
                                      '//*[@id="pane-side"]/div[2]/div')
    ActionChains(navegador) \
        .scroll_to_element(elemento) \
        .perform()
    time.sleep(0.5)
    pegar = {}
    contatos = navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
    for contato in contatos:
        nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
        data = contato.find_element(By.CLASS_NAME, "aprpv14t").text
        pegar[nome] = data
    menor = min(pegar.values())
    for chave in pegar.keys():
        if menor == pegar[chave]:
            ultimo = chave
            return ultimo


def pegar_contatos_recentes():
    ultimo = _pegar_ultimo()
    origin = navegador.find_element(By.XPATH,
                                    '//*[@id="pane-side"]')
    mover_pagina(pagina=origin, delta_y=-1000000)
    time.sleep(10)
    # Pegar os contatos e a data.
    contatos = navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
    contatos_recentes = {}
    for contato in contatos:
        nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
        data = _converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
        contatos_recentes[nome] = data

    quebrar = False
    while 1:
        # Descer a página
        delta_y = (origin.rect['y'])
        mover_pagina(pagina=origin, delta_y=delta_y)

        contatos = navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
        for contato in contatos:
            nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
            data = _converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
            contatos_recentes[nome] = data
        if ultimo in contatos_recentes:
            mover_pagina(pagina=origin, delta_y=1000000)

            contatos = navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
            for contato in contatos:
                nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
                data = _converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
                contatos_recentes[nome] = data
            quebrar = True
        if quebrar:
            break

    return contatos_recentes


eng = {"Segunda-Feira": "Monday", "Terça-Feira": "Tuesday", "Quarta-Feira": "Wednesday",
       "Quinta-Feira": "Thursday", "Sexta-Feira": "Friday", "Sábado": "Saturday", "Domingo": "Sunday"}
weekdays = {0: {'Sunday': -1, 'Saturday': -2, 'Friday': -3, 'Thursday': -4, 'Wednesday': -5, 'Tuesday': -6},
            1: {'Monday': -1, 'Sunday': -2, 'Saturday': -3, 'Friday': -4, 'Thursday': -5, 'Wednesday': -6},
            2: {'Tuesday': -1, 'Monday': -2, 'Sunday': -3, 'Saturday': -4, 'Friday': -5, 'Thursday': -6},
            3: {'Wednesday': -1, 'Tuesday': -2, 'Monday': -3, 'Sunday': -4, 'Saturday': -5, 'Friday': -6},
            4: {'Thursday': -1, 'Wednesday': -2, 'Tuesday': -3, 'Monday': -4, 'Sunday': -5, 'Saturday': -6},
            5: {'Friday': -1, 'Thursday': -2, 'Wednesday': -3, 'Tuesday': -4, 'Monday': -5, 'Sunday': -6},
            6: {'Saturday': -1, 'Friday': -2, 'Thursday': -3, 'Wednesday': -4, 'Tuesday': -5, 'Monday': -6}
            }


def _converter_data(data):
    if data == 'Ontem':
        valor = datetime.now() - timedelta(days=1)
        pegar = valor.strftime('%d/%m/%Y')
        datanova = pegar
        return datanova
    else:
        if data in eng.keys():
            pegar = weekdays[datetime.now().weekday()]
            valor = eng[data]
            datanova = (datetime.now() + timedelta(days=pegar[valor])).strftime('%d/%m/%Y')
            return datanova
        else:
            try:
                datetime_obj = datetime.strptime(data, '%d/%m/%Y')
                datanova = datetime_obj.strftime('%d/%m/%Y')
                return datanova
            except:
                datanova = datetime.now().strftime('%d/%m/%Y')
                return datanova

print(pegar_contatos_recentes())

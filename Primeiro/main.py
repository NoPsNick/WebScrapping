from selenium import webdriver
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from datetime import datetime, timedelta

import pyperclip

import time

from webdriver_manager.chrome import ChromeDriverManager


class Sender:
    service = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=service)
    navegador.get("https://web.whatsapp.com/")
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

    def __init__(self, receptor, mensagem, lista_contatos, foi_enviado: bool = False, com_data: bool = False):

        self.lista_contatos = lista_contatos
        self.com_data = com_data
        self.receptor = receptor
        self.mensagem = mensagem
        self.foi_enviado = foi_enviado

    def pegar_contatos(self):
        # Ir para a lista de contatos.
        self.navegador.find_element(By.XPATH,
                                    '//*[@id="app"]/div/div/div[4]/header/div[2]/div/span/div[4]/div/span'
                                    ).click()

        # Ir para o final da lista de contatos
        origin = self.navegador.find_element(By.XPATH,
                                             '//*[@id="app"]/div/div/div[3]/div[1]/span/div/span/div/div[2]/div['
                                             '5]/div/div/div[1]/div/div[2]'
                                             )
        self.mover_pagina(pagina=origin, delta_y=1000000)

        # Pegar os contatos
        lista = []
        contatos = self.navegador.find_elements(By.CLASS_NAME, '_30scZ')
        for contato in contatos:
            if contato.text not in lista:
                lista.append(contato.text)
        origin = self.navegador.find_element(By.XPATH,
                                             '//*[@id="app"]/div/div/div[3]/div[1]/span/div/span/div/div[2]')
        quebrar = False
        while 1:
            # Subir a página
            delta_y = -(origin.rect['y'])
            self.mover_pagina(pagina=origin, delta_y=(delta_y * 2))
            # Pegar os contatos atuais mostrando
            contatos = self.navegador.find_elements(By.CLASS_NAME, '_30scZ')
            for contato in contatos:
                if contato.text not in lista:
                    lista.append(contato.text)

            # Pegar os separadores para poder ver se acabou os contatos
            separadores = self.navegador.find_elements(By.CLASS_NAME, '_2a-B5')
            for ele in separadores:
                if ele.text.lower() == 'contatos no whatsapp':
                    self.mover_pagina(pagina=origin, delta_y=-1000000)
                    time.sleep(0.5)
                    for contato in contatos:
                        if contato.text not in lista:
                            lista.append(contato.text)
                    quebrar = True
                    break
            # Terminar o while
            if quebrar:
                break
        self.lista_contatos = lista
        self.com_data = False
        return lista

    def mover_pagina(self, pagina, delta_y):
        scroll_origin = ScrollOrigin.from_element(pagina)
        ActionChains(self.navegador) \
            .scroll_from_origin(scroll_origin, 0, delta_y) \
            .perform()
        time.sleep(0.5)

    def pegar_contatos_recentes(self):
        ultimo = self._pegar_ultimo()
        time.sleep(2)

        origin = self.navegador.find_element(By.XPATH,
                                             '//*[@id="pane-side"]')
        self.mover_pagina(pagina=origin, delta_y=-1000000)
        time.sleep(0.5)

        # Pegar os contatos e a data.
        contatos = self.navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
        contatos_recentes = {}
        for contato in contatos:
            nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
            data = self._converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
            contatos_recentes[nome] = data

        quebrar = False
        while 1:
            # Descer a página
            delta_y = (origin.rect['y'])
            self.mover_pagina(pagina=origin, delta_y=delta_y)

            contatos = self.navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
            for contato in contatos:
                nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
                data = self._converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
                contatos_recentes[nome] = data
            if ultimo in contatos_recentes:
                self.mover_pagina(pagina=origin, delta_y=1000000)

                contatos = self.navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
                for contato in contatos:
                    nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
                    data = self._converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
                    contatos_recentes[nome] = data
                quebrar = True
            if quebrar:
                break

        self.lista_contatos = contatos_recentes
        self.com_data = True
        return contatos_recentes

    def _converter_data(self, data):
        if data == 'Ontem' and data not in self.eng:
            valor = datetime.now() - timedelta(days=1)
            pegar = valor.strftime('%d/%m/%Y')
            data = pegar
        else:
            try:
                datetime_obj = datetime.strptime(data, '%d/%m/%Y')
                data = datetime_obj.strftime('%d/%m/%Y')
            except:
                data = datetime.now().strftime('%d/%m/%Y')
        return data

    def _pegar_ultimo(self):
        elemento = self.navegador.find_element(By.XPATH,
                                               '//*[@id="pane-side"]/div[2]/div')
        ActionChains(self.navegador) \
            .scroll_to_element(elemento) \
            .perform()
        time.sleep(0.5)
        pegar = {}
        contatos = self.navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
        for contato in contatos:
            nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
            data = contato.find_element(By.CLASS_NAME, "aprpv14t").text
            pegar[nome] = data
        menor = min(pegar.items())
        for chave in pegar.keys():
            if menor == pegar[chave]:
                ultimo = chave
                return ultimo

    def enviar_para_o_receptor(self):
        time.sleep(15)
        # O recetor seria a pessoa que irá receber a mensagem que deve ser
        # encaminhada para todas as outras a cada 5.
        # Clicar na lupa.
        self.navegador.find_element(
            'xpath',
            '//*[@id="side"]/div[1]/div/div[2]/button').click()
        # Escrever o nome de quem irá receber a mensagem para encaminhar para os outros.
        self.navegador.find_element(
            'xpath',
            '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div[1]/p').send_keys(str(self.receptor))
        # Apertar ENTER para enviar.
        self.navegador.find_element(
            'xpath',
            '//*[@id="side"]/div[1]/div/div/div[2]/div/div[1]/p').send_keys(Keys.ENTER)
        time.sleep(1)

        # Para enviar ‘emojis’ sem problemas.
        pyperclip.copy(self.mensagem)
        # Colar a mensagem e depois enviar.
        self.navegador.find_element('xpath',
                                    '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
                                    ).send_keys(Keys.CONTROL + "v")
        time.sleep(0.5)
        self.navegador.find_element('xpath',
                                    '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
                                    ).send_keys(Keys.ENTER)
        time.sleep(2)
        self.foi_enviado = True

    def _verificar_quantidade_de_envios(self):
        # Como será encaminhado a mensagem para a cada 5, pega a quantia
        # atual e divide por 5, se for perfeito, só pega o quanto deu, caso tenha resto
        # irá somar +1.
        qtde_contatos = len(self.lista_contatos)
        if qtde_contatos % 5 == 0:
            blocos = qtde_contatos / 5
        else:
            blocos = int(qtde_contatos / 5) + 1
        return int(blocos)

    def encaminhar_a_mensagem(self):
        if self.foi_enviado:
            time.sleep(5)
            for i in range(self._verificar_quantidade_de_envios()):
                # Rodar o codigo de encaminhar
                i_inicial = i * 5
                i_final = (i + 1) * 5
                lista_enviar = self.lista_contatos[i_inicial:i_final]

                # Selecionar a mensagem para enviar e abre a caixa de encaminhar
                lista_elementos = self.navegador.find_elements('class name', '_2AOIt')
                for item in lista_elementos:
                    mensagem = self.mensagem.replace("\n", "")
                    texto = item.text.replace("\n", "")
                    if mensagem in texto:
                        elemento = item

                ActionChains(self.navegador).move_to_element(elemento).perform()
                elemento.find_element('class name', '_3u9t-').click()
                time.sleep(0.5)
                self.navegador.find_element('xpath',
                                            '//*[@id="app"]/div/span[4]/div/ul/div/li[4]/div').click()
                self.navegador.find_element('xpath',
                                            '//*[@id="main"]/span[2]/div/button[4]/span').click()
                time.sleep(1)

                for nome in lista_enviar:
                    # Selecionar os 5 contatos para enviar
                    # Escrever o nome do contato
                    self.navegador.find_element('xpath',
                                                '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/div['
                                                '1]/div/div/div[2]/div/div[1]/p'
                                                ).send_keys(nome)
                    time.sleep(1)
                    # Dar enter
                    self.navegador.find_element('xpath',
                                                '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/div['
                                                '1]/div/div/div[2]/div/div[1]/p'
                                                ).send_keys(Keys.ENTER)
                    time.sleep(1)
                    # Apagar o nome do contato
                    self.navegador.find_element('xpath',
                                                '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/div['
                                                '1]/div/div/div[2]/div/div[1]/p'
                                                ).send_keys(Keys.BACKSPACE)
                    time.sleep(1)

                self.navegador.find_element('xpath',
                                            '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/span/div/div/div/span'
                                            ).click()
                time.sleep(3)
        else:
            return "Envie para o receptor primeiro, caso contrário, ocorrerá um erro."

if __name__ == '__main__':
    envio = Sender(receptor="Você", mensagem='Testando, 1.2..3...', com_data=False,
                   lista_contatos=["Mãe", "Grupo do Mininha"])
    envio.enviar_para_o_receptor()
    envio.encaminhar_a_mensagem()

from selenium import webdriver
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import pyperclip

import time

from webdriver_manager.chrome import ChromeDriverManager


class Sender:
    service = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=service)
    navegador.get("https://web.whatsapp.com/")
    lista_contatos = []

    def __init__(self, receptor, mensagem):
        self.receptor = receptor
        self.mensagem = mensagem

    def pegar_contatos(self):
        # Ir para a lista de contatos.
        self.navegador.find_element(By.XPATH,
                               '//*[@id="app"]/div/div/div[4]/header/div[2]/div/span/div[4]/div/span'
                               ).click()

        # Ir para o final da lista de contatos
        origin = self.navegador.find_element(By.XPATH,
                                        '//*[@id="app"]/div/div/div[3]/div[1]/span/div/span/div/div[2]/div[5]/div/div/div[1]/div/div[2]'
                                        )
        scroll_origin = ScrollOrigin.from_element(origin)
        ActionChains(self.navegador) \
            .scroll_from_origin(scroll_origin, 0, 100000) \
            .perform()
        time.sleep(1)
        lista = []

        # Pegar os contatos
        contatos = self.navegador.find_elements(By.CLASS_NAME, '_30scZ')
        for contato in contatos:
            if contato.text not in lista:
                lista.append(contato.text)
        origin = self.navegador.find_element(By.XPATH,
                                        '//*[@id="app"]/div/div/div[3]/div[1]/span/div/span/div/div[2]')
        scroll_origin = ScrollOrigin.from_element(origin)
        quebrar = False
        while 1:
            delta_y = -(origin.rect['y'])
            ActionChains(self.navegador) \
                .scroll_from_origin(scroll_origin, 0, int(delta_y * 2)) \
                .perform()
            time.sleep(0.5)

            contatos = self.navegador.find_elements(By.CLASS_NAME, '_30scZ')
            for contato in contatos:
                if contato.text not in lista:
                    lista.append(contato.text)

            separadores = self.navegador.find_elements(By.CLASS_NAME, '_2a-B5')
            for ele in separadores:
                if ele.text.lower() == 'contatos no whatsapp':
                    ActionChains(self.navegador) \
                        .scroll_from_origin(scroll_origin, 0, -1000000) \
                        .perform()
                    time.sleep(0.5)
                    for contato in contatos:
                        if contato.text not in lista:
                            lista.append(contato.text)
                    quebrar = True
            if quebrar:
                break

        return lista

    def pegar_contatos_recentes(self):
        contatos = self.navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
        lista_contatos_recentes = []
        for contato in contatos:
            nome = contato.find_element(By.CLASS_NAME, "_30scZ").text
            # data = contato.find_element(By.CLASS_NAME, "Dvjym")
            if nome not in lista_contatos_recentes:
                lista_contatos_recentes.append(nome)
        self.lista_contatos = lista_contatos_recentes
        return lista_contatos_recentes

    def enviar_para_o_receptor(self):
        # O recetor seria a pessoa que irá receber a mensagem que deve ser
        # encaminhada para todas as outras a cada 5.
        # Clicar na lupa.
        self.navegador.find_element(
            'xpath',
            '//*[@id="side"]/div[1]/div/div/button/div[2]/span').click()
        # Escrever o nome de quem irá receber a mensagem para encaminhar para os outros.
        self.navegador.find_element(
            'xpath',
            '//*[@id="side"]/div[1]/div/div/div[2]/div/div[1]/p').send_keys(str(self.receptor))
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

        self.navegador.find_element('xpath',
                                    '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
                                    ).send_keys(Keys.ENTER)
        time.sleep(2)

    def _verificar_quantidade_de_envios(self):
        qtde_contatos = len(self.lista_contatos)
        if qtde_contatos % 5 == 0:
            blocos = qtde_contatos / 5
        else:
            blocos = int(qtde_contatos / 5) + 1
        return int(blocos)

    def encaminhar_a_mensagem(self):
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
                                            '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div[1]/p'
                                            ).send_keys(nome)
                time.sleep(1)
                # Dar enter
                self.navegador.find_element('xpath',
                                            '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div[1]/p'
                                            ).send_keys(Keys.ENTER)
                time.sleep(1)
                # Apagar o nome do contato
                self.navegador.find_element('xpath',
                                            '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div[1]/p'
                                            ).send_keys(Keys.BACKSPACE)
                time.sleep(1)

            self.navegador.find_element('xpath',
                                        '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/span/div/div/div/span'
                                        ).click()
            time.sleep(3)

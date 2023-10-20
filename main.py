from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager

import pyperclip
import time


class Scrapper:
    service = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=service)
    navegador.get("https://web.whatsapp.com/")

    def __init__(self, receptor, mensagem, lista_contatos):
        self.receptor = receptor
        self.mensagem = mensagem
        self.lista_contatos = lista_contatos

    def _enviar_para_o_receptor(self):
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
        return blocos

    def encaminhar_a_mensagem(self):
        self._enviar_para_o_receptor()
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

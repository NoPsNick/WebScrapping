import math
import time
from datetime import datetime, timedelta

import pyperclip

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class Sender:
    """
    A classe tem como função armazenar o navegador e as suas funções,
    para iniciarlizar ela, você irá precisar informar o receptor, ou seja, quem irá
    receber a mensagem para ser encaminhada para as outras pessoas e a mensagem que
    será encaminhada, também há outras, como a lista_contatos, que caso você já possua,
    já poderá ser informada em formato de lista do python e o foi_enviado em formato
    booleano se caso o receptor já possua a mensagem recebida.
    """
    service = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=service)

    def __init__(self, receptor: str,
                 mensagem: str,
                 lista_contatos: list = None,
                 foi_enviado: bool = False,
                 conectado: bool = False,
                 ignorar: list = None):

        self.conectado = conectado
        if lista_contatos is None:
            self.lista_contatos = []
        else:
            self.lista_contatos = lista_contatos
        self.receptor = receptor
        if ignorar is None:
            self.ignorar = []
        else:
            self.ignorar = ignorar
        self.mensagem = mensagem
        self.foi_enviado = foi_enviado

    # Ligar o WhatsApp, esperando até conectar-se de alguma forma, para continuar.
    def conectar(self):
        self.navegador.get("https://web.whatsapp.com/")
        while 1:
            try:
                WebDriverWait(self.navegador, 10).until(
                    ec.presence_of_element_located(
                        (By.XPATH,
                         '//*[@id="app"]/div/div/div[4]/header/div[1]/div/img'))
                )
                self.conectado = True
                return "Conectado"
            except:
                pass

    def _verificar(self):
        try:
            self.navegador.find_element(By.XPATH,
                                        '//*[@id="app"]/div/div/div[4]/header/div[1]/div/img')
            if not self.conectado:
                raise Exception("Conectar-se antes utilizando a função conectar()")
        except:
            raise Exception("Conectar-se antes utilizando a função conectar()")
        time.sleep(2)

    # A função pegar_contatos irá pegar todos os seus contatos da sua lista de contatos
    # guardando eles numa lista python.
    def pegar_contatos(self):
        self._verificar()
        # Ir para a lista de contatos.
        self.navegador.find_element(By.XPATH,
                                    '//*[@id="app"]/div/div/div[4]/header/div[2]/div/span/div[4]/div/span'
                                    ).click()

        # Ir para o final da lista de contatos
        origin = self.navegador.find_element(By.XPATH,
                                             '//*[@id="app"]/div/div/div[3]/div[1]/span/div/span/div/div[2]/div['
                                             '5]/div/div/div[1]/div/div[2]'
                                             )
        self._mover_pagina(pagina=origin, delta_y=1000000)

        # Pegar os contatos
        self._pegar_contatos()

        origin = self.navegador.find_element(By.XPATH,
                                             '//*[@id="app"]/div/div/div[3]/div[1]/span/div/span/div/div[2]')
        quebrar = False
        while 1:
            # Subir a página
            delta_y = int(-(1.7 * origin.rect['y']))
            self._mover_pagina(pagina=origin, delta_y=delta_y)
            # Pegar os contatos atuais mostrando
            contatos = self._pegar_contatos()

            # Pegar os separadores para poder ver se acabou os contatos
            quebrar = self._verificar_quebra(contatos, origin, quebrar)
            # Terminar o while
            if quebrar:
                break
        return self.lista_contatos

    def _pegar_contatos(self):
        try:
            contatos = self.navegador.find_elements(By.CLASS_NAME, '_30scZ')
            for contato in contatos:
                if (contato.text not in self.lista_contatos and
                        contato.text not in self.ignorar and contato.text.lower() != self.receptor.lower()):
                    self.lista_contatos.append(contato.text)
        except:
            time.sleep(0.5)
            contatos = self.navegador.find_elements(By.CLASS_NAME, '_30scZ')
            for contato in contatos:
                if (contato.text not in self.lista_contatos and
                        contato.text not in self.ignorar and contato.text.lower() != self.receptor.lower()):
                    self.lista_contatos.append(contato.text)
        return contatos

    def _verificar_quebra(self, contatos, origin, quebrar):
        try:
            separadores = self.navegador.find_elements(By.CLASS_NAME, '_2a-B5')
            for ele in separadores:
                if ele.text.lower() == 'contatos no whatsapp':
                    self._mover_pagina(pagina=origin, delta_y=-1000000)
                    time.sleep(0.5)
                    for contato in contatos:
                        if contato.text not in self.lista_contatos:
                            self.lista_contatos.append(contato.text)
                    quebrar = True
                    break
        except:
            time.sleep(0.5)
            separadores = self.navegador.find_elements(By.CLASS_NAME, '_2a-B5')
            for ele in separadores:
                if ele.text.lower() == 'contatos no whatsapp':
                    self._mover_pagina(pagina=origin, delta_y=-1000000)
                    time.sleep(0.5)
                    for contato in contatos:
                        if contato.text not in self.lista_contatos:
                            self.lista_contatos.append(contato.text)
                    quebrar = True
                    break
        return quebrar

    def _mover_pagina(self, pagina, delta_y):
        scroll_origin = ScrollOrigin.from_element(pagina)
        ActionChains(self.navegador) \
            .scroll_from_origin(scroll_origin, 0, delta_y) \
            .perform()
        time.sleep(0.5)

    # A função enviar_para_o_receptor irá enviar a mensagem para o receptor e tornar o
    # foi_enviado em True, podendo então encaminhar as mensagens.
    def enviar_para_o_receptor(self):
        self._verificar()
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
        blocos = math.ceil(len(self.lista_contatos) / 5)
        return blocos

    # A função encaminhar_a_mensagem irá encaminhar a mensagem para todos da lista_contatos,
    # num intervalo a cada 5 para não haver bloqueio por parte do WhatsApp.
    def encaminhar_a_mensagem(self):
        if str(type(self.lista_contatos)) == "<class 'dict'>":
            raise Exception("Utilizar o encaminhar_a_mensagem_com_data()")
        self._verificar()
        if self.foi_enviado:
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


class SenderWithDate(Sender):
    """
    Com as mesmas funções da classe Sender, porém com extras, sendo elas:\n
    eng > Que seria a tradução dos dias da semana para o inglês.\n
    weekdays > Diferenciação entre o dia da semana 0 Segunda, 6 Domingo para poder
    transformar os dias da semana em data normal.\n
    lista_contatos > Lista de contatos, porém em forma de dicionário python, sendo
    o nome da pessoa referindo-se a data dá última mensagem recebida.\n
    desde > Uma data em formato padrão 00/00/0000, exemplo 07/05/2023, sendo a data primária.\n
    ate > Uma data em formato padrão 00/00/0000, exemplo 09/09/2023, sendo a data final.\n
    Com ambos valores acima, usando o exemplo, todos na lista_contatos que enviar mensagem
    entre o desde(começo) e o ate(fim), 07/05/2023 até 09/09/2023, receberão a mensagem.
    """
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

    def __init__(self, receptor: str, mensagem: str, conectado: bool = False, lista_contatos: dict = None,
                 foi_enviado: bool = False, desde: str = '01/01/0001', ate=datetime.now().strftime('%d/%m/%Y', ),
                 ignorar: list = None):

        super().__init__(receptor, mensagem, lista_contatos, foi_enviado, conectado, ignorar)
        self.conectado = conectado
        self.desde = desde
        self.ate = ate
        if lista_contatos is None:
            self.lista_contatos = {}
        else:
            self.lista_contatos = lista_contatos

    def _converter_data(self, data):
        if data == 'Ontem':
            datanova = datetime.now() - timedelta(days=1)
            return datanova
        else:
            if data in self.eng.keys():
                pegar = self.weekdays[datetime.now().weekday()]
                valor = self.eng[data]
                datanova = (datetime.now() + timedelta(days=pegar[valor]))
                return datanova
            else:
                try:
                    datanova = datetime.strptime(data, '%d/%m/%Y')
                    return datanova
                except:
                    datanova = datetime.now()
                    return datanova

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
            data = self._converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
            pegar[nome] = data
        menor = min(pegar.values())
        for chave in pegar.keys():
            if menor == pegar[chave]:
                ultimo = chave
                return ultimo

    # Pega os contatos que enviaram mensagem para você e a data da última mensagem,
    # salvando em formato dicionário python, sendo nome: data
    def pegar_contatos_recentes(self):
        self._verificar()
        ultimo = self._pegar_ultimo()
        time.sleep(1)

        origin = self.navegador.find_element(By.XPATH,
                                             '//*[@id="pane-side"]')
        self._mover_pagina(pagina=origin, delta_y=-1000000)
        time.sleep(0.5)

        # Pegar os contatos e a data.
        self._pegar_contatos_com_data()

        quebrar = False
        while 1:
            # Descer a página
            delta_y = int(1.7 * (origin.rect['y']))
            self._mover_pagina(pagina=origin, delta_y=delta_y)
            self._pegar_contatos_com_data()

            quebrar = self._verificar_ultimo(origin, quebrar, ultimo)
            if quebrar:
                break

        return self.lista_contatos

    def _pegar_contatos_com_data(self):
        try:
            contatos = self.navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
            for contato in contatos:
                nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
                data = self._converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
                if nome not in self.ignorar and nome.lower() != self.receptor.lower():
                    self.lista_contatos[nome] = data
        except:
            time.sleep(0.5)
            contatos = self.navegador.find_elements(By.CLASS_NAME, '_8nE1Y')
            for contato in contatos:
                nome = contato.find_element(By.CLASS_NAME, "_11JPr").text
                data = self._converter_data(contato.find_element(By.CLASS_NAME, "aprpv14t").text)
                if nome not in self.ignorar and nome.lower() != self.receptor.lower():
                    self.lista_contatos[nome] = data

    def _verificar_ultimo(self, origin, quebrar, ultimo):
        if ultimo in self.lista_contatos:
            self._mover_pagina(pagina=origin, delta_y=1000000)
            self._pegar_contatos_com_data()
            quebrar = True
        return quebrar

    # Encaminhará a mensagem para os contados entre as datas entregues através
    # dos elementos "desde" e "ate", exemplo:
    # desde = 01/11/2023 ate = 06/11/2023, todos os contatos que enviaram mensagem
    # entre 01/11/2023 e 06/11/2023 irão receber o encaminhamento da mensagem.
    def encaminhar_a_mensagem_com_data(self):
        if str(type(self.lista_contatos)) == "<class 'list'>":
            raise Exception("Utilizar o encaminhar_a_mensagem")
        self._verificar()
        if self.foi_enviado:
            time.sleep(5)
            lista_atualizada = []
            for nome in self.lista_contatos.keys():
                desde = datetime.strptime(self.desde, '%d/%m/%Y')
                ate = datetime.strptime(self.ate, '%d/%m/%Y')
                try:
                    transformar = datetime.strptime(self.lista_contatos[nome], '%d/%m/%Y')
                except:
                    transformar = self.lista_contatos[nome]
                if desde <= transformar <= ate:
                    if (nome not in self.ignorar and nome.lower() != self.receptor.lower() and
                            nome not in lista_atualizada):
                        lista_atualizada.append(nome)
            if not lista_atualizada == {}:
                for i in range(self._verificar_quantidade_de_envios()):
                    # Rodar o codigo de encaminhar
                    i_inicial = i * 5
                    i_final = (i + 1) * 5
                    lista_enviar = lista_atualizada[i_inicial:i_final]

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
                                                '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div/span/div/'
                                                'div/div/span'
                                                ).click()
                    time.sleep(3)
        else:
            return "Envie para o receptor primeiro, caso contrário, ocorrerá um erro."

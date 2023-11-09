# WebScrapping
Serão dois webscrapping, o primeiro(aula_webscrapping) é do youtube para aprendizagem, o segundo será utilizando tais conhecimento para fazer algo.
Foi finalizado, lembrando que este projeto foi feito totalmente baseando-se para fins de estudos, diversas notas foram evidentemente feitas para o melhor
entendimento do que está acontecendo naquele local apenas para estudo, ou seja, nada muito rebuscado e complicado para não ficar difícil o entendimento.

São duas classes, onde a segunda é uma extensão da outra, ou uma herança da primeira, sendo elas: Sender e SenderWithDate.
Sender: A base da classe, onde você fornece o receptor e a mensagem, primeiramente terá de se conectar no whatsapp utilizando a função
conectar, para então fazer o que deseja, como, enviar a mensagem para o receptor, para conseguir encaminhar, pegar todos os seus contatos
que receberão o encaminhamento da mensagem, ou apenas fornecer os contatos manualmente, você também pode já deixar a mensagem no receptor
e apenas informar que o recebido = True, porém caso ele não tenha a mensagem, erros podem acontecer, por fim conseguir encaminhar para todos
da lista ou informada ou coletada automaticamente de sua lista de contatos.
SenderWithDate: Herando a classe Sender, ela possuí as mesmas funções, porém o extra seria pegar os contatos que lhe enviaram alguma mensagem
e com isso pegar suas respectivas datas, para então utilizar o desde e o até, sendo assim, conseguir mandar mensagem apenas paras as pessoas
entre as datas informadas, como, desde = 01/10/2020 e ate = 01/11/2020, todos que enviaram a mensagem desde 01/10/2020 até todos que enviaram
em 01/11/2020 receberão o encaminhamento.

Exemplos:
# Sender

# Inicializar a classe.
principal = Sender(receptor="João", Mensagem="Quinta-Feira é dia de hora extra.")

# Totalmente necessário para ligar a página web para que você possa conectar seu WhatsApp.
print(principal.conectar())

# Enviar a mensagem para o receptor.
principal.enviar_para_o_receptor()

# Pegar contatos da lista de contatos do WhatsApp.
print(principal.pegar_contatos())

# Encaminhar a mensagem enviada para o receptor para todos da lista de contatos pegos, a cada 5.
principal.encaminhar_a_mensagem()

# Outra forma...

# Inicializar a classe, porém com a lista já informada.
secundario = Sender(receptor="João", Mensagem="Quinta-Feira é dia de hora extra.", lista_contatos=["Cleiton", "Cleber", "Maria", "Joseana", "Wagner"])

# Totalmente necessário para ligar a página web para que você possa conectar seu WhatsApp.
print(secundario.conectar())

# Enviar a mensagem para o receptor.
secundario.enviar_para_o_receptor()

# Encaminhar a mensagem enviada para o receptor para todos da lista de contatos informados, a cada 5.
secundario.encaminhar_a_mensagem()

# SenderWithDate

# Inicializar a classe.
principal = SenderWithDate(receptor="João", Mensagem="Salário será enviado em breve.", deste="11/10/2022", ate="05/11/2022")

# Totalmente necessário para ligar a página web para que você possa conectar seu WhatsApp.
print(principal.conectar())

# Enviar a mensagem para o receptor.
principal.enviar_para_o_receptor()

# Pegar contatos da lista de contatos do WhatsApp, porém com as datas inclusas.
print(principal.pegar_contatos_recentes())

# Encaminhar a mensagem enviada para o receptor para os contatos que estão entre o desde e o ate, a cada 5.
principal.encaminhar_a_mensagem()

# Outra forma...

# Inicializar a classe, porém com a lista já informada.
secundario = Sender(receptor="João", Mensagem="Salário será enviado em breve.", 
               lista_contatos={"Cleiton":"18/10/2022", "Cleber":"05/10/2022", "Maria":"12/09/2022", "Joseana":"05/11/2022", "Wagner":"03/10/2022"},
               deste="11/10/2022", ate="05/11/2022")

# Totalmente necessário para ligar a página web para que você possa conectar seu WhatsApp.
print(secundario.conectar())

# Enviar a mensagem para o receptor.
secundario.enviar_para_o_receptor()

# Encaminhar a mensagem enviada para o receptor para os contatos que estão entre o desde e o ate, a cada 5, Wagner e Maria não receberão o encaminhamento...
secundario.encaminhar_a_mensagem()

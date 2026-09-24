import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "episodios")
AVISO = "História de ficção, inspirada em causo de família."
DM = "Tem uma história assim? Me manda no direct — eu conto sem nome e sem rosto."

def B(fala, expr="neutra", arte=None, dest=(), tela=None, zoom=False):
    b = {"fala": fala, "expr": expr, "arte": arte, "destaque": list(dest)}
    if tela: b["tela"] = tela
    if zoom: b["zoom"] = True; b["arte"] = None
    return b

def ep(n, titulo, temporada, p1, p2, leg1, leg2, tags):
    for parte, bats, leg, cen, fim in ((1, p1, leg1, "tarde", "CONTINUA NA PARTE 2"),
                                       (2, p2, leg2, "noite", "SEGUE A NINA")):
        d = {"id": f"ep{n:03d}-p{parte}", "ep": n, "parte": parte, "titulo": titulo,
             "temporada": temporada, "cenario": cen, "batidas": bats, "fim": fim,
             "legenda_post": f"{leg}\n\n{DM}\n\n{AVISO}\n\n{tags}"}
        json.dump(d, open(os.path.join(D, d["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- EP02
ep(2, "A PULSEIRA VIP", "Noite", [
 B("Ela achou a pulseira quando foi tirar a roupa da máquina de lavar.", "ironica", ["titulo"], ["pulseira"]),
 B("Quem me mandou foi a Tatiane, vinte e oito anos, noiva do Rodrigo. Casamento marcado pra daqui a três semanas.", "neutra", ["direct", "TATIANE, 28"], ["três", "semanas."], tela="Quem me mandou foi a Tatiane, 28 anos, noiva do Rodrigo. Casamento daqui a 3 semanas."),
 B("Me segue, que essa tem duas partes, e a segunda você não vai acreditar.", "ironica", ["seguir"], ["segue,"]),
 B("Uma pulseira de balada. Rosa neon. Escrito VIP.", "desconfiada", ["pulseira", "VIP"], ["VIP."]),
 B("No sábado, o Rodrigo tinha dito que ia virar a noite fazendo inventário no estoque da loja.", "desconfiada", ["relogio", "23:00"], ["estoque"]),
 B("Estoque não dá pulseira VIP. Pelo menos nenhum que eu conheça.", "ironica", None, ["VIP."]),
 B("Ela pesquisou o nome da casa noturna que estava apagadinho na pulseira.", "neutra", ["celular", "Club Aurora"], ["pesquisou"]),
 B("E foi olhar as fotos que a própria balada posta toda segunda-feira.", "desconfiada", ["foto", "SÁBADO"], ["fotos"]),
 B("Foto dezessete. Camarote. Lá estava o Rodrigo.", "chocada", zoom=True, dest=["Rodrigo."], tela="Foto 17. Camarote. Lá estava o Rodrigo."),
 B("Com a mão na cintura de uma mulher de vestido verde, de costas pra câmera.", "brava", ["interrogacao"], ["verde,"]),
 B("De costas. Só dava pra ver o cabelo preso e uma tatuagem pequena no ombro.", "desconfiada", None, ["tatuagem"]),
 B("E a Tatiane conhecia aquela tatuagem. Uma andorinha.", "chocada", ["manchete", "UMA ANDORINHA"], ["andorinha."]),
 B("Ela já tinha visto aquela andorinha. Três vezes. Todas na mesma semana.", "desconfiada", ["calendario", "ESSA SEMANA"], ["mesma", "semana."]),
 B("Em todas as reuniões de preparação do casamento.", "triste", zoom=True, dest=["casamento."]),
 B("De quem era a andorinha, eu conto na parte dois. Chuta aqui nos comentários.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você caiu aqui agora, volta na parte um. A andorinha está lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("A Tatiane passou a noite olhando pra foto dezessete, dando zoom no ombro da mulher.", "neutra", ["foto", "FOTO 17"], ["foto", "dezessete,"], tela="A Tatiane passou a noite olhando a foto 17, dando zoom no ombro da mulher."),
 B("Me segue antes, que amanhã tem outra dessas.", "ironica", ["seguir"], ["segue"]),
 B("No dia seguinte tinha reunião marcada. Degustação do bufê.", "neutra", ["cafe"], ["bufê."]),
 B("E quem abriu a porta do espaço de eventos foi a cerimonialista. A Bianca.", "desconfiada", ["porta"], ["Bianca."]),
 B("Cabelo preso. Blusa de alcinha.", "desconfiada", None, ["alcinha."]),
 B("E uma andorinha no ombro.", "chocada", zoom=True, dest=["andorinha"]),
 B("A mulher que estava organizando o casamento dela estava organizando também o noivo.", "brava", ["alianca", "3 SEMANAS"], ["noivo."]),
 B("A Tatiane provou os salgadinhos, sorriu e escolheu o bolo de nozes.", "ironica", ["presente"], ["sorriu"]),
 B("Sem falar nada. Nenhuma palavra.", "neutra", None, ["Nenhuma"]),
 B("Na saída, a Bianca abraçou ela e disse: fica tranquila, vai ser o dia mais lindo da sua vida.", "desconfiada", ["conversa", "Fica tranquila, vai ser o dia mais lindo da sua vida."], ["mais", "lindo"]),
 B("O casamento continua marcado. Três semanas. Tudo pago.", "triste", ["extrato", "BUFÊ · PAGO"], ["Tudo", "pago."], tela="O casamento continua marcado. 3 semanas. Tudo pago."),
 B("E ela me perguntou uma coisa que eu não soube responder.", "neutra", ["interrogacao"], ["responder."]),
 B("Ela cancela tudo agora? Ou deixa a Bianca organizar o casamento até o fim, e fala no altar?", "ironica", ["manchete_v", "CANCELA OU NO ALTAR?"], ["altar?"]),
 B("Me conta aqui nos comentários o que você faria.", "ironica", ["manchete", "E VOCÊ?"], ["comentários"]),
], "Ela achou a pulseira na máquina de lavar. Rosa neon. Escrito VIP. 💃\n\nO noivo disse que ia virar a noite no estoque… mas estoque não dá pulseira de camarote. De quem era a andorinha no ombro? PARTE 2 no perfil.",
 "A andorinha no ombro era de quem ela menos esperava. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nE agora: ela cancela tudo ou deixa a cerimonialista organizar até o fim e fala no altar? Me conta nos comentários. 👇",
 "#traição #noivado #casamento #balada #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

# ---------------------------------------------------------------- EP03
ep(3, "O CRACHÁ DE VISITANTE", "Trabalho", [
 B("Ele achou um crachá de visitante no bolso do casaco dela. Com data de sábado.", "ironica", ["titulo"], ["sábado."]),
 B("Essa quem me mandou foi um homem. O Marcos, trinta e cinco anos, casado com a Renata há nove.", "neutra", ["direct", "MARCOS, 35"], ["Marcos,"], tela="Essa quem me mandou foi um homem. O Marcos, 35 anos, casado com a Renata há 9."),
 B("Me segue, porque essa história tem duas partes e um final que eu nunca vi.", "ironica", ["seguir"], ["segue,"]),
 B("Naquele sábado a Renata tinha passado o dia na casa da mãe. Foi o que ela disse.", "neutra", ["calendario", "SÁBADO"], ["mãe."]),
 B("Só que o crachá era de um prédio comercial no centro. Visitante. Sala mil duzentos e quatro.", "desconfiada", ["cracha", "VISITANTE SALA 1204"], ["1204."], tela="Só que o crachá era de um prédio comercial no centro. Visitante. Sala 1204."),
 B("Prédio comercial. Num sábado. Quem trabalha em prédio comercial num sábado?", "ironica", ["interrogacao"], ["sábado?"]),
 B("O Marcos não perguntou nada. Guardou o crachá na carteira.", "neutra", None, ["carteira."]),
 B("Na segunda, ele pediu a tarde de folga e foi até o prédio.", "desconfiada", ["carro"], ["prédio."]),
 B("Olhou o painel das salas no elevador. Mil duzentos e quatro.", "desconfiada", ["porta", "1204"], ["1204."], tela="Olhou o painel das salas no elevador. 1204."),
 B("E ali estava o nome da empresa. Uma consultoria.", "chocada", zoom=True, dest=["consultoria."]),
 B("A consultoria do chefe da Renata. O mesmo chefe que tinha jantado na casa deles no Natal.", "brava", ["manchete", "O CHEFE"], ["Natal."]),
 B("O Marcos desceu, sentou no carro e ficou ali. Parado.", "triste", ["carro"], ["Parado."]),
 B("Foi quando o celular vibrou. Uma mensagem de um número que ele não conhecia.", "desconfiada", ["notificacao", "Número desconhecido"], ["não", "conhecia."]),
 B("Oi, Marcos. Acho que a gente precisa conversar. Aqui é a mulher do Otávio.", "chocada", zoom=True, dest=["Otávio."]),
 B("O que ela queria com ele, eu conto na parte dois.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você chegou agora, volta na parte um. O crachá explica tudo.", "ironica", ["titulo"], ["parte", "um."]),
 B("A mensagem era da Luciana. A esposa do Otávio, o chefe da Renata.", "neutra", ["conversa", "Aqui é a mulher do Otávio."], ["Luciana."]),
 B("Me segue antes de continuar, que amanhã tem mais.", "ironica", ["seguir"], ["segue"]),
 B("Os dois marcaram um café. Numa padaria bem longe de tudo.", "neutra", ["cafe"], ["café."]),
 B("A Luciana chegou com uma pasta. Dentro, tudo organizado por data.", "desconfiada", ["extrato", "SALA 1204 · SÁBADOS"], ["pasta."]),
 B("Recibos, horários, fotos do carro da Renata na garagem do prédio.", "chocada", ["foto", "GARAGEM"], ["garagem"]),
 B("Ela desconfiava fazia oito meses. Oito meses juntando prova.", "chocada", zoom=True, dest=["oito", "meses."]),
 B("E aí ela fez uma proposta que o Marcos não esperava.", "desconfiada", None, ["proposta"]),
 B("Daqui a quinze dias tem a festa de fim de ano da empresa. Os dois casais foram convidados.", "ironica", ["presente", "FESTA"], ["festa"], tela="Daqui a 15 dias tem a festa de fim de ano da empresa. Os dois casais foram convidados."),
 B("A Luciana quer ir. Quer que o Marcos vá também. E quer entregar a pasta na frente de todo mundo.", "brava", ["carimbo", "NA FRENTE DE TODOS"], ["todo", "mundo."]),
 B("O Marcos não sabe se quer fazer isso. Nove anos de casamento.", "triste", ["alianca", "9 ANOS"], ["Nove", "anos"], tela="O Marcos não sabe se quer fazer isso. 9 anos de casamento."),
 B("E a Renata ainda não sabe de nada. Continua indo pra mãe dela aos sábados.", "ironica", ["calendario", "SÁBADO"], ["sábados."]),
 B("Então ele me perguntou. E eu passo pra vocês.", "neutra", ["interrogacao"], ["vocês."]),
 B("Ele vai na festa com a Luciana, ou conversa com a Renata antes, sozinho? Me conta aqui embaixo.", "ironica", ["manchete_v", "FESTA OU CONVERSA?"], ["festa"]),
], "Um crachá de visitante no bolso dela. Com data de sábado. 🏢\n\nEla disse que estava na casa da mãe. O crachá dizia sala 1204. E aí chegou uma mensagem que ele não esperava. PARTE 2 no perfil.",
 "Oito meses juntando prova. E uma festa de fim de ano marcada. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nEle vai na festa com a Luciana ou conversa com a esposa antes? Me conta nos comentários. 👇",
 "#traição #chefe #trabalho #casamento #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

# ---------------------------------------------------------------- EP04
ep(4, "OS QUILÔMETROS DO CAIO", "Casais", [
 B("Ele descobriu tudo por um aplicativo de corrida.", "ironica", ["titulo"], ["corrida."]),
 B("Quem me escreveu foi o Rafael, vinte e nove anos. Dois anos de namoro com o Caio.", "neutra", ["direct", "RAFAEL, 29"], ["Rafael,"], tela="Quem me escreveu foi o Rafael, 29 anos. 2 anos de namoro com o Caio."),
 B("Me segue, que essa tem duas partes.", "ironica", ["seguir"], ["segue,"]),
 B("O Caio corria toda terça e quinta. Dez quilômetros, sempre depois do trabalho.", "neutra", ["haltere"], ["terça", "quinta."], tela="O Caio corria toda terça e quinta. 10 km, sempre depois do trabalho."),
 B("O Rafael achava o máximo. Até curtia as corridas no aplicativo.", "neutra", ["celular", "Corrida: 10,2 km"], ["curtia"]),
 B("Até que um dia ele reparou no tempo. Dez quilômetros em uma hora e cinquenta.", "desconfiada", ["relogio", "1:50"], ["uma", "hora", "e", "cinquenta."], tela="Até que um dia ele reparou no tempo. 10 km em 1h50."),
 B("Isso não é corrida. Isso é caminhada com parada.", "ironica", None, ["parada."]),
 B("Ele abriu o mapa da corrida. E viu uma pausa.", "desconfiada", ["mapa"], ["pausa."]),
 B("Quarenta minutos parado. No mesmo ponto. Toda terça. Toda quinta.", "chocada", zoom=True, dest=["Quarenta", "minutos"], tela="40 minutos parado. No mesmo ponto. Toda terça. Toda quinta."),
 B("Rua das Acácias, cento e dezoito.", "desconfiada", ["porta", "118"], ["118."], tela="Rua das Acácias, 118."),
 B("O Rafael conhecia esse endereço. Já tinha deixado um presente de aniversário ali.", "chocada", ["presente"], ["presente"]),
 B("Dois anos atrás. Logo no começo do namoro.", "triste", ["calendario", "2 ANOS ATRÁS"], ["começo"]),
 B("A pedido do próprio Caio.", "brava", zoom=True, dest=["Caio."]),
 B("Quem mora na Rua das Acácias, eu conto na parte dois. E você, já sabe?", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você chegou agora, volta na parte um. O mapa está lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("Na Rua das Acácias, cento e dezoito, mora o Henrique. O ex do Caio.", "neutra", ["porta", "118"], ["ex"], tela="Na Rua das Acácias, 118, mora o Henrique. O ex do Caio."),
 B("Antes de continuar, me segue. Amanhã tem outra.", "ironica", ["seguir"], ["segue."]),
 B("O Caio sempre disse que eles eram só amigos. Que o fim tinha sido tranquilo.", "desconfiada", ["foto", "SÓ AMIGOS"], ["só", "amigos."]),
 B("O Rafael foi até lá numa quinta. Parou o carro do outro lado da rua.", "desconfiada", ["carro"], ["quinta."]),
 B("Sete e dez, o Caio chegou correndo. Tocou o interfone. A porta abriu.", "chocada", ["relogio", "19:10"], ["porta", "abriu."], tela="19h10, o Caio chegou correndo. Tocou o interfone. A porta abriu."),
 B("Quarenta minutos depois, saiu. Correndo de novo. Pra fechar os dez quilômetros.", "ironica", ["relogio", "19:50"], ["dez", "quilômetros."], tela="40 minutos depois, saiu. Correndo de novo. Pra fechar os 10 km."),
 B("No sábado, chegou um envelope na casa do Rafael e do Caio.", "neutra", ["presente", "CONVITE"], ["envelope"]),
 B("Um convite de casamento. Do Henrique.", "chocada", zoom=True, dest=["Henrique."]),
 B("O Henrique vai casar no mês que vem. E convidou os dois.", "desconfiada", ["alianca", "MÊS QUE VEM"], ["os", "dois."]),
 B("O Caio olhou o convite e disse: que bom, né? Ele merece ser feliz.", "ironica", ["conversa", "Que bom, né? Ele merece ser feliz."], ["merece"]),
 B("O Rafael não falou nada. Guardou o print do mapa.", "triste", ["mapa"], ["print"]),
 B("E agora ele me perguntou o que fazer com isso.", "neutra", ["interrogacao"], ["fazer"]),
 B("Ele vai no casamento e fala com o noivo? Ou confronta o Caio antes? Me diz aqui nos comentários.", "ironica", ["manchete_v", "VAI OU NÃO VAI?"], ["comentários."]),
], "O namorado corria 10 km toda terça e quinta. Em 1h50. 🏃\n\nNo mapa, uma pausa de 40 minutos no mesmo endereço. E o Rafael conhecia aquele endereço. PARTE 2 no perfil.",
 "Um convite de casamento chegou pelo correio. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nEle vai no casamento e fala com o noivo, ou confronta o namorado antes? Me conta nos comentários. 👇",
 "#traição #namoro #casal #corrida #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

# ---------------------------------------------------------------- EP05
ep(5, "O PORTÃO DA GARAGEM", "Vizinhança", [
 B("Ela apertou o controle do portão e abriu a garagem errada.", "ironica", ["titulo"], ["garagem", "errada."]),
 B("Quem me mandou foi a Cláudia, quarenta e dois anos, casada com o Sérgio há quinze.", "neutra", ["direct", "CLÁUDIA, 42"], ["Cláudia,"], tela="Quem me mandou foi a Cláudia, 42 anos, casada com o Sérgio há 15."),
 B("Me segue, que essa é em duas partes e o condomínio inteiro participa.", "ironica", ["seguir"], ["segue,"]),
 B("O Sérgio trocou o carro de vaga. Disse que a vaga antiga era muito apertada.", "neutra", ["carro"], ["vaga."]),
 B("Ele pegou emprestada uma vaga coberta. Na garagem da casa do lado.", "desconfiada", ["porta"], ["casa", "do", "lado."]),
 B("A casa da Vera. A vizinha do marido embarcado, que passa trinta dias no mar.", "desconfiada", ["mala", "30 DIAS"], ["embarcado,"], tela="A casa da Vera. A vizinha do marido embarcado, que passa 30 dias no mar."),
 B("Tudo combinado, tudo educado. A Vera até mandou um bolo de agradecimento.", "ironica", ["presente", "OBRIGADA!"], ["bolo"]),
 B("Um dia a Cláudia pegou o controle do Sérgio pra tirar o carro dela.", "neutra", None, ["controle"]),
 B("Eram onze da noite. O Sérgio tinha dito que ia na farmácia.", "desconfiada", ["relogio", "23:00"], ["farmácia."], tela="Eram 23h. O Sérgio tinha dito que ia na farmácia."),
 B("Ela apertou o botão errado. E o portão da Vera começou a subir.", "chocada", zoom=True, dest=["Vera"]),
 B("O carro do Sérgio estava lá dentro. Motor ainda quente.", "desconfiada", ["carro"], ["quente."]),
 B("Farmácia não fica dentro da garagem da vizinha.", "ironica", None, ["farmácia"]),
 B("E a luz da sala da Vera, que sempre apaga às dez, estava acesa.", "chocada", ["manchete", "LUZ ACESA"], ["acesa."]),
 B("O que a Cláudia fez com aquele controle na mão, eu conto na parte dois.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você caiu aqui agora, volta na parte um. O controle está lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("A Cláudia fechou o portão. Voltou pra casa. E esperou na sala, no escuro.", "neutra", ["porta"], ["escuro."]),
 B("Me segue antes, que amanhã tem outra.", "ironica", ["seguir"], ["segue"]),
 B("O Sérgio chegou meia-noite e meia. Com uma sacola de farmácia vazia.", "ironica", ["relogio", "00:30"], ["vazia."], tela="O Sérgio chegou 0h30. Com uma sacola de farmácia vazia."),
 B("Ela não perguntou nada. Ficou com o controle.", "desconfiada", None, ["controle."]),
 B("No dia seguinte, o grupo do condomínio apitou.", "neutra", ["notificacao", "Grupo do condomínio"], ["grupo"]),
 B("Era a Vera: gente, o Jorge desembarca sexta. Vamos fazer um churrasco de boas-vindas?", "chocada", ["conversa", "O Jorge desembarca sexta! Churrasco de boas-vindas?"], ["sexta."]),
 B("E marcou todo mundo. Inclusive a Cláudia. Inclusive o Sérgio.", "brava", zoom=True, dest=["Sérgio."]),
 B("O Jorge, o marido da Vera, é um homem que a Cláudia conhece faz quinze anos.", "triste", ["foto", "VIZINHOS"], ["quinze", "anos."], tela="O Jorge, o marido da Vera, é um homem que a Cláudia conhece faz 15 anos."),
 B("Ajudou a carregar a mudança dela. Foi padrinho do batizado do filho dela.", "triste", ["alianca", "PADRINHO"], ["padrinho"]),
 B("E o churrasco é sábado. Na garagem da Vera.", "ironica", ["calendario", "SÁBADO"], ["garagem"]),
 B("A Cláudia ainda está com o controle do portão na bolsa.", "desconfiada", ["mala"], ["controle"]),
 B("E me perguntou uma coisa.", "neutra", ["interrogacao"], ["perguntou"]),
 B("Ela conta pro Jorge antes do churrasco? Ou deixa o churrasco acontecer e fala na frente do condomínio inteiro? Me conta aqui.", "ironica", ["manchete_v", "ANTES OU NO CHURRASCO?"], ["churrasco?"]),
], "Ela apertou o controle do portão e abriu a garagem da vizinha. 🚗\n\nO marido tinha ido na farmácia. O carro dele estava lá dentro, com o motor quente. PARTE 2 no perfil.",
 "O marido da vizinha desembarca sexta. E o churrasco é sábado. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nEla conta pro Jorge antes ou fala no churrasco na frente de todo mundo? Me conta nos comentários. 👇",
 "#traição #vizinha #condomínio #casamento #storytime #históriadetraição #desabafo #fofoca #ninamecontou")
print("ok")

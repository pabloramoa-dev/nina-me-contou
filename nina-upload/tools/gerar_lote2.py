"""Lote 2 — EP06 a EP11 (ritmo novo: 2 episódios por dia).
Sem batida "me segue": o motor/cta.py põe o CTA de seguir no FINAL de cada vídeo.

    python tools/gerar_lote2.py
"""
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
        with open(os.path.join(D, d["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- EP06
ep(6, "A GARRAFINHA", "Academia", [
 B("A garrafinha de água dele voltou do treino com o nome de outra academia.", "ironica", ["titulo"], ["outra", "academia."]),
 B("Quem me mandou foi a Juliana, trinta e um anos, casada com o Diego há seis.", "neutra", ["direct", "JULIANA, 31"], ["Juliana,"], tela="Quem me mandou foi a Juliana, 31 anos, casada com o Diego há 6."),
 B("O Diego treina todo dia depois do trabalho. Na academia do bairro, a duas quadras de casa.", "neutra", ["haltere"], ["duas", "quadras"]),
 B("Ela até foi com ele uma vez. Achou pequena, abafada, mas tudo bem.", "ironica", None, ["abafada,"]),
 B("Numa segunda, ela foi lavar a garrafinha dele. Uma rosa, de plástico duro.", "desconfiada", ["caneca", "GARRAFINHA"], ["rosa,"]),
 B("E embaixo, num adesivo, estava escrito: Studio Equilíbrio. Unidade Centro.", "chocada", ["manchete", "STUDIO EQUILÍBRIO"], ["Studio", "Equilíbrio."]),
 B("Unidade Centro. Do outro lado da cidade. Quarenta minutos de ônibus.", "desconfiada", ["mapa", "40 MIN"], ["outro", "lado"], tela="Unidade Centro. Do outro lado da cidade. 40 minutos de ônibus."),
 B("E o Diego nunca teve garrafinha rosa. Ele só usa aquela preta, amassada.", "ironica", None, ["preta,"]),
 B("Ela perguntou, com jeitinho. Ele disse: ah, peguei emprestada de alguém no treino.", "desconfiada", ["conversa", "Peguei emprestada de alguém no treino."], ["alguém"]),
 B("Alguém. Na academia do bairro. Com garrafinha de outra academia.", "ironica", ["interrogacao"], ["Alguém."]),
 B("A Juliana abriu o Instagram do tal studio. E foi rolando as fotos.", "neutra", ["celular", "@studio.equilibrio"], ["rolando"]),
 B("Na terceira foto, uma turma de funcional. E no canto, de boné, o Diego.", "chocada", zoom=True, dest=["Diego."]),
 B("Quem estava do lado dele, eu conto na parte dois. Chuta aí.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você caiu aqui agora, volta na parte um. A garrafinha rosa está lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("Do lado do Diego, na foto, estava uma professora. Camiseta do studio. Garrafinha rosa na mão.", "desconfiada", ["foto", "TURMA DAS 19H"], ["Garrafinha", "rosa"]),
 B("A legenda da foto dizia: turma das sete, a mais animada.", "ironica", ["notificacao", "Turma das 19h, a mais animada!"], ["sete,"], tela="A legenda dizia: turma das 19h, a mais animada."),
 B("Sete da noite. O horário em que o Diego jurava estar a duas quadras de casa.", "brava", ["relogio", "19:00"], ["duas", "quadras"]),
 B("A Juliana não brigou. Fez uma coisa melhor.", "neutra", None, ["melhor."]),
 B("Marcou uma aula experimental no studio. Turma das sete.", "ironica", ["calendario", "QUINTA · 19H"], ["experimental"]),
 B("Chegou dez minutos antes. Colocou a garrafinha rosa em cima do banco.", "desconfiada", ["caneca", "GARRAFINHA"], ["garrafinha", "rosa"]),
 B("A professora entrou, olhou a garrafinha e sorriu: ué, essa é minha! Onde você achou?", "chocada", ["conversa", "Ué, essa é minha! Onde você achou?"], ["essa", "é", "minha!"]),
 B("E nessa hora, a porta abriu. E entrou o Diego.", "chocada", zoom=True, dest=["Diego."]),
 B("Ele viu a esposa. Viu a professora. Viu a garrafinha.", "ironica", ["interrogacao"], ["garrafinha."]),
 B("E disse: amor, eu ia te contar que troquei de academia.", "brava", ["conversa", "Amor, eu ia te contar que troquei de academia."], ["troquei"]),
 B("A aula começou. Os três ficaram. Ninguém falou nada.", "triste", None, ["Ninguém"]),
 B("E agora a Juliana me pergunta: ela devolve a garrafinha pra professora, ou pro marido? Me conta aqui.", "ironica", ["manchete_v", "DEVOLVE PRA QUEM?"], ["devolve"]),
], "A garrafinha dele voltou do treino com o nome de OUTRA academia. 🏋️\n\nDo outro lado da cidade. Na turma das 7. E numa foto, de boné, o marido. PARTE 2 no perfil.",
 "Ela marcou uma aula experimental. Na turma das 7. Com a garrafinha rosa na mão. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nE agora: devolve a garrafinha pra professora ou pro marido? Me conta nos comentários. 👇",
 "#traição #academia #casamento #treino #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

# ---------------------------------------------------------------- EP07
ep(7, "A COLEGA DO CAFÉ", "Trabalho", [
 B("Duas xícaras. Sempre lavadas juntas. Sempre guardadas juntas.", "ironica", ["titulo"], ["Duas", "xícaras."]),
 B("Essa quem me mandou foi a Patrícia, trinta e oito anos. Ela trabalha na mesma firma que o marido, o Fábio.", "neutra", ["direct", "PATRÍCIA, 38"], ["mesma", "firma"], tela="Quem me mandou foi a Patrícia, 38 anos. Trabalha na mesma firma que o marido, o Fábio."),
 B("Setores diferentes, andares diferentes. Ela no terceiro, ele no quinto.", "neutra", ["cracha", "ANDAR 5"], ["quinto."]),
 B("Um dia a máquina de café do terceiro andar quebrou. Ela subiu pro quinto.", "neutra", ["cafe"], ["quinto."]),
 B("Na copa, no escorredor, tinha uma caneca que ela conhecia. A caneca do Fábio. Do time dele.", "desconfiada", ["caneca", "DO FÁBIO"], ["caneca", "do", "Fábio."]),
 B("E do lado, encostada nela, uma xícara branca com um batom na borda.", "desconfiada", ["batom"], ["batom"]),
 B("Até aí, tudo bem. Copa é de todo mundo.", "ironica", None, ["todo", "mundo."]),
 B("Só que ela subiu no dia seguinte. E no outro. E as duas estavam sempre lá. Juntas.", "desconfiada", ["calendario", "3 DIAS SEGUIDOS"], ["Juntas."]),
 B("A faxineira do andar, a dona Neide, viu ela olhando e comentou baixinho.", "neutra", None, ["dona", "Neide,"]),
 B("Essas duas aí? Eles lavam juntos todo dia às três. É o café dos dois.", "chocada", ["conversa", "Eles lavam juntos todo dia às 3. É o café dos dois."], ["café", "dos", "dois."], tela="Essas duas aí? Eles lavam juntos todo dia às 3. É o café dos dois."),
 B("O café dos dois. O Fábio nem toma café. Pelo menos em casa, nunca tomou.", "ironica", None, ["nunca"]),
 B("No dia seguinte, às três em ponto, a Patrícia subiu pro quinto andar.", "desconfiada", ["relogio", "15:00"], ["três", "em", "ponto,"], tela="No dia seguinte, às 15h em ponto, a Patrícia subiu pro quinto andar."),
 B("Quem estava lavando a xícara do batom, eu conto na parte dois.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você caiu aqui agora, volta na parte um. As duas xícaras estão lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("Na copa do quinto andar, de costas pra porta, estava o Fábio. Lavando a caneca do time.", "desconfiada", ["caneca", "DO FÁBIO"], ["Fábio."]),
 B("E do lado dele, secando a xícara branca, a Sônia. A chefe da Patrícia.", "chocada", zoom=True, dest=["chefe"]),
 B("A chefe que tinha dado pra ela a pior avaliação do ano. Um mês antes.", "brava", ["extrato", "AVALIAÇÃO: REGULAR"], ["pior", "avaliação"]),
 B("A Sônia viu a Patrícia na porta e não perdeu a pose. Disse: ué, a máquina lá de baixo ainda não voltou?", "ironica", ["conversa", "Ué, a máquina lá de baixo ainda não voltou?"], ["pose."]),
 B("O Fábio derrubou a caneca. Quebrou a alça.", "chocada", None, ["Quebrou"]),
 B("A Patrícia pegou um copinho de plástico, tirou um café, e voltou pro terceiro andar.", "neutra", ["cafe"], ["copinho"]),
 B("Sem uma palavra. Nenhuma.", "neutra", None, ["Nenhuma."]),
 B("Em casa, o Fábio chegou com um discurso pronto: era só café, é colega, você está vendo coisa.", "ironica", ["conversa", "Era só café. Você está vendo coisa."], ["vendo", "coisa."]),
 B("Só que tem um detalhe. Na sexta tem a reunião de metas. Com a Sônia. E com o diretor.", "desconfiada", ["calendario", "SEXTA · METAS"], ["diretor."]),
 B("E a Patrícia guardou uma foto. Das duas xícaras, juntas, no escorredor.", "desconfiada", ["foto", "COPA · 5º ANDAR"], ["foto."]),
 B("Ela me perguntou o que fazer com essa foto.", "neutra", ["interrogacao"], ["foto."]),
 B("Mostra na reunião, na frente do diretor? Ou resolve só em casa? Me conta aqui nos comentários.", "ironica", ["manchete_v", "REUNIÃO OU EM CASA?"], ["comentários."]),
], "Duas xícaras. Sempre lavadas juntas. Sempre às 3 da tarde. ☕\n\nE uma delas era a caneca do marido dela, que nem toma café. PARTE 2 no perfil.",
 "Ela subiu pro 5º andar às 3 em ponto. E a xícara do batom era de quem ela menos queria. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nMostra a foto na reunião ou resolve em casa? Me conta nos comentários. 👇",
 "#traição #trabalho #firma #colegadetrabalho #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

# ---------------------------------------------------------------- EP08
ep(8, "A ENCOMENDA ERRADA", "Vizinhança", [
 B("O entregador tocou a campainha errada. E ela abriu um pacote que não era pra ela.", "ironica", ["titulo"], ["pacote"]),
 B("Quem me mandou foi a Simone, quarenta e cinco anos, casada com o Alberto há vinte.", "neutra", ["direct", "SIMONE, 45"], ["Simone,"], tela="Quem me mandou foi a Simone, 45 anos, casada com o Alberto há 20."),
 B("A Simone mora numa vila. Seis casas, um portão só, todo mundo se conhece.", "neutra", ["porta", "VILA · 6 CASAS"], ["Seis", "casas,"], tela="A Simone mora numa vila. 6 casas, um portão só, todo mundo se conhece."),
 B("Numa terça, o entregador deixou uma caixa na porta dela. Ela abriu sem nem olhar a etiqueta.", "neutra", ["presente", "CAIXA"], ["sem", "nem", "olhar"]),
 B("Dentro, um vestido vermelho. Tamanho P. E um cartão.", "desconfiada", ["presente", "TAM. P"], ["vermelho."]),
 B("A Simone veste G. E não compra vermelho desde mil novecentos e noventa e nove.", "ironica", None, ["vermelho"], tela="A Simone veste G. E não compra vermelho desde 1999."),
 B("Aí ela olhou a etiqueta. Destinatário: Alberto. O marido dela.", "chocada", ["carimbo", "ALBERTO"], ["Alberto."]),
 B("Mas o endereço era da casa quatro. Não da casa dois.", "desconfiada", ["porta", "CASA 4"], ["casa", "quatro."]),
 B("Na casa quatro mora a Denise. Divorciada, simpática, sempre de unha feita.", "desconfiada", None, ["Denise."]),
 B("E o cartão dizia: pro nosso sábado. Com um coração desenhado à mão.", "chocada", ["conversa", "Pro nosso sábado. ♥"], ["nosso", "sábado."]),
 B("Sábado. O dia em que o Alberto joga bola com os amigos. Faz doze anos.", "brava", ["calendario", "SÁBADO"], ["joga", "bola"], tela="Sábado. O dia em que o Alberto joga bola com os amigos. Faz 12 anos."),
 B("A Simone fechou a caixa. Colou a fita de volta, bem direitinho.", "ironica", None, ["direitinho."]),
 B("E o que ela fez com esse vestido, eu conto na parte dois.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você caiu aqui agora, volta na parte um. O vestido vermelho está lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("A Simone pegou a caixa, atravessou a vila e tocou na casa quatro.", "neutra", ["porta", "CASA 4"], ["casa", "quatro."]),
 B("A Denise abriu. De unha feita. E a Simone sorriu: chegou isso aqui pra você, veio lá em casa por engano.", "ironica", ["conversa", "Chegou isso pra você. Veio lá em casa por engano."], ["engano."]),
 B("A Denise viu o nome na etiqueta e ficou branca.", "chocada", zoom=True, dest=["branca."]),
 B("Obrigada, Simone. É uma encomenda do grupo de compras. Eu uso o nome de quem estiver perto.", "desconfiada", ["conversa", "Eu uso o nome de quem estiver perto."], ["perto."]),
 B("Desculpa esfarrapada. Mas a Simone agradeceu e voltou pra casa.", "ironica", None, ["esfarrapada."]),
 B("No sábado, o Alberto saiu de chuteira na mão, como sempre. Às duas da tarde.", "neutra", ["relogio", "14:00"], ["chuteira"], tela="No sábado, o Alberto saiu de chuteira na mão, como sempre. Às 14h."),
 B("A Simone ficou na janela. Viu o carro dele dar a volta no quarteirão.", "desconfiada", ["carro"], ["volta"]),
 B("E vinte minutos depois, a Denise saiu pelo portão da vila. De vestido vermelho.", "chocada", zoom=True, dest=["vermelho."], tela="E 20 minutos depois, a Denise saiu pelo portão da vila. De vestido vermelho."),
 B("A chuteira do Alberto voltou limpinha. Sem um grão de terra.", "ironica", None, ["limpinha."]),
 B("E agora vem a parte difícil. Domingo tem o aniversário da neta. Na casa da Simone. A vila inteira convidada.", "triste", ["presente", "DOMINGO · ANIVERSÁRIO"], ["vila", "inteira"]),
 B("Inclusive a Denise.", "brava", zoom=True, dest=["Denise."]),
 B("Ela desconvida a Denise? Ou deixa ela vir e espera pra ver se ela aparece de vermelho? Me conta aqui.", "ironica", ["manchete_v", "DESCONVIDA OU ESPERA?"], ["vermelho?"]),
], "O entregador errou a casa. E ela abriu um pacote com o nome do MARIDO e o endereço da vizinha. 📦\n\nDentro, um vestido vermelho tamanho P e um cartão: \"pro nosso sábado\". PARTE 2 no perfil.",
 "Ela devolveu o pacote pessoalmente. E no sábado, ficou na janela. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nDesconvida a vizinha do aniversário ou espera pra ver se ela aparece de vermelho? Me conta nos comentários. 👇",
 "#traição #vizinha #casamento #encomenda #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

# ---------------------------------------------------------------- EP09
ep(9, "O PERFUME DA MELHOR AMIGA", "Amizade", [
 B("A melhor amiga dela apareceu com perfume novo. E o perfume tinha cheiro de casa.", "ironica", ["titulo"], ["cheiro", "de", "casa."]),
 B("Quem me mandou foi a Carol, vinte e nove anos, namorando o Lucas há quatro.", "neutra", ["direct", "CAROL, 29"], ["Carol,"], tela="Quem me mandou foi a Carol, 29 anos, namorando o Lucas há 4."),
 B("A melhor amiga dela é a Thaís. Amiga desde a escola. Madrinha de tudo.", "neutra", ["coracao", "AMIGAS DESDE 2009"], ["Thaís."]),
 B("Num sábado, a Thaís chegou pra um café. Abraçou a Carol. E a Carol travou.", "desconfiada", ["cafe"], ["travou."]),
 B("Aquele cheiro. Amadeirado, meio doce. Ela conhecia aquele cheiro de olhos fechados.", "desconfiada", ["perfume"], ["Aquele", "cheiro."]),
 B("Era o perfume que ela tinha dado pro Lucas. No aniversário de namoro.", "chocada", ["presente", "4 ANOS DE NAMORO"], ["Lucas."]),
 B("Um perfume importado, masculino, que ela parcelou em seis vezes.", "ironica", ["extrato", "PERFUME · 6X"], ["seis", "vezes."], tela="Um perfume importado, masculino, que ela parcelou em 6 vezes."),
 B("Ela perguntou, rindo: amiga, que perfume é esse? A Thaís disse: ah, peguei o do meu irmão.", "desconfiada", ["conversa", "Peguei o do meu irmão."], ["irmão."]),
 B("A Thaís tem um irmão. Mora em Portugal. Faz três anos.", "ironica", ["mala", "PORTUGAL"], ["Portugal."], tela="A Thaís tem um irmão. Mora em Portugal. Faz 3 anos."),
 B("Quando a Thaís foi embora, a Carol foi direto no banheiro. Abriu o armário do Lucas.", "neutra", ["porta"], ["armário"]),
 B("O frasco estava lá. Mas pela metade. E ela lembrava muito bem: semana passada estava quase cheio.", "chocada", zoom=True, dest=["metade."]),
 B("O Lucas usa uma borrifada por dia. Uma.", "desconfiada", None, ["Uma."]),
 B("Quem gastou o resto do perfume, eu conto na parte dois.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você caiu aqui agora, volta na parte um. O perfume está lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("A Carol fez uma coisa simples. Marcou o nível do frasco com uma caneta.", "neutra", ["perfume"], ["caneta."]),
 B("Segunda: igual. Terça: igual. Quarta, dia do futebol do Lucas: o nível desceu.", "desconfiada", ["calendario", "QUARTA"], ["desceu."]),
 B("Futebol. Que termina às dez. O Lucas chegou meia-noite, de banho tomado.", "ironica", ["relogio", "00:00"], ["banho", "tomado."], tela="Futebol termina às 22h. O Lucas chegou meia-noite, de banho tomado."),
 B("E na quinta de manhã, a Thaís postou uma foto no story. Espelho do elevador. Legenda: noite boa.", "chocada", ["celular", "Noite boa ✨"], ["noite", "boa."]),
 B("No fundo da foto, no reflexo do espelho, um braço segurando a porta.", "desconfiada", ["foto", "REFLEXO"], ["braço"]),
 B("Com um relógio. Pulseira de couro marrom, fecho quebrado, preso com fita.", "chocada", zoom=True, dest=["fita."]),
 B("A Carol tinha colado aquela fita. Com as próprias mãos. No relógio do Lucas.", "brava", ["relogio", "FECHO COM FITA"], ["próprias", "mãos."]),
 B("Ela não mandou mensagem pra ninguém. Tirou print. Guardou.", "neutra", ["celular", "PRINT SALVO"], ["print."]),
 B("E agora vem o detalhe. Mês que vem é o aniversário da Carol.", "desconfiada", ["presente", "MÊS QUE VEM"], ["aniversário"]),
 B("E quem está organizando a festa surpresa, junto com o Lucas, é a Thaís.", "ironica", ["manchete", "FESTA SURPRESA"], ["Thaís."]),
 B("Ela me perguntou o que fazer.", "neutra", ["interrogacao"], ["fazer."]),
 B("Ela finge que não sabe e vai na festa? Ou devolve a surpresa e mostra o print pra todo mundo lá? Me conta aqui.", "ironica", ["manchete_v", "FINGE OU DEVOLVE?"], ["surpresa"]),
], "A melhor amiga apareceu com perfume novo. E o cheiro era o perfume que ela deu pro NAMORADO. 🌸\n\nO frasco em casa estava pela metade. E ele só usa uma borrifada por dia. PARTE 2 no perfil.",
 "Ela marcou o nível do frasco com caneta. E na quarta, desceu. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nEla finge que não sabe na festa surpresa ou mostra o print lá? Me conta nos comentários. 👇",
 "#traição #melhoramiga #namoro #amizade #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

# ---------------------------------------------------------------- EP10
ep(10, "OPEN BAR", "Noite", [
 B("Quatorze drinks. Numa noite só. Na fatura do cartão conjunto.", "ironica", ["titulo"], ["Quatorze", "drinks."]),
 B("Quem me mandou foi a Letícia, trinta e quatro anos, casada com o Bruno, que é vigilante noturno.", "neutra", ["direct", "LETÍCIA, 34"], ["vigilante"], tela="Quem me mandou foi a Letícia, 34 anos, casada com o Bruno, vigilante noturno."),
 B("O Bruno trabalha de plantão. Doze por trinta e seis. Numa empresa de segurança.", "neutra", ["relogio", "12 × 36"], ["plantão."], tela="O Bruno trabalha de plantão. 12 por 36. Numa empresa de segurança."),
 B("E a Letícia é quem cuida das contas da casa. Planilha, tudo anotado.", "neutra", ["extrato", "CONTAS DA CASA"], ["Planilha,"]),
 B("No fim do mês, chegou a fatura do cartão que os dois dividem.", "desconfiada", ["extrato", "FATURA"], ["fatura"]),
 B("Sexta-feira, uma e quarenta da manhã. Bar Lua Nova. Cento e oitenta e sete reais.", "chocada", ["extrato", "BAR LUA NOVA · R$ 187"], ["Bar", "Lua", "Nova."], tela="Sexta-feira, 1h40 da manhã. Bar Lua Nova. R$ 187."),
 B("Sexta-feira, uma e quarenta. O Bruno estava de plantão. Guardando um galpão.", "brava", ["calendario", "SEXTA · PLANTÃO"], ["plantão."], tela="Sexta-feira, 1h40. O Bruno estava de plantão. Guardando um galpão."),
 B("A Letícia ligou pro bar. Pediu o detalhe da comanda. Disse que era pra declarar no imposto.", "ironica", ["celular", "Bar Lua Nova"], ["imposto."]),
 B("E a moça mandou a foto da comanda. Quatorze drinks. Todos iguais.", "desconfiada", ["foto", "COMANDA · 14 DRINKS"], ["Todos", "iguais."], tela="E a moça mandou a foto da comanda. 14 drinks. Todos iguais."),
 B("Caipirinha de morango. Sem açúcar.", "chocada", zoom=True, dest=["morango."]),
 B("O Bruno odeia morango. Mas a Letícia conhecia alguém que só bebe isso.", "desconfiada", None, ["morango."]),
 B("E na comanda, no rodapé, a garçonete tinha anotado o nome da mesa.", "desconfiada", ["carimbo", "MESA 7"], ["nome", "da", "mesa."]),
 B("Que nome estava lá, eu conto na parte dois.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você caiu aqui agora, volta na parte um. A comanda está lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("No rodapé da comanda, a garçonete tinha escrito: mesa sete, Bruno e Kátia, aniversário.", "chocada", ["conversa", "Mesa 7 · Bruno e Kátia · aniversário"], ["Kátia,"], tela="No rodapé da comanda: mesa 7, Bruno e Kátia, aniversário."),
 B("Kátia. A supervisora do Bruno. A que liga lá em casa pra passar a escala.", "brava", ["cracha", "SUPERVISORA"], ["supervisora"]),
 B("E a que só bebe caipirinha de morango sem açúcar. A Letícia sabia disso por um motivo.", "desconfiada", None, ["morango"]),
 B("No churrasco de fim de ano da empresa, foi a própria Letícia que fez os drinks. E a Kátia pediu três.", "ironica", ["cafe"], ["própria", "Letícia"]),
 B("E a escala? A Letícia pediu pra ver a escala do mês. Com a desculpa do plano de saúde.", "neutra", ["calendario", "ESCALA DO MÊS"], ["escala"]),
 B("Na sexta do bar, o Bruno estava de folga. A escala dizia: folga.", "chocada", zoom=True, dest=["folga."]),
 B("E quem assinava a escala era a Kátia.", "brava", ["carimbo", "ASS.: KÁTIA"], ["Kátia."]),
 B("Ou seja: a chefe dava folga pra ele. E ele dizia em casa que estava de plantão.", "ironica", ["manchete", "FOLGA ≠ PLANTÃO"], ["plantão."]),
 B("A Letícia não falou nada. Mas separou a fatura. E marcou os cento e oitenta e sete reais de amarelo.", "neutra", ["extrato", "R$ 187"], ["amarelo."], tela="A Letícia não falou nada. Mas separou a fatura. E marcou os R$ 187 de amarelo."),
 B("Semana que vem é o jantar de fim de ano da empresa. Os cônjuges estão convidados.", "desconfiada", ["calendario", "JANTAR DA EMPRESA"], ["cônjuges"]),
 B("E a Kátia vai estar lá. Pedindo caipirinha de morango.", "ironica", None, ["morango."]),
 B("Ela vai no jantar e entrega a fatura pra Kátia pagar a parte dela? Ou resolve antes, em casa? Me conta aqui.", "ironica", ["manchete_v", "NO JANTAR OU EM CASA?"], ["fatura"]),
], "14 drinks numa noite só. Na fatura do cartão CONJUNTO. Numa sexta em que ele estava de plantão. 🍹\n\nE a comanda tinha um nome anotado no rodapé. PARTE 2 no perfil.",
 "O nome no rodapé da comanda era de quem assinava a escala dele. 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nEla entrega a fatura no jantar da empresa ou resolve em casa? Me conta nos comentários. 👇",
 "#traição #plantão #casamento #fatura #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

# ---------------------------------------------------------------- EP11
ep(11, "AS ALIANÇAS", "Casais", [
 B("Duas alianças no porta-luvas. E só uma era dela.", "ironica", ["titulo"], ["só", "uma"]),
 B("Quem me mandou foi a Mariana, trinta e três anos, casada com a Paula há cinco.", "neutra", ["direct", "MARIANA, 33"], ["Mariana,"], tela="Quem me mandou foi a Mariana, 33 anos, casada com a Paula há 5."),
 B("A Paula é representante comercial. Viaja pelo interior três vezes por mês.", "neutra", ["mala", "3 VIAGENS/MÊS"], ["Viaja"], tela="A Paula é representante comercial. Viaja pelo interior 3 vezes por mês."),
 B("E sempre tira a aliança pra viajar. Diz que é por segurança. Estrada, hotel, essas coisas.", "neutra", ["alianca"], ["segurança."]),
 B("A Mariana nunca achou estranho. Até o dia em que pegou o carro da Paula pra ir no mercado.", "desconfiada", ["carro"], ["mercado."]),
 B("Abriu o porta-luvas pra pegar o óculos de sol. E achou uma caixinha de veludo.", "desconfiada", ["presente", "CAIXINHA"], ["veludo."]),
 B("Dentro, duas alianças. Uma era a dela, a do casamento. Com a data gravada por dentro.", "neutra", ["alianca", "DATA GRAVADA"], ["a", "dela,"]),
 B("A outra era nova. Dourada. Mais fina. Com um nome gravado.", "chocada", ["alianca", "NOVA"], ["nome", "gravado."]),
 B("Não era Mariana. E não era Paula.", "chocada", zoom=True, dest=["Não", "era"]),
 B("Ela colocou tudo de volta, no mesmo lugar. Tirou foto antes.", "desconfiada", ["foto", "PORTA-LUVAS"], ["foto"]),
 B("E foi olhar a agenda da Paula. A próxima viagem era sexta. Pra mesma cidade de sempre.", "desconfiada", ["calendario", "SEXTA · VIAGEM"], ["mesma", "cidade"]),
 B("A mesma cidade. Nos últimos dois anos. Todo mês.", "brava", ["mapa", "2 ANOS"], ["Todo", "mês."], tela="A mesma cidade. Nos últimos 2 anos. Todo mês."),
 B("Qual era o nome gravado na aliança, eu conto na parte dois.", "ironica", ["manchete_v", "CONTINUA NA PARTE 2"], ["parte", "dois."]),
],[
 B("Se você caiu aqui agora, volta na parte um. A caixinha de veludo está lá.", "ironica", ["titulo"], ["parte", "um."]),
 B("Dentro da aliança nova estava gravado: Renata. E uma data.", "chocada", ["alianca", "RENATA"], ["Renata."]),
 B("A data era de um ano e meio atrás. Um mês depois das bodas de madeira da Mariana e da Paula.", "brava", ["calendario", "1 ANO E MEIO"], ["um", "mês", "depois"]),
 B("A Mariana procurou Renata nas redes, na cidade das viagens. Achou em dez minutos.", "desconfiada", ["celular", "Renata · perfil"], ["dez", "minutos."], tela="A Mariana procurou Renata nas redes, na cidade das viagens. Achou em 10 minutos."),
 B("Perfil aberto. Foto de capa: duas mãos com aliança, em cima de uma mesa de café.", "chocada", ["foto", "DUAS MÃOS"], ["aliança,"]),
 B("E uma das mãos tinha uma pintinha no dedo. A Mariana conhece aquela pintinha faz sete anos.", "chocada", zoom=True, dest=["pintinha"], tela="E uma das mãos tinha uma pintinha no dedo. A Mariana conhece aquela pintinha faz 7 anos."),
 B("Na legenda: minha esposa de sextas-feiras.", "ironica", ["conversa", "Minha esposa de sextas-feiras."], ["sextas-feiras."]),
 B("A Renata não sabe da Mariana. Pelo perfil, ela acha que a Paula mora sozinha. Na capital.", "desconfiada", ["interrogacao"], ["não", "sabe"]),
 B("Na quinta à noite, a Paula arrumou a mala. Beijou a Mariana. Disse: volto domingo, amor.", "triste", ["mala"], ["volto", "domingo,"]),
 B("E a Mariana respondeu: vai com Deus. E dirige com cuidado.", "ironica", ["conversa", "Vai com Deus. Dirige com cuidado."], ["cuidado."]),
 B("A caixinha de veludo continua no porta-luvas. Com as duas alianças.", "desconfiada", ["presente", "CAIXINHA"], ["duas", "alianças."]),
 B("Ela me mandou uma pergunta só.", "neutra", ["interrogacao"], ["pergunta"]),
 B("Ela manda mensagem pra Renata e conta tudo? Ou vai até a cidade na sexta e aparece no café? Me conta aqui.", "ironica", ["manchete_v", "MENSAGEM OU CAFÉ?"], ["café?"]),
], "Duas alianças no porta-luvas da esposa. Uma era a do casamento delas. A outra tinha OUTRO nome gravado. 💍\n\nE a viagem de trabalho é sempre pra mesma cidade, há 2 anos. PARTE 2 no perfil.",
 "O nome gravado na aliança tinha um perfil aberto. E uma legenda: \"minha esposa de sextas-feiras\". 🍷\n\nSe você caiu aqui agora, assiste a PARTE 1 primeiro.\n\nEla conta tudo pra outra por mensagem ou aparece na cidade na sexta? Me conta nos comentários. 👇",
 "#traição #casamento #casalLGBT #aliança #storytime #históriadetraição #desabafo #fofoca #ninamecontou")

"""Fixture de integração para CI: não publica nem entra na fila."""
import json
from pathlib import Path
p=Path('saida/teste-hf.json');p.parent.mkdir(exist_ok=True)
ep={'id':'teste-hf','ep':999,'parte':2,'titulo':'UM CLIQUE, OUTRA HISTÓRIA','cenario':'noite','fim':'SEGUE A NINA','legenda_post':'História de ficção. Teste técnico sem publicação.','batidas':[
 {'fala':'Ela apertou o controle. O portão começou a subir.','expr':'chocada','arte':['porta'],'zoom':True},
 {'fala':'Era o carro que ela estava procurando.','expr':'desconfiada','arte':['carro']},
 {'fala':'Uma mensagem chegou: o café está pronto.','expr':'neutra','arte':['conversa','O café está pronto.']},
 {'fala':'A surpresa estava naquela xícara.','expr':'ironica','arte':['cafe']},
 {'fala':'No relógio, já eram onze horas.','expr':'neutra','arte':['relogio','23:00']},
 {'fala':'E um presente esperava por ela.','expr':'ironica','arte':['presente','SURPRESA']},
 ]}
p.write_text(json.dumps(ep,ensure_ascii=False,indent=2));print(p)

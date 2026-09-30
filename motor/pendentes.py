"""Lista os episódios (JSON) que precisam ir pro estúdio: sem MP4 em reels/
ou com MP4 feito a partir de uma versão antiga do roteiro."""
import glob, os, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from src import fila  # noqa: E402

feitos = fila.ids_publicados()
for f in sorted(glob.glob(os.path.join(RAIZ, "episodios", "ep*-p*.json"))):
    ep = os.path.splitext(os.path.basename(f))[0]
    if ep not in feitos and fila.desatualizado(ep):
        print(os.path.relpath(f, RAIZ) if "--rel" in sys.argv else f)


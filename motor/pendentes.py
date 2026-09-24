"""Lista os episódios (JSON) que ainda não têm MP4 em reels/."""
import os, sys, glob
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in sorted(glob.glob(os.path.join(RAIZ, "episodios", "ep*-p*.json"))):
    ep = os.path.splitext(os.path.basename(f))[0]
    if not os.path.exists(os.path.join(RAIZ, "reels", ep + ".mp4")):
        print(f)

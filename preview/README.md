# Preview animation `idle` — ailes_dragon

Preview schematique de l'animation `idle` (1.6 s, boucle) generee a partir des
keyframes du modele Blockbench `ailes_dragon.bbmodel` (hierarchie
`dos` → `aile_d`/`aile_g` → `avbras_d`/`avbras_g` → `main_d`/`main_g`).

## Contenu

- `ailes_dragon_idle.gif` — 32 frames a 20 fps, boucle infinie, 560x560
- `ailes_dragon_idle.svg` — meme animation en SVG anime (SMIL), visible dans le navigateur
- `render_wings.py` — regenere le GIF (`pip install pillow` puis `python3 render_wings.py`)
- `make_svg.py` — regenere le SVG

Note : le rendu est schematique (segments colores + contours jaunes pour les
couches glow), pas le rendu texturé de Minecraft.

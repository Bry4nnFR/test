import math

KEY_TIMES = ";".join(f"{t/1.6:.6g}" for t in [0.0, 0.15, 0.4, 0.65, 0.8, 0.95, 1.2, 1.45, 1.6])

AILE_D = [(0.0, -5.0, -0.0), (0.15, 0.646, -3.889), (0.4, 28.5, -7.0),
          (0.65, 56.354, -3.889), (0.8, 62.0, -0.0), (0.95, 56.354, 3.889),
          (1.2, 28.5, 7.0), (1.45, 0.646, 3.889), (1.6, -5.0, -0.0)]
AVBRAS_D = [(0.0, 8.126), (0.15, 2.985), (0.4, 0.177), (0.65, 6.101),
            (0.8, 11.874), (0.95, 17.015), (1.2, 19.823), (1.45, 13.899), (1.6, 8.126)]
MAIN_D = [(0.0, 15.054), (0.15, 8.378), (0.4, 0.563), (0.65, 2.469),
          (0.8, 7.946), (0.95, 14.622), (1.2, 22.437), (1.45, 20.531), (1.6, 15.054)]
DOS_POS = [(0.0, 0.168), (0.15, 0.2), (0.4, 0.108), (0.65, -0.08),
           (0.8, -0.168), (0.95, -0.2), (1.2, -0.108), (1.45, 0.08), (1.6, 0.168)]

DUR = "1.6s"

def rot_vals(keys, static_z, sign):
    return ";".join(f"{sign * (k[2] if len(k) > 2 else 0.0) + static_z:.3f}" for k in keys)

def scale_vals(keys, sign):
    return ";".join(f"{math.cos(math.radians(sign * k[1])):.4f} 1" for k in keys)

def anims_rot_scale(rot_vals_s, scale_vals_s):
    return (f'<animateTransform attributeName="transform" type="rotate" additive="sum" '
            f'calcMode="linear" values="{rot_vals_s}" keyTimes="{KEY_TIMES}" dur="{DUR}" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="scale" additive="sum" '
            f'calcMode="linear" values="{scale_vals_s}" keyTimes="{KEY_TIMES}" dur="{DUR}" repeatCount="indefinite"/>')

def quad(x0, x1, y0, y1, fill, opacity="1"):
    return (f'<polygon points="{x0},{y0} {x1},{y0} {x1},{y1} {x0},{y1}" '
            f'fill="{fill}" fill-opacity="{opacity}" stroke="#1a1a22" stroke-width="0.25"/>')

def glow_quad(x0, x1, y0, y1):
    return (f'<polygon points="{x0},{y0} {x1},{y0} {x1},{y1} {x0},{y1}" '
            f'fill="none" stroke="#ffe05c" stroke-width="0.45"/>')

COLORS = {"epaule": "#c0392b", "avbras": "#9b59b6", "main": "#3498db"}

def side(sign, pivot_aile, pivot_avbras, pivot_main):
    """sign=1 right wing, -1 left wing (x mirrored)"""
    def X(v):
        return sign * v
    inner = []
    inner.append(glow_quad(X(0.6), X(6.28), 4.0, 31.0))
    inner.append(quad(X(0.6), X(6.28), 4.0, 31.0, COLORS["epaule"]))
    avbras_content = [glow_quad(X(6.28), X(11.48), 4.0, 31.0),
                      quad(X(6.28), X(11.48), 4.0, 31.0, COLORS["avbras"])]
    main_content = [glow_quad(X(11.48), X(24.6), 4.0, 31.0),
                    quad(X(11.48), X(24.6), 4.0, 31.0, COLORS["main"])]
    sgn = sign
    main_g = (f'<g transform="translate({X(11.48)},18)">'
              f'<g>{anims_rot_scale(rot_vals(MAIN_D, 0, sgn), scale_vals(MAIN_D, sgn))}'
              f'<g transform="translate({X(-11.48)},-18)">'
              + "".join(main_content) + '</g></g></g>')
    avbras_g = (f'<g transform="translate({X(6.28)},18)">'
                f'<g>{anims_rot_scale(rot_vals(AVBRAS_D, 0, sgn), scale_vals(AVBRAS_D, sgn))}'
                f'<g transform="translate({X(-6.28)},-18)">'
                + "".join(avbras_content) + main_g + '</g></g></g>')
    aile_g = (f'<g transform="translate({X(1.6)},18)">'
              f'<g>{anims_rot_scale(rot_vals(AILE_D, sign * 2.0, sgn), scale_vals(AILE_D, sgn))}'
              f'<g transform="translate({X(-1.6)},-18)">'
              + "".join(inner) + avbras_g + '</g></g></g>')
    return aile_g

dos_bob = (f'<animateTransform attributeName="transform" type="translate" calcMode="linear" '
           f'values="{";".join("0 " + f"{k[1]:.3f}" for k in DOS_POS)}" keyTimes="{KEY_TIMES}" '
           f'dur="{DUR}" repeatCount="indefinite"/>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-27 1.5 54 32" width="756" height="448">
<text x="-26" y="4" font-family="monospace" font-size="2.2" fill="#8a8a9a">ailes_dragon - idle (1.6s loop) - preview frontale</text>
<g>{dos_bob}
<rect x="-1.4" y="16.4" width="2.8" height="3" fill="#6e737d" stroke="#1a1a22" stroke-width="0.2"/>
<rect x="-0.25" y="16.9" width="0.5" height="2" fill="#ffe05c"/>
{side(1, None, None, None)}
{side(-1, None, None, None)}
</g>
</svg>'''

with open('/workspace/ailes_dragon_idle.svg', 'w') as f:
    f.write(svg)
print('svg written', len(svg), 'bytes')

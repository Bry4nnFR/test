import math
from PIL import Image, ImageDraw

FPS = 20
DUR = 1.6
N_FRAMES = int(FPS * DUR)  # 32
SIZE = 560

# ---------------- animation data (from bbmodel) ----------------
AILE_D = [(0.0, -5.0, -0.0), (0.15, 0.646, -3.889), (0.4, 28.5, -7.0),
          (0.65, 56.354, -3.889), (0.8, 62.0, -0.0), (0.95, 56.354, 3.889),
          (1.2, 28.5, 7.0), (1.45, 0.646, 3.889), (1.6, -5.0, -0.0)]
AVBRAS_D = [(0.0, 8.126), (0.15, 2.985), (0.4, 0.177), (0.65, 6.101),
            (0.8, 11.874), (0.95, 17.015), (1.2, 19.823), (1.45, 13.899), (1.6, 8.126)]
MAIN_D = [(0.0, 15.054), (0.15, 8.378), (0.4, 0.563), (0.65, 2.469),
          (0.8, 7.946), (0.95, 14.622), (1.2, 22.437), (1.45, 20.531), (1.6, 15.054)]
DOS_POS = [(0.0, 0.168), (0.15, 0.2), (0.4, 0.108), (0.65, -0.08),
           (0.8, -0.168), (0.95, -0.2), (1.2, -0.108), (1.45, 0.08), (1.6, 0.168)]

def interp(keys, t, idx):
    if t <= keys[0][0]:
        return keys[0][idx]
    if t >= keys[-1][0]:
        return keys[-1][idx]
    for i in range(len(keys) - 1):
        t0, t1 = keys[i][0], keys[i + 1][0]
        if t0 <= t <= t1:
            v0, v1 = keys[i][idx], keys[i + 1][idx]
            f = (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * f
    return keys[-1][idx]

# ---------------- bone rig ----------------
# (name, parent, origin, static_rot_z_deg)
BONES = {
    'dos':      (None,      [0.0, 18.0, 0.0], 0.0),
    'aile_d':   ('dos',     [1.6, 18.0, 2.6], 2.0),
    'avbras_d': ('aile_d',  [6.28, 18.0, 2.6], 0.0),
    'main_d':   ('avbras_d',[11.48, 18.0, 2.6], 0.0),
    'aile_g':   ('dos',     [-1.6, 18.0, 2.6], -2.0),
    'avbras_g': ('aile_g',  [-6.28, 18.0, 2.6], 0.0),
    'main_g':   ('avbras_g',[-11.48, 18.0, 2.6], 0.0),
}
CHAIN = {b: [] for b in BONES}
for b, (p, _, _) in BONES.items():
    cur, chain = b, []
    while cur:
        chain.append(cur)
        cur = BONES[cur][0]
    CHAIN[b] = list(reversed(chain))

def bone_xform(bone, t):
    """world matrix (4x4 list) for a bone at time t"""
    name = bone
    p, origin, sz = BONES[name]
    if name == 'dos':
        rx, ry, rz = 0.0, 0.0, 0.0
        ty = interp(DOS_POS, t, 1)
    elif name == 'aile_d':
        rx, ry, rz = 0.0, interp(AILE_D, t, 1), sz + interp(AILE_D, t, 2)
        ty = 0.0
    elif name == 'avbras_d':
        rx, ry, rz = 0.0, interp(AVBRAS_D, t, 1), 0.0
        ty = 0.0
    elif name == 'main_d':
        rx, ry, rz = 0.0, interp(MAIN_D, t, 1), 0.0
        ty = 0.0
    elif name == 'aile_g':
        rx, ry, rz = 0.0, -interp(AILE_D, t, 1), sz - interp(AILE_D, t, 2)
        ty = 0.0
    elif name == 'avbras_g':
        rx, ry, rz = 0.0, -interp(AVBRAS_D, t, 1), 0.0
        ty = 0.0
    else:  # main_g
        rx, ry, rz = 0.0, -interp(MAIN_D, t, 1), 0.0
        ty = 0.0
    return origin, rx, ry, rz, ty

def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def rot_mat(rx, ry, rz):
    ax, ay, az = math.radians(rx), math.radians(ry), math.radians(rz)
    cx, sx, cy, sy, cz, sz2 = (math.cos(ax), math.sin(ax), math.cos(ay),
                               math.sin(ay), math.cos(az), math.sin(az))
    mx = [[1, 0, 0, 0], [0, cx, -sx, 0], [0, sx, cx, 0], [0, 0, 0, 1]]
    my = [[cy, 0, sy, 0], [0, 1, 0, 0], [-sy, 0, cy, 0], [0, 0, 0, 1]]
    mz = [[cz, -sz2, 0, 0], [sz2, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    m = mat_mul(mx, mat_mul(my, mz))
    return m

def apply(mat, v):
    x, y, z = v
    return tuple(mat[i][0] * x + mat[i][1] * y + mat[i][2] * z + mat[i][3] for i in range(3))

def world_matrix(bone, t):
    m = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    for name in CHAIN[bone]:
        origin, rx, ry, rz, ty = bone_xform(name, t)
        t1 = [[1, 0, 0, -origin[0]], [0, 1, 0, -origin[1]], [0, 0, 1, -origin[2]], [0, 0, 0, 1]]
        r = rot_mat(rx, ry, rz)
        t2 = [[1, 0, 0, origin[0]], [0, 1, 0, origin[1] + ty], [0, 0, 1, origin[2]], [0, 0, 0, 1]]
        step = mat_mul(t2, mat_mul(r, t1))
        m = mat_mul(step, m)
    return m

# ---------------- cubes: (bone, x0, x1, y0, y1, z, kind) ----------------
CUBES = []
for bone, sgn in (('aile_d', 1), ('aile_g', -1)):
    segs = [('epaule', 0.6, 6.28, 'epaule'), ('avbras', 6.28, 11.48, 'avbras'), ('main', 11.48, 24.6, 'main')]
    for base, x0, x1, kind in segs:
        x0w, x1w = (x0, x1) if sgn > 0 else (-x1, -x0)
        CUBES.append((bone, x0w, x1w, 4.0, 31.0, 2.6, kind))
        CUBES.append((bone, x0w, x1w, 4.0, 31.0, 2.63, 'glow'))
        CUBES.append((bone, x0w, x1w, 4.0, 31.0, 2.57, 'glow'))
CUBES.append(('dos', -1.4, 1.4, 16.4, 19.4, 2.7, 'attache'))

COLORS = {'epaule': (192, 57, 43), 'avbras': (155, 89, 182),
          'main': (52, 152, 219), 'attache': (110, 115, 125),
          'glow': (255, 224, 92)}

# ---------------- camera ----------------
YAW, PITCH = math.radians(-22), math.radians(-18)
def cam(p):
    x, y, z = p
    cy, sy = math.cos(YAW), math.sin(YAW)
    x, z = cy * x + sy * z, -sy * x + cy * z
    cx, sx = math.cos(PITCH), math.sin(PITCH)
    y, z = cx * y - sx * z, sx * y + cx * z
    return x, y, z  # depth = z (bigger = farther after this transform sign)

def quad_pts(cube, t):
    bone, x0, x1, y0, y1, z, kind = cube
    corners = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    m = world_matrix(bone, t)
    return [cam(apply(m, c)) for c in corners]

# ---------------- precompute all frames, fit view ----------------
all_pts = []
for f in range(N_FRAMES):
    t = f / FPS
    for c in CUBES:
        all_pts += quad_pts(c, t)
minx = min(p[0] for p in all_pts); maxx = max(p[0] for p in all_pts)
miny = min(p[1] for p in all_pts); maxy = max(p[1] for p in all_pts)
margin = 60
scale = min((SIZE - 2 * margin) / (maxx - minx), (SIZE - 2 * margin) / (maxy - miny))
def to_screen(p):
    return (int((p[0] - (minx + maxx) / 2) * scale + SIZE / 2),
            int(((miny + maxy) / 2 - p[1]) * scale + SIZE / 2))

def shade(color, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in color)

frames = []
for f in range(N_FRAMES):
    t = f / FPS
    img = Image.new('RGB', (SIZE, SIZE), (24, 26, 34))
    d = ImageDraw.Draw(img)
    quads = []
    for c in CUBES:
        pts = quad_pts(c, t)
        depth = sum(p[2] for p in pts) / 4.0
        quads.append((depth, c, pts))
    quads.sort(key=lambda q: q[0])
    for depth, c, pts in quads:
        bone, x0, x1, y0, y1, z, kind = c
        sp = [to_screen(p) for p in pts]
        col = COLORS[kind]
        if kind == 'glow':
            d.line(sp + [sp[0]], fill=col, width=2)
        else:
            factor = 1.0 if z >= 2.6 else 0.72
            d.polygon(sp, fill=shade(col, factor))
            d.line(sp + [sp[0]], fill=shade(col, factor * 0.45), width=2)
    # spine marker (attache crossbar)
    label = f"idle  t={t:.2f}s"
    d.text((14, 12), label, fill=(200, 200, 210))
    d.text((14, SIZE - 26), "ailes_dragon - preview schematique (BetterModel keyframes)",
           fill=(140, 140, 155))
    frames.append(img)

frames[0].save('/workspace/ailes_dragon_idle.gif', save_all=True,
               append_images=frames[1:], duration=int(1000 / FPS), loop=0, optimize=True)
print('saved', len(frames), 'frames')

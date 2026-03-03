import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
import time

N = 100
PLANE_SIZE = 100.0
MIN_DISTANCE = 0.5
OUTPUT_DIR = "."

configs = [
    {'id':1,  'model':'exp',   'a':0.01,  'b':1.0,  'max_dist':None, 'max_deg':None},
    {'id':2,  'model':'exp',   'a':0.01,  'b':2.0,  'max_dist':None, 'max_deg':None},
    {'id':3,  'model':'exp',   'a':0.01,  'b':4.0,  'max_dist':None, 'max_deg':None},
    {'id':4,  'model':'exp',   'a':0.05,  'b':2.0,  'max_dist':None, 'max_deg':None},
    {'id':5,  'model':'exp',   'a':0.10,  'b':2.0,  'max_dist':None, 'max_deg':None},
    {'id':6,  'model':'exp',   'a':0.20,  'b':2.0,  'max_dist':None, 'max_deg':None},
    {'id':7,  'model':'power', 'a':None,  'b':1.0,  'max_dist':None, 'max_deg':None},
    {'id':8,  'model':'power', 'a':None,  'b':2.0,  'max_dist':None, 'max_deg':None},
    {'id':9,  'model':'power', 'a':None,  'b':3.0,  'max_dist':None, 'max_deg':None},
    {'id':10, 'model':'power', 'a':None,  'b':4.0,  'max_dist':None, 'max_deg':None},
    {'id':11, 'model':'exp',   'a':0.05,  'b':2.0,  'max_dist':20,   'max_deg':None},
    {'id':12, 'model':'exp',   'a':0.05,  'b':2.0,  'max_dist':10,   'max_deg':None},
    {'id':13, 'model':'exp',   'a':0.05,  'b':2.0,  'max_dist':5,    'max_deg':None},
    {'id':14, 'model':'exp',   'a':0.05,  'b':2.0,  'max_dist':None, 'max_deg':5},
    {'id':15, 'model':'exp',   'a':0.05,  'b':2.0,  'max_dist':None, 'max_deg':3},
    {'id':16, 'model':'exp',   'a':0.05,  'b':2.0,  'max_dist':None, 'max_deg':2},
    {'id':17, 'model':'power', 'a':None,  'b':2.0,  'max_dist':5,    'max_deg':None},
    {'id':18, 'model':'exp',   'a':0.05,  'b':2.0,  'max_dist':10,   'max_deg':4},
    {'id':19, 'model':'power', 'a':None,  'b':1.5,  'max_dist':None, 'max_deg':None},
    {'id':20, 'model':'exp',   'a':0.001, 'b':3.0,  'max_dist':15,   'max_deg':None},
]

def get_prob(d, a, b, model):
    if d < 1e-6:
        return 0.0
    if model == 'exp':
        return np.exp(-a * (d ** b))
    else:
        return 1.0 / (d ** b)

def grow_tree(points, dist_matrix, seed=0, a=None, b=None, model='exp',
              max_dist=None, max_deg=None):
    G = nx.Graph()
    G.add_node(seed)
    connected = {seed}

    MAX_ATTEMPTS = 150000
    attempt = 0

    while len(connected) < N and attempt < MAX_ATTEMPTS:
        attempt += 1

        candidates = [i for i in connected if max_deg is None or G.degree(i) < max_deg]
        if not candidates:
            break

        i = np.random.choice(candidates)

        possible = []
        weights = []
        for j in range(N):
            if j in connected:
                continue
            d = dist_matrix[i, j]
            if d < MIN_DISTANCE or (max_dist is not None and d > max_dist):
                continue
            w = get_prob(d, a, b, model)
            if w > 0:
                possible.append(j)
                weights.append(w)

        if possible:
            weights = np.array(weights)
            weights /= weights.sum()
            j = possible[np.random.choice(len(possible), p=weights)]

            G.add_edge(i, j)
            connected.add(j)

    return G

os.makedirs(OUTPUT_DIR, exist_ok=True)
print("Генерация 20 графов\n")

for cfg in configs:
    cfg_id = cfg['id']
    model = cfg['model']
    a = cfg['a']
    b = cfg['b']
    max_d = cfg['max_dist']
    max_deg = cfg['max_deg']

    points = np.random.uniform(0, PLANE_SIZE, (N, 2))
    diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    dist_matrix = np.sqrt(np.sum(diff**2, axis=-1))

    print(f"→ Граф #{cfg_id:02d}  ({model}, a={a}, b={b}, maxd={max_d}, maxdeg={max_deg})")

    start = time.time()
    G = grow_tree(points, dist_matrix, seed=0, a=a, b=b, model=model,
                  max_dist=max_d, max_deg=max_deg)
    elapsed = time.time() - start

    conn = len(G)
    edges = G.number_of_edges()
    max_deg_real = max(dict(G.degree()).values()) if G else 0

    plt.figure(figsize=(10, 10))

    plt.scatter(points[:, 0], points[:, 1],
                c='lightgray', s=20, alpha=0.5, label='Все вершины')

    existing = list(G.nodes())
    if existing:
        pos = {i: points[i] for i in existing}
        node_colors = ['red' if i == 0 else 'royalblue' for i in existing]
        node_sizes  = [120 if i == 0 else 60 for i in existing]

        nx.draw_networkx_nodes(G, pos,
                               node_color=node_colors,
                               node_size=node_sizes,
                               alpha=0.9)

        nx.draw_networkx_edges(G, pos,
                               edge_color='gray',
                               width=0.8,
                               alpha=0.7)

    title = f"#{cfg_id}: {model}"
    if model == 'exp':
        title += f" a={a} b={b}"
    else:
        title += f" b={b}"
    if max_d is not None: title += f" maxd={max_d}"
    if max_deg is not None: title += f" maxdeg={max_deg}"
    title += f"\nСоединено: {conn}/{N}   Рёбер: {edges}   max deg: {max_deg_real}   {elapsed:.1f}с"

    plt.title(title, fontsize=13)
    plt.axis('equal')
    plt.grid(True, alpha=0.25)
    plt.legend(loc='upper right', fontsize=9)

    fname = f"graph_{cfg_id:02d}.png"
    plt.savefig(fname, dpi=160, bbox_inches='tight')
    plt.close()

    print(f"   сохранено → {fname}   (соединено: {conn}, рёбер: {edges})\n")

print("\nГотово.")

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define MAX_NODES 20
#define MAX_EDGES 50

typedef struct {
    char from;
    char to;
    int duration;
} Edge;

typedef struct {
    int num_nodes;
    int num_edges;
    char nodes[MAX_NODES];
    Edge edges[MAX_EDGES];
    int graph[MAX_NODES][MAX_NODES];
    int pred[MAX_NODES][MAX_NODES];
    int num_pred[MAX_NODES];
    int succ[MAX_NODES][MAX_NODES];
    int num_succ[MAX_NODES];
} Graph;

int find_node_index(Graph* g, char node) {
    for (int i = 0; i < g->num_nodes; i++) {
        if (g->nodes[i] == node) return i;
    }
    return -1;
}

void init_graph(Graph* g) {
    g->num_nodes = 0;
    g->num_edges = 0;

    for (int i = 0; i < MAX_NODES; i++) {
        for (int j = 0; j < MAX_NODES; j++) {
            g->graph[i][j] = -1;
            g->pred[i][j] = -1;
            g->succ[i][j] = -1;
        }
        g->num_pred[i] = 0;
        g->num_succ[i] = 0;
    }
}

void add_node(Graph* g, char node) {
    if (find_node_index(g, node) == -1) {
        g->nodes[g->num_nodes++] = node;
    }
}

void add_edge(Graph* g, char from, char to, int duration) {
    int from_idx = find_node_index(g, from);
    int to_idx = find_node_index(g, to);

    if (from_idx == -1) {
        add_node(g, from);
        from_idx = find_node_index(g, from);
    }
    if (to_idx == -1) {
        add_node(g, to);
        to_idx = find_node_index(g, to);
    }

    g->edges[g->num_edges].from = from;
    g->edges[g->num_edges].to = to;
    g->edges[g->num_edges].duration = duration;
    g->num_edges++;

    g->graph[from_idx][to_idx] = duration;
    g->pred[to_idx][g->num_pred[to_idx]++] = from_idx;
    g->succ[from_idx][g->num_succ[from_idx]++] = to_idx;
}

void topological_sort(Graph* g, int order[]) {
    int indegree[MAX_NODES] = {0};
    int queue[MAX_NODES];
    int front = 0, rear = 0;
    int visited = 0;

    for (int i = 0; i < g->num_nodes; i++) {
        indegree[i] = g->num_pred[i];
        if (indegree[i] == 0) {
            queue[rear++] = i;
        }
    }

    while (front < rear) {
        int curr = queue[front++];
        order[visited++] = curr;

        for (int j = 0; j < g->num_nodes; j++) {
            if (g->graph[curr][j] != -1) {
                indegree[j]--;
                if (indegree[j] == 0) {
                    queue[rear++] = j;
                }
            }
        }
    }

    if (visited != g->num_nodes) {
        printf("Ошибка: в графе есть цикл!\n");
        exit(1);
    }
}

void calculate_cpm(Graph* g) {
    int topo_order[MAX_NODES];
    int et[MAX_NODES] = {0};

    topological_sort(g, topo_order);

    // Прямой проход
    for (int i = 0; i < g->num_nodes; i++) {
        int node_idx = topo_order[i];
        char node = g->nodes[node_idx];

        for (int j = 0; j < g->num_nodes; j++) {
            if (g->graph[node_idx][j] != -1) {
                int new_time = et[node_idx] + g->graph[node_idx][j];
                if (new_time > et[j]) {
                    et[j] = new_time;
                }
            }
        }
    }

    int project_duration = 0;
    for (int i = 0; i < g->num_nodes; i++) {
        if (et[i] > project_duration) {
            project_duration = et[i];
        }
    }

    int lt[MAX_NODES];
    for (int i = 0; i < g->num_nodes; i++) {
        lt[i] = project_duration;
    }

    // Обратный проход 
    for (int i = g->num_nodes - 1; i >= 0; i--) {
        int node_idx = topo_order[i];
        char node = g->nodes[node_idx];

        for (int p = 0; p < g->num_pred[node_idx]; p++) {
            int pred_idx = g->pred[node_idx][p];
            int candidate = lt[node_idx] - g->graph[pred_idx][node_idx];
            if (candidate < lt[pred_idx]) {
                lt[pred_idx] = candidate;
            }
        }

    }

    printf("Шифр | t  | t_rn | t_ro | t_pn | t_po |  R  |  r  | Крит\n");
    printf("-------|----|------|------|------|------|-----|-----|------\n");

    for (int e = 0; e < g->num_edges; e++) {
        char from = g->edges[e].from;
        char to   = g->edges[e].to;
        int duration = g->edges[e].duration;

        int i = find_node_index(g, from);
        int j = find_node_index(g, to);

        int t_rn = et[i];
        int t_ro = et[i] + duration;
        int t_po = lt[j];
        int t_pn = t_po - duration;
        
        int R = t_po - t_rn - duration;
        int r = et[j] - et[i] - duration;

        const char* critical = (R == 0) ? "+" : "-";

        printf("  %c-%c  | %2d |  %3d  |  %3d  |  %3d  |  %3d  |  %2d  |  %2d  |   %s\n",
               from, to, duration, t_rn, t_ro, t_pn, t_po, R, r, critical);
    }

    printf("\nКритический путь\n");

    int start_idx = -1;
    for (int i = 0; i < g->num_nodes; i++) {
        if (g->num_pred[i] == 0) {
            start_idx = i;
            break;
        }
    }

    if (start_idx == -1) {
        printf("Не найдено начальное событие\n");
        return;
    }

    printf("%c", g->nodes[start_idx]);
    int current = start_idx;

    while (1) {
        int next_found = 0;
        for (int j = 0; j < g->num_nodes; j++) {
            if (g->graph[current][j] != -1) {
                int R = lt[j] - et[current] - g->graph[current][j];
                if (R == 0) {
                    printf(" → %c", g->nodes[j]);
                    current = j;
                    next_found = 1;
                    break;
                }
            }
        }
        if (!next_found) break;
    }
    printf("\n");
}

int main() {
    Graph g;
    init_graph(&g);

    // 1) Пример, который разбирался на паре
    /*
    add_edge(&g, 'A', 'B', 3);
    add_edge(&g, 'A', 'C', 5);
    add_edge(&g, 'A', 'E', 2);
    add_edge(&g, 'B', 'D', 3);
    add_edge(&g, 'B', 'F', 4);
    add_edge(&g, 'C', 'D', 7);
    add_edge(&g, 'C', 'E', 6);
    add_edge(&g, 'D', 'F', 5);
    add_edge(&g, 'D', 'G', 0);
    add_edge(&g, 'E', 'G', 6);
    add_edge(&g, 'F', 'G', 7);
    */

    // 2) Пример, который дали в качестве дз (усложненный)
    /*
    add_edge(&g, 'A', 'B', 4);
    add_edge(&g, 'A', 'D', 3);
    add_edge(&g, 'B', 'C', 5);
    add_edge(&g, 'B', 'D', 3);
    add_edge(&g, 'C', 'E', 7);
    add_edge(&g, 'C', 'F', 4);
    add_edge(&g, 'D', 'F', 4);
    add_edge(&g, 'E', 'G', 3);
    add_edge(&g, 'F', 'G', 3);
    */

    // 3) Сложный пример
    add_edge(&g, 'A', 'B', 5);
    add_edge(&g, 'A', 'C', 4);
    add_edge(&g, 'B', 'D', 6);
    add_edge(&g, 'B', 'E', 8);
    add_edge(&g, 'C', 'E', 8);

    add_edge(&g, 'C', 'F', 7);
    add_edge(&g, 'D', 'G', 5);
    add_edge(&g, 'E', 'G', 5);
    add_edge(&g, 'E', 'H', 4);
    add_edge(&g, 'F', 'H', 4);

    add_edge(&g, 'G', 'I', 6);
    add_edge(&g, 'G', 'J', 7);
    add_edge(&g, 'H', 'J', 7);
    add_edge(&g, 'I', 'K', 5);
    add_edge(&g, 'J', 'K', 5);

    add_edge(&g, 'J', 'L', 8);
    add_edge(&g, 'K', 'M', 4);
    add_edge(&g, 'L', 'M', 4);
    add_edge(&g, 'M', 'N', 6);

    calculate_cpm(&g);

    return 0;
}

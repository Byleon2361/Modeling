import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial.distance import pdist, squareform
import random

class GraphGenerator:
    def __init__(self, num_points=100, area_size=100, seed=None):
        """
        Инициализация генератора графов
        
        Parameters:
        num_points: количество точек
        area_size: размер области (area_size x area_size)
        seed: seed для воспроизводимости
        """
        if seed:
            np.random.seed(seed)
            random.seed(seed)
        
        self.num_points = num_points
        self.area_size = area_size
        
        # Генерация случайных точек
        self.points = np.random.rand(num_points, 2) * area_size
        
        # Матрица расстояний
        self.distances = squareform(pdist(self.points))
        
        # Параметры ограничений
        self.max_degree = 10  # максимальная степень вершины
        self.max_distance = 50  # максимальное расстояние для ребра
        self.min_probability = 0.01  # минимальная вероятность соединения
        
        # Инициализация графа
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(num_points))
        
        # Степени вершин
        self.degrees = {i: 0 for i in range(num_points)}
        
    def calculate_probabilities_exp(self, node):
        """Вероятности по формуле P_ij = e^(-a*d_ij)"""
        a = 0.1  # параметр затухания
        distances = self.distances[node]
        
        # Применяем ограничения
        probabilities = np.exp(-a * distances)
        
        # Учитываем ограничения
        for j in range(self.num_points):
            if j == node:  # нет петель
                probabilities[j] = 0
            elif distances[j] > self.max_distance:  # ограничение по расстоянию
                probabilities[j] = 0
            elif self.degrees[j] >= self.max_degree:  # ограничение по степени
                probabilities[j] = 0
                
        # Нормализация
        total = np.sum(probabilities)
        if total > 0:
            probabilities = probabilities / total
        else:
            probabilities = np.zeros_like(probabilities)
            
        return probabilities
    
    def calculate_probabilities_inv(self, node):
        """Вероятности по формуле P_ij = 1/d_ij"""
        distances = self.distances[node]
        
        # Избегаем деления на ноль
        probabilities = np.zeros_like(distances)
        mask = distances > 0
        probabilities[mask] = 1.0 / distances[mask]
        
        # Учитываем ограничения
        for j in range(self.num_points):
            if j == node:  # нет петель
                probabilities[j] = 0
            elif distances[j] > self.max_distance:  # ограничение по расстоянию
                probabilities[j] = 0
            elif self.degrees[j] >= self.max_degree:  # ограничение по степени
                probabilities[j] = 0
                
        # Нормализация
        total = np.sum(probabilities)
        if total > 0:
            probabilities = probabilities / total
        else:
            probabilities = np.zeros_like(probabilities)
            
        return probabilities
    
    def add_edge_with_probability(self, node, prob_func):
        """Добавление ребра с заданной вероятностью"""
        probabilities = prob_func(node)
        
        # Проверяем, есть ли доступные вершины
        if np.sum(probabilities) == 0:
            return False
        
        # Разыгрываем вершину по вероятностям
        available_nodes = list(range(self.num_points))
        chosen_node = np.random.choice(available_nodes, p=probabilities)
        
        # Добавляем ребро
        self.graph.add_edge(node, chosen_node)
        self.degrees[node] += 1
        self.degrees[chosen_node] += 1
        
        return True
    
    def generate_graph(self, prob_type='exp', num_edges=None):
        """
        Генерация графа
        
        Parameters:
        prob_type: тип вероятности ('exp' или 'inv')
        num_edges: количество рёбер (если None, то генерируется пока возможно)
        """
        if prob_type == 'exp':
            prob_func = self.calculate_probabilities_exp
        else:
            prob_func = self.calculate_probabilities_inv
        
        edges_added = 0
        
        if num_edges:
            # Генерация заданного количества рёбер
            while edges_added < num_edges:
                # Выбираем случайную вершину
                node = random.randint(0, self.num_points - 1)
                
                # Проверяем, может ли вершина иметь больше рёбер
                if self.degrees[node] < self.max_degree:
                    if self.add_edge_with_probability(node, prob_func):
                        edges_added += 1
        else:
            # Генерация пока возможно добавлять рёбра
            max_attempts = self.num_points * 10
            attempts = 0
            
            while attempts < max_attempts:
                node = random.randint(0, self.num_points - 1)
                
                if self.degrees[node] < self.max_degree:
                    if self.add_edge_with_probability(node, prob_func):
                        edges_added += 1
                        attempts = 0
                    else:
                        attempts += 1
                else:
                    attempts += 1
        
        print(f"Добавлено рёбер: {edges_added}")
        return self.graph
    
    def visualize(self, title="Граф"):
        """Визуализация графа"""
        plt.figure(figsize=(12, 8))
        
        # Рисуем точки
        plt.scatter(self.points[:, 0], self.points[:, 1], 
                   c='lightblue', s=200, edgecolors='black', zorder=2)
        
        # Рисуем рёбра
        for edge in self.graph.edges():
            i, j = edge
            plt.plot([self.points[i, 0], self.points[j, 0]],
                    [self.points[i, 1], self.points[j, 1]],
                    'gray', alpha=0.5, linewidth=1, zorder=1)
        
        # Подписываем вершины
        for i, (x, y) in enumerate(self.points):
            plt.annotate(str(i), (x, y), xytext=(5, 5), 
                        textcoords='offset points', fontsize=8)
        
        plt.xlim(-5, self.area_size + 5)
        plt.ylim(-5, self.area_size + 5)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title(title)
        plt.grid(True, alpha=0.3)
        plt.gca().set_aspect('equal')
        plt.show()
    
    def analyze_graph(self):
        """Анализ характеристик графа"""
        print("\n=== Анализ графа ===")
        print(f"Количество вершин: {self.graph.number_of_nodes()}")
        print(f"Количество рёбер: {self.graph.number_of_edges()}")
        
        if self.graph.number_of_edges() > 0:
            # Степени вершин
            degrees = [d for n, d in self.graph.degree()]
            print(f"Средняя степень: {np.mean(degrees):.2f}")
            print(f"Макс степень: {max(degrees)}")
            print(f"Мин степень: {min(degrees)}")
            
            # Компоненты связности
            components = list(nx.connected_components(self.graph))
            print(f"Количество компонент связности: {len(components)}")
            
            # Размер максимальной компоненты
            if components:
                max_component = max(components, key=len)
                print(f"Размер макс компоненты: {len(max_component)}")
            
            # Коэффициент кластеризации
            clustering = nx.average_clustering(self.graph)
            print(f"Средний коэффициент кластеризации: {clustering:.3f}")
        else:
            print("Граф не содержит рёбер")

# Пример использования
def run_experiment():
    """Запуск эксперимента с разными типами вероятностей"""
    
    print("=" * 50)
    print("ГЕНЕРАЦИЯ ГРАФОВ, ПОХОЖИХ НА РЕАЛЬНЫЕ СЕТИ")
    print("=" * 50)
    
    # Создаем генератор
    generator = GraphGenerator(num_points=100, area_size=100, seed=42)
    
    # Генерация графа с вероятностью P_ij = e^(-a*d_ij)
    print("\n1. ГРАФ С ВЕРОЯТНОСТЬЮ P_ij = e^(-a*d_ij)")
    graph_exp = generator.generate_graph(prob_type='exp')
    generator.visualize("Граф с вероятностью P_ij = e^(-a*d_ij)")
    generator.analyze_graph()
    
    # Создаем новый генератор для второго типа вероятности
    generator2 = GraphGenerator(num_points=100, area_size=100, seed=42)
    
    # Генерация графа с вероятностью P_ij = 1/d_ij
    print("\n2. ГРАФ С ВЕРОЯТНОСТЬЮ P_ij = 1/d_ij")
    graph_inv = generator2.generate_graph(prob_type='inv')
    generator2.visualize("Граф с вероятностью P_ij = 1/d_ij")
    generator2.analyze_graph()
    
    # Сравнение распределений степеней
    plt.figure(figsize=(15, 5))
    
    # Экспоненциальная вероятность
    plt.subplot(1, 2, 1)
    degrees_exp = [d for n, d in graph_exp.degree()]
    plt.hist(degrees_exp, bins=range(max(degrees_exp)+2), alpha=0.7, 
             edgecolor='black', color='skyblue')
    plt.xlabel('Степень вершины')
    plt.ylabel('Количество вершин')
    plt.title('Распределение степеней (экспоненциальная вероятность)')
    plt.grid(True, alpha=0.3)
    
    # Обратная вероятность
    plt.subplot(1, 2, 2)
    degrees_inv = [d for n, d in graph_inv.degree()]
    plt.hist(degrees_inv, bins=range(max(degrees_inv)+2), alpha=0.7, 
             edgecolor='black', color='lightcoral')
    plt.xlabel('Степень вершины')
    plt.ylabel('Количество вершин')
    plt.title('Распределение степеней (обратная вероятность)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# Запуск эксперимента
if __name__ == "__main__":
    run_experiment()

import pygame
from queue import PriorityQueue

"""
Path Finding

É um programa em python desenvolvido durante a disciplina de Inteligência Artificial
da Faculdade de Tecnologia da Unicamp pelos alunos:
    1. Kevin Barrios
    2. Larissa Benevides
    3. Matheus Alves
    4. Matheus Bruder
    5. Miguel Amaral

O Objetivo deste programa é simular visualmente o cada uma das decisões tomadas em uma 
busca utilizando o algoritmo A*. Além disso, utilizamos tanto heurísticas admissíveis,
como heurísticas inadmissíveis para poder comparar os resultados.
"""


# -----------------------------------------------------------------------
# DISPLAY SETTINGS
# -----------------------------------------------------------------------

# Cores
RED = (237, 0, 38)  # Nós fechados
GREEN = (0, 101, 68)  # Nós abertos
BLUE = (120, 199, 235)  # Inicio
YELLOW = (253, 194, 0)  # Final
LIGHT_GREEN = (204, 225, 0)  # Caminho
GREY = (128, 128, 128)  # Linhas da matriz
WHITE = (255, 255, 255)  # Cor padrão
BLACK = (0, 0, 0)  # Obstáculos

WIDTH = 600  # Tamanho da tela
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))  # Definição da janela
pygame.display.set_caption('A(star) - Path Finding')


# -----------------------------------------------------------------------
# CLASSE PONTO
# -----------------------------------------------------------------------
"""
Classe utilizada para gerar cada um dos 'quadradinhos' ou 'nós' do grafo.
"""


class Point:

    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.width = width
        self.total_rows = total_rows

        # Desenhar cubos independentemente do tamanho da tela
        self.x = row * width
        self.y = col * width

        # Cor padrão
        self.color = WHITE

        # Pontos vizinhos
        self.nearby_points = []

        # heuristica de cada ponto
        self.h = 0
        self.g = 0

    # Getters & Setters

    def get_position(self):
        return self.row, self.col

    def is_open(self):
        return self.color == GREEN

    def is_closed(self):
        return self.color == RED

    def is_obstacle(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == BLUE

    def is_end(self):
        return self.color == YELLOW

    def set_empty(self):
        self.color = WHITE

    def set_close(self):
        self.color = RED

    def set_open(self):
        self.color = GREEN

    def set_obstacle(self):
        self.color = BLACK

    def set_start(self):
        self.color = YELLOW

    def set_end(self):
        self.color = BLUE

    def set_path(self):
        self.color = LIGHT_GREEN

    def set_h_manhanttan(self, end_pos):
        self.h = manhattan(self.get_position(), end_pos.get_position())

    def set_h_chebyshev(self, end_pos):
        self.h = chebyshev(self.get_position(), end_pos.get_position())

    def set_h_inadmissible(self, end_pos):
        self.h = inadmissible_heuristics(
            self.get_position(), end_pos.get_position())

    def set_g(self, valor):
        self.g = valor

    def get_heuristic(self):
        return self.h

    def get_g(self):
        return self.g

    def draw(self, window):
        '''
        Desenha um quadrado na jenela (pygame window) passada por parâmetro.

        Parâmetros:
            window (pygame window): janela do pygame.

        Observação: O ponto (0, 0) fica localizado no vértice superior esquerdo. 
        Logo, aumentar o Y significa ir para baixo e aumentar o X ir para a direita.
        '''
        pygame.draw.rect(window, self.color,
                         (self.x, self.y, self.width, self.width))

    def update_nearby_points(self, matrix):
        '''
        Atualizar a lista com todos os pontos próximos ao ponto em questão, verificando
        se o ponto existe e se não é um obstáculo.

        Parâmetro:
            matrix (list): lista de listas.
        '''
        self.nearby_points = []
        # O ponto de baixo existe? Ele é um obstaculo?
        # DOWN
        if self.row < self.total_rows - 1 and not matrix[self.row + 1][self.col].is_obstacle():
            self.nearby_points.append(matrix[self.row + 1][self.col])
        # O ponto de cima existe? Ele é um obstaculo?
        # UP
        # -1 pois Y cresce inversamente
        if self.row > 0 and not matrix[self.row - 1][self.col].is_obstacle():
            self.nearby_points.append(matrix[self.row - 1][self.col])
        # O ponto da direita existe? Ele é um obstaculo?
        # RIGHT
        if self.col < self.total_rows - 1 and not matrix[self.row][self.col + 1].is_obstacle():
            self.nearby_points.append(matrix[self.row][self.col + 1])
        # O ponto da esquerda existe? Ele é um obstaculo?
        # LEFT
        if self.col > 0 and not matrix[self.row][self.col - 1].is_obstacle():
            self.nearby_points.append(matrix[self.row][self.col - 1])

    def __lt__(self, other):
        return False

    def __str__(self):
        return str(self.get_position())

# -----------------------------------------------------------------------
# HEURÍSTICAS
# -----------------------------------------------------------------------

# Manhattan -> Admissível


def manhattan(p1, p2):
    '''
    Heurística 01: Manhattan. Será utilizada a distância de Manhattan como 
    uma das heurísticas adimissíveis.

    Parâmetros:
        p1 (Point): ponto inicial, de onde quer sair.
        p2 (Point): ponto final, para onde quer ir.

    Retorno:
        int: distância 'Manhattan' entre p1 e p2.
    '''
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


# Chebyshev -> Admissível
def chebyshev(p1, p2):
    '''
    Heurística 02: Chebyshev. Retona a maior entre as diferenças de X e Y de dois pontos.

    Parâmetros:
        p1 (Point): ponto inicial, de onde quer sair.
        p2 (Point): ponto final, para onde quer ir.

    Retorno:
        int: distância 'Chebyshev' entre p1 e p2.
    '''
    x1, y1 = p1
    x2, y2 = p2
    return max(abs(x1 - x2), abs(y1 - y2))


# Inadmissível
def inadmissible_heuristics(p1, p2):
    '''
    Heurística 03: Calculo totalmente doido inventado por nós para gerar uma heurística não admissível.

    Parâmetros:
        p1 (Point): ponto inicial, de onde quer sair.
        p2 (Point): ponto final, para onde quer ir.

    Retorno:
        int: distância inventada entre p1 e p2.
    '''
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - y1) * abs(y2 + x2) - abs(x2 - y1) * abs(y1 + x2)

# -----------------------------------------------------------------------
# A STAR
# -----------------------------------------------------------------------


def a_start_path_finding(redraw_screen, matrix, start_pos, end_pos):
    '''
    Função mais importante do projeto. É aqui que o algoritmo A* é definido, 
    todas as estruturas de dados são modificadas e a melhor decisão é tomada 
    com base em uma determinada função de avaliação.

    F(n) = g(n) + h(n)

    Parâmetros:
        redraw_screen (function): função que atualiza a tela.
        matrix (list): lista de listas.
        start_pos (Point): ponto inicial, do qual parte-se.
        end_pos (Point): ponto final, no qual pretende-se chegar.
    '''
    count = 0
    path = {}

    # Estrutura de dados dos nós abertos e visitados
    open_list_queue = PriorityQueue()  # Retorna sempre o menor elemento da fila
    open_list_queue.put((0, count, start_pos))
    open_list = {start_pos}
    closed_list = set()

    # Parâmetros para função de avaliação
    g = {point: float("inf") for row in matrix for point in row}
    g[start_pos] = 0
    f = {point: float("inf") for row in matrix for point in row}

    while not open_list_queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_list_queue.get()[2]
        current.set_g(g[current])

        # Desenhar melhor caminho
        if current == end_pos:
            print(f'CUSTO REAL = {end_pos.get_g()}')
            # Enviar listas por parametros
            great_way(path, end_pos, redraw_screen)
            end_pos.set_end()
            start_pos.set_start()
            return True

        for nearby_point in current.nearby_points:
            temp_g = g[current] + 1

            if temp_g < g[nearby_point]:
                path[nearby_point] = current
                g[nearby_point] = temp_g
                # Atualizar f para tomar decisão
                f[nearby_point] = temp_g + nearby_point.get_heuristic()
                # print(f[nearby_point])
                if nearby_point not in open_list and nearby_point not in closed_list:
                    count += 1
                    open_list_queue.put((f[nearby_point], count, nearby_point))
                    open_list.add(nearby_point)
                    nearby_point.set_open()

        redraw_screen()

        if current != start_pos:
            open_list.remove(current)
            closed_list.add(current)
            current.set_close()

        print(f'LISTA ABERTA')
        for item in open_list:
            print(item, end=" ")
        print()

        print(f'LISTA FECHADA')
        for item in closed_list:
            print(item, end=" ")
        print()

    print()
    return False

# -----------------------------------------------------------------------
# ESTRUTURA DE DADOS
# -----------------------------------------------------------------------


def create_matrix(rows, width):
    '''
    Criar uma matriz, ou seja, uma lista de listas para guardar cada
    um dos pontos criados.

    Parâmetros:
        rows (int): número de linhas.
        width (int): tamanho da janela.

    Retorno:
        list: lista de listas, a matriz.

    '''
    matrix = []
    space = width // rows  # Espaço entre as linhas da janela pygame
    for i in range(rows):
        matrix.append([])
        for j in range(rows):
            # Novo ponto (nó)
            point = Point(row=i, col=j, width=space, total_rows=rows)
            matrix[i].append(point)

    return matrix

# -----------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------


def draw_matrix(window, rows, width):
    '''
    Desenhar as linhas que delimitam cada um dos pontos (nós) do grafo. Isto é, aqui 
    é gerada a representação visual da estrutura de dados, ou melhor, da matriz.

    Parâmetros:
        window (pygame window): janela do pygame.
        rows (int): número de linhas.
        width (int): tamanho da janela.
    '''
    space = width // rows  # Espaço entre as linhas da janela pygame
    # Desenhar linhas horizontais
    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i * space), (width, i * space))
    # Desenhar linhas verticais
    for j in range(rows):
        pygame.draw.line(window, GREY, (j * space, 0), (j * space, width))


def redraw_screen(window, matrix, rows, width):
    '''
    Resenha, isto é, limpa a tela e redenha tudo novamente com os estados atuais.

    Parâmetros:
        window (pygame window): janela do pygame.
        matrix (list): lista de listas.
        rows (int): número de linhas.
        width (int): tamanho da janela.
    '''
    window.fill(WHITE)  # limpar a tela

    for row in matrix:
        for point in row:
            # Desenhe cada ponto de cada uma das linhas
            point.draw(window)

    draw_matrix(window, rows, width)
    pygame.display.update()


def get_clicked_mouse_position(mouse_position, rows, width):
    '''
    Retorna a posição em que o mouse estava quando houve o clique.

    Parâmetros:
        mouse_position (tuple): posição do mouse [linha, coluna] no momento do clique.
        rows (int): número de linhas.
        width (int): tamanho da janela.

    Retorno:
        tuple: posição x, y do mouse quando houver clique.

    '''
    space = width // rows  # Espaço entre as linhas da janela pygame
    i, j = mouse_position

    row = i // space
    col = j // space

    return row, col


def great_way(path, current, redraw_screen):
    '''
    Desenha na tela o melhor caminho após o algoritmo ter encontrado uma solução.
    Somente será o melhor caminho caso a heurística escolhida seja admissível.

    Parâmetros:
        path(dict): dicionário com todos o nós do melhor caminho. 
        current(Point): ponto atual, o destino.
        redraw_screen(function): função que redesenha a tela.
    '''
    print(
        f'Ponto: {current.get_position()} G:  {current.get_g()}  H: {current.get_heuristic()} | F = {current.get_g() + current.get_heuristic()}',  end="  ")
    print()
    while current in path:
        current.set_path()
        current = path[current]
        redraw_screen()
        print(
            f'Ponto: {current.get_position()} G:  {current.get_g()}  H: {current.get_heuristic()} | F = {current.get_g() + current.get_heuristic()}')

        redraw_screen()

# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------


def main(window, width):
    # Parâmetros iniciais
    ROWS = 5
    matrix = create_matrix(ROWS, width)
    start_position = None
    end_position = None
    is_running = True
    while is_running:
        # Desenha a tela cada mudança de estado
        redraw_screen(window, matrix, ROWS, width)

        for event in pygame.event.get():

            # Finalizar jogo
            if event.type == pygame.QUIT:
                is_running = False

            # get_pressed()[0] -> BOTAO ESQUERDO DO MOUSE
            if pygame.mouse.get_pressed()[0]:
                # Obter posicao do mouse e mapear na matriz
                mouse_position = pygame.mouse.get_pos()
                row, col = get_clicked_mouse_position(
                    mouse_position, ROWS, width)
                point = matrix[row][col]
                # Setar posicao inicial
                if not start_position and point != end_position:
                    start_position = point
                    start_position.set_start()
                # Setar posicao final
                elif not end_position and point != start_position:
                    end_position = point
                    end_position.set_end()
                # Setar obstaculos
                elif point != start_position and point != end_position:
                    point.set_obstacle()

            # get_pressed()[2] -> BOTAO DIREITO DO MOUSE
            elif pygame.mouse.get_pressed()[2]:
                # Obter posicao do mouse e mapear na matriz
                mouse_position = pygame.mouse.get_pos()
                row, col = get_clicked_mouse_position(
                    mouse_position, ROWS, width)
                point = matrix[row][col]
                point.set_empty()  # Apagar ponto (white)

                # Apagar ponto inicial e final
                if point == start_position:
                    start_position = None
                elif point == end_position:
                    end_position = None

            # Inicializar jogo, rodar algoritmo
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start_position and end_position:
                    for row in matrix:
                        for point in row:
                            # Todos pontos vizinhos
                            point.update_nearby_points(matrix)
                            # point.set_h_manhanttan(end_position)
                            point.set_h_chebyshev(end_position)
                            # point.set_h_inadmissible(end_position)

                    # Iniciar algoritmo
                    a_start_path_finding(
                        lambda: redraw_screen(window, matrix, ROWS, width),
                        matrix,
                        start_position,
                        end_position,
                    )

                # Limpar tela após execução
                if event.key == pygame.K_BACKSPACE:
                    start_position = None
                    end_position = None
                    matrix = create_matrix(ROWS, width)

    pygame.quit()  # Fechar a janela


# -----------------------------------------------------------------------
# START GAME
# -----------------------------------------------------------------------

main(window=WINDOW, width=WIDTH)

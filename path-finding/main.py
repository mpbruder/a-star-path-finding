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
O Objetivo deste programa é simular visualmente cada uma das decisões tomadas em uma 
busca utilizando o algoritmo A*. Além disso, utilizamos tanto heurísticas admissíveis,
como heurísticas inadmissíveis para poder comparar os resultados.
"""

# -----------------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# -----------------------------------------------------------------------

# Cada estado de um Nó é representado por uma cor:
ESTADOS = {
    'vazio': (255, 255, 255), # Branco
    'fechado': (237, 0, 38), # Vermelho
    'aberto': (0, 101, 68), # Verde
    'inicio': (120, 199, 235), # Azul
    'fim': (253, 194, 0), # Amarelo
    'obstaculo': (0, 0, 0), # Preto
    'caminho': (204, 225, 0), # Verde Claro
}

# Dimensões:
LARGURA = 1600  
ALTURA = 800
JANELA = pygame.display.set_mode((LARGURA, ALTURA))  # Tamanho da janela
pygame.display.set_caption('Busca de caminhos com A*') # Título da janela
pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(), 15)
arvore_busca = font.render('Árvore de Busca aqui', True, (0, 0, 0))
lista_nos = font.render('Lista de nós abertos e fechados aqui', True, (0, 0, 0))
open_list = font.render('Open (x, y): [(0,0), (0,1)]', True, (0, 0, 0))
closed_list = font.render('Closed (x, y): [(3,4), (6,6)]', True, (0, 0, 0))

# arvore_busca_img = pygame.image.load(r'arvore.png')
# -----------------------------------------------------------------------
# CLASSE PARA CADA UM DOS NÓS DISPOSTOS NA TELA
# -----------------------------------------------------------------------
class Node:
    """
    Classe utilizada para gerar cada uma das células da matriz, ou nós do grafo.
    """
    # Construtor:
    def __init__(self, linha, coluna, largura, qtd_linhas):
        self.linha = linha
        self.coluna = coluna
        self.largura = largura
        self.qtd_linhas = qtd_linhas

        # Desenhar cubos independentemente do tamanho da tela
        self.x = linha * largura
        self.y = coluna * largura

        # Cor padrão
        self.estado = ESTADOS['vazio']

        # Pontos vizinhos
        self.vizinhos = []

    # Getters & Setters:
    def get_posicao(self):
        return self.linha, self.coluna

    def set_vazio(self):
        self.estado = ESTADOS['vazio']

    def set_fechado(self):
        self.estado = ESTADOS['fechado']

    def set_aberto(self):
        self.estado = ESTADOS['aberto']

    def set_obstaculo(self):
        self.estado = ESTADOS['obstaculo']

    def set_inicio(self):
        self.estado = ESTADOS['inicio']

    def set_fim(self):
        self.estado = ESTADOS['fim']

    def set_caminho(self):
        self.estado = ESTADOS['caminho']
        
    # Métodos para checagem de estados do nó:
    def is_aberto(self):
        return self.estado == ESTADOS['aberto']

    def is_fechado(self):
        return self.estado == ESTADOS['fechado']

    def is_obstaculo(self):
        return self.estado == ESTADOS['obstaculo']

    def is_inicio(self):
        return self.estado == ESTADOS['inicio']

    def is_fim(self):
        return self.estado == ESTADOS['fim']

    # Métodos:
    def desenhar(self, janela):
        '''
        Desenha um quadrado na janela (pygame window) passada por parâmetro.
        Parâmetros:
            janela (pygame window): janela do pygame.
        Observação: O ponto (0, 0) fica localizado no vértice superior esquerdo. 
        Logo, aumentar o Y significa ir para baixo e aumentar o X ir para a direita.
        '''
        pygame.draw.rect(janela, self.estado,
                         (self.x, self.y, self.largura, self.largura))

    def atualizar_pontos_vizinhos(self, matriz):
        '''
        Atualizar a lista com todos os pontos próximos ao ponto em questão, verificando
        se o ponto existe e se não é um obstáculo.
        Parâmetro:
            matrix (list): lista de listas.
        '''
        self.vizinhos = []
        # O ponto de baixo existe? Ele é um obstaculo?
        # DOWN
        if self.linha < self.qtd_linhas - 1 and not matriz[self.linha + 1][self.coluna].is_obstaculo():
            self.vizinhos.append(matriz[self.linha + 1][self.coluna])
        # O ponto de cima existe? Ele é um obstaculo?
        # UP
        # -1 pois Y cresce inversamente
        if self.linha > 0 and not matriz[self.linha - 1][self.coluna].is_obstaculo():
            self.vizinhos.append(matriz[self.linha - 1][self.coluna])
        # O ponto da direita existe? Ele é um obstaculo?
        # RIGHT
        if self.coluna < self.qtd_linhas - 1 and not matriz[self.linha][self.coluna + 1].is_obstaculo():
            self.vizinhos.append(matriz[self.linha][self.coluna + 1])
        # O ponto da esquerda existe? Ele é um obstaculo?
        # LEFT
        if self.coluna > 0 and not matriz[self.linha][self.coluna - 1].is_obstaculo():
            self.vizinhos.append(matriz[self.linha][self.coluna - 1])

    def __lt__(self, other):
        return False


# -----------------------------------------------------------------------
# HEURÍSTICAS
# -----------------------------------------------------------------------

# Manhattan -> Admissível
def heuristica_1(p1, p2):
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

# Others -> Admissível / Inadimissível

# -----------------------------------------------------------------------
# Buscador de Caminhos com A*
# -----------------------------------------------------------------------
def buscar_caminhos_a_estrela(redesenhar_tela, matriz, pos_inicio, pos_fim):
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
    contador = 0
    fila = PriorityQueue()  # Retorna sempre o menor elemento da fila
    fila.put((0, contador, pos_inicio))
    caminho_backtracking = {}

    # Parametros para função de avaliação
    g = {node: float("inf") for linha in matriz for node in linha}
    g[pos_inicio] = 0
    
    f = {node: float("inf") for linha in matriz for node in linha}
    f[pos_inicio] = heuristica_1(pos_inicio.get_posicao(), pos_fim.get_posicao())

    fila_hash = {pos_inicio}

    while not fila.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        atual = fila.get()[2]
        fila_hash.remove(atual)

        # Desenhar melhor caminho
        if atual == pos_fim:
            desenhar_melhor_caminho(caminho_backtracking, pos_fim, redesenhar_tela)
            pos_fim.set_fim()
            pos_inicio.set_inicio()
            return True

        for ponto_vizinho in atual.vizinhos:
            temp_g = g[atual] + 1

            if temp_g < g[ponto_vizinho]:
                caminho_backtracking[ponto_vizinho] = atual
                g[ponto_vizinho] = temp_g
                f[ponto_vizinho] = temp_g + \
                    heuristica_1(ponto_vizinho.get_posicao(), pos_fim.get_posicao())
                if ponto_vizinho not in fila_hash:
                    contador += 1
                    fila.put((f[ponto_vizinho], contador, ponto_vizinho))
                    fila_hash.add(ponto_vizinho)
                    ponto_vizinho.set_aberto()

        redesenhar_tela()

        if atual != pos_inicio:
            atual.set_fechado()

    return False


# -----------------------------------------------------------------------
# ESTRUTURA DE DADOS
# -----------------------------------------------------------------------
def criar_matriz(qtd_linhas, largura):
    '''
    Cria uma matriz, ou seja, uma lista de listas para guardar cada
    um dos pontos criados.
    Parâmetros:
        qtd_linhas (int): número de linhas.
        largura (int): tamanho da janela.
    Retorno:
        matriz: lista de listas, a matriz.
    '''
    matriz = []
    margem = largura // qtd_linhas  # Espaço entre os nós
    for linha in range(qtd_linhas):
        matriz.append([])
        for coluna in range(qtd_linhas):
            # Novo ponto (nó)
            node = Node(linha=linha, coluna=coluna, largura=margem, qtd_linhas=qtd_linhas)
            matriz[linha].append(node)

    return matriz


# -----------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------
def desenhar_grade(janela, qtd_linhas, largura):
    '''
    Desenha as linhas que delimitam cada um dos pontos (nós) do grafo. Isto é, gera
    a representação visual da estrutura de dados, ou melhor, da matriz.
    Parâmetros:
        janela (pygame window): janela do pygame.
        qtd_linhas (int): número de linhas.
        largura (int): tamanho da janela.
    '''
    
    COR_LINHAS = (128, 128, 128)
    margem = largura // qtd_linhas  # Espaço entre as linhas da janela pygame
    # Desenhar linhas verticais
    for linha in range(qtd_linhas):
        pygame.draw.line(janela, COR_LINHAS, (0, linha * margem), (largura, linha * margem))
    # Desenhar linhas horizontais
    for coluna in range(qtd_linhas):
        pygame.draw.line(janela, COR_LINHAS, (coluna * margem, 0), (coluna * margem, largura))


def redesenhar_tela(janela, matriz, qtd_linhas, largura):
    '''
    Redesenha, isto é, limpa a tela e redenha tudo novamente com os estados atuais.
    Parâmetros:
        window (pygame window): janela do pygame.
        matrix (list): lista de listas.
        rows (int): número de linhas.
        width (int): tamanho da janela.
    '''
    janela.fill(ESTADOS['vazio'])  # limpa a tela, setando todos os nós como branco (vazio)

    janela.blit(arvore_busca, dest=(900, 50))
    # janela.blit(arvore_busca_img, dest=(860, 100))
    janela.blit(lista_nos, dest=(1250, 50))
    janela.blit(open_list, dest=(1250, 70))
    janela.blit(closed_list, dest=(1250, 90))
    
    
    
    for linha in matriz:
        for ponto in linha:
            # Desenha cada ponto de cada uma das linhas
            ponto.desenhar(janela)

    desenhar_grade(janela, qtd_linhas, largura)
    pygame.display.update()


def get_mouse_pos(mouse_pos, qtd_linhas, largura):
    '''
    Retorna a posição em que o mouse estava quando houve o clique.
    Parâmetros:
        mouse_pos (tuple): posição do mouse [linha, coluna] no momento do clique.
        qtd_linhas (int): número de linhas.
        largura (int): tamanho da janela.
    Retorno:
        tuple: posição x, y do mouse quando houver clique.
    '''
    margem = largura // qtd_linhas  # Espaço entre as linhas da janela pygame
    x, y = mouse_pos

    linha = x // margem
    coluna = y // margem

    return linha, coluna


def desenhar_melhor_caminho(caminho, atual, redesenhar_tela):
    '''
    Desenha na tela o melhor caminho após o algoritmo ter encontrado uma solução.
    Somente será o melhor caminho caso a heurística escolhida seja admissível.
    Parâmetros:
        caminho(dict): dicionário com todos o nós do melhor caminho. 
        atual(Point): ponto atual, o destino.
        redesenhar_tela(function): função que redesenha a tela.
    '''
    while atual in caminho:
        atual = caminho[atual]
        atual.set_caminho()
        redesenhar_tela()

# -----------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# -----------------------------------------------------------------------
def main(janela, largura):
    # Configurações iniciais:
    NUM_LINHAS = 25
    matriz = criar_matriz(NUM_LINHAS, largura//2)
    pos_inicial = None
    pos_final = None
    em_execucao = True
    while em_execucao:
        # Desenha a tela cada mudança de estado
        redesenhar_tela(janela, matriz, NUM_LINHAS, largura//2)

        for event in pygame.event.get():

            # Finalizar jogo
            if event.type == pygame.QUIT:
                em_execucao = False

            if pygame.mouse.get_pressed()[0]: # Botão esquerdo do mouse
                # Obter posicao do mouse e mapear na matriz
                pos_mouse = pygame.mouse.get_pos()
                linha, coluna = get_mouse_pos(
                    pos_mouse, NUM_LINHAS, largura//2)
                ponto = matriz[linha][coluna]
                # Setar posicao inicial
                if not pos_inicial and ponto != pos_final:
                    pos_inicial = ponto
                    pos_inicial.set_inicio()
                # Setar posicao final
                elif not pos_final and ponto != pos_inicial:
                    pos_final = ponto
                    pos_final.set_fim()
                # Setar obstaculos
                elif ponto != pos_inicial and ponto != pos_final:
                    ponto.set_obstaculo()

            elif pygame.mouse.get_pressed()[2]: # Botão direito do mouse
                # Obter posicao do mouse e mapear na matriz
                pos_mouse = pygame.mouse.get_pos()
                linha, coluna = get_mouse_pos(
                    pos_mouse, NUM_LINHAS, largura//2)
                ponto = matriz[linha][coluna]
                ponto.set_vazio()  # Apagar ponto (white)

                # Apagar ponto inicial e final
                if ponto == pos_inicial:
                    pos_inicial = None
                elif ponto == pos_final:
                    pos_final = None

            # Inicializar jogo, rodar algoritmo
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and pos_inicial and pos_final:
                    for linha in matriz:
                        for ponto in linha:
                            # Todos pontos vizinhos
                            ponto.atualizar_pontos_vizinhos(matriz)

                    # Iniciar algoritmo
                    buscar_caminhos_a_estrela(
                        lambda: redesenhar_tela(janela, matriz, NUM_LINHAS, largura//2),
                        matriz,
                        pos_inicial,
                        pos_final
                    )

                # Recriar tela após execução
                if event.key == pygame.K_BACKSPACE:
                    pos_inicial = None
                    pos_final = None
                    matriz = criar_matriz(NUM_LINHAS, largura//2)

    pygame.quit()  # Encerra a execução


# -----------------------------------------------------------------------
# INICIA O JOGO
# -----------------------------------------------------------------------
main(janela=JANELA, largura=LARGURA)
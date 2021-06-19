import pygame
from queue import PriorityQueue

"""
Path Finding
É um programa em python desenvolvido durante a disciplina de 
Inteligência Artificial da Faculdade de Tecnologia da Unicamp pelos alunos:
    1. Kevin Barrios
    2. Larissa Benevides
    3. Matheus Alves
    4. Matheus Bruder
    5. Miguel Amaral
O Objetivo deste programa é simular visualmente cada uma das decisões tomadas 
em uma busca utilizando o algoritmo A*. Além disso, utilizamos tanto de
heurísticas admissíveis, como heurísticas inadmissíveis 
para poder comparar os resultados.
"""

# -----------------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# -----------------------------------------------------------------------

# Cada estado de um Nó é representado por uma cor:
ESTADOS = {
    'vazio': (255, 255, 255),  # Branco
    'fechado': (237, 0, 38, 0.5),  # Vermelho
    'aberto': (0, 101, 68),  # Verde
    'inicio': (120, 199, 235),  # Azul
    'fim': (253, 194, 0),  # Amarelo
    'obstaculo': (0, 0, 0),  # Preto
    'caminho': (204, 225, 0),  # Verde Claro
}

# Dimensões:
LARGURA = 1600
ALTURA = 800
JANELA = pygame.display.set_mode((LARGURA, ALTURA))  # Tamanho da janela
pygame.display.set_caption('Buscador de caminhos com A*')  # Título da janela

# Definições para escrita de texto na tela do jogo:
pygame.font.init()
font_titulo = pygame.font.Font(pygame.font.get_default_font(), 30)
font = pygame.font.Font(pygame.font.get_default_font(), 12)
font_aviso = pygame.font.Font(pygame.font.get_default_font(), 15)
COR_FONTE = (255, 255, 255)

# Definição dos títulos textuais dentro da tela:
cabecalho_arvore_busca = font_titulo.render('Árvore de Busca', True, COR_FONTE)
cabecalho_lista_abertos = font_titulo.render(
    'Lista de nós abertos', True, COR_FONTE)
cabecalho_lista_fechados = font_titulo.render(
    'Lista de nós fechados', True, COR_FONTE)

# Deslocamento dos textos na tela:
deslocamento_y_abertos = 90
deslocamento_x_abertos = 1250

deslocamento_y_fechados = 440
deslocamento_x_fechados = 1250

deslocamento_y_arvore = 90
deslocamento_x_arvore = 900

# -----------------------------------------------------------------------
# CLASSE PARA CADA UM DOS NÓS DISPOSTOS NA TELA
# -----------------------------------------------------------------------


class Ponto:
    """
    Classe utilizada para gerar cada um dos 'quadradinhos' ou 'nós' do grafo.
    """
    # Construtor:

    def __init__(self, linha, coluna, largura, qtd_linhas):
        self.linha = linha
        self.coluna = coluna
        self.largura = largura
        self.qtd_linhas = qtd_linhas

        # Atributos para desenhar cubos independentemente do tamanho da tela:
        self.x = linha * largura
        self.y = coluna * largura

        # Estado padrão padrão dos nós:
        self.estado = ESTADOS['vazio']

        # Pontos vizinhos:
        self.vizinhos = []

        # Heurística de cada nó:
        self.h = 0
        self.g = 0

    # Getters:
    def get_posicao(self):
        return self.linha, self.coluna

    def get_heuristica(self):
        return self.h

    def get_g(self):
        return self.g

    # Setters:
    def set_g(self, valor):
        self.g = valor

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

    def set_h_manhanttan(self, end_pos):
        self.h = manhattan(self.get_posicao(), end_pos.get_posicao())

    def set_h_chebyshev(self, end_pos):
        self.h = chebyshev(self.get_posicao(), end_pos.get_posicao())

    def set_h_inadmissivel(self, end_pos, obs):
        h = heuristica_inadmissivel(
            self.get_posicao(), end_pos.get_posicao())
        self.h = abs(h + obs)

    # Métodos para checagem de estados de cada nó:
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

    # Outros Métodos:
    def desenhar(self, janela):
        '''
        Desenha um quadrado na janela (pygame window) passada por parâmetro.
        Parâmetros:
            janela (pygame window): janela do pygame.
        Observação: 
        O ponto (0, 0) fica localizado no vértice superior esquerdo. 
        Logo, aumentar o Y significa ir para baixo e 
        aumentar o X ir para a direita.
        '''
        pygame.draw.rect(janela, self.estado,
                         (self.x, self.y, self.largura, self.largura))

    def atualizar_pontos_vizinhos(self, matriz):
        '''
        Atualizar a lista com todos os pontos próximos ao ponto em questão, 
        verificando se o ponto existe e se não é um obstáculo.
        Parâmetro:
            matrix (list): lista de listas.
        '''
        self.vizinhos = []
        # O ponto de baixo existe? Ele é um obstaculo?:
        if self.linha < self.qtd_linhas - 1 \
                and not matriz[self.linha + 1][self.coluna].is_obstaculo():
            self.vizinhos.append(matriz[self.linha + 1][self.coluna])

        # O ponto de cima existe? Ele é um obstaculo?:
        if self.linha > 0 \
                and not matriz[self.linha - 1][self.coluna].is_obstaculo():
            self.vizinhos.append(matriz[self.linha - 1][self.coluna])

        # O ponto da direita existe? Ele é um obstaculo?:
        if self.coluna < self.qtd_linhas - 1 \
                and not matriz[self.linha][self.coluna + 1].is_obstaculo():
            self.vizinhos.append(matriz[self.linha][self.coluna + 1])

        # O ponto da esquerda existe? Ele é um obstaculo?:
        if self.coluna > 0 \
                and not matriz[self.linha][self.coluna - 1].is_obstaculo():
            self.vizinhos.append(matriz[self.linha][self.coluna - 1])

    def __lt__(self, other):
        return False

    def __str__(self):
        return str(self.get_posicao())


# -----------------------------------------------------------------------
# HEURÍSTICAS
# -----------------------------------------------------------------------
def manhattan(p1, p2):  # -> Admissível
    '''
    Heurística 01: Manhattan. Será utilizada a distância de Manhattan como 
    uma das heurísticas adimissíveis.
    Parâmetros:
        p1 (Ponto): ponto inicial, de onde quer sair.
        p2 (Ponto): ponto final, para onde quer ir.
    Retorno:
        int: distância 'Manhattan' entre p1 e p2.
    '''
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def chebyshev(p1, p2):  # -> Admissível
    '''
    Heurística 02: Chebyshev. Retona a maior entre as diferenças 
    de X e Y de dois pontos.
    Parâmetros:
        p1 (Ponto): ponto inicial, de onde quer sair.
        p2 (Ponto): ponto final, para onde quer ir.
    Retorno:
        int: distância 'Chebyshev' entre p1 e p2.
    '''
    x1, y1 = p1
    x2, y2 = p2
    return max(abs(x1 - x2), abs(y1 - y2))


def heuristica_inadmissivel(p1, p2):  # -> Inadmissível
    '''
    Heurística 03: Multiplica a distância de manhattan pela 
    distância de chebyshev.
    Parâmetros:
        p1 (Ponto): ponto inicial, de onde quer sair.
        p2 (Ponto): ponto final, para onde quer ir.
    Retorno:
        int: distância "inventada" entre p1 e p2.
    '''

    return manhattan(p1, p2) * chebyshev(p1, p2)


# -----------------------------------------------------------------------
# Buscador de Caminhos com A*
# -----------------------------------------------------------------------
def busca_A_estrela(redesenhar_tela, matriz, pos_inicio, pos_fim):
    '''
    Função central do projeto. É aqui que o algoritmo A* é definido, 
    todas as estruturas de dados são modificadas e a melhor decisão é tomada 
    com base em uma determinada função de avaliação.
    F(n) = g(n) + h(n)
    Parâmetros:
        redesenhar_tela (function): função que atualiza a tela.
        matriz (list): lista de listas.
        pos_inicio (Ponto): ponto inicial, do qual parte-se.
        pos_fim (Ponto): ponto final, no qual pretende-se chegar.
    '''

    contador = 0
    caminho = {}
    global deslocamento_y_abertos, deslocamento_x_abertos, deslocamento_x_fechados, deslocamento_y_fechados

    # Estrutura de dados dos nós abertos e fechados:
    fila = PriorityQueue()  # Retorna sempre o menor elemento da fila
    fila.put((0, contador, pos_inicio))
    lista_abertos = {pos_inicio}
    lista_fechados = set()

    # Parâmetros para função de avaliação:
    g = {ponto: float("inf") for linha in matriz for ponto in linha}
    g[pos_inicio] = 0

    f = {ponto: float("inf") for linha in matriz for ponto in linha}

    while not fila.empty():
        # Encerra o jogo ao clicar no botão de sair:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        atual = fila.get()[2]
        atual.set_g(g[atual])  # Valor de 'g' para cada nó

        # Solução encontrada? Desenha o melhor caminho:
        if atual == pos_fim:
            lista_abertos.remove(pos_fim)
            lista_fechados.add(pos_fim)
            printar_listas(lista_abertos, lista_fechados)
            print(f'CUSTO REAL = {pos_fim.get_g()}')
            # Enviar listas por parametros
            desenhar_melhor_caminho(caminho, pos_fim, redesenhar_tela)
            pos_fim.set_fim()
            pos_inicio.set_inicio()

            for ponto in lista_abertos:
                # Exibe o nó aberto na tela do jogo:
                if deslocamento_x_abertos > LARGURA - 50:
                    deslocamento_x_abertos = 1250
                    deslocamento_y_abertos += 20
                JANELA.blit(font.render(str(ponto) + ',', True, COR_FONTE),
                            dest=(deslocamento_x_abertos, deslocamento_y_abertos))
                deslocamento_x_abertos += 55

            for ponto in lista_fechados:
                # Exibe o nó fechado na tela do jogo:
                if deslocamento_x_fechados > LARGURA - 50:
                    deslocamento_x_fechados = 1250
                    deslocamento_y_fechados += 20

                JANELA.blit(font.render(str(ponto) + ',', True, COR_FONTE),
                            dest=(deslocamento_x_fechados, deslocamento_y_fechados))

                deslocamento_x_fechados += 55

            return True

        # Caso contrário:
        for ponto_vizinho in atual.vizinhos:
            temp_g = g[atual] + 1

            if temp_g < g[ponto_vizinho]:
                caminho[ponto_vizinho] = atual
                g[ponto_vizinho] = temp_g

                # Atualiza valor de f para tomar decisão:
                f[ponto_vizinho] = temp_g + ponto_vizinho.get_heuristica()

                # Alteração de estado - Nó aberto:
                if ponto_vizinho not in lista_abertos \
                        and ponto_vizinho not in lista_fechados:
                    contador += 1
                    fila.put((f[ponto_vizinho], contador, ponto_vizinho))
                    lista_abertos.add(ponto_vizinho)
                    ponto_vizinho.set_aberto()

        redesenhar_tela()

        # Alteração de estado - Nó fechado:
        lista_abertos.remove(atual)
        lista_fechados.add(atual)
        atual.set_fechado()

        printar_listas(lista_abertos, lista_fechados)

    return False


# -----------------------------------------------------------------------
# ESTRUTURA DE DADOS
# -----------------------------------------------------------------------
def criar_matriz(qtd_linhas, largura):
    '''
    Criar uma matriz, ou seja, uma lista de listas para guardar cada
    um dos pontos criados.
    Parâmetros:
        qtd_linhas (int): número de linhas.
        largura (int): tamanho da janela.
    Retorno:
        list: lista de listas, a matriz.
    '''
    matriz = []
    margem = largura // qtd_linhas  # Espaço entre os nós dentro do jogo
    for linha in range(qtd_linhas):
        matriz.append([])
        for coluna in range(qtd_linhas):
            # Criação de um novo nó:
            ponto = Ponto(linha=linha, coluna=coluna,
                          largura=margem, qtd_linhas=qtd_linhas)
            matriz[linha].append(ponto)

    return matriz


# -----------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------
def printar_listas(lista_abertos, lista_fechados):
    print('LISTA NOS ABERTOS: ')
    for item in lista_abertos:
        print(f'{item},', end=" ")

    print('\n\nLISTA NOS FECHADOS: ')
    for item in lista_fechados:
        print(f'{item},', end=" ")
    print('', end='\n\n\n')


def desenhar_grade(janela, qtd_linhas, largura):
    '''
    Desenha as linhas que delimitam cada um dos pontos (nós) do grafo. Isto é, 
    aqui é gerada a representação visual da estrutura de dados, ou melhor, 
    da matriz.
    Parâmetros:
        janela (pygame window): janela do pygame.
        qtd_linhas (int): número de linhas.
        largura (int): tamanho da janela.
    '''

    COR_LINHAS = (128, 128, 128)
    margem = largura // qtd_linhas  # Espaço entre os nós dentro do jogo

    # Desenha as linhas horizontais:
    for linha in range(qtd_linhas):
        pygame.draw.line(janela, COR_LINHAS,
                         (0, linha * margem), (largura, linha * margem))

    # Desenha as linhas verticais:
    for coluna in range(qtd_linhas):
        pygame.draw.line(janela, COR_LINHAS,
                         (coluna * margem, 0), (coluna * margem, largura))


def redesenhar_tela(janela, matriz, qtd_linhas, largura):
    '''
    Redesenha, isto é, limpa a tela e redenha tudo novamente com os estados atuais.
    Parâmetros:
        janela (pygame window): janela do pygame.
        matriz (list): lista de listas.
        qtd_linhas (int): número de linhas.
        largura (int): tamanho da janela.
    '''
    janela.blit(cabecalho_arvore_busca, dest=(900, 50))

    janela.blit(cabecalho_lista_abertos, dest=(1250, 50))

    janela.blit(cabecalho_lista_fechados, dest=(1250, 400))

    janela.blit(font_aviso.render(
        'Aperte a tecla "f5" para reiniciar o jogo', False, (0, 255, 0)), dest=(1300, 25))

    for linha in matriz:
        for ponto in linha:
            # Desenha cada nó de cada uma das linhas:
            ponto.desenhar(janela)

    desenhar_grade(janela, qtd_linhas, largura)
    pygame.display.update()


def get_mouse_pos(mouse_pos, qtd_linhas, largura):
    '''
    Retorna a posição em que o mouse estava quando houve o clique.
    Parâmetros:
        mouse_pos (tuple): posição do mouse [x, y] no momento do clique.
        qtd_linhas (int): número de linhas.
        largura (int): tamanho da janela.
    Retorno:
        tuple: posição x, y do mouse quando houver clique.
    '''
    margem = largura // qtd_linhas  # Espaço entre os nós dentro do jogo
    x, y = mouse_pos

    linha = x // margem
    coluna = y // margem

    return linha, coluna


def desenhar_melhor_caminho(caminho, atual, redesenhar_tela):
    '''
    Desenha na tela o melhor caminho após o algoritmo ter encontrado 
    uma solução. Somente será o melhor caminho caso a heurística escolhida 
    seja admissível.
    Parâmetros:
        caminho(dict): dicionário com todos o nós do melhor caminho. 
        atual(Point): ponto atual, o destino.
        redesenhar_tela(function): função que redesenha a tela.
    '''

    global deslocamento_y_arvore, deslocamento_x_arvore
    print('CAMINHO ESCOLHIDO')
    print(f'Ponto: {atual.get_posicao()} G:  {atual.get_g()}  H: {atual.get_heuristica()} | F = {atual.get_g() + atual.get_heuristica()}',  end="  ")

    JANELA.blit(font.render(
        str(f'Ponto: {atual.get_posicao()} G:  {atual.get_g()}  H: {atual.get_heuristica()} | F = {atual.get_g() + atual.get_heuristica()}'), True, COR_FONTE),
        dest=(deslocamento_x_arvore, 90))

    print()
    while atual in caminho:
        atual.set_caminho()
        atual = caminho[atual]
        redesenhar_tela()

        deslocamento_y_arvore += 20

        JANELA.blit(font.render(
            str(f'Ponto: {atual.get_posicao()} G:  {atual.get_g()}  H: {atual.get_heuristica()} | F = {atual.get_g() + atual.get_heuristica()}'), True, COR_FONTE),
            dest=(deslocamento_x_arvore, deslocamento_y_arvore))

        print(
            f'Ponto: {atual.get_posicao()} G:  {atual.get_g()}  H: {atual.get_heuristica()} | F = {atual.get_g() + atual.get_heuristica()}')

        redesenhar_tela()


# -----------------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# -----------------------------------------------------------------------
def main(janela, largura):
    # Parâmetros iniciais
    NUM_LINHAS = 20
    matriz = criar_matriz(NUM_LINHAS, largura // 2)
    pos_inicial = None
    pos_final = None
    em_execucao = True

    while em_execucao:
        # Desenha na tela cada mudança de estado:
        redesenhar_tela(janela, matriz, NUM_LINHAS, largura // 2)

        # Para cada evento detectado no jogo:
        for event in pygame.event.get():
            # Finalizar jogo:
            if event.type == pygame.QUIT:
                em_execucao = False

            # Caso botão esquerdo do mouse for pressionado:
            if pygame.mouse.get_pressed()[0]:
                # Obtém a posição do mouse e mapeia na matriz:
                pos_mouse = pygame.mouse.get_pos()
                linha, coluna = get_mouse_pos(
                    pos_mouse, NUM_LINHAS, largura // 2)
                if linha >= NUM_LINHAS or coluna >= NUM_LINHAS:
                    break
                ponto = matriz[linha][coluna]

                # Define a posição inicial:
                if not pos_inicial and ponto != pos_final:
                    pos_inicial = ponto
                    pos_inicial.set_inicio()

                # Define a posição final:
                elif not pos_final and ponto != pos_inicial:
                    pos_final = ponto
                    pos_final.set_fim()

                # Define obstáculos:
                elif ponto != pos_inicial and ponto != pos_final:
                    ponto.set_obstaculo()

            # Caso botão direito do mouse for pressionado:
            elif pygame.mouse.get_pressed()[2]:
                # Obtém a posição do mouse e mapeia na matriz:
                pos_mouse = pygame.mouse.get_pos()
                linha, coluna = get_mouse_pos(
                    pos_mouse, NUM_LINHAS, largura // 2)
                if linha >= NUM_LINHAS or coluna >= NUM_LINHAS:
                    break
                ponto = matriz[linha][coluna]
                ponto.set_vazio()

                # Apaga os pontos inicial e final caso clicado neles:
                if ponto == pos_inicial:
                    pos_inicial = None
                elif ponto == pos_final:
                    pos_final = None

            # Contador de obstáculos (utilizado na heurística inadmissível):
            obstaculos = 0
            for linha in matriz:
                for ponto in linha:
                    if ponto.is_obstaculo():
                        obstaculos += 1

            # Botão de espaço = inicializa o jogo:
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'f5':
                    pygame.draw.rect(JANELA, (0, 0, 0),
                                     pygame.Rect(700, 0, 1000, 1000))

                    global deslocamento_y_abertos, deslocamento_x_abertos, deslocamento_y_fechados, \
                        deslocamento_x_fechados, deslocamento_y_arvore, deslocamento_x_arvore

                    # Reseta as variáveis de deslocamento do texto:
                    deslocamento_y_abertos = 90
                    deslocamento_x_abertos = 1250
                    deslocamento_y_fechados = 440
                    deslocamento_x_fechados = 1250
                    deslocamento_y_arvore = 90
                    deslocamento_x_arvore = 900

                    # Desenha a grade novamente para um novoz
                    main(janela=JANELA, largura=LARGURA)

                if event.key == pygame.K_SPACE and pos_inicial and pos_final:
                    for linha in matriz:
                        for ponto in linha:
                            # Pontos vizinhos:
                            ponto.atualizar_pontos_vizinhos(matriz)

                            # Descomente uma das três heurísticas abaixo:
                            ponto.set_h_manhanttan(pos_final)
                            # ponto.set_h_chebyshev(pos_final)
                            # ponto.set_h_inadmissivel(pos_final, obstaculos)

                    # Inicia o algoritmo A*:
                    busca_A_estrela(
                        lambda: redesenhar_tela(
                            janela, matriz, NUM_LINHAS, largura // 2),
                        matriz,
                        pos_inicial,
                        pos_final,
                    )

                # Recria a tela após execução:
                if event.key == pygame.K_BACKSPACE:
                    pos_inicial = None
                    pos_final = None
                    matriz = criar_matriz(NUM_LINHAS, largura // 2)

    pygame.quit()  # Encerra a execução


# -----------------------------------------------------------------------
# INICIA O JOGO
# -----------------------------------------------------------------------
main(janela=JANELA, largura=LARGURA)

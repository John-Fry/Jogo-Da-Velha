import pygame
from grid import Grid

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '200,100'

surface = pygame.display.set_mode((600,600))
pygame.display.set_caption('Jogo da Velha')

# Cria uma thread separada para enviar e receber dados do servidor
import threading
def thread(target):
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

# criação do socket TCP para o cliente
import socket
HOST = '192.168.1.4'
PORT = 65432
connection_established = False
conn, addr = None, None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

def processaJogadas():
    global turn
    while True:
        data = conn.recv(1024).decode() 
        data = data.split('-') 
        x, y = int(data[0]), int(data[1])
        if data[2] == 'yourturn':
            turn = True
        if data[3] == 'False':
            grid.game_over = True
        if grid.get_cell_value(x, y) == 0:
            grid.set_cell_value(x, y, 'O')

def esperandoConexao():
    global connection_established, conn, addr
    conn, addr = sock.accept() # espera por uma conexão
    print('Cliente está conectado')
    connection_established = True
    processaJogadas()

# executa as funções de bloqueio em um thread separado
thread(esperandoConexao)

grid = Grid()
running = True
player = "X"
turn = True
playing = 'True'

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and connection_established:
            if pygame.mouse.get_pressed()[0]:
                if turn and not grid.game_over:
                    pos = pygame.mouse.get_pos()
                    cellX, cellY = pos[0] // 200, pos[1] // 200
                    grid.get_mouse(cellX, cellY, player)
                    if grid.game_over:
                        playing = 'False'
                    send_data = '{}-{}-{}-{}'.format(cellX, cellY, 'yourturn', playing).encode()
                    conn.send(send_data)
                    turn = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and grid.game_over:
                grid.clear_grid()
                grid.game_over = False
                playing = 'True'
            elif event.key == pygame.K_ESCAPE:
                running = False


    surface.fill((0,0,0))

    grid.draw(surface)

    pygame.display.flip()
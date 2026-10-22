from canvaslib import *

# -----------------------------------
# Dimensões do jogo
# -----------------------------------

LARGURA = 600
ALTURA = 400

arena = Canvas(LARGURA, ALTURA, BLACK)

# -----------------------------------
# Bola
# -----------------------------------

bola_x = 300
bola_y = 100

bola_raio = 10

bola_dx = 3
bola_dy = 3

# -----------------------------------
# Nave
# -----------------------------------

nave_x = 250
nave_y = 360

nave_largura = 100
nave_altura = 15

nave_velocidade = 25

# -----------------------------------
# Estado do jogo
# -----------------------------------

jogo_terminado = False


# -----------------------------------
# Desenhar o jogo
# -----------------------------------

def desenhar():

    arena.erase()

    # Desenhar a bola
    arena.drawCircle(
        bola_x,
        bola_y,
        bola_raio,
        RED
    )

    # Desenhar a nave
    arena.drawRect(
        nave_x,
        nave_y,
        nave_largura,
        nave_altura,
        BLUE
    )


# -----------------------------------
# Movimentar a nave
# -----------------------------------

def tecla_premida(tecla):

    global nave_x

    if tecla.text == "Left":
        nave_x = nave_x - nave_velocidade

    if tecla.text == "Right":
        nave_x = nave_x + nave_velocidade

    # Impedir que a nave saia do ecrã
    if nave_x < 0:
        nave_x = 0

    if nave_x + nave_largura > LARGURA:
        nave_x = LARGURA - nave_largura


# -----------------------------------
# Atualizar o jogo
# -----------------------------------

def atualizar(tempo):

    global bola_x, bola_y
    global bola_dx, bola_dy
    global jogo_terminado

    if jogo_terminado:
        return

    # Movimentar a bola
    bola_x = bola_x + bola_dx
    bola_y = bola_y + bola_dy

    # Colisão com a parede esquerda
    if bola_x - bola_raio <= 0:
        bola_x = bola_raio
        bola_dx = -bola_dx

    # Colisão com a parede direita
    if bola_x + bola_raio >= LARGURA:
        bola_x = LARGURA - bola_raio
        bola_dx = -bola_dx

    # Colisão com o teto
    if bola_y - bola_raio <= 0:
        bola_y = bola_raio
        bola_dy = -bola_dy

    # Colisão com a nave
    if bola_dy > 0:

        if bola_y + bola_raio >= nave_y:

            if bola_y - bola_raio <= nave_y + nave_altura:

                if bola_x + bola_raio >= nave_x:

                    if bola_x - bola_raio <= nave_x + nave_largura:

                        bola_y = nave_y - bola_raio
                        bola_dy = -bola_dy

    # Verificar se a bola caiu
    if bola_y - bola_raio > ALTURA:
        jogo_terminado = True

    # Desenhar o jogo
    desenhar()

    if jogo_terminado:
        arena.drawText(
            180,
            200,
            "GAME OVER",
            RED,
            35
        )


# -----------------------------------
# Iniciar o jogo
# -----------------------------------

arena.onKeyPressed(tecla_premida)

arena.onTimeProgress(16, atualizar)

arena.run()
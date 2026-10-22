from canvaslib import *

LARGURA, ALTURA = 600, 400
arena = Canvas(LARGURA, ALTURA, BLACK)

bola_x, bola_y = 300.0, 100.0
bola_dx, bola_dy = 180.0, 180.0  # píxeis por segundo
raio = 10
nave_x, nave_y = 250.0, 360
nave_largura, nave_altura = 100, 15
nave_velocidade = 360  # píxeis por segundo
esquerda = direita = False
terminado = False
iniciado = False
ultimo_tempo = 0


def premir(tecla):
    global esquerda, direita, iniciado
    if not iniciado and not terminado:
        iniciado = True
    if tecla.text == "Left":
        esquerda = True
    if tecla.text == "Right":
        direita = True


def libertar(tecla):
    global esquerda, direita
    if tecla.text == "Left":
        esquerda = False
    if tecla.text == "Right":
        direita = False


def atualizar(tempo):
    global bola_x, bola_y, bola_dx, bola_dy, nave_x, terminado, ultimo_tempo
    dt = min((tempo - ultimo_tempo) / 1000, 0.05)
    ultimo_tempo = tempo
    if iniciado and not terminado:
        if esquerda:
            nave_x -= nave_velocidade * dt
        if direita:
            nave_x += nave_velocidade * dt
        nave_x = max(0, min(nave_x, LARGURA - nave_largura))

        bola_x += bola_dx * dt
        bola_y += bola_dy * dt
        if bola_x - raio <= 0:
            bola_x, bola_dx = raio, abs(bola_dx)
        if bola_x + raio >= LARGURA:
            bola_x, bola_dx = LARGURA - raio, -abs(bola_dx)
        if bola_y - raio <= 0:
            bola_y, bola_dy = raio, abs(bola_dy)

        if (bola_dy > 0 and bola_y + raio >= nave_y
                and bola_y - raio <= nave_y + nave_altura
                and bola_x + raio >= nave_x
                and bola_x - raio <= nave_x + nave_largura):
            bola_y = nave_y - raio
            bola_dy = -abs(bola_dy)
        if bola_y - raio > ALTURA:
            terminado = True

    arena.erase()
    arena.drawCircle(bola_x, bola_y, raio, RED)
    arena.drawRect(nave_x, nave_y, nave_largura, nave_altura, BLUE)
    if not iniciado:
        arena.drawText(75, 210, "PRIME UMA TECLA PARA COMEÇAR", WHITE, 19)
    elif terminado:
        arena.drawText(185, 210, "GAME OVER", WHITE, 32)


arena.onKeyPressed(premir)
arena.onKeyReleased(libertar)
arena.onTimeProgress(16, atualizar)
arena.run()

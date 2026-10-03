# create a Maze game!
from pygame import *
from random import randint

# estadisticas
score = 0
lost = 0
goal = 21
max_lost = 5 

# musica y sonidos
mixer.init()

fire_sound = mixer.Sound('laser.ogg')
sonido_fondo = mixer.Sound('fondo.ogg')
sonido_fondo.set_volume(0.2)
sonido_fondo.play(-1)  # reproduce en bucle continuo

# sonido de explosión
sonido_explosion = mixer.Sound('fire.ogg')  # reemplaza por 'explosion.ogg' si tienes un archivo dedicado
sonido_explosion.set_volume(0.4)

# fuentes
font.init()
font1 = font.Font(None, 18)
font2 = font.Font('fuente2.ttf', 28)
font3 = font.Font('fuente2.ttf', 18)
font4 = font.Font('fuente2.ttf', 80)
font5_instrucciones = font.Font(None, 24)

text_esc = font5_instrucciones.render('Presiona ESC para pausar', 1, (255, 255, 255))
text_direccion = font5_instrucciones.render('Flechas DERECHA e IZQUIERDA para moverte', 1, (255, 255, 255))
text_disparar = font5_instrucciones.render('ESPACIO para disparar', 1, (255, 255, 255))
text_bomba = font5_instrucciones.render('SHIFT IZQ para lanzar bombas', 1, (255, 255, 255))
text_especial = font5_instrucciones.render('SHIFT DER para lanzar laceres especiales', 1, (255, 255, 255))

win = font1.render('YEA WIN', True, (255, 255, 0))
lose = font1.render('HA HA LOSER', True, (119, 240, 50))

text_pausa = font2.render('PAUSA', 1, (255, 255, 0))

text_puntaje = font3.render('PUNTAJE', 1, (230, 230, 230))
text_fallos = font3.render('FALLOS', 1, (230, 230, 230))

# Imágenes
img_back = "galaxy.jpg"
img_hero = "player.png"
img_Enemy = "enemy.png"
img_bullet = "bala.png"
img_bullet_desviada = "bala_desviada.png"
img_bullet_bomba = "enemy.png"
img_fondo = "fondo.jpg"
img_titulo = "titulo.png"
img_score = 'score.png'

# ventana
win_width = 900
win_height = 650

ventana = display.set_mode((win_width, win_height))
display.set_caption("Verschollen im Weltraum")
fondo = transform.scale(image.load(img_fondo), (win_width, win_height))

# Animación de explosión (cargada e inicializada con el sprite original + las fases)
animacion_frames = [
    transform.scale(image.load(img_Enemy).convert_alpha(), (48, 48)),
    transform.scale(image.load("animacion/explosion_1_02.png").convert_alpha(), (48, 48)),
    transform.scale(image.load("animacion/explosion_1_03.png").convert_alpha(), (48, 48)),
    transform.scale(image.load("animacion/explosion_1_04.png").convert_alpha(), (48, 48)),
    transform.scale(image.load("animacion/explosion_1_05.png").convert_alpha(), (48, 48)),
    transform.scale(image.load("animacion/explosion_1_06.png").convert_alpha(), (48, 48)),
    transform.scale(image.load("animacion/explosion_1_07.png").convert_alpha(), (48, 48))
]


class Gamesprite(sprite.Sprite):
    def __init__(self, Player_image, Player_x, Player_y, size_x, size_y, Player_speed):
        super().__init__()
        self.image = transform.scale(image.load(Player_image), (size_x, size_y))
        self.speed = Player_speed
        self.rect = self.image.get_rect()
        self.rect.x = Player_x
        self.rect.y = Player_y

    def reset(self):
        ventana.blit(self.image, (self.rect.x, self.rect.y))


class Player(Gamesprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 64, 64, -15)
        bullets.add(bullet)
    
    def fire_sin(self):
        bullet = BulletSin(img_bullet_desviada, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

    def bomb(self):
        bullet = Bullet(img_bullet_bomba, self.rect.centerx, self.rect.bottom - 32, 32, 32, 0)
        bullets.add(bullet)


class Enemy(Gamesprite):
    def update(self):
        self.rect.y += self.speed
        global lost

        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1 


class Bullet(Gamesprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        fire_sound.play()
     
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()


class BulletSin(Bullet):
    count = 0
    side = 1
    
    def update(self):
        self.rect.y += self.speed
        self.rect.x += 5 * self.side
        self.count += 1

        if self.count >= 10:
            self.count = 0
            self.side *= -1

        if self.rect.y < 0:
            self.kill()


class Explosion(sprite.Sprite):
    def __init__(self, center_x, center_y):
        super().__init__()
        self.frames = animacion_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (center_x, center_y)
        self.tick_count = 0
        sonido_explosion.play()

    def update(self):
        self.tick_count += 1
        # Cambia de frame cada 3 ticks (~20 fps de animación)
        if self.tick_count >= 3:
            self.tick_count = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_index]


class Button():
    def __init__(self, x, y, ancho, alto, color, color_hover, texto, color_texto=(255, 255, 255), accion=None):
        self.rect = Rect(x, y, ancho, alto)
        self.color_actual = color
        self.color_original = color
        self.color_hover = color_hover
        self.texto = texto
        self.color_texto = color_texto
        self.accion = accion
  
        self.font = font.Font('fuente2.ttf', 28)
        self.text_surface = self.font.render(self.texto, True, self.color_texto)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
  
    def actualizar(self, pos_raton):
        if self.rect.collidepoint(pos_raton):
            self.color_actual = self.color_hover
        else:
            self.color_actual = self.color_original
  
    def dibujar(self):
        draw.rect(ventana, self.color_actual, self.rect, border_radius=10)
        ventana.blit(self.text_surface, self.text_rect)

    def verificar_click(self, pos_raton):
        if self.rect.collidepoint(pos_raton) and self.accion:
            self.accion()


# personajes y grupos
Neil_Armstrong = Player(img_hero, 5, win_height - 100, 80, 100, 10)

monsters = sprite.Group()
for i in range(1, 5):
    monster = Enemy(img_Enemy, randint(80, win_width - 80), 70, 48, 48, randint(1, 5))
    monsters.add(monster)

bullets = sprite.Group()
explosions = sprite.Group()

# interfaz
boton_inicio = Button(
    win_width // 2 - 100, 
    win_height // 2 + 50, 
    200, 
    50, 
    (0, 128, 255), 
    (0, 255, 128), 
    'JUGAR',
    (255, 255, 255), 
    accion=lambda: cambiar_estado('juego')
)

lista_botones = [boton_inicio]

# ciclo de juego
finish = False
ejecutando = True
pausa = False
reloj = time.Clock()
FPS = 60

estado_juego = 'menu'

def cambiar_estado(nuevo_estado):
    global estado_juego
    estado_juego = nuevo_estado

while ejecutando:
    # EVENTOS
    for evento in event.get():
        if evento.type == QUIT:
            ejecutando = False
   
        elif evento.type == KEYDOWN:
            if evento.key == K_ESCAPE:
                pausa = not pausa
    
            if not pausa and estado_juego == 'juego':
                if evento.key == K_SPACE:
                    Neil_Armstrong.fire()

                if evento.key == K_LSHIFT:
                    Neil_Armstrong.bomb()

                if evento.key == K_RSHIFT:
                    Neil_Armstrong.fire_sin()
     
        elif evento.type == MOUSEBUTTONDOWN:
            if not pausa:
                if evento.button == 1:
                    for btn in lista_botones:
                        btn.verificar_click(evento.pos)

    if not finish:
        ventana.blit(fondo, (0, 0))
  
        if estado_juego == 'menu':
            ventana.blit(
                image.load(img_titulo), 
                (win_width // 2 - 250, win_height // 2 - 200)
            )

            ventana.blit(text_esc, (20, win_height - 180))
            ventana.blit(text_direccion, (20, win_height - 150))
            ventana.blit(text_disparar, (20, win_height - 120))
            ventana.blit(text_bomba, (20, win_height - 90))
            ventana.blit(text_especial, (20, win_height - 60))
      
            for btn in lista_botones:
                btn.actualizar(mouse.get_pos())
                btn.dibujar()
            
        elif estado_juego == 'juego':
            # interfaz hud
            ventana.blit(image.load(img_score), (30, 15))
   
            text_valor__puntaje = font2.render(str(score), 1, (135, 223, 165))
            ventana.blit(text_puntaje, (120, 39))
            ventana.blit(text_valor__puntaje, (205, 32))
   
            text_valor_fallos = font2.render(str(lost), 1, (246, 79, 66))
            ventana.blit(text_fallos, (305, 48))
            ventana.blit(text_valor_fallos, (380, 40))

            # renderizado de sprites
            Neil_Armstrong.reset()
            monsters.draw(ventana)
            bullets.draw(ventana)
            explosions.draw(ventana)

            if not pausa:
                # movimiento y actualizaciones
                Neil_Armstrong.update()
                monsters.update()
                bullets.update()
                explosions.update()

                # colisiones proyectiles vs enemigos
                collides = sprite.groupcollide(monsters, bullets, True, True)
                
                for c in collides:
                    score = score + 1
                    # generar animación de explosión en la posición del enemigo
                    boom = Explosion(c.rect.centerx, c.rect.centery)
                    explosions.add(boom)
                    
                    # regenerar enemigo
                    monster = Enemy(img_Enemy, randint(80, win_width - 80), 70, 48, 48, randint(1, 5))
                    monsters.add(monster)

                # colisiones de fin de partida
                if sprite.spritecollide(Neil_Armstrong, monsters, False) or lost >= max_lost:
                    finish = True
                    ventana.blit(lose, (200, 200))

                if score >= goal:
                    finish = True
                    ventana.blit(win, (200, 200))
                
            else:
                ventana.blit(text_pausa, (win_width // 2 - 50, win_height // 2 - 50))
    
    display.update()
    reloj.tick(FPS)
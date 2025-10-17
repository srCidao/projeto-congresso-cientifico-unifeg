import pygame
import random
import math
import sys
import ctypes

pygame.init()

# ======== CONFIGURAÇÕES ========
FPS = 60
TEMPO_JOGO = 15
VELOCIDADE_FRUTAS = 0.1
PONTOS_POR_FRUTA = 10

# ======== CORES ========
BRANCO, PRETO = (255, 255, 255), (0, 0, 0)
VERMELHO, VERDE, AZUL = (255, 0, 0), (0, 255, 0), (0, 120, 255)
AMARELO, LARANJA, ROXO = (255, 255, 0), (255, 165, 0), (128, 0, 128)
FUNDO = (245, 250, 255)
CORES_FRUTA = [VERMELHO, LARANJA, AMARELO, ROXO, VERDE, AZUL]

# ======== TELA E CURSOR ========
tela = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

# Maximiza a janela no Windows
user32 = ctypes.windll.user32
hwnd = pygame.display.get_wm_info()['window']
user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE = 3

LARGURA, ALTURA = tela.get_size()

pygame.display.set_caption("Corta Frutas - Explosão")
relogio = pygame.time.Clock()

try:
    cursor_img = pygame.image.load("cursor_mao.png").convert_alpha()
    cursor_img = pygame.transform.scale(cursor_img, (64, 64))
    pygame.mouse.set_visible(False)
except:
    print("⚠️  Arquivo 'cursor_mao.png' não encontrado!")
    sys.exit()

# ======== CLASSES ========
class Particula:
    def __init__(self, x, y, cor, tamanho=5, velocidade=6):
        self.x, self.y = x, y
        self.vel_x = random.uniform(-velocidade, velocidade)
        self.vel_y = random.uniform(-velocidade - 2, -1)
        self.raio = random.randint(tamanho // 2, tamanho)
        self.vida = random.randint(25, 50)
        self.alpha = 255
        self.cor_original = cor
        self.cor = cor

    def atualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.4
        self.vida -= 1
        self.alpha = max(0, self.alpha - 6)
        fator = self.alpha / 255
        self.cor = tuple(max(0, min(255, int(c * fator))) for c in self.cor_original)
        self.raio = max(0, self.raio - 0.05)

    def desenhar(self, tela):
        if self.alpha > 0:
            superficie = pygame.Surface((self.raio * 2, self.raio * 2), pygame.SRCALPHA)
            pygame.draw.circle(superficie, (*self.cor, int(self.alpha)), (int(self.raio), int(self.raio)), int(self.raio))
            tela.blit(superficie, (self.x - self.raio, self.y - self.raio))

    def ativa(self):
        return self.vida > 0 and self.alpha > 0


class Fruta:
    def __init__(self):
        self.cor = random.choice(CORES_FRUTA)
        self.tamanho = random.randint(40, 60)
        self.x = random.randint(50, LARGURA - 50)
        self.y = ALTURA + self.tamanho
        self.velocidade_x = random.uniform(-VELOCIDADE_FRUTAS * 1.5, VELOCIDADE_FRUTAS * 1.5)
        self.velocidade_y = -math.sqrt(2 * 0.5 * (self.y - self.tamanho))
        self.fatiada = False
        self.tempo_fatiada = 0

    def atualizar(self):
        self.velocidade_y += 0.6
        self.x += self.velocidade_x
        self.y += self.velocidade_y
        if self.fatiada:
            self.tempo_fatiada += 1

    def desenhar(self, tela):
        if not self.fatiada:
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.tamanho)
        else:
            for offset in [-15, 15]:
                pygame.draw.circle(tela, self.cor, (int(self.x + offset), int(self.y)), self.tamanho // 2)

    def esta_fora_da_tela(self):
        return self.y > ALTURA + self.tamanho or self.tempo_fatiada > 30

    def foi_fatiada(self, mouse_x, mouse_y):
        return not self.fatiada and math.hypot(self.x - mouse_x, self.y - mouse_y) < self.tamanho


# ======== FUNÇÕES AUXILIARES ========
def desenhar_texto(texto, tamanho, cor, x, y, centralizado=True):
    fonte = pygame.font.SysFont(None, tamanho)
    imagem = fonte.render(texto, True, cor)
    rect = imagem.get_rect(center=(x, y)) if centralizado else (x, y)
    tela.blit(imagem, rect)

def desenhar_botao(texto, rect, cor, texto_cor):
    pygame.draw.rect(tela, cor, rect, border_radius=20)
    desenhar_texto(texto, 48, texto_cor, rect.centerx, rect.centery)

def criar_explosao(x, y, cor):
    return [Particula(x, y, cor, tamanho=8, velocidade=7) for _ in range(40)]


# ======== LOOP PRINCIPAL ========
def main():
    frutas = []
    particulas = []
    tempo_restante = TEMPO_JOGO
    pontuacao = 0
    jogo_ativo = False
    ultimo_tempo_fruta = 0

    rect_play = pygame.Rect(LARGURA // 2 - 100, ALTURA // 2 - 40, 200, 80)
    rect_restart = pygame.Rect(LARGURA // 2 - 100, int(ALTURA * 0.65), 200, 80)

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                rodando = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        tempo_atual = pygame.time.get_ticks()

        if not jogo_ativo:
            tela.fill(FUNDO)
            if tempo_restante >= TEMPO_JOGO / 2:
                desenhar_botao("PLAY", rect_play, AZUL if rect_play.collidepoint(mouse_x, mouse_y) else ROXO, BRANCO)
                if rect_play.collidepoint(mouse_x, mouse_y):
                    jogo_ativo = True
                    frutas.clear()
                    particulas.clear()
                    tempo_restante = TEMPO_JOGO
                    pontuacao = 0
            else:
                desenhar_texto("Fim de Jogo!", 48, VERMELHO, LARGURA // 2, ALTURA // 4)
                desenhar_texto(f"Pontuação Final: {pontuacao}", 48, VERMELHO, LARGURA // 2, ALTURA // 2)
                desenhar_botao("REINICIAR", rect_restart, AZUL if rect_restart.collidepoint(mouse_x, mouse_y) else ROXO, BRANCO)
                if rect_restart.collidepoint(mouse_x, mouse_y):
                    jogo_ativo = True
                    frutas.clear()
                    particulas.clear()
                    tempo_restante = TEMPO_JOGO
                    pontuacao = 0

            tela.blit(cursor_img, (mouse_x - 32, mouse_y - 32))
            pygame.display.flip()
            relogio.tick(FPS)
            continue

        # Atualização do jogo
        tempo_restante -= 1 / FPS
        if tempo_restante <= 0:
            jogo_ativo = False
            continue

        if tempo_atual - ultimo_tempo_fruta > 1000:
            frutas.append(Fruta())
            ultimo_tempo_fruta = tempo_atual

        for fruta in frutas[:]:
            fruta.atualizar()
            if fruta.esta_fora_da_tela():
                frutas.remove(fruta)
            elif fruta.foi_fatiada(mouse_x, mouse_y):
                fruta.fatiada = True
                pontuacao += PONTOS_POR_FRUTA
                particulas.extend(criar_explosao(fruta.x, fruta.y, fruta.cor))

        particulas = [p for p in particulas if p.ativa()]
        for p in particulas:
            p.atualizar()

        # Desenho
        tela.fill(FUNDO)
        for fruta in frutas:
            fruta.desenhar(tela)
        for p in particulas:
            p.desenhar(tela)

        desenhar_texto(f"Pontuação: {pontuacao}", 36, PRETO, 20, 20, centralizado=False)
        desenhar_texto(f"Tempo: {int(tempo_restante)}s", 36, PRETO, 20, 60, centralizado=False)
        tela.blit(cursor_img, (mouse_x - 32, mouse_y - 32))
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

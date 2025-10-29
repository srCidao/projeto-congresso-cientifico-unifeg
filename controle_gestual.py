"""
Controle gestual do cursor com a mão.

Este código implementa a interface de controle gestual para qualquer jogo ou aplicação, mais com foco jogo Corta Frutas - Explosão,
permitindo mover o cursor com a mão dentro de uma zona ativa na tela. A estrutura principal do
sistema inclui cadastro do jogador, execução do jogo e registro de pontuações (ranking).

O fluxo do sistema segue a ordem: cadastro → jogo → ranking. Durante o jogo, frutas são
lançadas aleatoriamente e o jogador as corta usando o cursor controlado pela mão. A pontuação
é calculada com base nas frutas cortadas dentro do tempo disponível.

O sistema utiliza OpenCV e MediaPipe para rastreamento da mão, PyAutoGUI para controle do
mouse, e numpy para cálculos de filtragem e suavização de movimentos. O jogo fornece
feedback visual da zona ativa e da posição da mão, garantindo precisão e suavidade.
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# =========================
# Inicialização da câmera e do rastreador de mãos
# =========================
screen_w, screen_h = pyautogui.size()  # largura e altura da tela do computador
cap = cv2.VideoCapture(0)  # captura de vídeo da webcam

mp_hands = mp.solutions.hands  # módulo de detecção de mãos do MediaPipe
hands = mp_hands.Hands(
    static_image_mode=False,           # rastreamento contínuo
    max_num_hands=1,                   # detectar apenas uma mão
    min_detection_confidence=0.7,      # confiança mínima para detecção
    min_tracking_confidence=0.7        # confiança mínima para rastreamento
)
mp_draw = mp.solutions.drawing_utils  # utilitários para desenhar os pontos da mão
tips_ids = [4, 8, 12, 16, 20]         # IDs dos pontos das pontas dos dedos

ativo = False  # estado do controle gestual (ativo/desativado)
pyautogui.FAILSAFE = False  # desativa proteção de segurança do mouse
pyautogui.PAUSE = 0          # remove pausa entre comandos do mouse

last_mouse = None  # posição anterior do mouse
EMA_ALPHA_MIN = 0.25  # peso mínimo para filtragem exponencial
EMA_ALPHA_MAX = 0.6   # peso máximo para filtragem exponencial
SPEED_PX_REF = 180.0  # referência de velocidade para ajuste adaptativo
MAX_STEP = 90         # limite máximo de movimento do cursor por frame

draw_landmarks = True  # exibir ou não os pontos da mão na tela
prev_t = time.time()   # tempo do frame anterior para cálculo de FPS

# =========================
# Zona ativa (área de controle do cursor)
# =========================
# coordenadas relativas da zona vermelha onde o cursor pode se mover
zone_left = 0.50
zone_top = 0.15
zone_right = 0.90
zone_bottom = 0.55

# =========================
# Funções de filtragem e suavização do movimento
# =========================
def adaptive_alpha(prev_xy, curr_xy):
    """
    Calcula o fator alpha adaptativo da filtragem exponencial baseado na velocidade
    do movimento do cursor, permitindo movimentos suaves em diferentes velocidades.
    """
    if prev_xy is None:
        return EMA_ALPHA_MAX
    dx = curr_xy[0] - prev_xy[0]
    dy = curr_xy[1] - prev_xy[1]
    speed = (dx*dx + dy*dy) ** 0.5
    ratio = np.clip(speed / SPEED_PX_REF, 0.0, 1.0)
    return EMA_ALPHA_MIN + (EMA_ALPHA_MAX - EMA_ALPHA_MIN) * ratio

def ema(prev_xy, curr_xy, alpha):
    """
    Aplica filtragem exponencial para suavizar o movimento do cursor.
    Combina a posição atual e a anterior com o fator alpha.
    """
    if prev_xy is None:
        return curr_xy
    px, py = prev_xy
    cx, cy = curr_xy
    return (alpha * cx + (1 - alpha) * px, alpha * cy + (1 - alpha) * py)

def cap_velocity(prev_xy, curr_xy, max_step):
    """
    Limita a velocidade máxima do cursor para evitar saltos abruptos.
    """
    if prev_xy is None:
        return curr_xy
    px, py = prev_xy
    cx, cy = curr_xy
    dx, dy = cx - px, cy - py
    dist = (dx * dx + dy * dy) ** 0.5
    if dist <= max_step:
        return curr_xy
    scale = max_step / (dist + 1e-6)
    return (px + dx * scale, py + dy * scale)

def contar_dedos(hand_landmarks):
    """
    Retorna uma lista indicando quais dedos estão levantados:
    [polegar, indicador, médio, anular, mínimo] → 1 se levantado, 0 caso contrário.
    """
    dedos = []
    lm = hand_landmarks.landmark
    dedos.append(1 if lm[4].x < lm[3].x else 0)   # polegar
    dedos.append(1 if lm[8].y < lm[6].y else 0)   # indicador
    dedos.append(1 if lm[12].y < lm[10].y else 0) # médio
    dedos.append(1 if lm[16].y < lm[14].y else 0) # anular
    dedos.append(1 if lm[20].y < lm[18].y else 0) # mínimo
    return dedos

# =========================
# Instruções de uso
# =========================
print("Controles:")
print("🖐️  Mão aberta → ativa controle")
print("✊  Mão fechada → desativa controle")
print("☝️  Apenas indicador → move ponteiro (apenas dentro da zona vermelha)")
print("ESC → sair\n")

# =========================
# Configuração da janela do OpenCV
# =========================
window_name = "Controle Gestual - Mouse"
win_w, win_h = 480, 270
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # permite redimensionamento
cv2.resizeWindow(window_name, win_w, win_h)
cv2.moveWindow(window_name, screen_w - win_w, 0)  # posiciona no canto superior direito

# =========================
# Loop principal de captura e controle do cursor
# =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)               # espelha a imagem horizontalmente
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)            # processa a imagem para detectar a mão

    # Desenhar zona ativa
    x1, y1 = int(zone_left * w), int(zone_top * h)
    x2, y2 = int(zone_right * w), int(zone_bottom * h)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.putText(frame, "ZONA ATIVA", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        dedos = contar_dedos(hand)
        total = sum(dedos)

        # Ativa controle gestual ao abrir a mão
        if not ativo and total == 5:
            ativo = True
            last_mouse = None

        # Desativa controle ao fechar a mão
        if ativo and total == 0:
            ativo = False
            last_mouse = None

        # Move cursor se apenas o indicador estiver levantado
        if ativo and dedos[1] == 1 and total == 1:
            lm = hand.landmark[8]
            cam_x, cam_y = lm.x, lm.y

            # Verifica se o ponto do indicador está dentro da zona ativa
            if zone_left <= cam_x <= zone_right and zone_top <= cam_y <= zone_bottom:
                # Normaliza posição do dedo dentro da zona
                norm_x = (cam_x - zone_left) / (zone_right - zone_left)
                norm_y = (cam_y - zone_top) / (zone_bottom - zone_top)

                target_x = np.interp(norm_x, [0, 1], [0, screen_w])
                target_y = np.interp(norm_y, [0, 1], [0, screen_h])

                # Aplica filtragem adaptativa e limita velocidade
                a = adaptive_alpha(last_mouse, (target_x, target_y))
                filt = ema(last_mouse, (target_x, target_y), a)
                filt = cap_velocity(last_mouse, filt, MAX_STEP)
                last_mouse = filt

                pyautogui.moveTo(filt[0], filt[1], duration=0)  # move cursor
                cv2.circle(frame, (int(cam_x * w), int(cam_y * h)), 10, (255, 0, 255), -1)
            else:
                # Indica posição fora da zona ativa
                cv2.circle(frame, (int(cam_x * w), int(cam_y * h)), 10, (100, 100, 100), -1)

        # Desenha landmarks da mão se ativado
        if draw_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    # Exibe estado do controle na tela
    estado = "ATIVO" if ativo else "DESATIVADO"
    cv2.putText(frame, estado, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0) if ativo else (0, 0, 255), 2)

    # Calcula e exibe FPS
    now = time.time()
    fps = 1.0 / (now - prev_t + 1e-9)
    prev_t = now
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Controle Gestual - Mouse", frame)

    # Sair ao pressionar ESC
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

# =========================
# Libera recursos
# =========================
cap.release()
cv2.destroyAllWindows()

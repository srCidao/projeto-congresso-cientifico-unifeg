import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# =========================
# Inicialização
# =========================
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils
tips_ids = [4, 8, 12, 16, 20]

ativo = False
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

last_mouse = None
EMA_ALPHA_MIN = 0.25
EMA_ALPHA_MAX = 0.6
SPEED_PX_REF = 180.0
MAX_STEP = 90

draw_landmarks = True
prev_t = time.time()

# =========================
# Zona ativa (retângulo vermelho)
# =========================
# Posição ajustada para o canto superior direito
zone_left = 0.50
zone_top = 0.15
zone_right = 0.90
zone_bottom = 0.55

def adaptive_alpha(prev_xy, curr_xy):
    if prev_xy is None:
        return EMA_ALPHA_MAX
    dx = curr_xy[0] - prev_xy[0]
    dy = curr_xy[1] - prev_xy[1]
    speed = (dx*dx + dy*dy) ** 0.5
    ratio = np.clip(speed / SPEED_PX_REF, 0.0, 1.0)
    return EMA_ALPHA_MIN + (EMA_ALPHA_MAX - EMA_ALPHA_MIN) * ratio

def ema(prev_xy, curr_xy, alpha):
    if prev_xy is None:
        return curr_xy
    px, py = prev_xy
    cx, cy = curr_xy
    return (alpha * cx + (1 - alpha) * px, alpha * cy + (1 - alpha) * py)

def cap_velocity(prev_xy, curr_xy, max_step):
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
    dedos = []
    lm = hand_landmarks.landmark
    dedos.append(1 if lm[4].x < lm[3].x else 0)
    dedos.append(1 if lm[8].y < lm[6].y else 0)
    dedos.append(1 if lm[12].y < lm[10].y else 0)
    dedos.append(1 if lm[16].y < lm[14].y else 0)
    dedos.append(1 if lm[20].y < lm[18].y else 0)
    return dedos

print("Controles:")
print("🖐️  Mão aberta → ativa controle")
print("✊  Mão fechada → desativa controle")
print("☝️  Apenas indicador → move ponteiro (apenas dentro da zona vermelha)")
print("ESC → sair\n")

#Configura a janela
window_name = "Controle Gestual - Mouse"
win_w, win_h = 480, 270
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # permitir redimensionar
cv2.resizeWindow(window_name, win_w, win_h)
cv2.moveWindow(window_name, screen_w - win_w, 0)  # canto superior direito

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Desenhar zona ativa (retângulo vermelho)
    x1, y1 = int(zone_left * w), int(zone_top * h)
    x2, y2 = int(zone_right * w), int(zone_bottom * h)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.putText(frame, "ZONA ATIVA", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        dedos = contar_dedos(hand)
        total = sum(dedos)

        # Ativa controle com mão aberta
        if not ativo and total == 5:
            ativo = True
            last_mouse = None

        # Desativa com punho fechado
        if ativo and total == 0:
            ativo = False
            last_mouse = None

        # Move o mouse se apenas o indicador estiver levantado
        if ativo and dedos[1] == 1 and total == 1:
            lm = hand.landmark[8]
            cam_x, cam_y = lm.x, lm.y

            # Verifica se o dedo está dentro da zona ativa
            if zone_left <= cam_x <= zone_right and zone_top <= cam_y <= zone_bottom:
                # Normaliza coordenadas dentro da zona ativa
                norm_x = (cam_x - zone_left) / (zone_right - zone_left)
                norm_y = (cam_y - zone_top) / (zone_bottom - zone_top)

                target_x = np.interp(norm_x, [0, 1], [0, screen_w])
                target_y = np.interp(norm_y, [0, 1], [0, screen_h])

                a = adaptive_alpha(last_mouse, (target_x, target_y))
                filt = ema(last_mouse, (target_x, target_y), a)
                filt = cap_velocity(last_mouse, filt, MAX_STEP)
                last_mouse = filt

                pyautogui.moveTo(filt[0], filt[1], duration=0)
                cv2.circle(frame, (int(cam_x * w), int(cam_y * h)), 10, (255, 0, 255), -1)
            else:
                cv2.circle(frame, (int(cam_x * w), int(cam_y * h)), 10, (100, 100, 100), -1)

        if draw_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    estado = "ATIVO" if ativo else "DESATIVADO"
    cv2.putText(frame, estado, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0) if ativo else (0, 0, 255), 2)

    now = time.time()
    fps = 1.0 / (now - prev_t + 1e-9)
    prev_t = now
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Controle Gestual - Mouse", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()

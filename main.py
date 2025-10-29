"""
Este script gerencia a execução simultânea de um jogo e seu sistema de controle gestual.

O propósito principal é iniciar ambos os processos e garantir que a interface de
controle gestual permaneça em primeiro plano para interação contínua.

Estrutura principal:
- Funções utilitárias para obter janelas por PID e manter janelas no topo.
- Funções para iniciar o jogo e o controle gestual como subprocessos.
- Loop principal que monitora os processos e mantém a janela do controle gestual ativa.

Fluxo de funcionamento:
1. O jogo é iniciado.
2. O controle gestual é iniciado.
3. A janela do controle gestual é mantida como topmost.
4. Loop contínuo verifica o estado dos processos e garante prioridade da janela.

Tecnologias utilizadas:
- Python padrão (subprocess, sys, time, os)
- Módulos Windows (win32gui, win32con, win32process)

Funcionamento geral:
- O script monitora ambos os processos e encerra ambos caso algum deles seja fechado
  ou em caso de interrupção manual pelo usuário (Ctrl+C).
"""

import subprocess
import sys
import time
import win32gui
import win32con
import win32process
import os

def get_hwnd_by_pid(pid):
    """Retorna uma lista de handles de janela associadas ao processo especificado pelo PID."""
    hwnds = []
    def callback(hwnd, _):
        tid, win_pid = win32process.GetWindowThreadProcessId(hwnd)
        if win_pid == pid:
            hwnds.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return hwnds

def manter_janela_topmost(pid):
    """Define as janelas do processo como topmost, garantindo prioridade na tela."""
    hwnds = get_hwnd_by_pid(pid)
    for hwnd in hwnds:
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )

def run_game():
    """Inicia o subprocesso do jogo e retorna o objeto Popen correspondente."""
    return subprocess.Popen([sys.executable, "game.py"])

def run_controle_gestual():
    """Inicia o subprocesso do controle gestual e retorna o objeto Popen correspondente."""
    return subprocess.Popen([sys.executable, "controle_gestual.py"])

if __name__ == "__main__":
    # Inicia o subprocesso do jogo
    game_proc = run_game()
    time.sleep(1.5)  # aguarda a inicialização do jogo

    # Inicia o subprocesso do controle gestual
    controle_gestual_proc = run_controle_gestual()
    time.sleep(2)  # aguarda a inicialização do controle gestual

    # Garante que a janela do controle gestual fique em primeiro plano
    manter_janela_topmost(controle_gestual_proc.pid)

    # Loop de monitoramento dos processos
    try:
        while True:
            game_status = game_proc.poll()  # verifica se o jogo foi encerrado
            controle_status = controle_gestual_proc.poll()  # verifica se o controle gestual foi encerrado

            if game_status is not None or controle_status is not None:
                # Encerra ambos os processos caso algum seja finalizado
                game_proc.terminate()
                controle_gestual_proc.terminate()
                break

            # Mantém a janela do controle gestual em primeiro plano continuamente
            manter_janela_topmost(controle_gestual_proc.pid)

            time.sleep(0.5)  # intervalo de verificação
    except KeyboardInterrupt:
        # Finaliza ambos os processos em caso de interrupção pelo usuário
        game_proc.terminate()
        controle_gestual_proc.terminate()

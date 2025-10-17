import subprocess
import sys
import time

def run_fruit():
    """Inicia o jogo normalmente, sem tela cheia."""
    return subprocess.Popen([sys.executable, "game.py"])

def run_cod_gpt():
    """Inicia o controle gestual sem mover a janela."""
    return subprocess.Popen([sys.executable, "controle_gestual.py"])

if __name__ == "__main__":
    # Inicia ambos os programas simultaneamente
    fruit_proc = run_fruit()
    cod_proc = run_cod_gpt()

    # Monitora: se qualquer um encerrar, fecha o outro
    try:
        while True:
            fruit_status = fruit_proc.poll()
            cod_status = cod_proc.poll()

            if fruit_status is not None or cod_status is not None:
                # Se qualquer um dos dois terminar, encerra o outro
                fruit_proc.terminate()
                cod_proc.terminate()
                break

            time.sleep(0.2)
    except KeyboardInterrupt:
        fruit_proc.terminate()
        cod_proc.terminate()

====================================================
CORTA FRUTAS - EXPLSÃO: CONTROLE GESTUAL INTELIGENTE
====================================================

Descrição
----------
Este projeto integra um sistema de **controle gestual por câmera** com um jogo interativo chamado **Corta Frutas – Explosão**.  
O jogador utiliza o movimento da mão para controlar o cursor e cortar frutas lançadas na tela, acumulando pontos dentro de um tempo limite.

O sistema é composto por três módulos principais:
- **game.py** → executa o jogo de corte de frutas.
- **controle_gestual.py** → controla o cursor do mouse por gestos usando visão computacional.
- **main.py** → gerencia a execução simultânea do jogo e do controle gestual.

O objetivo é proporcionar uma experiência interativa e divertida, com aplicações potenciais em **reabilitação motora**, **treinamento cognitivo** e **interação natural com sistemas**.

----------------------------------------------------

Instalação
-----------
Requisitos:
- Python 3.9 ou superior
- Sistema operacional Windows (necessário para manipulação de janelas via `pywin32`)

Passos para instalação:

1. **Baixe o projeto completo** e extraia em uma pasta local.
2. **Instale as dependências** executando o comando abaixo no terminal (dentro da pasta do projeto):
3. **Certifique-se de possuir uma webcam conectada.**

----------------------------------------------------

Uso
----
1. Execute o arquivo principal: python main.py

2. O script abrirá duas janelas:
- A janela do **jogo Corta Frutas – Explosão**.
- A janela do **controle gestual**, responsável pelo rastreamento da mão.

3. **Gestos disponíveis:**
- 🖐️ Mão aberta → ativa o controle.
- ✊ Mão fechada → desativa o controle.
- ☝️ Apenas o indicador → move o cursor (apenas dentro da zona vermelha).
- ESC → encerra o programa.

4. O jogo registra automaticamente as pontuações em um arquivo Excel (`jogadores.xlsx`), mantendo um ranking com os melhores resultados.

----------------------------------------------------

Bibliotecas e Funções
----------------------
Biblioteca           | Função principal
--------------------- | ------------------------------------------------
opencv-python        | Captura de vídeo da webcam e exibição do feed de imagem
mediapipe            | Rastreamento da mão e detecção dos dedos
pyautogui            | Movimento e controle do cursor do mouse
numpy                | Cálculos matemáticos e suavização de movimento
pygame               | Engine gráfica e lógica do jogo
openpyxl             | Leitura e escrita de dados (pontuações e cadastros) em planilha Excel
pywin32              | Controle de janelas e manipulação de processos no Windows
sys / os / time / subprocess | Gerenciamento de processos e sincronização entre módulos
random / math / ctypes | Cálculos auxiliares e manipulação do sistema
collections          | Organização de pontuações por jogador

----------------------------------------------------

Licença
--------
Este projeto é distribuído para fins educacionais e de pesquisa.  
Uso comercial requer autorização explícita do autor.

----------------------------------------------------

Autores:
David Igor Gomes de Oliveira;
Jean Estevan Godoi Silva;
Octavio Moraes Ribeiro;
Suzana Silva Rezende;
Vitor Hugo dos Santos Sanchez Queiroz.

Projeto desenvolvido inicialmente para uso no curso de Ciência da Computação, Centro Universitário da Fundação Educacional Guaxupé (UNIFEG), Guaxupé – MG.

Descrição:
Projeto desenvolvido no contexto de pesquisa em interfaces inteligentes e reabilitação motora, utilizando Python e visão computacional.

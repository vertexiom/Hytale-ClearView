CLEARVIEW 0.1.2 — LINUX x64

1. Extraia a pasta inteira. Não mova só o install.sh.
2. Feche o Hytale.
3. Abra um terminal nesta pasta e execute:

   bash install.sh

4. Na interface, clique em Continuar, confira a pasta do Hytale e instale.
5. Ao concluir, abra o jogo pelo launcher normal. F9 abre o painel.

O mesmo comando abre a interface para atualizar ou remover o mod.
Seus ajustes são preservados. Não execute install.sh com sudo.
Não precisa instalar .deb, usar a loja ou compilar o mod.

A interface precisa de Python 3, GTK 4, PyGObject e Cairo do sistema.
Se faltarem dependências, no Ubuntu/Debian instale uma vez:
  sudo apt install python3 python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-4.0
Depois rode bash install.sh novamente, sem sudo.

Este pacote foi preparado no Ubuntu 26.04 amd64; o mod requer glibc >= 2.38.
Outras distribuições e runtimes precisam de validação. As dependências GTK
não estão incluídas. Não é um executável universal independente do sistema.

O mod fica instalado na pasta do Hytale. Apagar esta pasta do instalador
não remove o mod: use a opção Remover instalação dentro da interface.
Nenhum arquivo original do Hytale acompanha este pacote.

Suporte Discord: tallmannzera
Projeto: https://github.com/vertexiom/Hytale-ClearView

Uso avançado sem interface: bash install.sh --cli --help

Ao abrir, o instalador registra seu nome e ícone em ~/.local/share/applications e ~/.local/share/icons (ou XDG_DATA_HOME), sem sudo. Se mover a pasta, execute bash install.sh novamente para atualizar o atalho.

import tkinter as tk
from datetime import datetime
import random

SIMS_GREEN     = "#5ec400"
SIMS_GLOW_MID  = "#2d6e00"
SIMS_GLOW_OUT  = "#0d2a00"
SIMS_HIGHLIGHT = "#aaee40"
SIMS_TOPLINE   = "#e8ff90"
SIMS_SHINE     = "#d0f870"
SIMS_BG        = "#040803"
SIMS_PANEL     = "#060c02"
SIMS_BORDER    = "#1c3c08"

BAR_LEFT  = 14
BAR_RIGHT = 386
BAR_TOP   = 36
BAR_BOT   = 54
BAR_WIDTH = BAR_RIGHT - BAR_LEFT


class BarraWidget:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x80")
        self.root.configure(bg=SIMS_BG)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.config(relief=tk.FLAT, bd=0)

        self.canvas = tk.Canvas(
            root, width=400, height=80,
            bg=SIMS_BG, highlightthickness=0, bd=0
        )
        self.canvas.pack()

        self._criar_fundo()
        self._criar_barra()
        self._criar_labels()

        self.shine_pos = -25
        self.largura_barra_atual = 0
        self.sparkles = []

        self.atualizar()
        self.animar()

        self.root.bind('<Button-1>', self.drag_start)
        self.root.bind('<B1-Motion>', self.drag_motion)
        self.drag_data = {'x': 0, 'y': 0}

    def _criar_fundo(self):
        self.canvas.create_rectangle(0, 0, 400, 80, fill=SIMS_BG, outline="")
        # Painel externo
        self.canvas.create_rectangle(8, 28, 392, 62, fill=SIMS_PANEL, outline=SIMS_BORDER, width=1)
        # Painel interno mais escuro
        self.canvas.create_rectangle(10, 30, 390, 60, fill="#030601", outline="#0e2204")

    def _criar_barra(self):
        # Background da barra
        self.canvas.create_rectangle(BAR_LEFT, BAR_TOP, BAR_RIGHT, BAR_BOT, fill="#020600", outline="")

        # Glow externo (extravasa acima e abaixo da barra)
        self.glow_out = self.canvas.create_rectangle(
            BAR_LEFT, BAR_TOP - 4, BAR_LEFT, BAR_BOT + 4,
            fill=SIMS_GLOW_OUT, outline=""
        )
        # Glow médio
        self.glow_mid = self.canvas.create_rectangle(
            BAR_LEFT, BAR_TOP - 2, BAR_LEFT, BAR_BOT + 2,
            fill=SIMS_GLOW_MID, outline=""
        )
        # Barra principal
        self.barra = self.canvas.create_rectangle(
            BAR_LEFT, BAR_TOP, BAR_LEFT, BAR_BOT,
            fill=SIMS_GREEN, outline=""
        )
        # Sombra na base (dá profundidade)
        self.shadow = self.canvas.create_rectangle(
            BAR_LEFT, BAR_BOT - 4, BAR_LEFT, BAR_BOT,
            fill="#2a6000", outline=""
        )
        # Highlight no topo
        self.highlight = self.canvas.create_rectangle(
            BAR_LEFT, BAR_TOP, BAR_LEFT, BAR_TOP + 5,
            fill=SIMS_HIGHLIGHT, outline=""
        )
        # Linha fina brilhante no topo
        self.topline = self.canvas.create_rectangle(
            BAR_LEFT, BAR_TOP, BAR_LEFT, BAR_TOP + 2,
            fill=SIMS_TOPLINE, outline=""
        )
        # Borda brilhante na ponta da barra (leading edge)
        self.leading_edge = self.canvas.create_rectangle(
            0, 0, 0, 0, fill="#ffffff", outline=""
        )
        # Shine animado
        self.shine = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=SIMS_SHINE, outline=""
        )

    def _criar_labels(self):
        self.lbl_perc = self.canvas.create_text(
            14, 16, text="0%",
            fill="#78d020", font=("Verdana", 8, "bold"), anchor="w"
        )
        self.lbl_hora = self.canvas.create_text(
            386, 16, text="--:--",
            fill="#4a8015", font=("Verdana", 8), anchor="e"
        )
        self.lbl_status = self.canvas.create_text(
            200, 70, text="Carregando...",
            fill="#2e5a0a", font=("Verdana", 7), anchor="center"
        )

    def animar(self):
        if self.largura_barra_atual > 10:
            # Mover shine da esquerda para a direita e reiniciar
            self.shine_pos += 5
            if self.shine_pos > self.largura_barra_atual + 30:
                self.shine_pos = -30

            s1 = BAR_LEFT + self.shine_pos - 18
            s2 = BAR_LEFT + self.shine_pos + 18
            s1 = max(BAR_LEFT, s1)
            s2 = min(BAR_LEFT + self.largura_barra_atual, s2)
            if s2 > s1:
                self.canvas.coords(self.shine, s1, BAR_TOP, s2, BAR_BOT)
            else:
                self.canvas.coords(self.shine, 0, 0, 0, 0)

            # Criar sparkles aleatórios
            if random.random() < 0.22 and self.largura_barra_atual > 15:
                x = BAR_LEFT + random.randint(3, int(self.largura_barra_atual) - 3)
                y = random.randint(BAR_TOP + 2, BAR_BOT - 2)
                sz = random.randint(1, 2)
                item = self.canvas.create_oval(
                    x - sz, y - sz, x + sz, y + sz,
                    fill="#c8ff50", outline=""
                )
                self.sparkles.append([item, random.randint(6, 18)])

            # Envelhecer e remover sparkles
            vivos = []
            for s in self.sparkles:
                s[1] -= 1
                if s[1] <= 0:
                    self.canvas.delete(s[0])
                else:
                    vivos.append(s)
            self.sparkles = vivos
        else:
            self.canvas.coords(self.shine, 0, 0, 0, 0)

        self.root.after(50, self.animar)

    def atualizar(self):
        agora = datetime.now()
        hora   = agora.hour
        minuto = agora.minute

        minuto_atual = hora * 60 + minuto
        inicio   = 13 * 60
        fim      = 16 * 60 + 50
        duracao  = fim - inicio

        self.canvas.itemconfig(self.lbl_hora, text=f"{hora:02d}:{minuto:02d}")

        if minuto_atual < inicio:
            percentual = 0
            status = "Aguardando início..."
        elif minuto_atual >= fim:
            percentual = 100
            status = "Concluído!"
        else:
            percentual = int(((minuto_atual - inicio) / duracao) * 100)
            status = "Carregando..."

        largura = (percentual / 100) * BAR_WIDTH
        self.largura_barra_atual = largura
        x2 = BAR_LEFT + largura

        self.canvas.coords(self.glow_out,   BAR_LEFT, BAR_TOP - 4, x2, BAR_BOT + 4)
        self.canvas.coords(self.glow_mid,   BAR_LEFT, BAR_TOP - 2, x2, BAR_BOT + 2)
        self.canvas.coords(self.barra,      BAR_LEFT, BAR_TOP,     x2, BAR_BOT)
        self.canvas.coords(self.shadow,     BAR_LEFT, BAR_BOT - 4, x2, BAR_BOT)
        self.canvas.coords(self.highlight,  BAR_LEFT, BAR_TOP,     x2, BAR_TOP + 5)
        self.canvas.coords(self.topline,    BAR_LEFT, BAR_TOP,     x2, BAR_TOP + 2)

        if largura > 4:
            self.canvas.coords(self.leading_edge, x2 - 3, BAR_TOP - 4, x2, BAR_BOT + 4)
        else:
            self.canvas.coords(self.leading_edge, 0, 0, 0, 0)

        self.canvas.itemconfig(self.lbl_perc,   text=f"{percentual}%")
        self.canvas.itemconfig(self.lbl_status, text=status)

        self.root.after(1000, self.atualizar)

    def drag_start(self, event):
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def drag_motion(self, event):
        delta_x = event.x - self.drag_data['x']
        delta_y = event.y - self.drag_data['y']
        x = self.root.winfo_x() + delta_x
        y = self.root.winfo_y() + delta_y
        self.root.geometry(f'+{x}+{y}')


if __name__ == "__main__":
    root = tk.Tk()
    app = BarraWidget(root)
    root.mainloop()

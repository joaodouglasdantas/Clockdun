import tkinter as tk
from datetime import datetime
import random

# --- Fundo e painel ---
SIMS_BG     = "#040803"
SIMS_PANEL  = "#060c02"
SIMS_BORDER = "#1c3c08"

# --- Amarelo: 08:00–12:00 ---
YEL_BAR      = "#d4b800"
YEL_GLOW_OUT = "#2a2200"
YEL_GLOW_MID = "#5e4e00"
YEL_HIGHLIGHT= "#fff080"
YEL_TOPLINE  = "#ffffc0"
YEL_SHINE    = "#ffff90"
YEL_SHADOW   = "#604e00"
YEL_SPARKLE  = "#ffe050"

# --- Verde: 13:00–17:00 ---
GRN_BAR      = "#5ec400"
GRN_GLOW_OUT = "#0d2a00"
GRN_GLOW_MID = "#2d6e00"
GRN_HIGHLIGHT= "#aaee40"
GRN_TOPLINE  = "#e8ff90"
GRN_SHINE    = "#d0f870"
GRN_SHADOW   = "#2a6000"
GRN_SPARKLE  = "#c8ff50"

# --- Geometria ---
W, H     = 420, 80
BAR_TOP  = 36
BAR_BOT  = 54

L_LEFT   = 14
L_RIGHT  = 196
L_WIDTH  = L_RIGHT - L_LEFT   # 182 px

R_LEFT   = 224
R_RIGHT  = 406
R_WIDTH  = R_RIGHT - R_LEFT   # 182 px

# Centro do separador
SEP_CX = (L_RIGHT + R_LEFT) // 2  # 210
SEP_CY = (BAR_TOP + BAR_BOT) // 2  # 45


class BarraIntegral:
    def __init__(self, root):
        self.root = root
        self.root.geometry(f"{W}x{H}")
        self.root.configure(bg=SIMS_BG)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.config(relief=tk.FLAT, bd=0)

        self.canvas = tk.Canvas(
            root, width=W, height=H,
            bg=SIMS_BG, highlightthickness=0, bd=0
        )
        self.canvas.pack()

        self._criar_fundo()
        self.esq = self._criar_metade(L_LEFT, L_RIGHT, YEL_BAR, YEL_GLOW_OUT, YEL_GLOW_MID,
                                      YEL_HIGHLIGHT, YEL_TOPLINE, YEL_SHINE, YEL_SHADOW)
        self.dir = self._criar_metade(R_LEFT, R_RIGHT, GRN_BAR, GRN_GLOW_OUT, GRN_GLOW_MID,
                                      GRN_HIGHLIGHT, GRN_TOPLINE, GRN_SHINE, GRN_SHADOW)
        self._criar_separador()
        self._criar_labels()

        self.shine_l   = -25
        self.shine_r   = -25
        self.larg_esq  = 0
        self.larg_dir  = 0
        self.sparkles  = []

        self.atualizar()
        self.animar()

        self.root.bind('<Button-1>', self.drag_start)
        self.root.bind('<B1-Motion>', self.drag_motion)
        self.drag_data = {'x': 0, 'y': 0}

    # ------------------------------------------------------------------

    def _criar_fundo(self):
        self.canvas.create_rectangle(0, 0, W, H, fill=SIMS_BG, outline="")
        self.canvas.create_rectangle(8, 28, 412, 62, fill=SIMS_PANEL, outline=SIMS_BORDER, width=1)
        self.canvas.create_rectangle(10, 30, 410, 60, fill="#030601", outline="#0e2204")

    def _criar_metade(self, xl, xr, bar, go, gm, hl, tl, sh, sw):
        """Cria as camadas de uma metade da barra e retorna dict de items."""
        self.canvas.create_rectangle(xl, BAR_TOP, xr, BAR_BOT, fill="#020600", outline="")
        items = {
            'glow_out' : self.canvas.create_rectangle(xl, BAR_TOP-4, xl, BAR_BOT+4, fill=go, outline=""),
            'glow_mid' : self.canvas.create_rectangle(xl, BAR_TOP-2, xl, BAR_BOT+2, fill=gm, outline=""),
            'barra'    : self.canvas.create_rectangle(xl, BAR_TOP,   xl, BAR_BOT,   fill=bar, outline=""),
            'shadow'   : self.canvas.create_rectangle(xl, BAR_BOT-4, xl, BAR_BOT,   fill=sw, outline=""),
            'highlight': self.canvas.create_rectangle(xl, BAR_TOP,   xl, BAR_TOP+5, fill=hl, outline=""),
            'topline'  : self.canvas.create_rectangle(xl, BAR_TOP,   xl, BAR_TOP+2, fill=tl, outline=""),
            'edge'     : self.canvas.create_rectangle(0, 0, 0, 0, fill="#ffffff", outline=""),
            'shine'    : self.canvas.create_rectangle(0, 0, 0, 0, fill=sh, outline=""),
            'xl': xl,
        }
        return items

    def _criar_separador(self):
        """Plumbob (diamante) entre as duas metades."""
        cx, cy = SEP_CX, SEP_CY
        s = 9  # meia-diagonal
        # Sombra
        self.canvas.create_polygon(cx, cy-s-1, cx+s+1, cy, cx, cy+s+1, cx-s-1, cy,
                                   fill="#04100a", outline="")
        # Corpo
        self.canvas.create_polygon(cx, cy-s, cx+s, cy, cx, cy+s, cx-s, cy,
                                   fill="#1c3c08", outline="#2e6010", width=1)
        # Miolo
        h = s // 2
        self.canvas.create_polygon(cx, cy-h, cx+h, cy, cx, cy+h, cx-h, cy,
                                   fill="#3a7010", outline="")
        # Brilho
        self.canvas.create_oval(cx-2, cy-s+1, cx+2, cy-s+4, fill="#78d020", outline="")

    def _criar_labels(self):
        self.lbl_perc_esq = self.canvas.create_text(
            L_LEFT, 16, text="0%",
            fill="#c8a800", font=("Verdana", 8, "bold"), anchor="w"
        )
        self.lbl_hora = self.canvas.create_text(
            SEP_CX, 16, text="--:--",
            fill="#3a6010", font=("Verdana", 7), anchor="center"
        )
        self.lbl_perc_dir = self.canvas.create_text(
            R_RIGHT, 16, text="0%",
            fill="#78d020", font=("Verdana", 8, "bold"), anchor="e"
        )
        self.lbl_status = self.canvas.create_text(
            SEP_CX, 70, text="Aguardando início...",
            fill="#2e5a0a", font=("Verdana", 7), anchor="center"
        )

    # ------------------------------------------------------------------

    def _mover_metade(self, items, largura, shine_pos):
        xl = items['xl']
        x2 = xl + largura
        self.canvas.coords(items['glow_out'],  xl, BAR_TOP-4, x2, BAR_BOT+4)
        self.canvas.coords(items['glow_mid'],  xl, BAR_TOP-2, x2, BAR_BOT+2)
        self.canvas.coords(items['barra'],     xl, BAR_TOP,   x2, BAR_BOT)
        self.canvas.coords(items['shadow'],    xl, BAR_BOT-4, x2, BAR_BOT)
        self.canvas.coords(items['highlight'], xl, BAR_TOP,   x2, BAR_TOP+5)
        self.canvas.coords(items['topline'],   xl, BAR_TOP,   x2, BAR_TOP+2)
        if largura > 4:
            self.canvas.coords(items['edge'], x2-3, BAR_TOP-4, x2, BAR_BOT+4)
        else:
            self.canvas.coords(items['edge'], 0, 0, 0, 0)
        # shine
        if largura > 10:
            s1 = max(xl, xl + shine_pos - 18)
            s2 = min(x2, xl + shine_pos + 18)
            if s2 > s1:
                self.canvas.coords(items['shine'], s1, BAR_TOP, s2, BAR_BOT)
                return
        self.canvas.coords(items['shine'], 0, 0, 0, 0)

    def _spawn_sparkle(self, xl, largura, cor):
        if largura < 12:
            return
        x  = xl + random.randint(3, int(largura) - 3)
        y  = random.randint(BAR_TOP + 2, BAR_BOT - 2)
        sz = random.randint(1, 2)
        item = self.canvas.create_oval(x-sz, y-sz, x+sz, y+sz, fill=cor, outline="")
        self.sparkles.append([item, random.randint(6, 18)])

    def animar(self):
        # Avançar shines
        if self.larg_esq > 10:
            self.shine_l += 5
            if self.shine_l > self.larg_esq + 30:
                self.shine_l = -30
        if self.larg_dir > 10:
            self.shine_r += 5
            if self.shine_r > self.larg_dir + 30:
                self.shine_r = -30

        self._mover_metade(self.esq, self.larg_esq, self.shine_l)
        self._mover_metade(self.dir, self.larg_dir, self.shine_r)

        # Sparkles
        if random.random() < 0.20:
            self._spawn_sparkle(L_LEFT, self.larg_esq, YEL_SPARKLE)
        if random.random() < 0.20:
            self._spawn_sparkle(R_LEFT, self.larg_dir, GRN_SPARKLE)

        vivos = []
        for s in self.sparkles:
            s[1] -= 1
            if s[1] <= 0:
                self.canvas.delete(s[0])
            else:
                vivos.append(s)
        self.sparkles = vivos

        self.root.after(50, self.animar)

    def atualizar(self):
        agora  = datetime.now()
        hora   = agora.hour
        minuto = agora.minute
        m      = hora * 60 + minuto

        ini_m = 8 * 60    # 480
        fim_m = 12 * 60   # 720
        ini_t = 13 * 60   # 780
        fim_t = 17 * 60   # 1020

        if m < ini_m:
            perc_esq, perc_dir = 0, 0
            status = "Aguardando início..."
        elif m <= fim_m:
            perc_esq = int(((m - ini_m) / (fim_m - ini_m)) * 100)
            perc_dir = 0
            status = "1ª Metade  •  08:00 – 12:00"
        elif m < ini_t:
            perc_esq, perc_dir = 100, 0
            status = "Intervalo  •  retoma às 13:00"
        elif m <= fim_t:
            perc_esq = 100
            perc_dir = int(((m - ini_t) / (fim_t - ini_t)) * 100)
            status = "2ª Metade  •  13:00 – 17:00"
        else:
            perc_esq, perc_dir = 100, 100
            status = "Concluído!"

        self.larg_esq = (perc_esq / 100) * L_WIDTH
        self.larg_dir = (perc_dir / 100) * R_WIDTH

        self.canvas.itemconfig(self.lbl_perc_esq, text=f"{perc_esq}%")
        self.canvas.itemconfig(self.lbl_perc_dir, text=f"{perc_dir}%")
        self.canvas.itemconfig(self.lbl_hora,     text=f"{hora:02d}:{minuto:02d}")
        self.canvas.itemconfig(self.lbl_status,   text=status)

        self.root.after(1000, self.atualizar)

    # ------------------------------------------------------------------

    def drag_start(self, event):
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def drag_motion(self, event):
        dx = event.x - self.drag_data['x']
        dy = event.y - self.drag_data['y']
        self.root.geometry(f'+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}')


if __name__ == "__main__":
    root = tk.Tk()
    app = BarraIntegral(root)
    root.mainloop()

import tkinter as tk
from datetime import datetime
import random

# ── Paleta ──────────────────────────────────────────────────────────
SIMS_BG     = "#040803"
SIMS_PANEL  = "#060c02"
SIMS_BORDER = "#1c3c08"

GRN = dict(bar="#5ec400", go="#0d2a00", gm="#2d6e00",
           hl="#aaee40", tl="#e8ff90", sh="#d0f870", sw="#2a6000", sp="#c8ff50")
PUR = dict(bar="#8b2fc9", go="#1a0530", gm="#4a1070",
           hl="#cc88ff", tl="#eebbff", sh="#dd99ff", sw="#3a0a60", sp="#cc77ff")

# ── Geometria ───────────────────────────────────────────────────────
W, H           = 400, 80
BAR_LEFT       = 14
BAR_RIGHT      = 386
BAR_TOP, BAR_BOT = 36, 54
BAR_WIDTH      = BAR_RIGHT - BAR_LEFT

ANIM_KEYS = ('glow_out','glow_mid','barra','shadow','highlight','topline','edge','shine')

# ── Estados ─────────────────────────────────────────────────────────
WAITING, ACTIVE, DONE = "waiting", "active", "done"
PURPLE_STATES = {WAITING, DONE}


class BarraWidget:
    def __init__(self, root):
        self.root = root
        self.root.geometry(f"{W}x{H}")
        self.root.configure(bg=SIMS_BG)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.config(relief=tk.FLAT, bd=0)

        self.canvas = tk.Canvas(root, width=W, height=H,
                                bg=SIMS_BG, highlightthickness=0, bd=0)
        self.canvas.pack()

        # Z-order: fundo → grn → pur → labels
        # pur oculto = grn aparece; pur visível = cobre grn
        self._criar_fundo()
        self.grn = self._mk_bar(GRN, with_bg=True)
        self.pur = self._mk_bar(PUR, with_bg=False)
        self._criar_labels()

        self.estado   = WAITING
        self.shine_g  = -25.0
        self.shine_p  = -25.0
        self.largura  = 0.0
        self.sparkles = []

        # Inicia em roxo
        self._set_pur_visible(True)
        self._set_width(self.pur, BAR_WIDTH)

        self.atualizar()
        self.animar()

        self.root.bind('<Button-1>', self.drag_start)
        self.root.bind('<B1-Motion>', self.drag_motion)
        self.drag_data = {'x': 0, 'y': 0}

    # ── Construtores ────────────────────────────────────────────────

    def _criar_fundo(self):
        c = self.canvas
        c.create_rectangle(0, 0, W, H, fill=SIMS_BG, outline="")
        c.create_rectangle(8, 28, 392, 62, fill=SIMS_PANEL, outline=SIMS_BORDER, width=1)
        c.create_rectangle(10, 30, 390, 60, fill="#030601", outline="#0e2204")

    def _mk_bar(self, pal, with_bg):
        c = self.canvas
        if with_bg:
            c.create_rectangle(BAR_LEFT, BAR_TOP, BAR_RIGHT, BAR_BOT, fill="#020600", outline="")
        return dict(
            pal      = pal,
            glow_out =c.create_rectangle(BAR_LEFT, BAR_TOP-4, BAR_LEFT, BAR_BOT+4, fill=pal['go'], outline=""),
            glow_mid =c.create_rectangle(BAR_LEFT, BAR_TOP-2, BAR_LEFT, BAR_BOT+2, fill=pal['gm'], outline=""),
            barra    =c.create_rectangle(BAR_LEFT, BAR_TOP,   BAR_LEFT, BAR_BOT,   fill=pal['bar'], outline=""),
            shadow   =c.create_rectangle(BAR_LEFT, BAR_BOT-4, BAR_LEFT, BAR_BOT,   fill=pal['sw'], outline=""),
            highlight=c.create_rectangle(BAR_LEFT, BAR_TOP,   BAR_LEFT, BAR_TOP+5, fill=pal['hl'], outline=""),
            topline  =c.create_rectangle(BAR_LEFT, BAR_TOP,   BAR_LEFT, BAR_TOP+2, fill=pal['tl'], outline=""),
            edge     =c.create_rectangle(0, 0, 0, 0, fill="#ffffff", outline=""),
            shine    =c.create_rectangle(0, 0, 0, 0, fill=pal['sh'], outline=""),
        )

    def _criar_labels(self):
        c = self.canvas
        self.lbl_perc   = c.create_text(BAR_LEFT, 16, text="",     fill="#78d020",
                                         font=("Verdana", 8, "bold"), anchor="w")
        self.lbl_hora   = c.create_text(BAR_RIGHT, 16, text="--:--", fill="#9060c0",
                                         font=("Verdana", 8), anchor="e")
        self.lbl_status = c.create_text(W//2, 70, text="...",       fill="#2e5a0a",
                                         font=("Verdana", 7), anchor="center")

    # ── Visibilidade ────────────────────────────────────────────────

    def _set_pur_visible(self, show):
        st = 'normal' if show else 'hidden'
        for k in ANIM_KEYS:
            self.canvas.itemconfig(self.pur[k], state=st)

    # ── Geometria ───────────────────────────────────────────────────

    def _set_width(self, bar, largura):
        x2 = BAR_LEFT + largura
        c  = self.canvas
        c.coords(bar['glow_out'],  BAR_LEFT, BAR_TOP-4, x2, BAR_BOT+4)
        c.coords(bar['glow_mid'],  BAR_LEFT, BAR_TOP-2, x2, BAR_BOT+2)
        c.coords(bar['barra'],     BAR_LEFT, BAR_TOP,   x2, BAR_BOT)
        c.coords(bar['shadow'],    BAR_LEFT, BAR_BOT-4, x2, BAR_BOT)
        c.coords(bar['highlight'], BAR_LEFT, BAR_TOP,   x2, BAR_TOP+5)
        c.coords(bar['topline'],   BAR_LEFT, BAR_TOP,   x2, BAR_TOP+2)

    def _set_anim(self, bar, largura, shine_pos, ativo):
        x2 = BAR_LEFT + largura
        c  = self.canvas
        if ativo and largura > 4:
            c.coords(bar['edge'], x2-3, BAR_TOP-4, x2, BAR_BOT+4)
        else:
            c.coords(bar['edge'], 0, 0, 0, 0)
        if ativo and largura > 10:
            s1 = max(BAR_LEFT, BAR_LEFT + shine_pos - 18)
            s2 = min(x2, BAR_LEFT + shine_pos + 18)
            if s2 > s1:
                c.coords(bar['shine'], s1, BAR_TOP, s2, BAR_BOT)
                return
        c.coords(bar['shine'], 0, 0, 0, 0)

    # ── Animação ────────────────────────────────────────────────────

    def _spawn(self, largura, cor):
        if largura < 12:
            return
        x  = BAR_LEFT + random.randint(3, int(largura) - 3)
        y  = random.randint(BAR_TOP + 2, BAR_BOT - 2)
        sz = random.randint(1, 2)
        item = self.canvas.create_oval(x-sz, y-sz, x+sz, y+sz, fill=cor, outline="")
        self.sparkles.append([item, random.randint(6, 18)])

    def animar(self):
        e      = self.estado
        purple = e in PURPLE_STATES

        if e == ACTIVE:
            self.shine_g += 5
            if self.shine_g > self.largura + 30: self.shine_g = -30
            if random.random() < 0.22: self._spawn(self.largura, GRN['sp'])
        elif purple:
            self.shine_p += 5
            if self.shine_p > BAR_WIDTH + 30: self.shine_p = -30
            if random.random() < 0.20: self._spawn(BAR_WIDTH, PUR['sp'])

        self._set_anim(self.grn, self.largura,  self.shine_g, e == ACTIVE)
        self._set_anim(self.pur, BAR_WIDTH,     self.shine_p, purple)

        vivos = []
        for s in self.sparkles:
            s[1] -= 1
            if s[1] <= 0:
                self.canvas.delete(s[0])
            else:
                vivos.append(s)
        self.sparkles = vivos

        self.root.after(50, self.animar)

    # ── Lógica de tempo ─────────────────────────────────────────────

    def atualizar(self):
        agora        = datetime.now()
        hora, minuto = agora.hour, agora.minute
        m            = hora * 60 + minuto

        inicio  = 13 * 60
        fim     = 16 * 60 + 50
        duracao = fim - inicio

        ant = self.estado

        if m < inicio:
            self.estado  = WAITING
            percentual   = 0
            status       = "Aguardando início  •  aula começa às 13:00"
        elif m >= fim:
            self.estado  = DONE
            percentual   = 100
            status       = "Concluído!"
        else:
            self.estado  = ACTIVE
            percentual   = int(((m - inicio) / duracao) * 100)
            status       = "Carregando...  •  13:00 – 16:50"

        if self.estado != ant:
            for s in self.sparkles: self.canvas.delete(s[0])
            self.sparkles = []

        purple = self.estado in PURPLE_STATES

        self.largura = (percentual / 100) * BAR_WIDTH
        self._set_width(self.grn, self.largura)
        self._set_width(self.pur, BAR_WIDTH)

        self._set_pur_visible(purple)

        c = self.canvas
        if purple:
            c.itemconfig(self.lbl_perc, text="")
            c.itemconfig(self.lbl_hora, fill="#9060c0")
        else:
            c.itemconfig(self.lbl_perc, text=f"{percentual}%")
            c.itemconfig(self.lbl_hora, fill="#4a8015")

        c.itemconfig(self.lbl_hora,   text=f"{hora:02d}:{minuto:02d}")
        c.itemconfig(self.lbl_status, text=status)

        self.root.after(1000, self.atualizar)

    # ── Drag ────────────────────────────────────────────────────────

    def drag_start(self, event):
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def drag_motion(self, event):
        dx = event.x - self.drag_data['x']
        dy = event.y - self.drag_data['y']
        self.root.geometry(f'+{self.root.winfo_x() + dx}+{self.root.winfo_y() + dy}')


if __name__ == "__main__":
    root = tk.Tk()
    app = BarraWidget(root)
    root.mainloop()

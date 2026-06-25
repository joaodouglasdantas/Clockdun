import tkinter as tk
from datetime import datetime
import random

# ── Paleta ──────────────────────────────────────────────────────────
SIMS_BG     = "#040803"
SIMS_PANEL  = "#060c02"
SIMS_BORDER = "#1c3c08"

YEL = dict(bar="#d4b800", go="#2a2200", gm="#5e4e00",
           hl="#fff080", tl="#ffffc0", sh="#ffff90", sw="#604e00", sp="#ffe050")
GRN = dict(bar="#5ec400", go="#0d2a00", gm="#2d6e00",
           hl="#aaee40", tl="#e8ff90", sh="#d0f870", sw="#2a6000", sp="#c8ff50")
PUR = dict(bar="#8b2fc9", go="#1a0530", gm="#4a1070",
           hl="#cc88ff", tl="#eebbff", sh="#dd99ff", sw="#3a0a60", sp="#cc77ff")

# ── Estados ─────────────────────────────────────────────────────────
WAITING, MORNING, BREAK, AFTERNOON, DONE = "waiting","morning","break","afternoon","done"
PURPLE_STATES = {WAITING, BREAK, DONE}

MINI_H = 8

# ── Geometria ───────────────────────────────────────────────────────
W, H           = 420, 80
BAR_TOP, BAR_BOT = 36, 54

L_LEFT, L_RIGHT = 14, 196
R_LEFT, R_RIGHT = 224, 406
L_WIDTH = L_RIGHT - L_LEFT   # 182 px
R_WIDTH = R_RIGHT - R_LEFT   # 182 px

P_LEFT, P_RIGHT = L_LEFT, R_RIGHT
P_WIDTH = P_RIGHT - P_LEFT   # 392 px

SEP_CX = (L_RIGHT + R_LEFT) // 2   # 210
SEP_CY = (BAR_TOP + BAR_BOT) // 2  # 45

ANIM_KEYS = ('glow_out','glow_mid','barra','shadow','highlight','topline','edge','shine')


class BarraIntegral:
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

        # Z-order de criação: fundo → esq → dir → sep → pur → labels
        # pur acima de esq/dir; pur oculto = esq/dir aparecem; sep oculto durante roxo
        self._criar_fundo()
        self.esq = self._mk_half(L_LEFT, L_RIGHT, YEL, with_bg=True)
        self.dir = self._mk_half(R_LEFT, R_RIGHT, GRN, with_bg=True)
        self.sep = self._criar_sep()
        self.pur = self._mk_half(P_LEFT, P_RIGHT, PUR, with_bg=False)
        self._criar_labels()
        self._criar_mini()

        self.estado     = WAITING
        self.shine_l    = -25.0
        self.shine_r    = -25.0
        self.shine_p    = -25.0
        self.larg_esq   = 0.0
        self.larg_dir   = 0.0
        self.sparkles   = []
        self.minimizado = False

        # Estado inicial roxo
        self._set_pur_visible(True)
        self._set_sep_visible(False)
        self._set_width(self.pur, P_WIDTH)

        self.atualizar()
        self.animar()

        self.root.bind('<Button-1>', self.drag_start)
        self.root.bind('<B1-Motion>', self.drag_motion)
        self.root.bind('<Button-3>', self.toggle_mini)
        self.drag_data = {'x': 0, 'y': 0}

    # ── Construtores ────────────────────────────────────────────────

    def _criar_mini(self):
        """Faixa fina (MINI_H px) exibida quando minimizado.
        Lado esquerdo = amarelo (manhã), lado direito = verde (tarde).
        Durante roxo: barra roxa full width."""
        c = self.canvas
        mid = W // 2
        self.mini_fundo  = c.create_rectangle(0, 0, W,   MINI_H, fill="#04080a", outline="", state='hidden')
        self.mini_bar_esq= c.create_rectangle(0, 0, 0,   MINI_H, fill=YEL['bar'], outline="", state='hidden')
        self.mini_bar_dir= c.create_rectangle(mid, 0, mid, MINI_H, fill=GRN['bar'], outline="", state='hidden')
        self.mini_bar_pur= c.create_rectangle(0, 0, 0,   MINI_H, fill=PUR['bar'], outline="", state='hidden')

    def _criar_fundo(self):
        c = self.canvas
        c.create_rectangle(0, 0, W, H, fill=SIMS_BG, outline="")
        c.create_rectangle(8, 28, 412, 62, fill=SIMS_PANEL, outline=SIMS_BORDER, width=1)
        c.create_rectangle(10, 30, 410, 60, fill="#030601", outline="#0e2204")

    def _mk_half(self, xl, xr, pal, with_bg):
        c = self.canvas
        if with_bg:
            c.create_rectangle(xl, BAR_TOP, xr, BAR_BOT, fill="#020600", outline="")
        return dict(
            xl=xl, xr=xr, pal=pal,
            glow_out =c.create_rectangle(xl, BAR_TOP-4, xl, BAR_BOT+4, fill=pal['go'], outline=""),
            glow_mid =c.create_rectangle(xl, BAR_TOP-2, xl, BAR_BOT+2, fill=pal['gm'], outline=""),
            barra    =c.create_rectangle(xl, BAR_TOP,   xl, BAR_BOT,   fill=pal['bar'], outline=""),
            shadow   =c.create_rectangle(xl, BAR_BOT-4, xl, BAR_BOT,   fill=pal['sw'], outline=""),
            highlight=c.create_rectangle(xl, BAR_TOP,   xl, BAR_TOP+5, fill=pal['hl'], outline=""),
            topline  =c.create_rectangle(xl, BAR_TOP,   xl, BAR_TOP+2, fill=pal['tl'], outline=""),
            edge     =c.create_rectangle(0, 0, 0, 0, fill="#ffffff", outline=""),
            shine    =c.create_rectangle(0, 0, 0, 0, fill=pal['sh'], outline=""),
        )

    def _criar_sep(self):
        c, cx, cy, s = self.canvas, SEP_CX, SEP_CY, 9
        h = s // 2
        return [
            c.create_polygon(cx, cy-s-1, cx+s+1, cy, cx, cy+s+1, cx-s-1, cy,
                             fill="#04100a", outline=""),
            c.create_polygon(cx, cy-s, cx+s, cy, cx, cy+s, cx-s, cy,
                             fill="#1c3c08", outline="#2e6010", width=1),
            c.create_polygon(cx, cy-h, cx+h, cy, cx, cy+h, cx-h, cy,
                             fill="#3a7010", outline=""),
            c.create_oval(cx-2, cy-s+1, cx+2, cy-s+4, fill="#78d020", outline=""),
        ]

    def _criar_labels(self):
        c = self.canvas
        self.lbl_esq    = c.create_text(L_LEFT,  16, text="", fill="#c8a800",
                                         font=("Verdana", 8, "bold"), anchor="w")
        self.lbl_hora   = c.create_text(SEP_CX,  16, text="--:--", fill="#9060c0",
                                         font=("Verdana", 7), anchor="center")
        self.lbl_dir    = c.create_text(R_RIGHT, 16, text="", fill="#78d020",
                                         font=("Verdana", 8, "bold"), anchor="e")
        self.lbl_status = c.create_text(SEP_CX,  70, text="...", fill="#2e5a0a",
                                         font=("Verdana", 7), anchor="center")

    # ── Mini mode ───────────────────────────────────────────────────

    def toggle_mini(self, event=None):
        self.minimizado = not self.minimizado
        st = 'normal' if self.minimizado else 'hidden'
        for item in (self.mini_fundo, self.mini_bar_esq, self.mini_bar_dir, self.mini_bar_pur):
            self.canvas.itemconfig(item, state=st)
        x, y = self.root.winfo_x(), self.root.winfo_y()
        if self.minimizado:
            self.root.geometry(f"{W}x{MINI_H}+{x}+{y + H - MINI_H}")
        else:
            self.root.geometry(f"{W}x{H}+{x}+{y - H + MINI_H}")

    def _atualizar_mini(self, pe, pd, purple):
        mid = W // 2
        if purple:
            self.canvas.coords(self.mini_bar_pur, 0, 0, W, MINI_H)
            self.canvas.coords(self.mini_bar_esq, 0, 0, 0, MINI_H)
            self.canvas.coords(self.mini_bar_dir, mid, 0, mid, MINI_H)
        else:
            self.canvas.coords(self.mini_bar_pur, 0, 0, 0, MINI_H)
            # Esquerda: amarelo, 0..mid proporcional a pe
            esq_w = (pe / 100) * mid
            self.canvas.coords(self.mini_bar_esq, 0, 0, esq_w, MINI_H)
            # Direita: verde, mid..W proporcional a pd
            dir_w = (pd / 100) * mid
            self.canvas.coords(self.mini_bar_dir, mid, 0, mid + dir_w, MINI_H)

    # ── Visibilidade ────────────────────────────────────────────────

    def _set_pur_visible(self, show):
        st = 'normal' if show else 'hidden'
        for k in ANIM_KEYS:
            self.canvas.itemconfig(self.pur[k], state=st)

    def _set_sep_visible(self, show):
        st = 'normal' if show else 'hidden'
        for item in self.sep:
            self.canvas.itemconfig(item, state=st)

    # ── Geometria dos halves ─────────────────────────────────────────

    def _set_width(self, half, largura):
        xl, x2 = half['xl'], half['xl'] + largura
        c = self.canvas
        c.coords(half['glow_out'],  xl, BAR_TOP-4, x2, BAR_BOT+4)
        c.coords(half['glow_mid'],  xl, BAR_TOP-2, x2, BAR_BOT+2)
        c.coords(half['barra'],     xl, BAR_TOP,   x2, BAR_BOT)
        c.coords(half['shadow'],    xl, BAR_BOT-4, x2, BAR_BOT)
        c.coords(half['highlight'], xl, BAR_TOP,   x2, BAR_TOP+5)
        c.coords(half['topline'],   xl, BAR_TOP,   x2, BAR_TOP+2)

    def _set_anim(self, half, largura, shine_pos, ativo):
        """Atualiza shine e edge branca. ativo=False zera ambos."""
        xl, x2 = half['xl'], half['xl'] + largura
        c = self.canvas
        if ativo and largura > 4:
            c.coords(half['edge'], x2-3, BAR_TOP-4, x2, BAR_BOT+4)
        else:
            c.coords(half['edge'], 0, 0, 0, 0)
        if ativo and largura > 10:
            s1 = max(xl, xl + shine_pos - 18)
            s2 = min(x2, xl + shine_pos + 18)
            if s2 > s1:
                c.coords(half['shine'], s1, BAR_TOP, s2, BAR_BOT)
                return
        c.coords(half['shine'], 0, 0, 0, 0)

    # ── Animação ────────────────────────────────────────────────────

    def _spawn(self, xl, larg, cor):
        if larg < 12:
            return
        x  = xl + random.randint(3, int(larg) - 3)
        y  = random.randint(BAR_TOP + 2, BAR_BOT - 2)
        sz = random.randint(1, 2)
        item = self.canvas.create_oval(x-sz, y-sz, x+sz, y+sz, fill=cor, outline="")
        self.sparkles.append([item, random.randint(6, 18)])

    def animar(self):
        e = self.estado
        purple = e in PURPLE_STATES

        if e == MORNING:
            self.shine_l += 5
            if self.shine_l > self.larg_esq + 30: self.shine_l = -30
            if random.random() < 0.20: self._spawn(L_LEFT, self.larg_esq, YEL['sp'])
        elif e == AFTERNOON:
            self.shine_r += 5
            if self.shine_r > self.larg_dir + 30: self.shine_r = -30
            if random.random() < 0.20: self._spawn(R_LEFT, self.larg_dir, GRN['sp'])
        elif purple:
            self.shine_p += 5
            if self.shine_p > P_WIDTH + 30: self.shine_p = -30
            if random.random() < 0.20: self._spawn(P_LEFT, P_WIDTH, PUR['sp'])

        # Shine e edge: só na metade ativa
        self._set_anim(self.esq, self.larg_esq, self.shine_l, e == MORNING)
        self._set_anim(self.dir, self.larg_dir,  self.shine_r, e == AFTERNOON)
        self._set_anim(self.pur, P_WIDTH,         self.shine_p, purple)

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

        ini_m, fim_m = 8*60,  12*60
        ini_t, fim_t = 13*60, 17*60

        ant = self.estado

        if m < ini_m:
            self.estado = WAITING
            pe, pd = 0, 0
            status = "Aguardando início  •  aula começa às 08:00"
        elif m <= fim_m:
            self.estado = MORNING
            pe = int(((m - ini_m) / (fim_m - ini_m)) * 100)
            pd = 0
            status = "1ª Metade  •  08:00 – 12:00"
        elif m < ini_t:
            self.estado = BREAK
            pe, pd = 100, 0
            status = "Intervalo  •  retoma às 13:00"
        elif m <= fim_t:
            self.estado = AFTERNOON
            pe = 100
            pd = int(((m - ini_t) / (fim_t - ini_t)) * 100)
            status = "2ª Metade  •  13:00 – 17:00"
        else:
            self.estado = DONE
            pe, pd = 100, 100
            status = "Concluído!"

        if self.estado != ant:
            for s in self.sparkles: self.canvas.delete(s[0])
            self.sparkles = []

        purple = self.estado in PURPLE_STATES

        self.larg_esq = (pe / 100) * L_WIDTH
        self.larg_dir = (pd / 100) * R_WIDTH

        self._set_width(self.esq, self.larg_esq)
        self._set_width(self.dir, self.larg_dir)
        self._set_width(self.pur, P_WIDTH)

        self._set_pur_visible(purple)
        self._set_sep_visible(not purple)
        self._atualizar_mini(pe, pd, purple)

        c = self.canvas
        if purple:
            c.itemconfig(self.lbl_esq,  text="")
            c.itemconfig(self.lbl_dir,  text="")
            c.itemconfig(self.lbl_hora, fill="#9060c0")
        else:
            c.itemconfig(self.lbl_esq,  text=f"{pe}%")
            c.itemconfig(self.lbl_dir,  text=f"{pd}%")
            c.itemconfig(self.lbl_hora, fill="#3a6010")

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
    app = BarraIntegral(root)
    root.mainloop()

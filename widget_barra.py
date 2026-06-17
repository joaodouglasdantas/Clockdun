import tkinter as tk
from datetime import datetime
import math

class BarraWidget:
    def __init__(self, root):
        self.root = root
        self.root.geometry("380x50")
        self.root.configure(bg="#0f1419")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove barra de título
        self.root.resizable(False, False)

        # Remove borda padrão
        self.root.config(relief=tk.FLAT, bd=0)

        # Frame principal com gradient simulado
        main_frame = tk.Frame(root, bg="#0f1419")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Container com padding
        container = tk.Frame(main_frame, bg="#0f1419", padx=8, pady=6)
        container.pack(fill=tk.BOTH, expand=True)


        # Barra principal com canvas
        barra_bg = tk.Frame(container, bg="#1a1f26", height=12)
        barra_bg.pack(fill=tk.X, pady=(0, 4), ipady=3)
        barra_bg.pack_propagate(False)

        # Canvas para barra com gradiente
        self.canvas = tk.Canvas(
            barra_bg,
            width=364,
            height=10,
            bg="#1a1f26",
            highlightthickness=0,
            relief=tk.FLAT,
            bd=0
        )
        self.canvas.pack(padx=0, pady=1)

        # Barra de progresso (gradiente de verde/grama)
        self.barra_rect = self.canvas.create_rectangle(
            0, 0, 0, 10,
            fill="#2d5016",
            outline="#2d5016"
        )

        # Brilho dinâmico para animação
        self.barra_shine = self.canvas.create_rectangle(
            0, 0, 20, 10,
            fill="#7ec850",
            outline="#7ec850"
        )

        # Info frame com estatísticas
        info_frame = tk.Frame(container, bg="#0f1419")
        info_frame.pack(fill=tk.X, pady=(2, 0))

        # Percentual
        self.label_percentual = tk.Label(
            info_frame,
            text="0%",
            font=("Helvetica", 10, "bold"),
            bg="#0f1419",
            fg="#4a7c2d"
        )
        self.label_percentual.pack(side=tk.LEFT)

        # Hora
        self.label_hora = tk.Label(
            info_frame,
            text="--:--",
            font=("Helvetica", 9),
            bg="#0f1419",
            fg="#888888"
        )
        self.label_hora.pack(side=tk.RIGHT)

        # Animação de brilho
        self.shine_pos = 0
        self.shine_direction = 1
        self.largura_barra_atual = 0

        # Começar a atualizar
        self.atualizar()
        self.animar_brilho()

        # Permitir arrastar a janela
        self.root.bind('<Button-1>', self.drag_start)
        self.root.bind('<B1-Motion>', self.drag_motion)
        self.drag_data = {'x': 0, 'y': 0}

    def animar_brilho(self):
        """Anima o brilho se movendo apenas na parte preenchida"""
        # Só animar se há progresso
        if self.largura_barra_atual <= 0:
            self.canvas.coords(self.barra_shine, 0, 0, 0, 10)
            self.root.after(50, self.animar_brilho)
            return

        # Atualizar posição do brilho
        self.shine_pos += self.shine_direction * 6

        # Inverter direção ao chegar nas extremidades da barra preenchida
        if self.shine_pos > self.largura_barra_atual - 30 or self.shine_pos < 0:
            self.shine_direction *= -1

        # Colocar o brilho dentro dos limites da barra preenchida
        self.shine_pos = max(0, min(self.shine_pos, self.largura_barra_atual - 20))

        # Atualizar posição do brilho no canvas (só dentro da barra preenchida)
        self.canvas.coords(
            self.barra_shine,
            self.shine_pos, 0,
            min(self.shine_pos + 30, self.largura_barra_atual), 10
        )

        # Agendar próxima animação
        self.root.after(50, self.animar_brilho)

    def drag_start(self, event):
        self.drag_data['x'] = event.x
        self.drag_data['y'] = event.y

    def drag_motion(self, event):
        delta_x = event.x - self.drag_data['x']
        delta_y = event.y - self.drag_data['y']
        x = self.root.winfo_x() + delta_x
        y = self.root.winfo_y() + delta_y
        self.root.geometry(f'+{x}+{y}')

    def atualizar(self):
        agora = datetime.now()
        hora = agora.hour
        minuto = agora.minute

        minuto_atual = hora * 60 + minuto
        inicio = 13 * 60  # 13:00
        fim = 16 * 60 + 50  # 16:50
        duracao = fim - inicio

        # Hora formatada
        hora_str = f"{hora:02d}:{minuto:02d}"
        self.label_hora.config(text=hora_str)

        # Calcular percentual
        if minuto_atual < inicio:
            percentual = 0
            cor_texto = "#888888"
        elif minuto_atual >= fim:
            percentual = 100
            cor_texto = "#4a9d83"
        else:
            tempo_decorrido = minuto_atual - inicio
            percentual = int((tempo_decorrido / duracao) * 100)
            cor_texto = "#6ba644"

        # Atualizar barra (largura máxima é 364)
        largura_barra = (percentual / 100) * 364
        self.largura_barra_atual = largura_barra
        self.canvas.coords(self.barra_rect, 0, 0, largura_barra, 10)

        # Gradiente de cor conforme progride
        if percentual <= 100:
            r = int(45 + (107 - 45) * (percentual / 100))
            g = int(80 + (166 - 80) * (percentual / 100))
            b = int(22 + (68 - 22) * (percentual / 100))
            cor_dinamica = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.itemconfig(self.barra_rect, fill=cor_dinamica)

        # Atualizar labels
        self.label_percentual.config(text=f"{percentual}%", fg=cor_texto)

        # Agendar próxima atualização
        self.root.after(1000, self.atualizar)

if __name__ == "__main__":
    root = tk.Tk()
    app = BarraWidget(root)
    root.mainloop()

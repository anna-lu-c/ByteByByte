# confetti.py
import random
from tkinter import Canvas
from app.core.config import COLORS, current_theme


class Confetti:
    def __init__(self, parent):
        self.parent = parent
        bg_color = COLORS[current_theme]["bg"]
        self.canvas = Canvas(parent, highlightthickness=0, bg=bg_color)
        self.canvas.place(x=0, y=0, width=parent.winfo_width(), height=parent.winfo_height())
        self.particles = []
        for _ in range(80):
            x = random.randint(0, parent.winfo_width())
            y = random.randint(-100, -20)
            size = random.randint(4, 8)
            color = random.choice(["#10b981", "#8b5cf6", "#3b82f6", "#f59e0b"])
            vx = random.uniform(-2, 2)
            vy = random.uniform(3, 8)
            self.particles.append([x, y, size, color, vx, vy])
        self.animate()
        parent.after(2500, self.destroy)

    def animate(self):
        for p in self.particles:
            p[0] += p[4]
            p[1] += p[5]
            if p[1] > self.parent.winfo_height():
                p[1] = -20
                p[0] = random.randint(0, self.parent.winfo_width())
            self.canvas.create_rectangle(p[0], p[1], p[0]+p[2], p[1]+p[2],
                                         fill=p[3], outline="")
        self.parent.after(30, self.animate)

    def destroy(self):
        self.canvas.destroy()

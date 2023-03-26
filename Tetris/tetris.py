import tkinter as tk
import random
from threading import Lock

root = tk.Tk()



COULEUR_BLOC = ['gray', 'lightgreen', 'pink', 'blue', 'orange', 'purple']


# -------------------------------------------- GENERATION DES TETROMINOS -------------------------------------------- #
class Tetris():
    FIELD_HEIGHT = 20
    FIELD_WIDTH = 10
    SCORE_PER_ELIMINATED_LINES = (0, 40, 100, 300, 1200)
    TETROMINOS = [
        [(0, 0), (0, 1), (1, 0), (1,1)], 
        [(0, 0), (0, 1), (1, 1), (2,1)], 
        [(0, 1), (1, 1), (2, 1), (2,0)],  
        [(0, 1), (1, 0), (1, 1), (2,0)], 
        [(0, 1), (1, 0), (1, 1), (2,1)], 
        [(0, 0), (1, 0), (1, 1), (2,1)], 
        [(0, 1), (1, 1), (2, 1), (3,1)], 
    ]
# ------------------------------------------------------------------------------------------------------------------ #




# ------------ INITIALISE LES VARIABLES TELLES QUE LE TERRAIN, LE SCORE, LE NIEAU, LES LIGNES ELIMINEES ------------- #
    def __init__(self):
        self.field = [[0 for c in range(Tetris.FIELD_WIDTH)] for r in range(Tetris.FIELD_HEIGHT)]
        self.score = 0
        self.level = 0
        self.total_lines_eliminated = 0
        self.game_over = False
        self.move_lock = Lock()
        self.nouveau_tetrominos()
# ------------------------------------------------------------------------------------------------------------------ #





# -------------------------------------------- SPAWN UN AUTRE TETROMINOS -------------------------------------------- #
    def nouveau_tetrominos(self):
        self.tetromino = random.choice(Tetris.TETROMINOS)[:]
        self.tetromino_color = random.randint(1, len(COULEUR_BLOC)-1)
        self.tetromino_offset = [-2, Tetris.FIELD_WIDTH//2]
        self.game_over = any(not self.place_libre(r, c) for (r, c) in self.get_tetromino_coords())
# ------------------------------------------------------------------------------------------------------------------ #




# ----------------------- RENVOIE LES COORDONNES DES TETROMINOS ACTUEL SUR LE TERRAIN DE JEU.----------------------- #
    def get_tetromino_coords(self):
        return [(r+self.tetromino_offset[0], c + self.tetromino_offset[1]) for (r, c) in self.tetromino]
# ------------------------------------------------------------------------------------------------------------------ #




# ------MET A JOUR LE TERRAIN, AJOUTE DES NOUVEAU TETROMINOS, ELIMINE LES LIGNES COMPLETE, MET A JOUR LE SCORE------ #
    def ajout_tetrominos(self):
        for (r, c) in self.get_tetromino_coords():
            self.field[r][c] = self.tetromino_color

        new_field = [row for row in self.field if any(tile == 0 for tile in row)]
        lines_eliminated = len(self.field)-len(new_field)
        self.total_lines_eliminated += lines_eliminated
        self.field = [[0]*Tetris.FIELD_WIDTH for x in range(lines_eliminated)] + new_field
        self.score += Tetris.SCORE_PER_ELIMINATED_LINES[lines_eliminated] * (self.level + 1)
        self.level = self.total_lines_eliminated // 10
        self.nouveau_tetrominos()
# ----------------------------------------------------------------------------------------------------------------- #





# ---------------------------------- RENVOIE LA COULEUR D'UNE CELLULE SUR LE TERRAIN ------------------------------ #
    def get_color(self, r, c):
        return self.tetromino_color if (r, c) in self.get_tetromino_coords() else self.field[r][c]
# ----------------------------------------------------------------------------------------------------------------- #




# -------------------------------- VERIFIE SI LA PLACE SUR LE TERRAIN EST LIBRE OU NON ---------------------------- #
    def place_libre(self, r, c):
        return r < Tetris.FIELD_HEIGHT and 0 <= c < Tetris.FIELD_WIDTH and (r < 0 or self.field[r][c] == 0)
# ----------------------------------------------------------------------------------------------------------------- #




# --------------------- DEPLACE LES TETROMINOS DANS UNE DIRECTION, VERIFIE SI LE JEU EST TERMINE ------------------ #
    def move(self, dr, dc):
        with self.move_lock:
            if self.game_over:
                return

            if all(self.place_libre(r + dr, c + dc) for (r, c) in self.get_tetromino_coords()):
                self.tetromino_offset = [self.tetromino_offset[0] + dr, self.tetromino_offset[1] + dc]
            elif dr == 1 and dc == 0:
                self.game_over = any(r < 0 for (r, c) in self.get_tetromino_coords())
                if not self.game_over:
                    self.ajout_tetrominos()
# ----------------------------------------------------------------------------------------------------------------- #






# ------------------------------- RETOURNE LE TETROMINOS, VERIFIE SI LE JEU EST TERMINE --------------------------- #
    def rotation(self):
        with self.move_lock:
            if self.game_over:
                self.__init__()
                return

            ys = [r for (r, c) in self.tetromino]
            xs = [c for (r, c) in self.tetromino]
            size = max(max(ys) - min(ys), max(xs)-min(xs))
            rotated_tetromino = [(c, size-r) for (r, c) in self.tetromino]
            wallkick_offset = self.tetromino_offset[:]
            tetromino_coord = [(r+wallkick_offset[0], c + wallkick_offset[1]) for (r, c) in rotated_tetromino]
            min_x = min(c for r, c in tetromino_coord)
            max_x = max(c for r, c in tetromino_coord)
            max_y = max(r for r, c in tetromino_coord)
            wallkick_offset[1] -= min(0, min_x)
            wallkick_offset[1] += min(0, Tetris.FIELD_WIDTH - (1 + max_x))
            wallkick_offset[0] += min(0, Tetris.FIELD_HEIGHT - (1 + max_y))

            tetromino_coord = [(r+wallkick_offset[0], c + wallkick_offset[1]) for (r, c) in rotated_tetromino]
            if all(self.place_libre(r, c) for (r, c) in tetromino_coord):
                self.tetromino, self.tetromino_offset = rotated_tetromino, wallkick_offset
# ----------------------------------------------------------------------------------------------------------------- #




class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.tetris = Tetris()
        self.pack()
        self.create_widgets()
        self.update_clock()

    def update_clock(self):
        self.tetris.move(1, 0)
        self.update()  
        self.master.after(int(1000*(0.66**self.tetris.level)), self.update_clock)
    
    def create_widgets(self):
        PIECE_SIZE = 30
        self.canvas = tk.Canvas(self, height=PIECE_SIZE*self.tetris.FIELD_HEIGHT, 
                                      width = PIECE_SIZE*self.tetris.FIELD_WIDTH, bg="black", bd=0)
        self.canvas.bind('<Left>', lambda _: (self.tetris.move(0, -1), self.update()))
        self.canvas.bind('<Right>', lambda _: (self.tetris.move(0, 1), self.update()))
        self.canvas.bind('<Down>', lambda _: (self.tetris.move(1, 0), self.update()))
        self.canvas.bind('<Up>', lambda _: (self.tetris.rotation(), self.update()))
        self.canvas.focus_set()
        self.rectangles = [
            self.canvas.create_rectangle(c*PIECE_SIZE, r*PIECE_SIZE, (c+1)*PIECE_SIZE, (r+1)*PIECE_SIZE)
                for r in range(self.tetris.FIELD_HEIGHT) for c in range(self.tetris.FIELD_WIDTH)
        ]
        self.canvas.pack(side="left")
        self.status_msg = tk.Label(self, anchor='w', width=11, font=("Courier", 24))
        self.status_msg.pack(side="top")
        self.game_over_msg = tk.Label(self, anchor='w', width=11, font=("Courier", 24), fg='red')
        self.game_over_msg.pack(side="top")
    
    def update(self):
        for i, _id in enumerate(self.rectangles):
            color_num = self.tetris.get_color(i//self.tetris.FIELD_WIDTH, i % self.tetris.FIELD_WIDTH)
            self.canvas.itemconfig(_id, fill=COULEUR_BLOC[color_num])
    
        self.status_msg['text'] = "Score: {}\nNiveau: {}".format(self.tetris.score, self.tetris.level)
        self.game_over_msg['text'] = "GAME OVER.\nflèche\n du haut\nPour\n relancer\n une partie" if self.tetris.game_over else ""

app = Application(master=root) 
app.mainloop()
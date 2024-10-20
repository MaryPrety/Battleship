import tkinter as tk
from tkinter import messagebox
import random

# Инициализация окна
root = tk.Tk()
root.title("Морской бой")

# Цвета
FIELD_COLOR = "#FEFDED"
LINE_COLOR = "#C6EBC5"
SHIP_COLOR = "#A1C398"
HIT_COLOR = "#FA7070"
MISS_COLOR = "#F0F0F0"

# Размеры поля
GRID_SIZE = 7
CELL_SIZE = 50

# Поля
player_field = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
ai_field = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
ai_visible_field = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

# Состояние игры
player_turn = True
game_over = False
player_shots = 0
ai_shots = 0
history = []  # История выстрелов

# Корабли
ships = [3, 2, 1]  # Три корабля: 3 клетки, 2 клетки, 1 клетка
current_ship_index = 0  # Индекс текущего корабля для ручного режима
ship_orientation = 'horizontal'  # Ориентация текущего корабля
ship_placement_mode = False  # Флаг режима расстановки

# Статистика
player_remaining_ships = sum(ships)  # Общее количество клеток кораблей у игрока
ai_remaining_ships = sum(ships)  # Общее количество клеток кораблей у ИИ

# Отображение
canvas = tk.Canvas(root, width=GRID_SIZE * CELL_SIZE * 2 + 60, height=GRID_SIZE * CELL_SIZE + 200, bg=FIELD_COLOR)
canvas.pack()

# История выстрелов (статистика выводится только после начала игры)
history_text = tk.Text(root, height=5, width=60)
history_text.pack()

def log_shot(text):
    """Добавление записи в историю выстрелов и статистики."""
    history.append(text)
    history_text.insert(tk.END, text + "\n")
    history_text.see(tk.END)

def draw_grid(offset_x=0):
    """Рисование сетки для игрового поля."""
    for i in range(GRID_SIZE + 1):
        canvas.create_line(offset_x + i * CELL_SIZE, 40, offset_x + i * CELL_SIZE, GRID_SIZE * CELL_SIZE + 40, fill=LINE_COLOR)
        canvas.create_line(offset_x, i * CELL_SIZE + 40, offset_x + GRID_SIZE * CELL_SIZE, i * CELL_SIZE + 40, fill=LINE_COLOR)

def draw_ships(field, offset_x=0, show_ships=False):
    """Отображение кораблей и выстрелов на поле."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x1, y1 = offset_x + col * CELL_SIZE, 40 + row * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            if field[row][col] == 1 and show_ships:
                canvas.create_rectangle(x1, y1, x2, y2, fill=SHIP_COLOR, outline=LINE_COLOR)
            elif field[row][col] == 2:
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=HIT_COLOR)
            elif field[row][col] == 3:
                canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=MISS_COLOR)

def update_stats():
    """Обновление статистики на экране."""
    log_shot(f"Статистика: Клекти игрока: {player_remaining_ships}, Клектки ИИ: {ai_remaining_ships}\n"
             f"Выстрелов игрока: {player_shots}, Выстрелов ИИ: {ai_shots}")

def player_shot(event):
    """Выстрел игрока по полю ИИ."""
    global player_turn, player_shots, ai_remaining_ships, game_over
    if game_over or not player_turn:
        return
    x = (event.x - (GRID_SIZE * CELL_SIZE + 60)) // CELL_SIZE
    y = (event.y - 40) // CELL_SIZE
    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and ai_visible_field[y][x] == 0:
        if ai_field[y][x] == 1:
            ai_visible_field[y][x] = 2
            ai_remaining_ships -= 1
            log_shot(f"Попадание по координатам ({x}, {y})!")
            check_winner()
        else:
            ai_visible_field[y][x] = 3
            player_turn = False
            log_shot(f"Промах по координатам ({x}, {y}).")
        player_shots += 1
        draw_ships(ai_visible_field, offset_x=GRID_SIZE * CELL_SIZE + 60, show_ships=False)
        update_stats()
        if not player_turn:
            root.after(500, ai_turn)

def ai_turn():
    """Ход ИИ. ИИ продолжает стрелять после попадания."""
    global player_turn, ai_shots, game_over
    if game_over:
        return
    while True:
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if player_field[y][x] in [0, 1]:
            break
    if player_field[y][x] == 1:
        player_field[y][x] = 2
        global player_remaining_ships
        player_remaining_ships -= 1
        log_shot(f"ИИ попал по координатам ({x}, {y}).")
        check_winner()
        if not game_over:
            root.after(500, ai_turn)  # ИИ продолжает стрелять
    else:
        player_field[y][x] = 3
        player_turn = True
        log_shot(f"ИИ промахнулся по координатам ({x}, {y}).")
    ai_shots += 1
    draw_ships(player_field, offset_x=0, show_ships=True)
    update_stats()

def check_winner():
    """Проверка победителя и вывод финальной статистики."""
    global game_over
    if ai_remaining_ships <= 0:
        game_over = True
        messagebox.showinfo("Победа!", "Игрок победил!")
        log_shot(f"Победа игрока! Остаток кораблей игрока: {player_remaining_ships}")
    elif player_remaining_ships <= 0:
        game_over = True
        messagebox.showinfo("Поражение!", "ИИ победил!")
        log_shot(f"Победа ИИ! Остаток кораблей ИИ: {ai_remaining_ships}")

def place_random_ships(field):
    """Рандомная расстановка трех кораблей для игрока или ИИ."""
    for ship_len in ships:
        placed = False
        while not placed:
            orientation = random.choice(['horizontal', 'vertical'])
            if orientation == 'horizontal':
                row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - ship_len)
                if can_place_ship(field, row, col, ship_len, orientation):
                    for i in range(ship_len):
                        field[row][col + i] = 1
                    placed = True
            else:
                row, col = random.randint(0, GRID_SIZE - ship_len), random.randint(0, GRID_SIZE - 1)
                if can_place_ship(field, row, col, ship_len, orientation):
                    for i in range(ship_len):
                        field[row + i][col] = 1
                    placed = True

def can_place_ship(field, row, col, ship_len, orientation):
    """Проверка на возможность размещения корабля с учетом отступа."""
    for i in range(ship_len):
        if orientation == 'horizontal':
            if col + i >= GRID_SIZE or field[row][col + i] != 0:
                return False
        else:
            if row + i >= GRID_SIZE or field[row + i][col] != 0:
                return False

    # Проверка на расстояние в одну клетку от корабля
    for r in range(row - 1, row + (ship_len if orientation == 'vertical' else 1) + 1):
        for c in range(col - 1, col + (ship_len if orientation == 'horizontal' else 1) + 1):
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and field[r][c] == 1:
                return False
    return True

def clear_fields():
    """Очистка полей и сброс состояния игры."""
    global player_remaining_ships, ai_remaining_ships, player_shots, ai_shots, game_over, history, current_ship_index, ship_placement_mode
    player_remaining_ships = sum(ships)
    ai_remaining_ships = sum(ships)
    player_shots = 0
    ai_shots = 0
    game_over = False
    history = []
    current_ship_index = 0
    ship_placement_mode = False
    history_text.delete(1.0, tk.END)  # Очистка истории выстрелов
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            player_field[i][j] = 0
            ai_field[i][j] = 0
            ai_visible_field[i][j] = 0
    canvas.delete("all")
    draw_grid(0)
    draw_grid(GRID_SIZE * CELL_SIZE + 60)

def setup_random():
    """Настройка рандомной игры."""
    clear_fields()
    place_random_ships(ai_field)
    place_random_ships(player_field)
    draw_ships(player_field, show_ships=True)
    draw_ships(ai_field, show_ships=False)
    canvas.bind("<Button-1>", player_shot)

def main_menu():
    """Главное меню."""
    clear_fields()
    canvas.delete("all")
    canvas.create_text(GRID_SIZE * CELL_SIZE // 2, 20, text="Морской бой", font=("Arial", 24), fill="black")
    canvas.create_text(GRID_SIZE * CELL_SIZE // 2, 80, text="Выберите режим:", font=("Arial", 18), fill="black")
    random_button = tk.Button(root, text="Рандомная расстановка", command=setup_random)
    manual_button = tk.Button(root, text="Ручная расстановка", command=setup_manual)
    random_button_window = canvas.create_window(GRID_SIZE * CELL_SIZE // 2, 120, window=random_button)
    manual_button_window = canvas.create_window(GRID_SIZE * CELL_SIZE // 2, 160, window=manual_button)

def setup_manual():
    """Настройка ручной расстановки."""
    clear_fields()
    global ship_placement_mode
    ship_placement_mode = True
    canvas.bind("<Motion>", move_ship_with_mouse)
    canvas.bind("<Button-1>", place_ship)

def move_ship_with_mouse(event):
    """Следование корабля за курсором."""
    if current_ship_index >= len(ships):
        return
    x = event.x // CELL_SIZE
    y = (event.y - 40) // CELL_SIZE
    canvas.delete("ship_preview")
    ship_len = ships[current_ship_index]
    for i in range(ship_len):
        if ship_orientation == 'horizontal':
            canvas.create_rectangle((x + i) * CELL_SIZE, y * CELL_SIZE + 40, (x + i + 1) * CELL_SIZE, (y + 1) * CELL_SIZE + 40, fill=SHIP_COLOR, outline=LINE_COLOR, tags="ship_preview")
        else:
            canvas.create_rectangle(x * CELL_SIZE, (y + i) * CELL_SIZE + 40, (x + 1) * CELL_SIZE, (y + i + 1) * CELL_SIZE + 40, fill=SHIP_COLOR, outline=LINE_COLOR, tags="ship_preview")

def place_ship(event):
    """Размещение корабля игроком на поле."""
    global current_ship_index, ship_orientation
    if current_ship_index >= len(ships):
        return
    x = event.x // CELL_SIZE
    y = (event.y - 40) // CELL_SIZE
    ship_len = ships[current_ship_index]
    if can_place_ship(player_field, y, x, ship_len, ship_orientation):
        for i in range(ship_len):
            if ship_orientation == 'horizontal':
                player_field[y][x + i] = 1
            else:
                player_field[y + i][x] = 1
        current_ship_index += 1
        if current_ship_index >= len(ships):
            canvas.unbind("<Motion>")
            canvas.bind("<Button-1>", player_shot)
            draw_ships(ai_field, show_ships=False)
        draw_ships(player_field, show_ships=True)

def rotate_ship():
    """Поворот корабля."""
    global ship_orientation
    ship_orientation = 'vertical' if ship_orientation == 'horizontal' else 'horizontal'

# Клавиша для поворота корабля
root.bind("<r>", lambda event: rotate_ship())

# Запуск главного меню
main_menu()
root.mainloop()

import pyxel
import random

WIDTH = 160
HEIGHT = 120

PLAYER_X = 10
PLAYER_SPEED = 2

# ===== ゲーム状態 =====
bullets = []
enemies = []
explosions = []

score = 0
total_kill = 0
time_limit = 60 * 30

game_over = False
game_started = False

difficulty = 1
secret_unlocked = False
true_secret_unlocked = False

# ===== 解禁条件 =====
unlock_secret_kill = 30
unlock_true_kill = 80

# ===== ボス =====
boss = None
boss_hp = 0
boss_max_hp = 0
boss_active = False

# ===== ゲージ =====
gauge = 0
gauge_max = 100

difficulty_settings = [
    {"name": "Easy", "enemy_speed": 1, "spawn_rate": 0.01, "color": 11},
    {"name": "Normal", "enemy_speed": 2, "spawn_rate": 0.02, "color": 10},
    {"name": "Hard", "enemy_speed": 3, "spawn_rate": 0.03, "color": 8},
    {"name": "Secret", "enemy_speed": 4, "spawn_rate": 0.05, "color": 13},
    {"name": "TrueSecret", "enemy_speed": 5, "spawn_rate": 0.07, "color": 7},
]

def init():
    global player_y, bullets, enemies, explosions
    global score, time_limit, game_over
    global boss, boss_hp, boss_max_hp, boss_active
    global gauge

    player_y = HEIGHT // 2
    bullets = []
    enemies = []
    explosions = []

    score = 0
    time_limit = 60 * 30
    game_over = False

    boss = None
    boss_hp = 0
    boss_max_hp = 0
    boss_active = False

    gauge = 0

def update():
    global player_y, score, total_kill
    global game_over, time_limit, game_started
    global difficulty, secret_unlocked, true_secret_unlocked
    global boss, boss_hp, boss_max_hp, boss_active
    global gauge

    # ===== タイトル =====
    if not game_started:
        if pyxel.btnp(pyxel.KEY_1): difficulty = 0
        if pyxel.btnp(pyxel.KEY_2): difficulty = 1
        if pyxel.btnp(pyxel.KEY_3): difficulty = 2
        if secret_unlocked and pyxel.btnp(pyxel.KEY_4): difficulty = 3
        if true_secret_unlocked and pyxel.btnp(pyxel.KEY_5): difficulty = 4
        if pyxel.btnp(pyxel.KEY_RETURN):
            init()
            game_started = True
        return

    if game_over:
        if pyxel.btnp(pyxel.KEY_R):
            game_started = False
        return

    time_limit -= 1

    # ===== ボス出現 =====
    if time_limit == 10 * 30 and not boss_active:
        boss = [WIDTH - 30, HEIGHT // 2 - 10]
        boss_hp = 40 + difficulty * 20
        boss_max_hp = boss_hp
        boss_active = True

    if time_limit <= 0:
        game_over = True
        return

    # ===== プレイヤー移動 =====
    if pyxel.btn(pyxel.KEY_UP):
        player_y = max(player_y - PLAYER_SPEED, 0)
    if pyxel.btn(pyxel.KEY_DOWN):
        player_y = min(player_y + PLAYER_SPEED, HEIGHT - 8)

    # ===== 弾 =====
    if pyxel.btnp(pyxel.KEY_SPACE):
        bullets.append([PLAYER_X + 8, player_y + 4])

    for b in bullets:
        b[0] += 4
    bullets[:] = [b for b in bullets if b[0] < WIDTH]

    settings = difficulty_settings[difficulty]

    # ===== 通常敵 =====
    if not boss_active:
        if random.random() < settings["spawn_rate"]:
            enemies.append([WIDTH, random.randint(0, HEIGHT - 8)])

    for e in enemies:
        e[0] -= settings["enemy_speed"]
    enemies[:] = [e for e in enemies if e[0] > 0]

    # ===== 通常敵衝突 =====
    for b in bullets[:]:
        for e in enemies[:]:
            if e[0] < b[0] < e[0]+8 and e[1] < b[1] < e[1]+8:
                bullets.remove(b)
                enemies.remove(e)
                score += 1
                total_kill += 1
                gauge = min(gauge + 5, gauge_max)
                explosions.append([e[0], e[1], 10])
                break

    # ===== 解禁判定 =====
    if total_kill >= unlock_secret_kill:
        secret_unlocked = True
    if total_kill >= unlock_true_kill:
        true_secret_unlocked = True

    # ===== ボス処理 =====
    if boss_active:
        boss[1] += random.choice([-1,1]) * settings["enemy_speed"]
        boss[1] = max(0, min(HEIGHT-20, boss[1]))

        for b in bullets[:]:
            if boss[0] < b[0] < boss[0]+20 and boss[1] < b[1] < boss[1]+20:
                bullets.remove(b)
                boss_hp -= 1
                if boss_hp <= 0:
                    explosions.append([boss[0]+10, boss[1]+10, 30])
                    boss_active = False
                    score += 100
                break

    # ===== MAP兵器 =====
    if pyxel.btnp(pyxel.KEY_M) and gauge >= gauge_max:
        for e in enemies:
            explosions.append([e[0], e[1], 15])
        enemies.clear()

        if boss_active:
            boss_hp -= boss_max_hp // 3
        gauge = 0

    # 爆発更新
    for ex in explosions:
        ex[2] -= 1
    explosions[:] = [ex for ex in explosions if ex[2] > 0]

def draw():
    pyxel.cls(0)

    if not game_started:
        pyxel.text(40,20,"SELECT DIFFICULTY",7)
        for i in range(3):
            c = 8 if i==difficulty else 7
            pyxel.text(40,40+i*10,f"{i+1}:{difficulty_settings[i]['name']}",c)

        if not secret_unlocked:
            remain = unlock_secret_kill - total_kill
            pyxel.text(20,90,f"Secret: defeat {remain}",6)
        else:
            pyxel.text(40,70,"4:Secret",13)

        if not true_secret_unlocked:
            remain = unlock_true_kill - total_kill
            pyxel.text(20,100,f"TrueSecret: defeat {remain}",5)
        else:
            pyxel.text(40,80,"5:TrueSecret",5)

        pyxel.text(30,110,"ENTER:START",7)
        return

    # プレイヤー
    pyxel.rect(PLAYER_X, player_y, 8, 8, 12)

    for b in bullets:
        pyxel.rect(b[0], b[1], 2, 2, 8)

    for e in enemies:
        pyxel.rect(e[0], e[1], 8, 8,
                   difficulty_settings[difficulty]["color"])

    # ボス
    if boss_active:
        if difficulty >= 3:
            if difficulty == 4:
                boss_color = 13 if pyxel.frame_count % 10 < 5 else 5
            else:
                boss_color = 13
        else:
            boss_color = 8

        if boss_hp < boss_max_hp // 2:
            boss_color = 14

        pyxel.rect(boss[0], boss[1], 20, 20, boss_color)
        pyxel.text(boss[0], boss[1]-5, f"HP:{boss_hp}",7)

    # 爆発
    for ex in explosions:
        pyxel.circ(ex[0], ex[1], (30-ex[2])//2, 10)

    # UI
    pyxel.text(5,5,f"Score:{score}",7)
    pyxel.text(5,15,f"Kill:{total_kill}",7)
    pyxel.text(5,25,f"Time:{time_limit//30}",7)

    # ゲージ
    pyxel.rect(5,35, gauge_max//2, 5, 1)
    pyxel.rect(5,35, gauge//2, 5, 11)
    if gauge >= gauge_max:
        pyxel.text(5,45,"M:MAP WEAPON READY!",8)

    if game_over:
        pyxel.text(45,60,"GAME OVER",8)
        pyxel.text(30,75,"R:TITLE",7)

pyxel.init(WIDTH, HEIGHT, title="Ultimate Shooting")
init()
pyxel.run(update, draw)
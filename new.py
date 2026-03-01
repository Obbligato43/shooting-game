import pyxel
import random

WIDTH = 160
HEIGHT = 120

PLAYER_X = 10
PLAYER_SPEED = 2

# ===============================
# ■ 難易度設定
# ===============================
difficulty_settings = [
    {"name": "Easy", "enemy_speed": 1, "spawn_rate": 0.01, "boss_hp": 20, "color": 11},
    {"name": "Normal", "enemy_speed": 1.5, "spawn_rate": 0.02, "boss_hp": 30, "color": 10},
    {"name": "Hard", "enemy_speed": 2.5, "spawn_rate": 0.04, "boss_hp": 45, "color": 8},
    {"name": "Secret", "enemy_speed": 3.5, "spawn_rate": 0.06, "boss_hp": 60, "color": 13},
]

selected_difficulty = 0
difficulty = 0

secret_unlocked = False
unlock_kill = 30
total_kill = 0  # ★ 倒した敵の総数（クリア条件に使う）

game_started = False
game_over = False
game_clear = False

bullets = []
enemies = []
explosions = []

score = 0
time_limit = 30 * 30

hp = 3

boss_active = False
boss_hp = 0
boss_max_hp = 0
boss_x = WIDTH
boss_y = 40
boss_phase2 = False

bg_scroll = 0
shake = 0

# ===============================
# ■ MAP兵器ゲージ
# ===============================
gauge = 0
gauge_max = 50  # ★ 最大値


# ===============================
# ■ 初期化
# ===============================
def init():
    global player_y, bullets, enemies, explosions
    global score, time_limit, game_over, game_clear
    global hp, boss_active, boss_hp, boss_x
    global boss_phase2, boss_max_hp, gauge, total_kill

    player_y = HEIGHT // 2
    bullets = []
    enemies = []
    explosions = []

    score = 0
    total_kill = 0  # ★ 撃破数リセット
    time_limit = 30 * 30
    hp = 3
    gauge = 0  # ★ ゲージリセット

    boss_active = False
    boss_phase2 = False
    boss_hp = difficulty_settings[difficulty]["boss_hp"]
    boss_max_hp = boss_hp
    boss_x = WIDTH

    game_over = False
    game_clear = False


# ===============================
# ■ 更新処理
# ===============================
def update():
    global player_y, score, time_limit
    global game_started, game_over, game_clear
    global hp, boss_active, boss_hp
    global boss_x, shake, total_kill
    global difficulty, selected_difficulty
    global secret_unlocked, boss_phase2
    global bg_scroll, gauge

    # ===============================
    # ■ タイトル画面処理
    # ===============================
    if not game_started:
        if pyxel.btnp(pyxel.KEY_UP):
            selected_difficulty -= 1
        if pyxel.btnp(pyxel.KEY_DOWN):
            selected_difficulty += 1

        max_index = 3 if secret_unlocked else 2
        selected_difficulty = max(0, min(max_index, selected_difficulty))

        if pyxel.btnp(pyxel.KEY_RETURN):
            difficulty = selected_difficulty
            init()
            game_started = True
        return

    # ===============================
    # ■ 終了画面
    # ===============================
    if game_over or game_clear:
        if pyxel.btnp(pyxel.KEY_RETURN):
            game_started = False
        return

    settings = difficulty_settings[difficulty]

    # 背景スクロール
    bg_scroll = (bg_scroll + 1) % WIDTH

    # 制限時間
    time_limit -= 1
    if time_limit <= 0:
        game_over = True

    # ===============================
    # ■ プレイヤー移動
    # ===============================
    if pyxel.btn(pyxel.KEY_UP):
        player_y -= PLAYER_SPEED
    if pyxel.btn(pyxel.KEY_DOWN):
        player_y += PLAYER_SPEED
    player_y = max(0, min(HEIGHT - 8, player_y))

    # ===============================
    # ■ 通常弾発射
    # ===============================
    if pyxel.btnp(pyxel.KEY_SPACE):
        bullets.append([PLAYER_X + 8, player_y + 3])

    for b in bullets[:]:
        b[0] += 4
        if b[0] > WIDTH:
            bullets.remove(b)

    # ===============================
    # ■ 敵出現
    # ===============================
    if random.random() < settings["spawn_rate"]:
        enemies.append([WIDTH, random.randint(0, HEIGHT - 8)])

    for e in enemies[:]:
        e[0] -= settings["enemy_speed"]

        # ★ プレイヤーとの当たり判定
        if (
            PLAYER_X < e[0] + 8 and
            PLAYER_X + 8 > e[0] and
            player_y < e[1] + 8 and
            player_y + 8 > e[1]
        ):
            enemies.remove(e)
            hp -= 1
            shake = 10
            if hp <= 0:
                game_over = True

        if e[0] < 0:
            enemies.remove(e)

    # ===============================
    # ■ 弾と敵の当たり判定
    # ===============================
    for b in bullets[:]:
        for e in enemies[:]:
            if (
                b[0] < e[0] + 8 and
                b[0] + 2 > e[0] and
                b[1] < e[1] + 8 and
                b[1] + 2 > e[1]
            ):
                bullets.remove(b)
                enemies.remove(e)
                explosions.append([e[0], e[1], 1])
                score += 1
                total_kill += 1  # ★ 撃破数加算
                gauge += 2       # ★ ゲージ増加

                if gauge > gauge_max:
                    gauge = gauge_max

                # ===============================
                # ★ 30体倒したら全難易度クリア
                # ===============================
                if total_kill >= 30:
                    game_clear = True

                break

    # ===============================
    # ■ MAP兵器発動（Mキー）
    # ===============================
    if pyxel.btnp(pyxel.KEY_M) and gauge == gauge_max:
        shake = 20

        # ★ 画面内の敵を全滅させる
        for e in enemies[:]:
            explosions.append([e[0], e[1], 5])
            enemies.remove(e)
            score += 1

        # ★ ボスにもダメージ
        if boss_active:
            boss_hp -= 10

        gauge = 0  # ★ ゲージ消費

    # ===============================
    # ■ 爆発アニメ
    # ===============================
    for ex in explosions[:]:
        ex[2] += 1
        if ex[2] > 10:
            explosions.remove(ex)

    # ===============================
    # ■ Secret解禁条件
    # ===============================
    if total_kill >= unlock_kill:
        secret_unlocked = True

    # ===============================
    # ■ ボス出現
    # ===============================
    if time_limit < 10 * 30 and not boss_active:
        boss_active = True

    if boss_active:
        boss_x -= 0.5
        if boss_x < WIDTH - 40:
            boss_x = WIDTH - 40

        for b in bullets[:]:
            if (
                b[0] < boss_x + 24 and
                b[0] + 2 > boss_x and
                b[1] < boss_y + 24 and
                b[1] + 2 > boss_y
            ):
                bullets.remove(b)
                boss_hp -= 1
                shake = 5

                if boss_hp <= 0:
                    game_clear = True

    if shake > 0:
        shake -= 1


# ===============================
# ■ 描画
# ===============================
def draw():
    pyxel.cls(0)

    if not game_started:
        pyxel.text(40, 20, "SELECT DIFFICULTY", 7)
        y = 50
        for i, d in enumerate(difficulty_settings):
            marker = ">" if i == selected_difficulty else " "
            name = "???" if i == 3 and not secret_unlocked else d["name"]
            pyxel.text(50, y, f"{marker} {name}", d["color"])
            y += 12
        pyxel.text(35, 95, "PRESS ENTER", 7)
        return

    offset_x = random.randint(-2, 2) if shake > 0 else 0

    pyxel.rect(PLAYER_X + offset_x, player_y, 8, 8, 9)

    for b in bullets:
        pyxel.rect(b[0] + offset_x, b[1], 2, 2, 7)

    for e in enemies:
        pyxel.rect(e[0] + offset_x, e[1], 8, 8,
                   difficulty_settings[difficulty]["color"])

    if boss_active:
        pyxel.rect(boss_x + offset_x, boss_y, 24, 24, 8)
        pyxel.text(boss_x, boss_y - 6, f"HP:{boss_hp}", 7)

    for ex in explosions:
        pyxel.circ(ex[0] + offset_x, ex[1], ex[2], 10)

    # ★ UI表示
    pyxel.text(5, 5, f"SCORE:{score}", 7)
    pyxel.text(5, 12, f"HP:{hp}", 8)

    # ★ MAPゲージ表示
    pyxel.rect(5, 20, gauge_max, 4, 1)
    pyxel.rect(5, 20, gauge, 4, 11)
    pyxel.text(5, 27, "MAP:M", 7)

    if game_over:
        pyxel.text(45, 60, "GAME OVER", 8)

    if game_clear:
        pyxel.text(45, 60, "GAME CLEAR!", 11)


pyxel.init(WIDTH, HEIGHT)
init()
pyxel.run(update, draw)
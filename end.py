import pyxel
import random

# 画面サイズ
WIDTH = 160
HEIGHT = 120

# プレイヤーの設定
PLAYER_X = 10
PLAYER_Y = HEIGHT // 2
PLAYER_SPEED = 2

# 弾の設定
BULLET_SPEED = 4
bullets = []

# 敵の設定
ENEMY_SPEED = 1
enemies = []

# ゲームの設定
score = 0
time_limit = 60 * 30  # 1分（60秒 * 30フレーム）
game_over = False

# 初期化
def init():
    global player_y, score, bullets, enemies, game_over
    player_y = PLAYER_Y
    score = 0
    bullets = []
    enemies = []
    game_over = False

# 更新
def update():
    global player_y, score, game_over, time_limit

    if game_over:
        return

    # 制限時間のカウントダウン
    time_limit -= 1
    if time_limit <= 0:
        game_over = True
        return

    # プレイヤーの移動
    if pyxel.btn(pyxel.KEY_UP):
        player_y = max(player_y - PLAYER_SPEED, 0)
    if pyxel.btn(pyxel.KEY_DOWN):
        player_y = min(player_y + PLAYER_SPEED, HEIGHT - 8)

    # 弾の発射
    if pyxel.btnp(pyxel.KEY_SPACE):
        bullets.append([PLAYER_X + 8, player_y + 4])

    # 弾の移動
    for bullet in bullets:
        bullet[0] += BULLET_SPEED

    # 画面外の弾を削除
    bullets[:] = [bullet for bullet in bullets if bullet[0] < WIDTH]

    # 敵の生成
    if random.random() < 0.02:
        enemies.append([WIDTH, random.randint(0, HEIGHT - 8)])

    # 敵の移動
    for enemy in enemies:
        enemy[0] -= ENEMY_SPEED

    # 画面外の敵を削除
    enemies[:] = [enemy for enemy in enemies if enemy[0] > 0]

    # 弾と敵の衝突判定
    for bullet in bullets:
        for enemy in enemies:
            if (enemy[0] < bullet[0] < enemy[0] + 8 and
                enemy[1] < bullet[1] < enemy[1] + 8):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                break

# 描画
def draw():
    pyxel.cls(0)
    pyxel.rect(PLAYER_X, player_y, 8, 8, 9)  # プレイヤー
    for bullet in bullets:
        pyxel.rect(bullet[0], bullet[1], 2, 2, 7)  # 弾
    for enemy in enemies:
        pyxel.rect(enemy[0], enemy[1], 8, 8, 8)  # 敵

    # スコアと時間の表示
    pyxel.text(5, 5, f"Score: {score}", 7)
    pyxel.text(5, 15, f"Time: {time_limit // 30}", 7)

    # ゲームオーバーの表示
    if game_over:
        pyxel.text(WIDTH // 2 - 20, HEIGHT // 2, "Game Over!", 8)

# ゲーム開始
pyxel.init(WIDTH, HEIGHT, title="Shooting Game")
init()
pyxel.run(update, draw)
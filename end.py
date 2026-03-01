import pyxel

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

# 初期化
def init():
    global player_y
    player_y = PLAYER_Y

# 更新
def update():
    global player_y

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

# 描画
def draw():
    pyxel.cls(0)
    pyxel.rect(PLAYER_X, player_y, 8, 8, 9)  # プレイヤー
    for bullet in bullets:
        pyxel.rect(bullet[0], bullet[1], 2, 2, 7)  # 弾

# ゲーム開始
pyxel.init(WIDTH, HEIGHT, title="Shooting Game")
init()
pyxel.run(update, draw)
import pygame
import chess
import sys
from engine import RandomAgent, PoorAgent, AverageAgent, GoodAgent

# --- THÔNG SỐ CƠ BẢN ---
WIDTH = 512
HEIGHT = 512
SQ_SIZE = WIDTH // 8
MAX_FPS = 30
IMAGES = {}


# --- HÀM TẢI ẢNH ---
def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        try:
            img = pygame.image.load(f"a2/images/{piece}.png")
            IMAGES[piece] = pygame.transform.scale(img, (SQ_SIZE, SQ_SIZE))
        except FileNotFoundError:
            print(
                f"LỖI CHÍNH MẠNG: Không tìm thấy file images/{piece}.png. Cậu chưa tải ảnh về!"
            )
            sys.exit(1)


# --- VẼ BÀN CỜ VÀ QUÂN CỜ ---
def draw_board(screen, board, dragging_square, mouse_pos, is_flipped):
    colors = [pygame.Color(235, 236, 208), pygame.Color(115, 149, 82)]

    # Vẽ 64 ô
    for r in range(8):
        for c in range(8):
            display_row = 7 - r if is_flipped else r
            display_col = 7 - c if is_flipped else c
            color = colors[(display_row + display_col) % 2]
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(
                    display_col * SQ_SIZE, display_row * SQ_SIZE, SQ_SIZE, SQ_SIZE
                ),
            )

    # Highlight ô đang chọn
    if dragging_square is not None:
        col = chess.square_file(dragging_square)
        row = chess.square_rank(dragging_square)
        draw_col = 7 - col if is_flipped else col
        draw_row = row if is_flipped else 7 - row

        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(pygame.Color("yellow"))
        screen.blit(s, (draw_col * SQ_SIZE, draw_row * SQ_SIZE))

    # Vẽ quân cờ
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and square != dragging_square:
            col = chess.square_file(square)
            row = chess.square_rank(square)
            draw_col = 7 - col if is_flipped else col
            draw_row = row if is_flipped else 7 - row

            piece_name = (
                "w" if piece.color == chess.WHITE else "b"
            ) + piece.symbol().upper()
            screen.blit(
                IMAGES[piece_name],
                pygame.Rect(draw_col * SQ_SIZE, draw_row * SQ_SIZE, SQ_SIZE, SQ_SIZE),
            )

    # Vẽ quân cờ đang kéo thả bám theo chuột
    if dragging_square is not None and mouse_pos is not None:
        piece = board.piece_at(dragging_square)
        if piece:
            piece_name = (
                "w" if piece.color == chess.WHITE else "b"
            ) + piece.symbol().upper()
            x, y = mouse_pos
            screen.blit(
                IMAGES[piece_name],
                pygame.Rect(x - SQ_SIZE // 2, y - SQ_SIZE // 2, SQ_SIZE, SQ_SIZE),
            )


# --- VẼ MÀN HÌNH KẾT THÚC ---
def draw_game_over(screen, board):
    if board.is_game_over():
        result = board.result()
        if result == "1-0":
            text, color = "White win!", pygame.Color("white")
        elif result == "0-1":
            text, color = "Black win!", pygame.Color("black")
        else:
            text, color = "Draw!", pygame.Color("gray")

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont("Arial", 48, bold=True)
        text_surface = font.render(text, True, color)
        outline_surface = font.render(text, True, pygame.Color("red"))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        screen.blit(outline_surface, (text_rect.x - 2, text_rect.y - 2))
        screen.blit(text_surface, text_rect)


# --- CHẾ ĐỘ TEST KẾT QUẢ THEO YÊU CẦU ---
def auto_test_10_matches(bot_class, bot_is_white):
    print("\n" + "=" * 50)
    print(
        f"BẮT ĐẦU TEST 10 TRẬN: {bot_class.__name__} ({'Trắng' if bot_is_white else 'Đen'}) VS RandomAgent"
    )
    print("=" * 50)

    results = {"Bot Win": 0, "Random Win": 0, "Draw": 0}

    for i in range(1, 11):
        board = chess.Board()
        bot = bot_class()
        opponent = RandomAgent()

        while not board.is_game_over():
            if (board.turn == chess.WHITE) == bot_is_white:
                move = bot.get_move(board)
            else:
                move = opponent.get_move(board)

            # Đề phòng lỗi thuật toán trả về None
            if move is None or move not in board.legal_moves:
                print(
                    f"Trận {i}: LỖI CHÍ MẠNG! Thuật toán trả về nước đi không hợp lệ hoặc None."
                )
                break

            board.push(move)

        res = board.result()
        if (res == "1-0" and bot_is_white) or (res == "0-1" and not bot_is_white):
            results["Bot Win"] += 1
            result_str = "Bot Thắng"
        elif res == "1/2-1/2":
            results["Draw"] += 1
            result_str = "Hòa"
        else:
            results["Random Win"] += 1
            result_str = "Random Thắng"

        print(f"Trận {i:02d}: {result_str} | Số nước đi: {board.fullmove_number}")

    print("-" * 50)
    print(
        f"TỔNG KẾT: Bot Thắng: {results['Bot Win']} | Random Thắng: {results['Random Win']} | Hòa: {results['Draw']}"
    )
    print("=" * 50 + "\n")


# --- HÀM MAIN ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess AI - C03061")
    clock = pygame.time.Clock()

    load_images()

    # Biến trạng thái State Machine
    state = "MENU"
    selected_bot_class = PoorAgent
    player_is_white = True

    # Các biến khi chơi
    board = None
    bot_player = None
    is_flipped = False
    dragging = False
    selected_square = None
    ai_turn_start_time = None

    font_menu = pygame.font.SysFont("Arial", 24)

    running = True
    while running:
        # -----------------------------------------------------------------
        # TRẠNG THÁI 1: MENU
        # -----------------------------------------------------------------
        if state == "MENU":
            screen.fill(pygame.Color("darkslategray"))

            # Render Text
            texts = [
                "Chess.com",
                "",
                "Choose level (Press 1-3):",
                f"  1. Poor Agent {'<--' if selected_bot_class == PoorAgent else ''}",
                f"  2. Average Agent {'<--' if selected_bot_class == AverageAgent else ''}",
                f"  3. Good Agent {'<--' if selected_bot_class == GoodAgent else ''}",
                "",
                "Choose color (Press W / B):",
                f"  White (First move) {'<--' if player_is_white else ''}",
                f"  Black (Second move) {'<--' if not player_is_white else ''}",
                "",
                "Action:",
                "  [ENTER] - Start playing",
                "  [T] - 10 random rule-based agent tests",
            ]

            for i, text in enumerate(texts):
                color = (
                    pygame.Color("yellow") if "<--" in text else pygame.Color("white")
                )
                text_surface = font_menu.render(text, True, color)
                screen.blit(text_surface, (50, 30 + i * 30))

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_1:
                        selected_bot_class = PoorAgent
                    elif e.key == pygame.K_2:
                        selected_bot_class = AverageAgent
                    elif e.key == pygame.K_3:
                        selected_bot_class = GoodAgent
                    elif e.key == pygame.K_w:
                        player_is_white = True
                    elif e.key == pygame.K_b:
                        player_is_white = False
                    elif e.key == pygame.K_t:
                        # Chạy ngầm 10 trận
                        auto_test_10_matches(selected_bot_class, not player_is_white)
                    elif e.key == pygame.K_RETURN:
                        # Khởi tạo ván chơi
                        board = chess.Board()
                        bot_player = selected_bot_class()
                        is_flipped = not player_is_white
                        state = "PLAYING"

            pygame.display.flip()
            clock.tick(MAX_FPS)
            continue

        # -----------------------------------------------------------------
        # TRẠNG THÁI 2: PLAYING
        # -----------------------------------------------------------------
        if state == "PLAYING":
            human_turn = (board.turn == chess.WHITE and player_is_white) or (
                board.turn == chess.BLACK and not player_is_white
            )

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

                # Nhấn ESC để quay lại Menu
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    state = "MENU"

                # XỬ LÝ CHUỘT DÀNH CHO NGƯỜI CHƠI
                elif (
                    e.type == pygame.MOUSEBUTTONDOWN
                    and human_turn
                    and not board.is_game_over()
                ):
                    pos = (
                        pygame.event.get()[0].pos
                        if e.type == pygame.MOUSEMOTION
                        else pygame.mouse.get_pos()
                    )
                    x, y = pos

                    # Chuyển đổi tọa độ chuột sang ô vuông (Tính cả việc bàn cờ bị lật)
                    col = 7 - (x // SQ_SIZE) if is_flipped else x // SQ_SIZE
                    row = y // SQ_SIZE if is_flipped else 7 - (y // SQ_SIZE)

                    # Rào lỗi click ngoài màn hình
                    if 0 <= col <= 7 and 0 <= row <= 7:
                        sq = chess.square(col, row)
                        if (
                            board.piece_at(sq)
                            and board.piece_at(sq).color == board.turn
                        ):
                            dragging = True
                            selected_square = sq

                elif e.type == pygame.MOUSEBUTTONUP and dragging:
                    pos = pygame.mouse.get_pos()
                    x, y = pos

                    col = 7 - (x // SQ_SIZE) if is_flipped else x // SQ_SIZE
                    row = y // SQ_SIZE if is_flipped else 7 - (y // SQ_SIZE)

                    if 0 <= col <= 7 and 0 <= row <= 7:
                        target_square = chess.square(col, row)
                        move = chess.Move(selected_square, target_square)

                        # Phong cấp (Mặc định Hậu)
                        if board.piece_at(
                            selected_square
                        ).piece_type == chess.PAWN and (row == 0 or row == 7):
                            move = chess.Move(
                                selected_square, target_square, promotion=chess.QUEEN
                            )

                        if move in board.legal_moves:
                            board.push(move)

                    dragging = False
                    selected_square = None

            # XỬ LÝ LƯỢT AI (Có Delay 1s)
            if not human_turn and not board.is_game_over():
                if ai_turn_start_time is None:
                    ai_turn_start_time = pygame.time.get_ticks()

                current_time = pygame.time.get_ticks()
                if current_time - ai_turn_start_time > 1000:
                    ai_move = bot_player.get_move(board)
                    if ai_move and ai_move in board.legal_moves:
                        board.push(ai_move)
                    else:
                        print("CẢNH BÁO: AI trả về nước đi lỗi. Tự động random.")
                        legal = list(board.legal_moves)
                        if legal:
                            board.push(legal[0])

                    ai_turn_start_time = None

            # Render đồ họa
            mouse_pos = pygame.mouse.get_pos()
            draw_board(
                screen,
                board,
                selected_square if dragging else None,
                mouse_pos,
                is_flipped,
            )
            draw_game_over(screen, board)

            # Gợi ý thoát
            if board.is_game_over():
                text_surface = font_menu.render(
                    "Press ESC to back to Menu", True, pygame.Color("blue")
                )
                screen.blit(text_surface, (10, 10))

            pygame.display.flip()
            clock.tick(MAX_FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

import pygame
import chess
import sys
# Import đầy đủ các loại Agent từ file engine.py
from engine import (
    RandomAgent, 
    PoorAgent, AverageAgent, GoodAgent,
    MLPoorAgent, MLAverageAgent, MLGoodAgent
)

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
            img = pygame.image.load(f"images/{piece}.png")
            IMAGES[piece] = pygame.transform.scale(img, (SQ_SIZE, SQ_SIZE))
        except FileNotFoundError:
            print(f"LỖI: Không tìm thấy file images/{piece}.png. Hãy kiểm tra thư mục images!")
            sys.exit(1)

# --- VẼ BÀN CỜ VÀ QUÂN CỜ ---
def draw_board(screen, board, dragging_square, mouse_pos, is_flipped):
    colors = [pygame.Color(235, 236, 208), pygame.Color(115, 149, 82)]
    for r in range(8):
        for c in range(8):
            display_row = 7 - r if is_flipped else r
            display_col = 7 - c if is_flipped else c
            color = colors[(display_row + display_col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(display_col * SQ_SIZE, display_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    if dragging_square is not None:
        col, row = chess.square_file(dragging_square), chess.square_rank(dragging_square)
        draw_col, draw_row = (7 - col if is_flipped else col), (row if is_flipped else 7 - row)
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100); s.fill(pygame.Color("yellow"))
        screen.blit(s, (draw_col * SQ_SIZE, draw_row * SQ_SIZE))

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and square != dragging_square:
            col, row = chess.square_file(square), chess.square_rank(square)
            draw_col, draw_row = (7 - col if is_flipped else col), (row if is_flipped else 7 - row)
            piece_name = ("w" if piece.color == chess.WHITE else "b") + piece.symbol().upper()
            screen.blit(IMAGES[piece_name], pygame.Rect(draw_col * SQ_SIZE, draw_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    if dragging_square is not None and mouse_pos is not None:
        piece = board.piece_at(dragging_square)
        if piece:
            piece_name = ("w" if piece.color == chess.WHITE else "b") + piece.symbol().upper()
            screen.blit(IMAGES[piece_name], pygame.Rect(mouse_pos[0] - SQ_SIZE // 2, mouse_pos[1] - SQ_SIZE // 2, SQ_SIZE, SQ_SIZE))

# --- VẼ MÀN HÌNH KẾT THÚC ---
def draw_game_over(screen, board):
    if board.is_game_over():
        result = board.result()
        text = "White win!" if result == "1-0" else "Black win!" if result == "0-1" else "Draw!"
        color = pygame.Color("white") if result == "1-0" else pygame.Color("black") if result == "0-1" else pygame.Color("gray")
        overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(180); overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("Arial", 48, bold=True)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

# --- CHẾ ĐỘ TEST 10 TRẬN (REQUIREMENT 2) ---
def auto_test_10_matches(bot_class, bot_is_white):
    print("\n" + "=" * 60)
    print(f"TESTING 10 MATCHES: {bot_class.__name__} ({'White' if bot_is_white else 'Black'}) VS RandomAgent")
    print("=" * 60)

    results = {"Bot Win": 0, "Random Win": 0, "Draw": 0}
    total_moves = 0  # Biến mới: Dùng để cộng dồn số hiệp của cả 10 trận

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
                print(f"Trận {i}: Error! No moves available.")
                break

            board.push(move)

        res = board.result()
        if (res == "1-0" and bot_is_white) or (res == "0-1" and not bot_is_white):
            results["Bot Win"] += 1
            result_str = "Bot Win   "
        elif res == "1/2-1/2":
            results["Draw"] += 1
            result_str = "Draw         "
        else:
            results["Random Win"] += 1
            result_str = "Random Win"

        # LẤY SỐ HIỆP CỦA VÁN CỜ NÀY
        match_moves = board.fullmove_number
        total_moves += match_moves # Cộng dồn vào tổng

        print(f"Match {i:02d}: {result_str} | Full moves: {match_moves}")

    # TÍNH TRUNG BÌNH CỘNG
    avg_moves = total_moves / 10

    print("-" * 60)
    print(f"Final Result: Bot Win: {results['Bot Win']} | Random Win: {results['Random Win']} | Draw: {results['Draw']}")
    print(f"Avg Move:  {avg_moves:.1f} moves per game.")
    print("=" * 60 + "\n")

# --- MAIN LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess AI Assignment - Semester 252")
    clock = pygame.time.Clock()
    load_images()

    state = "MENU"
    bot_type = "SEARCH" # Hoặc "ML"
    selected_level = 2 # 1: Poor, 2: Average, 3: Good
    player_is_white = True
    board, bot_player, is_flipped, dragging, selected_square, ai_timer = None, None, False, False, None, None
    font_menu = pygame.font.SysFont("Arial", 22)

    while True:
        if state == "MENU":
            screen.fill(pygame.Color("darkslategray"))
            menu_items = [
                "CHESS AI ASSIGNMENT", "",
                f"1. Bot Type: {bot_type} (Press M to toggle)",
                f"2. Level: {['Poor', 'Average', 'Good'][selected_level-1]} (Press 1, 2, 3)",
                f"3. Your Side: {'White' if player_is_white else 'Black'} (Press W or B)",
                "", "[ENTER] - Start Game", "[T] - Test 10 Matches vs Random"
            ]
            for i, text in enumerate(menu_items):
                screen.blit(font_menu.render(text, True, pygame.Color("white")), (50, 50 + i * 35))

            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_m: bot_type = "ML" if bot_type == "SEARCH" else "SEARCH"
                    if e.key in [pygame.K_1, pygame.K_2, pygame.K_3]: selected_level = int(e.unicode)
                    if e.key == pygame.K_w: player_is_white = True
                    if e.key == pygame.K_b: player_is_white = False
                    if e.key == pygame.K_t:
                        agent_map = {
                            "SEARCH": [PoorAgent, AverageAgent, GoodAgent],
                            "ML": [MLPoorAgent, MLAverageAgent, MLGoodAgent]
                        }
                        auto_test_10_matches(agent_map[bot_type][selected_level-1], not player_is_white)
                    if e.key == pygame.K_RETURN:
                        agent_map = {
                            "SEARCH": [PoorAgent, AverageAgent, GoodAgent],
                            "ML": [MLPoorAgent, MLAverageAgent, MLGoodAgent]
                        }
                        bot_player = agent_map[bot_type][selected_level-1]()
                        board = chess.Board(); is_flipped = not player_is_white; state = "PLAYING"

        elif state == "PLAYING":
            human_turn = (board.turn == chess.WHITE and player_is_white) or (board.turn == chess.BLACK and not player_is_white)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: state = "MENU"
                if e.type == pygame.MOUSEBUTTONDOWN and human_turn and not board.is_game_over():
                    x, y = pygame.mouse.get_pos()
                    col = 7 - (x // SQ_SIZE) if is_flipped else x // SQ_SIZE
                    row = y // SQ_SIZE if is_flipped else 7 - (y // SQ_SIZE)
                    sq = chess.square(col, row)
                    if board.piece_at(sq) and board.piece_at(sq).color == board.turn:
                        dragging, selected_square = True, sq
                if e.type == pygame.MOUSEBUTTONUP and dragging:
                    x, y = pygame.mouse.get_pos()
                    col = 7 - (x // SQ_SIZE) if is_flipped else x // SQ_SIZE
                    row = y // SQ_SIZE if is_flipped else 7 - (y // SQ_SIZE)
                    target = chess.square(col, row)
                    move = chess.Move(selected_square, target)
                    if board.piece_at(selected_square).piece_type == chess.PAWN and (row == 0 or row == 7):
                        move = chess.Move(selected_square, target, promotion=chess.QUEEN)
                    if move in board.legal_moves: board.push(move)
                    dragging, selected_square = False, None

            if not human_turn and not board.is_game_over():
                if ai_timer is None: ai_timer = pygame.time.get_ticks()
                if pygame.time.get_ticks() - ai_timer > 800:
                    board.push(bot_player.get_move(board))
                    ai_timer = None

            draw_board(screen, board, selected_square if dragging else None, pygame.mouse.get_pos(), is_flipped)
            draw_game_over(screen, board)
            if board.is_game_over():
                screen.blit(font_menu.render("Press ESC for Menu", True, pygame.Color("blue")), (10, 10))
        
        pygame.display.flip()
        clock.tick(MAX_FPS)

if __name__ == "__main__":
    main()
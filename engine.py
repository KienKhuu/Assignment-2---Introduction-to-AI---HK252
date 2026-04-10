import chess
import random
import math


class Player:
    """
    Class gốc (Base class). TẤT CẢ các bot phải kế thừa từ class này.
    """

    def get_move(self, board: chess.Board) -> chess.Move:
        """
        Hàm cốt lõi. Nhận vào trạng thái bàn cờ hiện tại và BẮT BUỘC
        phải trả về một đối tượng chess.Move hợp lệ.
        """
        raise NotImplementedError(
            "Đồng đội của cậu chưa implement hàm get_move() cho class này."
        )


class RandomAgent(Player):
    """
    Bot đánh ngẫu nhiên. Dùng để test UI và đáp ứng Requirement 2. [cite: 25]
    Đã hoàn thiện. Không cần sửa.
    """

    def get_move(self, board: chess.Board) -> chess.Move:
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        return random.choice(legal_moves)


class BaseSearchAgent(Player):
    """
    [DÀNH CHO ĐỒNG ĐỘI CỦA CẬU]
    Bộ khung thuật toán Tìm kiếm (Minimax / Alpha-Beta).
    Họ phải viết code vào các hàm có chữ 'TODO'.
    """

    def __init__(self, depth: int):
        self.depth = depth

    def evaluate_board(self, board: chess.Board) -> float:
        """
        TODO: Viết hàm lượng giá (Heuristic function) tại đây.
        - Trả về số dương lớn nếu Trắng có lợi.
        - Trả về số âm lớn nếu Đen có lợi.
        """
        # Trả về 0.0 tạm thời để game không crash khi chưa có code
        return 0.0

    def minimax(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing_player: bool,
    ) -> float:
        """
        TODO: Triển khai logic Minimax có cắt tỉa Alpha-Beta tại đây. [cite: 38, 39]
        """
        ### Sample guide
        # Điều kiện dừng: Hết độ sâu hoặc game kết thúc
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if maximizing_player:
            max_eval = -math.inf
            for move in board.legal_moves:
                board.push(move)  # Thử đi
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()  # Hoàn tác
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Cắt tỉa Beta
            return max_eval
        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Cắt tỉa Alpha
            return min_eval

    def get_move(self, board: chess.Board) -> chess.Move:
        """
        TODO: Gọi hàm minimax để tìm ra nước đi tốt nhất.
        Đoạn code dưới đây chỉ là bộ khung cơ bản, đồng đội của cậu cần tối ưu nó.
        """
        ### Sample guide
        best_move = None
        legal_moves = list(board.legal_moves)

        if not legal_moves:
            return None

        maximizing_player = board.turn == chess.WHITE
        best_value = -math.inf if maximizing_player else math.inf

        # Tối ưu hóa (Move Ordering): Ưu tiên kiểm tra các nước ăn quân trước
        legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)

        for move in legal_moves:
            board.push(move)
            # Gọi minimax cho nhánh con
            board_value = self.minimax(
                board, self.depth - 1, -math.inf, math.inf, not maximizing_player
            )
            board.pop()

            if maximizing_player:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move

        # Fallback an toàn nếu thuật toán lỗi và không chọn được nước nào
        if best_move is None:
            best_move = random.choice(legal_moves)

        return best_move


# --- CÁC LEVEL CỤ THỂ ĐỂ BIND VÀO UI ---


class PoorAgent(BaseSearchAgent):
    """Level 1: Nhìn trước 1 nước. Đánh cực ngu, dễ dàng bị lừa."""

    def __init__(self):
        super().__init__(depth=3)

    # Đồng đội 1 có thể override hàm evaluate_board ở đây để chỉ tính điểm vật chất cơ bản (Tốt=1, Xe=5...)


class AverageAgent(BaseSearchAgent):
    """Level 2: Nhìn trước 2-3 nước. Đánh tàm tạm."""

    def __init__(self):
        super().__init__(depth=3)

    # Đồng đội 2 có thể override hàm evaluate_board ở đây để tính thêm vị trí đứng của quân cờ (Piece-Square Tables).


class GoodAgent(BaseSearchAgent):
    """Level 3: Nhìn trước 4 nước trở lên. Cần tối ưu thuật toán tốt (như move ordering) để không bị chậm."""

    def __init__(self):
        super().__init__(depth=4) 
        
        # 1. Điểm cơ bản của các quân cờ
        self.piece_value = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }

        # 2. Piece-Square Tables (Khuyến khích quân cờ đi vào vị trí tốt)
        # Các bảng này được cấu hình theo góc nhìn của quân Trắng (index 0 là A1, 63 là H8)
        
        self.pawn_pst = [
             0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5, -5,-10,  0,  0,-10, -5,  5,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        self.knight_pst = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]

    def evaluate_board(self, board: chess.Board) -> float:
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -99999.0 
            else:
                return 99999.0
                
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        eval_score = 0.0
        
        # Duyệt qua tất cả 64 ô trên bàn cờ
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Tính điểm material
                material_score = self.piece_value.get(piece.piece_type, 0)
                
                position_score = 0  # Tính điểm vị trí dựa theo loại quân
                
                # Phải lật ngược bàn cờ (mirror) nếu tính cho quân Đen vì PST thiết kế cho Trắng
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                
                if piece.piece_type == chess.PAWN:
                    position_score = self.pawn_pst[pst_index]
                elif piece.piece_type == chess.KNIGHT:
                    position_score = self.knight_pst[pst_index]

                # Tổng hợp điểm: Quân Trắng làm tăng điểm (+), Quân Đen làm giảm điểm (-)
                if piece.color == chess.WHITE:
                    eval_score += (material_score + position_score)
                else:
                    eval_score -= (material_score + position_score)

        return eval_score
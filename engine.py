import chess
import random
import math
import joblib
import numpy as np


def board_to_features(board: chess.Board):
    features = np.zeros(64)
    piece_values = { chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100 }
    for square, piece in board.piece_map().items():
        val = piece_values[piece.piece_type]
        if piece.color == chess.BLACK: val = -val
        features[square] = val
    return features

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
        Triển khai logic Minimax có cắt tỉa Alpha-Beta
        """
        # 1. ĐIỀU KIỆN DỪNG: Bị chiếu hết
        if board.is_checkmate():
            return (-99999 - depth) if board.turn == chess.WHITE else (99999 + depth)
        
        if board.is_game_over(): 
            return 0.0

        if depth == 0:
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
        # legal_moves = list(board.legal_moves)
        # return random.choice(legal_moves) if legal_moves else None


# --- CÁC LEVEL CỤ THỂ ĐỂ BIND VÀO UI ---


class PoorAgent(BaseSearchAgent):
    """Level 1: Nhìn trước 1 nước. Đánh cực ngu, dễ dàng bị lừa."""

    def __init__(self):
        super().__init__(depth=3)

    # Đồng đội 1 có thể override hàm evaluate_board ở đây để chỉ tính điểm vật chất cơ bản (Tốt=1, Xe=5...)

class MLPoorAgent(BaseSearchAgent):
    """
    Dummy ML Agent (Level 1).
    Hiện tại chưa có mô hình. Sau khi train xong, nạp file pkl vào đây.
    """
    def __init__(self):
        super().__init__(depth=1) # Độ sâu rất nông, chỉ nhìn trước 1 bước
        self.model = None
        
        # MẪU CODE ĐỂ LOAD MODEL SAU NÀY (Bỏ comment khi đã có file):
        # try:
        #     self.model = joblib.load("poor_ml_model.pkl")
        # except FileNotFoundError:
        #     print("Chưa có file poor_ml_model.pkl")

    def evaluate_board(self, board: chess.Board) -> float:
        if board.is_checkmate():
            return -99999 if board.turn == chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0
            
        # Dummy behavior: Nếu chưa có não (model), mù lòa trả về 0
        if self.model is None:
            return 0.0
            
        # TƯƠNG LAI: Viết code gọi model.predict() ở đây giống MLAverageAgent
        # features = board_to_features(board)
        # return float(self.model.predict([features])[0])

class MLAverageAgent(BaseSearchAgent):
    def __init__(self):
        # Đặt depth=2 để cân bằng giữa thời gian và độ khôn
        # Decision Tree chạy rất nhanh nên depth=2 sẽ mất khoảng vài giây/nước
        super().__init__(depth=3) 
        
        try:
            # Load mô hình Cây quyết định (Decision Tree) đã train theo Chapter 10
            self.model = joblib.load("./models/avg_model.pkl")
        except FileNotFoundError:
            print("CẢNH BÁO: Không tìm thấy avg_model.pkl. Bot sẽ đánh ngẫu nhiên.")
            self.model = None
            
        # KHỞI TẠO CACHE: Đây là chìa khóa để bot chạy nhanh
        # Lưu kết quả dự đoán của mô hình theo chuỗi FEN (trạng thái bàn cờ)
        self.table_cache = {}

    def evaluate_board(self, board: chess.Board) -> float:
        if self.model is None:
            return 0.0

        fen_key = board.fen()
        if fen_key in self.table_cache:
            return self.table_cache[fen_key]

        features = board_to_features(board) 
        score = float(self.model.predict([features])[0])
        
        # MẸO HACK MOBILITY: Đếm số lượng nước đi hợp lệ hiện tại
        # Trắng đến lượt -> Số nước đi của trắng. Đen đến lượt -> Số nước đi của đen.
        mobility = len(list(board.legal_moves))
        
        # Cộng một lượng điểm RẤT NHỎ (0.01) để không làm hỏng trọng số của ML
        # Nhưng đủ để phân loại các nước đi có cùng điểm ML
        if board.turn == chess.WHITE:
            score += (mobility * 0.01)
        else:
            score -= (mobility * 0.01)

        self.table_cache[fen_key] = score
        return score

class AverageAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__(depth=3)
        
        # 1. BẢNG GIÁ TRỊ VẬT CHẤT (Centipawns: 1 Tốt = 100 điểm)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }

        # 2. BẢNG VỊ TRÍ (PST) - Góc nhìn của quân Trắng        
        self.knight_pst = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50,
        ]

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

        self.bishop_pst = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,
        ]

        self.rook_pst = [
             0,  0,  0,  0,  0,  0,  0,  0,
             5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
             0,  0,  0,  5,  5,  0,  0,  0
        ]

        self.queen_pst = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
             -5,  0,  5,  5,  5,  5,  0, -5,
              0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]

        self.king_pst = [
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 30, 10,  0,  0, 10, 30, 20
        ]

    def evaluate_board(self, board: chess.Board) -> float:
        """
        Ghi đè hàm đánh giá từ class cha.
        Luật bắt buộc: Trả về số dương nếu Trắng đang lợi thế, số âm nếu Đen lợi thế.
        """
        # Kiểm tra trạng thái kết thúc game trước tiên
        if board.is_checkmate():
            # Nếu đến lượt Trắng đi mà bị chiếu hết -> Đen thắng -> Trả về âm vô cực
            return -99999 if board.turn == chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        score = 0.0
        
        # Duyệt qua tất cả các quân cờ đang có trên bàn
        for square, piece in board.piece_map().items():
            # Lấy giá trị cơ bản của quân cờ
            val = self.piece_values[piece.piece_type]
            
            # Cộng điểm vị trí (chỉ áp dụng cho Tốt và Mã để đơn giản hóa, 
            # cậu có thể tự Google thêm PST cho Xe, Tượng, Hậu)
            pst_val = 0
            if piece.piece_type == chess.KNIGHT:
                # Nếu là quân Đen, phải lật ngược bảng PST lại (63 - square)
                sq_idx = square if piece.color == chess.WHITE else 63 - square
                pst_val = self.knight_pst[sq_idx]
            elif piece.piece_type == chess.PAWN:
                sq_idx = square if piece.color == chess.WHITE else 63 - square
                pst_val = self.pawn_pst[sq_idx]

            # Nếu là quân Trắng -> cộng vào tổng điểm. Nếu là Đen -> trừ đi.
            if piece.color == chess.WHITE:
                score += (val + pst_val)
            else:
                score -= (val + pst_val)

        return score
    # Đồng đội 2 có thể override hàm evaluate_board ở đây để tính thêm vị trí đứng của quân cờ (Piece-Square Tables).

class MLGoodAgent(BaseSearchAgent):
    """
    Dummy ML Agent (Level 3).
    Cần một mô hình Multi-Layer Perceptron (Mạng nơ-ron) xịn và depth cao hơn.
    """
    def __init__(self):
        super().__init__(depth=3) # Nhìn xa hơn để tận dụng mô hình xịn
        self.model = None
        
        # MẪU CODE ĐỂ LOAD MODEL SAU NÀY (Bỏ comment khi đã có file):
        # try:
        #     self.model = joblib.load("good_ml_model.pkl")
        # except FileNotFoundError:
        #     print("Chưa có file good_ml_model.pkl")

    def evaluate_board(self, board: chess.Board) -> float:
        if board.is_checkmate():
            return -99999 if board.turn == chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0
            
        # Dummy behavior
        if self.model is None:
            return 0.0
            
        # TƯƠNG LAI: Viết code gọi model.predict() ở đây
        # features = board_to_features(board)
        # return float(self.model.predict([features])[0])

class GoodAgent(BaseSearchAgent):
    """Level 3: Nhìn trước 4 nước. Tối ưu Move Ordering và Transposition Table (Cache)."""
    
    def __init__(self):
        super().__init__(depth=4) # Nhìn sâu 4 nước
        self.table_cache = {}     # Bộ nhớ đệm giúp tiết kiệm tính toán
        
        # Bảng giá trị vật chất
        self.piece_values = {
            chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
            chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
        }

    def order_moves(self, board: chess.Board, moves: list) -> list:
        """
        [QUAN TRỌNG] Tối ưu thuật toán: Sắp xếp nước đi (Move Ordering).
        Giúp Alpha-Beta Pruning cắt tỉa được cực kỳ nhiều nhánh vô ích.
        """
        def move_guess_score(move):
            score = 0
            # 1. Ưu tiên ăn quân (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
            if board.is_capture(move):
                if board.is_en_passant(move):
                    score += 100
                else:
                    victim = board.piece_at(move.to_square)
                    attacker = board.piece_at(move.from_square)
                    if victim and attacker:
                        # Ăn quân có giá trị cao bằng quân có giá trị thấp -> Điểm cực cao
                        score += 10 * self.piece_values.get(victim.piece_type, 0) - self.piece_values.get(attacker.piece_type, 0)
            
            # 2. Ưu tiên nước phong cấp
            if move.promotion:
                score += 900
                
            # 3. Ưu tiên nước chiếu Vua
            if board.gives_check(move):
                score += 50
                
            return score

        # Sắp xếp danh sách nước đi theo điểm ưu tiên giảm dần
        return sorted(moves, key=move_guess_score, reverse=True)

    def evaluate_board(self, board: chess.Board) -> float:
        """Hàm đánh giá: Vật chất + Kiểm soát trung tâm + Độ cơ động"""
        # Kiểm tra Cache trước để tránh tính lại
        fen = board.fen()
        if fen in self.table_cache:
            return self.table_cache[fen]

        if board.is_checkmate():
            return -99999 if board.turn == chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        score = 0.0
        
        # 1. Tính điểm vật chất và Kiểm soát trung tâm
        for square, piece in board.piece_map().items():
            val = self.piece_values[piece.piece_type]
            
            # Thưởng điểm nếu quân đứng ở 4 ô trung tâm (D4, E4, D5, E5)
            if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                val += 30
            # Thưởng nhẹ nếu đứng ở vòng ngoài trung tâm
            elif square in [chess.C3, chess.C4, chess.C5, chess.C6, 
                            chess.F3, chess.F4, chess.F5, chess.F6]:
                val += 10

            if piece.color == chess.WHITE:
                score += val
            else:
                score -= val

        # 2. Tính độ cơ động (Mobility)
        mobility = len(list(board.legal_moves))
        if board.turn == chess.WHITE:
            score += (mobility * 2)
        else:
            score -= (mobility * 2)

        # Lưu lại vào Cache
        self.table_cache[fen] = score
        return score

    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        """Ghi đè Minimax của BaseSearchAgent để chèn Move Ordering vào"""
        if board.is_checkmate():
            return (-99999 - depth) if board.turn == chess.WHITE else (99999 + depth)
        if board.is_game_over():
            return 0.0
        if depth == 0:
            return self.evaluate_board(board)

        # GỌI HÀM SẮP XẾP NƯỚC ĐI Ở ĐÂY
        ordered_moves = self.order_moves(board, list(board.legal_moves))

        if maximizing_player:
            max_eval = -math.inf
            for move in ordered_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in ordered_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_move(self, board: chess.Board) -> chess.Move:
        """Khởi chạy vòng Minimax đầu tiên kèm Move Ordering"""
        best_move = None
        ordered_moves = self.order_moves(board, list(board.legal_moves))
        if not ordered_moves:
            return None

        maximizing_player = board.turn == chess.WHITE
        best_value = -math.inf if maximizing_player else math.inf

        for move in ordered_moves:
            board.push(move)
            board_value = self.minimax(board, self.depth - 1, -math.inf, math.inf, not maximizing_player)
            board.pop()

            if maximizing_player:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move

        # Fallback an toàn
        if best_move is None:
            best_move = random.choice(ordered_moves)
        return best_move
import chess
import random


class Player:
    def get_move(self, board: chess.Board) -> chess.Move:
        """Hàm ảo. Phải trả về một đối tượng chess.Move hợp lệ."""
        raise NotImplementedError


class RandomAgent(Player):
    def get_move(self, board: chess.Board) -> chess.Move:
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves) if legal_moves else None


class SearchAgent(Player):
    def __init__(self, depth: int):
        self.depth = depth
        # Có thể thêm các tham số level ở đây để đáp ứng yêu cầu 3

    def evaluate_board(self, board: chess.Board) -> float:
        """
        [CHỖ CHO BẠN CẬU VIẾT CODE]
        Hàm đánh giá điểm số của bàn cờ (Heuristic evaluation).
        """
        score = 0.0
        # Thêm logic tính điểm quân cờ, vị trí, kiểm soát trung tâm...
        return score

    def get_move(self, board: chess.Board) -> chess.Move:
        """
        [CHỖ CHO BẠN CẬU VIẾT CODE]
        Triển khai Minimax / Alpha-Beta Pruning tại đây.
        """
        # Placeholder hiện tại: trả về random để cậu test UI trước
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves) if legal_moves else None


# 1. evaluate_board: Kẻ đánh giá hiện trạng (Tĩnh)
# Hàm này hoàn toàn mù tịt về tương lai. Nhiệm vụ duy nhất của nó là nhìn vào một bức ảnh chụp nhanh của bàn cờ ngay tại một thời điểm cụ thể và ném ra một con số (điểm số).
# Bản chất: Nó là một thước đo tĩnh (Static Heuristic). E.x: nNó đếm vật chất (Hậu 9 điểm, Xe 5 điểm...), đánh giá cấu trúc tốt, mức độ an toàn của Vua, độ kiểm soát trung tâm...
# Giới hạn: Nó không biết nước đi trước đó là gì, và cũng hoàn toàn không biết nước tiếp theo ai sẽ ăn quân ai. Nó chỉ nhìn thấy "Vua trắng đang an toàn, quân Trắng hơn 1 con Mã" và phán: +3 điểm cho Trắng. Chấm hết.

# 2. get_move: Bộ não chiến lược (Động)
# Đây mới là nơi AI thực sự "suy nghĩ". Hàm này không tự tay đánh giá bàn cờ. Nó sử dụng thuật toán tìm kiếm (Minimax / Alpha-Beta Pruning) để vạch ra các nhánh tương lai (Game Tree).
# Bản chất: Nó liên tục giả định: "Nếu mình đi nước A, đối thủ sẽ đáp trả bằng B, C, hoặc D. Nếu họ đi B, cục diện sẽ thế nào?".
# Sự kết hợp: get_move đào sâu xuống 3, 4, hoặc 5 lượt đi (Depth). Máy tính không có sức mạnh vô hạn để tính toán đến tận cuối ván cờ. Khi nó chạm đến giới hạn độ sâu mà cậu thiết lập, nó buộc phải dừng lại.
# Đúng tại thời điểm dừng lại đó ở tương lai, nó mới gọi hàm evaluate_board để hỏi: "Đến cái ngã rẽ này rồi, thế cờ đang có lợi cho ai?". Sau đó, nó đẩy điểm số đó ngược lên trên (theo luật Minimax) để đưa ra quyết định xem nước đi ban đầu nào là khôn ngoan nhất.

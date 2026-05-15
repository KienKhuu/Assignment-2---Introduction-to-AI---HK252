import pandas as pd
import numpy as np
import chess
# IMPORT DECISION TREE THAY VÌ RANDOM FOREST
from sklearn.tree import DecisionTreeRegressor 
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

def board_to_features(board: chess.Board):
    features = np.zeros(64)
    piece_values = { chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100 }
    for square, piece in board.piece_map().items():
        val = piece_values[piece.piece_type]
        if piece.color == chess.BLACK:
            val = -val
        features[square] = val
    return features

def main():
    print("1. Đang đọc dữ liệu từ CSV...")
    df = pd.read_csv("chess_data.csv") # NHỚ ĐỔI TÊN FILE CHO ĐÚNG
    
    # Lấy 100,000 dòng. Decision Tree train rất nhanh nên lấy nhiều data cũng không sao.
    df = df.head(500000) 

    print("2. Đang trích xuất đặc trưng (Feature Extraction)...")
    X, y = [], []
    for index, row in df.iterrows():
        try:
            board = chess.Board(row['FEN'])
            X.append(board_to_features(board))
            
            score = str(row['Evaluation'])
            if '#' in score:
                score_val = 9999.0 if '+' in score else -9999.0
            else:
                score_val = float(score)
            y.append(score_val)
        except Exception:
            continue

    X = np.array(X)
    y = np.array(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("3. Đang huấn luyện các mô hình Cây quyết định (Decision Tree)...")
    
    # LEVEL 1: POOR AGENT (Cây rất nông, Underfitting, học ngu)
    print("- Đang train Poor Model (max_depth=5)...")
    poor_model = DecisionTreeRegressor(max_depth=5, random_state=42)
    poor_model.fit(X_train, y_train)
    joblib.dump(poor_model, "poor_model.pkl")

    # LEVEL 2: AVERAGE AGENT (Cây vừa phải)
    print("- Đang train Average Model (max_depth=12)...")
    avg_model = DecisionTreeRegressor(max_depth=12, random_state=42)
    avg_model.fit(X_train, y_train)
    joblib.dump(avg_model, "avg_model.pkl")

    # LEVEL 3: GOOD AGENT (Cây rất sâu, cố gắng fit toàn bộ data)
    print("- Đang train Good Model (max_depth=None)...")
    good_model = DecisionTreeRegressor(max_depth=None, random_state=42)
    good_model.fit(X_train, y_train)
    joblib.dump(good_model, "good_model.pkl")

    print("\nHOÀN TẤT! ")

if __name__ == "__main__":
    main()
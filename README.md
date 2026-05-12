# ⚔️ Hnefatafl — Viking Chess

A Python implementation of **Hnefatafl**, the ancient Viking board game, featuring an AI opponent powered by **Minimax with Alpha-Beta Pruning** and a neon-themed graphical interface built with **Tkinter**.

---

## 📸 Overview

Hnefatafl (pronounced "neh-fah-tah-fl") is an asymmetric strategy game from the Viking Age. One side plays as **Attackers** trying to capture the King, while the other plays as **Defenders** trying to escort the King to a corner of the board.

---

## 🎮 Features

- ♟️ Full Hnefatafl game logic on a **9×9 board**
- 🤖 AI opponent using **Minimax** with **Alpha-Beta Pruning**
- 🎯 Three difficulty levels: **Easy**, **Medium**, **Hard**
- 🖼️ Neon-themed **GUI** built with Python's Tkinter
- ⚔️ Play as **Attackers** or **Defenders**
- 👑 King escape detection and capture logic
- 🏰 Special squares: Throne and Corners
- ✅ Legal move highlighting on click

---

## 🧠 AI Algorithm

The AI is implemented using **Minimax with Alpha-Beta Pruning**:

- **Minimax** explores the game tree to find the optimal move by simulating both players playing perfectly
- **Alpha-Beta Pruning** cuts off branches that cannot affect the final decision, making the search significantly faster
- The AI evaluates positions based on:
  - Piece count (attackers vs defenders)
  - King's distance to corners
  - King's mobility
  - Attackers adjacent to the King
- King escape moves are prioritized above all other moves

| Difficulty | Search Depth |
|---|---|
| Easy | 1 |
| Medium | 3 |
| Hard | 5 |

---

## 📁 Project Structure

```
hnefatafl/
│
├── hnefatafl.py      # Entry point
├── gui.py            # Tkinter GUI (HnefataflGUI class)
├── ai.py             # AlphaBetaAI — Minimax + Alpha-Beta Pruning
├── gameLogic.py      # Game rules, board state, move generation
└── README.md
```

---

## 🕹️ How to Play

### Rules
- **Attackers** start on the edges and move first
- **Defenders** start in the center protecting the King
- All pieces move like rooks in chess (any number of squares orthogonally)
- A piece is captured when sandwiched between two enemies orthogonally
- **Defenders win** if the King reaches any corner
- **Attackers win** if the King is surrounded on all 4 sides

### Controls
1. Click a piece to select it — valid moves are highlighted in blue
2. Click a highlighted square to move
3. The AI responds automatically after your move

---

## 🚀 Getting Started

### Requirements
- Python 3.10+
- Tkinter (included with standard Python installation)

### Run the game

```bash
git clone https://github.com/yourusername/hnefatafl.git
cd hnefatafl
python hnefatafl.py
```

No external dependencies required!

---

## ⚙️ Settings

At the top of the window you can configure:

| Setting | Options |
|---|---|
| Board Size | 9×9 |
| Your Side | Attackers / Defenders |
| Difficulty | Easy / Medium / Hard |

Click **START NEW GAME** to apply settings and begin.

---

## 🎨 GUI Design

The interface uses a **neon dark theme** with:
- Deep space black background
- Cyan, pink, green, and gold neon piece colors
- Special markers for the Throne (center) and corner escape squares
- Glow effects on pieces and selected cells

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

- Inspired by the historical **Viking board game Hnefatafl**
- AI based on the classic **Minimax algorithm** with **Alpha-Beta Pruning** optimization

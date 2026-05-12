import tkinter as tk
from tkinter import messagebox, ttk
from ai import AlphaBetaAI
from gameLogic import DIFFICULTY_DEPTH, Move, Piece, Side, createInitialState
appBackground = "#05050f"
panelBackground = "#0a0a1a"
gridLineColor = "#1a1a3a"
normalCellColor = "#0d0d22"
throneCellColor = "#120a2e"
cornerCellColor = "#0a1f0a"
accentCyan = "#00f5ff"
accentPink = "#ff00aa"
accentGreen = "#00ff88"
accentGold = "#ffe44d"
accentBlue = "#3d5afe"
accentPurple = "#bf5fff"
glowCyanColor = "#00c8d4"
glowPinkColor = "#cc0088"
glowGreenColor = "#00cc66"
primaryTextColor = "#e0e8ff"
secondaryTextColor = "#5060a0"

class HnefataflGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Viking Chess")
        self.root.configure(bg=appBackground)
        self.cellSZ = 60
        self.boardMargin=28
        self.SzVar=tk.StringVar(value="9")
        self.humanSideVar=tk.StringVar(value=Side.DEFENDERS.value)
        self.dificultyChoice=tk.StringVar(value="Medium")
        self.statusVar=tk.StringVar(value="Choose settings and start game.")

        self.state=createInitialState(9)
        self.selectedCell:tuple[int, int]|None=None
        self.validTargets:set[tuple[int, int]]=set()
        self.aiOpponent=AlphaBetaAI(maxDepth=DIFFICULTY_DEPTH[self.dificultyChoice.get()])
        self.applyStyle()
        self.buildControls()
        self.buildBoard()
        self.drawBoard()

    def applyStyle(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Neon.TFrame",background=panelBackground)
        style.configure("Neon.TLabel",background=panelBackground,foreground=secondaryTextColor,font=("Courier New", 9, "bold"))
        style.configure("Title.TLabel",background=appBackground,foreground=accentCyan,font=("Courier New", 11, "bold"))
        style.configure("Status.TLabel",background=appBackground,foreground=accentGreen,font=("Courier New", 10, "bold"),padding=(12, 6))
        style.configure("Neon.TCombobox",fieldbackground=panelBackground,background=panelBackground,foreground=accentCyan,selectbackground=panelBackground,selectforeground=accentCyan,arrowcolor=accentCyan)
        style.map("Neon.TCombobox",fieldbackground=[("readonly", panelBackground)],foreground=[("readonly", accentCyan)],selectbackground=[("readonly", panelBackground)])
        self.btnCfg = dict(bg=panelBackground,fg=accentPink,activebackground=accentPink,activeforeground=appBackground,relief="flat",font=("Courier New", 9, "bold"),
                           padx=14, pady=4,cursor="hand2",bd=1,highlightthickness=1,highlightbackground=accentPink,highlightcolor=accentPink,)
        
    def buildControls(self) -> None:
        frame = ttk.Frame(self.root, style="Neon.TFrame", padding=(10, 8))
        frame.pack(side=tk.TOP, fill=tk.X)
        def lbl(text: str) -> ttk.Label:
            return ttk.Label(frame, text=text, style="Neon.TLabel")
        def combo(var: tk.StringVar, vals: list, w: int) -> ttk.Combobox:
            cb = ttk.Combobox(frame, textvariable=var, values=vals,width=w, state="readonly", style="Neon.TCombobox")
            self.root.option_add("*TCombobox*Listbox.background", panelBackground)
            self.root.option_add("*TCombobox*Listbox.foreground", accentCyan)
            self.root.option_add("*TCombobox*Listbox.selectBackground", accentBlue)
            self.root.option_add("*TCombobox*Listbox.selectForeground", appBackground)
            return cb
        lbl("BOARD:").pack(side=tk.LEFT, padx=(0, 4))
        combo(self.SzVar, ["9"], 4).pack(side=tk.LEFT)
        lbl("  SIDE:").pack(side=tk.LEFT, padx=(8, 4))
        combo(self.humanSideVar,[Side.ATTACKERS.value, Side.DEFENDERS.value], 11).pack(side=tk.LEFT)
        lbl("  DIFF:").pack(side=tk.LEFT, padx=(8, 4))
        combo(self.dificultyChoice, ["Easy", "Medium", "Hard"], 7).pack(side=tk.LEFT)
        tk.Button(frame, text="START NEW GAME",
                  command=self.newGame, **self.btnCfg).pack(side=tk.LEFT, padx=12)
        sep = tk.Frame(self.root, bg=accentBlue, height=1)
        sep.pack(fill=tk.X)
        ttk.Label(self.root, textvariable=self.statusVar,style="Status.TLabel").pack(side=tk.TOP, fill=tk.X)
        tk.Frame(self.root, bg=accentCyan, height=1).pack(fill=tk.X)
    def buildBoard(self) -> None:
        side = self.boardSideLength()
        self.canvas = tk.Canvas(self.root, width=side, height=side,bg=appBackground, highlightthickness=0)
        self.canvas.pack(padx=14, pady=14)
        self.canvas.bind("<Button-1>", self.onClick)
    def drawBoard(self) -> None:
        self.canvas.delete("all")
        self.drawBoardFrame()
        for row in range(self.state.size):
            for col in range(self.state.size):
                x1, y1, x2, y2 = self.cellBounds(row, col)
                self.drawCell(row, col, x1, y1, x2, y2)
    def drawBoardFrame(self) -> None:
        size = self.state.size
        boardMargin = self.boardMargin
        cell = self.cellSZ
        for offset, color in [(6, "#00203a"), (3, "#003355"), (1, accentCyan)]:
            self.canvas.create_rectangle(
                boardMargin - offset, boardMargin - offset,
                boardMargin + size * cell + offset, boardMargin + size * cell + offset,
                outline=color, width=1 if offset > 1 else 2,
            )
    def drawCell(self, row: int, col: int, x1: float, y1: float, x2: float, y2: float) -> None:
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=self.cellFill(row, col),
            outline=gridLineColor,
            width=1,
        )
        if (row, col) in self.state.corners():
            self.drawCornerDecoration(x1, y1, x2, y2)
        if (row, col) == self.state.throne():
            self.drawThroneDecoration(x1, y1, x2, y2)
        if self.selectedCell == (row, col):
            self.drawselectedCellCell(x1, y1, x2, y2)
        elif (row, col) in self.validTargets:
            self.drawTargetCell(x1, y1, x2, y2)
        piece = self.state.getPiece(row, col)
        if piece != Piece.EMPTY:
            self.drawPiece(x1, y1, x2, y2, piece)

    def cellBounds(self, row: int, col: int) -> tuple[float, float, float, float]:
        x1 = self.boardMargin + col * self.cellSZ
        y1 = self.boardMargin + row * self.cellSZ
        return x1, y1, x1 + self.cellSZ, y1 + self.cellSZ
    
    def cellFill(self, row: int, col: int) -> str:
        position = (row, col)
        if position in self.state.corners():
            return cornerCellColor
        if position == self.state.throne():
            return throneCellColor
        return normalCellColor

    def drawCornerDecoration(self, x1: float, y1: float, x2: float, y2: float) -> None:
        pad = 6
        self.canvas.create_rectangle(
            x1 + pad, y1 + pad, x2 - pad, y2 - pad,
            outline=accentGreen, width=2, fill="",)
        self.canvas.create_rectangle(
            x1 + pad + 3, y1 + pad + 3, x2 - pad - 3, y2 - pad - 3,
            outline=glowGreenColor, width=1, fill="",)

    def drawThroneDecoration(self, x1: float, y1: float, x2: float, y2: float) -> None:
        centerX = (x1 + x2) / 2
        centerY = (y1 + y2) / 2
        outer = [centerX, y1 + 6, x2 - 6, centerY, centerX, y2 - 6, x1 + 6, centerY]
        inner = [centerX, y1 + 10, x2 - 10, centerY, centerX, y2 - 10, x1 + 10, centerY]
        self.canvas.create_polygon(outer, outline=accentPurple, fill="", width=2)
        self.canvas.create_polygon(inner, outline=glowCyanColor, fill="", width=1)

    def drawselectedCellCell(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.canvas.create_rectangle(
            x1 + 2, y1 + 2, x2 - 2, y2 - 2,
            outline=accentCyan, width=3, fill="",
        )
        self.canvas.create_rectangle(
            x1 + 5, y1 + 5, x2 - 5, y2 - 5,
            outline=glowCyanColor, width=1, fill="",
        )

    def drawTargetCell(self, x1: float, y1: float, x2: float, y2: float) -> None:
        centerX = (x1 + x2) / 2
        centerY = (y1 + y2) / 2
        radius = 9
        self.canvas.create_oval(
            centerX - radius - 3, centerY - radius - 3,
            centerX + radius + 3, centerY + radius + 3,
            fill="", outline=accentBlue, width=1,
        )
        self.canvas.create_oval(
            centerX - radius, centerY - radius,
            centerX + radius, centerY + radius,
            fill=accentBlue, outline="",
        )

    def drawPiece(self, x1: float, y1: float, x2: float, y2: float, piece: Piece) -> None:
        pad = 8
        px1, py1 = x1 + pad, y1 + pad
        px2, py2 = x2 - pad, y2 - pad
        cx, cy   = (x1 + x2) / 2, (y1 + y2) / 2

        if piece == Piece.ATTACKER:
            for gpad, gcol in [(2, "#440022"), (1, glowPinkColor)]:
                self.canvas.create_oval(px1 - gpad, py1 - gpad,
                                        px2 + gpad, py2 + gpad,
                                        fill="", outline=gcol, width=1)
            self.canvas.create_oval(px1, py1, px2, py2,
                                    fill="#1a0012", outline=accentPink, width=2)
            self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                                    fill=accentPink, outline="")

        elif piece == Piece.DEFENDER:
            for gpad, gcol in [(2, "#003322"), (1, glowGreenColor)]:
                self.canvas.create_oval(px1 - gpad, py1 - gpad,
                                        px2 + gpad, py2 + gpad,
                                        fill="", outline=gcol, width=1)
            self.canvas.create_oval(px1, py1, px2, py2,
                                    fill="#001a10", outline=accentGreen, width=2)
            self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                                    fill=accentGreen, outline="")

        elif piece == Piece.KING:
            for gpad, gcol in [(5, "#332200"), (3, "#886600"), (1, accentGold)]:
                self.canvas.create_oval(px1 - gpad, py1 - gpad,
                                        px2 + gpad, py2 + gpad,
                                        fill="", outline=gcol, width=1)
            self.canvas.create_oval(px1, py1, px2, py2,
                                    fill="#1a1000", outline=accentGold, width=3)
            self.canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6,
                                    fill=accentGold, outline="")
            self.canvas.create_text(cx, cy,
                                    text="K",
                                    font=("Courier New", 11, "bold"),
                                    fill=appBackground)

    @property
    def humanSide(self) -> Side:
        return Side(self.humanSideVar.get())
        #attacker or defender
    @property
    def aiSide(self) -> Side:
        return Side.DEFENDERS if self.humanSide == Side.ATTACKERS else Side.ATTACKERS

    def refreshAiSettings(self) -> None:
        self.aiOpponent.maxDepth = DIFFICULTY_DEPTH[self.dificultyChoice.get()]
        #update diff of ai

    def boardSideLength(self) -> int:
        return self.boardMargin * 2 + self.state.size * self.cellSZ

    def targetsForPiece(self, row: int, col: int) -> set[tuple[int, int]]:
        return {(move.toR, move.toC) for move in self.state.pieceMoves(row, col)}
        #return tuble with all valid moves

    def selectPiece(self, row: int, col: int) -> None:
        self.selectedCell = (row, col)
        self.validTargets = self.targetsForPiece(row, col)
        #calc all valid moves for the selected cell

    def clearSelection(self) -> None:
        self.selectedCell = None
        self.validTargets.clear()

    def newGame(self) -> None:
        self.refreshAiSettings()
        size = int(self.SzVar.get())
        self.state = createInitialState(size)
        self.clearSelection()
        side = self.boardSideLength()
        self.canvas.config(width=side, height=side)
        self.drawBoard()
        self.updateStatus()
        self.root.after(200, self.maybeAiTurn)

    def onClick(self, event: tk.Event) -> None:
        if self.state.winner is not None:
            return
        if self.state.turn != self.humanSide:
            return
        r, c = self.pixelToCell(event.x, event.y)
        if r is None:
            return

        piece = self.state.getPiece(r, c)

        if self.selectedCell is None:
            if self.state.ownsPiece(self.humanSide, piece):
                self.selectPiece(r, c)
                self.drawBoard()
            return

        if (r, c) == self.selectedCell:
            self.clearSelection()
            self.drawBoard()
            return

        if (r, c) in self.validTargets:
            sr, sc = self.selectedCell
            self.state = self.state.applyMove(Move(sr, sc, r, c))
            self.clearSelection()
            self.drawBoard()
            self.updateStatus()
            self.checkEndgamePopup()
            self.root.after(250, self.maybeAiTurn)
            return

        if self.state.ownsPiece(self.humanSide, piece):
            self.selectPiece(r, c)
            self.drawBoard()
            #press on another owned cell clac its valid moves

    def maybeAiTurn(self) -> None:
        if self.state.winner is not None:
            return
        if self.state.turn != self.aiSide:
            return
        self.statusVar.set(f"SYSTEM :: {self.aiSide.value.upper()} Thinking...")
        self.root.update_idletasks()

        self.refreshAiSettings()
        move = self.aiOpponent.chooseMove(self.state)
        if move is None:
            self.state.winner = self.humanSide
        else:
            self.state = self.state.applyMove(move)
        self.drawBoard()
        self.updateStatus()
        self.checkEndgamePopup()

    def updateStatus(self) -> None:
        if self.state.winner is None:
            side = self.state.turn.value.upper()
            you  = " <- YOUR TURN" if self.state.turn == self.humanSide else ""
            self.statusVar.set(f"ACTIVE :: {side}{you}")
        elif self.state.winner == Side.ATTACKERS:
            self.statusVar.set("Attackers Won  ·  KING CAPTURED")
        else:
            self.statusVar.set("Defenders Won  ·  KING ESCAPED")

    def checkEndgamePopup(self) -> None:
        if self.state.winner is None:
            return
        if self.state.winner == Side.ATTACKERS:
            messagebox.showinfo("GAME OVER", "ATTACKERS WIN\nThe King has been captured.")
        else:
            messagebox.showinfo("GAME OVER", "DEFENDERS WIN\nThe King reached a corner.")

    def pixelToCell(self, x: int, y: int) -> tuple[int | None, int | None]:
        x -= self.boardMargin
        y -= self.boardMargin
        if x < 0 or y < 0:
            return None, None
        c = x // self.cellSZ
        r = y // self.cellSZ
        if 0 <= r < self.state.size and 0 <= c < self.state.size:
            return int(r), int(c)
        return None, None


def main() -> None:
    root = tk.Tk()
    root.configure(bg=appBackground)
    app = HnefataflGUI(root)
    app.newGame()
    root.mainloop()


if __name__ == "__main__":
    main()
from enum import Enum


class Piece(str, Enum):
    EMPTY = "."
    ATTACKER = "A"
    DEFENDER = "D"
    KING = "K"


class Side(str, Enum):
    ATTACKERS = "attackers"
    DEFENDERS = "defenders"


DIFFICULTY_DEPTH = {"Easy": 1, "Medium": 3, "Hard": 5}


class Move:
    def __init__(self, fromR: int, fromC: int, toR: int, toC: int):
        self.fromR = fromR
        self.fromC = fromC
        self.toR = toR
        self.toC = toC


class GameState:
    def __init__(
        self,
        size: int,
        board: list[list[Piece]],
        turn: Side,
        winner: Side | None = None,
        kingPos: tuple[int, int] | None = None,
        attackerCount: int = 0,
        defenderCount: int = 0,
    ):
        self.size = size
        self.board = board
        self.turn = turn
        self.winner = winner
        self.kingPos = kingPos
        self.attackerCount = attackerCount
        self.defenderCount = defenderCount

    def center(self) -> tuple[int, int]:
        c = self.size // 2
        return c, c

    def corners(self) -> set[tuple[int, int]]:
        s = self.size - 1
        return {(0, 0), (0, s), (s, 0), (s, s)}

    def throne(self) -> tuple[int, int]:
        return self.center()

    def clone(self) -> "GameState":
        return GameState(
            size=self.size,
            board=[row[:] for row in self.board],
            turn=self.turn,
            winner=self.winner,
            kingPos=self.kingPos,
            attackerCount=self.attackerCount,
            defenderCount=self.defenderCount,
        )

    def inBounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size

    def getPiece(self, r: int, c: int) -> Piece:
        return self.board[r][c]

    def setPiece(self, r: int, c: int, p: Piece) -> None:
        self.board[r][c] = p

    def isSpecial(self, r: int, c: int) -> bool:
        return (r, c) == self.throne() or (r, c) in self.corners()

    def ownsPiece(self, side: Side, piece: Piece) -> bool:
        if side == Side.ATTACKERS:
            return piece == Piece.ATTACKER
        return piece in (Piece.DEFENDER, Piece.KING)

    def enemySide(self, side: Side) -> Side:
        return Side.DEFENDERS if side == Side.ATTACKERS else Side.ATTACKERS

    def isKingOnCorner(self) -> bool:
        for r, c in self.corners():
            if self.getPiece(r, c) == Piece.KING:
                return True
        return False

    def findKing(self) -> tuple[int, int] | None:
        return self.kingPos

    def isWall(self, r: int, c: int) -> bool:
        return r == 0 or c == 0 or r == self.size - 1 or c == self.size - 1


    def pieceMoves(self, r: int, c: int) -> list[Move]:
        piece = self.getPiece(r, c)
        if piece == Piece.EMPTY or not self.ownsPiece(self.turn, piece):
            return []

        moves: list[Move] = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            row = r + dr
            col = c + dc
            while self.inBounds(row, col) and self.getPiece(row, col) == Piece.EMPTY:
                if piece != Piece.KING and self.isSpecial(row, col):
                    row += dr
                    col += dc
                    continue
                moves.append(Move(r, c, row, col))
                row += dr
                col += dc
        return moves

    def legalMoves(self) -> list[Move]:
        allMoves: list[Move] = []
        for r in range(self.size):
            for c in range(self.size):
                allMoves.extend(self.pieceMoves(r, c))
        return allMoves

    def _isHostileSquareForCapture(self, capturer: Side, r: int, c: int) -> bool:
        if not self.inBounds(r, c):
            return False
        piece = self.getPiece(r, c)
        if capturer == Side.ATTACKERS:
            if piece == Piece.ATTACKER:
                return True
            if piece == Piece.EMPTY and self.isSpecial(r, c):
                return True
            return False

        if piece == Piece.DEFENDER:
            return True
        if piece == Piece.EMPTY and self.isSpecial(r, c):
            return True
        return False

    def applyMove(self, move: Move) -> "GameState":
        newState = self.clone()
        movingPiece = newState.getPiece(move.fromR, move.fromC)
        newState.setPiece(move.fromR, move.fromC, Piece.EMPTY)
        newState.setPiece(move.toR, move.toC, movingPiece)
        if movingPiece == Piece.KING:
            newState.kingPos = (move.toR, move.toC)

        if movingPiece != Piece.KING and newState.isSandwichedByEnemies(move.toR, move.toC):
            newState.setPiece(move.toR, move.toC, Piece.EMPTY)
            if movingPiece == Piece.ATTACKER:
                newState.attackerCount -= 1
            elif movingPiece == Piece.DEFENDER:
                newState.defenderCount -= 1
        else:
            newState.captureAfterMove(move.toR, move.toC)

        if newState.isKingOnCorner():
            newState.winner = Side.DEFENDERS
            return newState

        kingPos = newState.findKing()
        if kingPos is None:
            newState.winner = Side.ATTACKERS
            return newState
        if newState.isKingCaptured(*kingPos):
            newState.setPiece(kingPos[0], kingPos[1], Piece.EMPTY)
            newState.kingPos = None
            newState.winner = Side.ATTACKERS
            return newState

        newState.turn = newState.enemySide(newState.turn)
        if not newState.legalMoves():
            newState.winner = newState.enemySide(newState.turn)
        return newState

    def captureAfterMove(self, r: int, c: int) -> None:
        movingPiece = self.getPiece(r, c)
        capturer = Side.ATTACKERS if movingPiece == Piece.ATTACKER else Side.DEFENDERS
        enemySide = self.enemySide(capturer)

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            enemyR, enemyC = r + dr, c + dc
            behindR, behindC = r + 2 * dr, c + 2 * dc
            if not self.inBounds(enemyR, enemyC):
                continue
            target = self.getPiece(enemyR, enemyC)
            if target == Piece.EMPTY or target == Piece.KING:
                continue
            if not self.ownsPiece(enemySide, target):
                continue
            if self._isHostileSquareForCapture(capturer, behindR, behindC):
                self.setPiece(enemyR, enemyC, Piece.EMPTY)
                if target == Piece.ATTACKER:
                    self.attackerCount -= 1
                elif target == Piece.DEFENDER:
                    self.defenderCount -= 1

    def isSandwichedByEnemies(self, r: int, c: int) -> bool:
        if not self.inBounds(r, c):
            return False

        mover = self.getPiece(r, c)
        if mover in (Piece.EMPTY, Piece.KING):
            return False

        if mover == Piece.ATTACKER:
            enemyPieces = {Piece.DEFENDER, Piece.KING}
        else:
            enemyPieces = {Piece.ATTACKER}

        left = (r, c - 1)
        right = (r, c + 1)
        if self.inBounds(*left) and self.inBounds(*right):
            if self.getPiece(*left) in enemyPieces and self.getPiece(*right) in enemyPieces:
                return True

        up = (r - 1, c)
        down = (r + 1, c)
        if self.inBounds(*up) and self.inBounds(*down):
            if self.getPiece(*up) in enemyPieces and self.getPiece(*down) in enemyPieces:
                return True
        return False

    def isKingCaptured(self, kr: int, kc: int) -> bool:
        if not self.inBounds(kr, kc):
            return False
        if self.getPiece(kr, kc) != Piece.KING:
            return False
        throneR, throneC = self.throne()
        throneAdjacent = abs(kr - throneR) + abs(kc - throneC) == 1

        specialWallCapture = self.isWall(kr, kc) and self.defenderCount == 0

        blocked = 0
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            nr, nc = kr + dr, kc + dc
            if not self.inBounds(nr, nc):
                if specialWallCapture:
                    blocked += 1
                continue

            if self.getPiece(nr, nc) == Piece.ATTACKER:
                blocked += 1
                continue

            if throneAdjacent and (nr, nc) == (throneR, throneC):
                blocked += 1

        if specialWallCapture:
            return blocked >= 3
        return blocked >= 4


def createInitialState(size: int = 9) -> GameState:
    if size != 9:
        raise ValueError("Board size must be 9.")

    board = [[Piece.EMPTY for _ in range(size)] for _ in range(size)]
    c = size // 2
    board[c][c] = Piece.KING

    defenderOffsets = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-2, 0),
        (2, 0),
        (0, -2),
        (0, 2),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]
    for dr, dc in defenderOffsets:
        board[c + dr][c + dc] = Piece.DEFENDER

    for col in range(c - 2, c + 3):
        board[0][col] = Piece.ATTACKER

    board[1][c] = Piece.ATTACKER

    for row in range(2, 7):
        board[row][0] = Piece.ATTACKER
        board[row][size - 1] = Piece.ATTACKER

    board[c][1] = Piece.ATTACKER
    board[c][size - 2] = Piece.ATTACKER

    for col in range(c - 2, c + 3):
        board[size - 1][col] = Piece.ATTACKER

    board[size - 2][c] = Piece.ATTACKER

    return GameState(
        size=size,
        board=board,
        turn=Side.ATTACKERS,
        kingPos=(c, c),
        attackerCount=24,
        defenderCount=12,
    )
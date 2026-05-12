import math
from gameLogic import GameState, Move, Piece, Side

class AlphaBetaAI:
    def __init__(self, maxDepth: int):
        self.maxDepth = maxDepth
        self.rootSide: Side | None = None

    def chooseMove(self, state: GameState) -> Move | None:
        if state.winner is not None:
            return None

        if isinstance(state, GameState):
            escapeMove: Move | None = None
            escapeDistance: int | None = None
            for move in state.legalMoves():
                piece = state.getPiece(move.fromR, move.fromC)
                if piece != Piece.KING:
                    continue
                if (move.toR, move.toC) not in state.corners():
                    continue

                distance = abs(move.toR - move.fromR) + abs(move.toC - move.fromC)
                if escapeDistance is None or distance < escapeDistance:
                    escapeMove = move
                    escapeDistance = distance

            if escapeMove is not None:
                return escapeMove

        self.rootSide = state.turn

        rootValue = self._maxValue(state, self.maxDepth, -math.inf, math.inf)

        for mv in state.legalMoves():
            child = state.applyMove(mv)
            childValue = self._minValue(child, self.maxDepth - 1, -math.inf, math.inf)
            if self._closeEnough(childValue, rootValue):
                return mv
        return None

    def _utility(self, state: GameState) -> float:
        base = self.evaluate(state)
        if self.rootSide == Side.ATTACKERS:
            return base
        return -base

    def _closeEnough(self, a: float, b: float) -> bool:
        return abs(a - b) < 1e-6

    def _maxValue(self, state: GameState, depth: int, alpha: float, beta: float) -> float:
        if state.winner is not None:
            return self._utility(state)

        if depth == 0:
            return self._utility(state)

        v = -math.inf
        for mv in state.legalMoves():
            child = state.applyMove(mv)
            childV = self._minValue(child, depth - 1, alpha, beta)
            if childV > v:
                v = childV

            if v >= beta:
                return v

            if alpha < v:
                alpha = v
        return v

    def _minValue(self, state: GameState, depth: int, alpha: float, beta: float) -> float:
        if state.winner is not None:
            return self._utility(state)

        if depth == 0:
            return self._utility(state)

        v = math.inf
        for mv in state.legalMoves():
            child = state.applyMove(mv)
            childV = self._maxValue(child, depth - 1, alpha, beta)
            if childV < v:
                v = childV

            if v <= alpha:
                return v

            if beta > v:
                beta = v
        return v

    def evaluate(self, state: GameState) -> float:
        if state.winner == Side.ATTACKERS:
            return 100_000
        if state.winner == Side.DEFENDERS:
            return -100_000

        kingPos = state.findKing()
        if kingPos is None:
            return 100_000
        attackers, defenders = state.attackerCount, state.defenderCount

        kr, kc = kingPos

        minDistance: int | None = None
        for cornerR, cornerC in state.corners():
            distance = abs(kr - cornerR) + abs(kc - cornerC)
            if minDistance is None or distance < minDistance:
                minDistance = distance
        distToCorner = minDistance if minDistance is not None else 0

        kingMobility = self._kingMobility(state, kr, kc)

        adjacentAttackers = 0
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            nr, nc = kr + dr, kc + dc
            if state.inBounds(nr, nc) and state.getPiece(nr, nc) == Piece.ATTACKER:
                adjacentAttackers += 1

        score = 0.0
        score += 50.0 * (attackers - defenders)
        score += 40.0 * adjacentAttackers
        score += 8.0 * distToCorner
        score -= 25.0 * kingMobility
        return score

    def _kingMobility(self, state: GameState, kr: int, kc: int) -> int:
        mobility = 0
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            nr, nc = kr + dr, kc + dc
            while state.inBounds(nr, nc) and state.getPiece(nr, nc) == Piece.EMPTY:
                mobility += 1
                nr += dr
                nc += dc
        return mobility
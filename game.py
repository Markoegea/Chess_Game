import numpy as np
from pieces import Square, Pawn, Rook, Knight, Bishop, Queen, King
import datetime
class GameState():

    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 characters.
        #The first character represents the color of the piece, 'b' or 'w'
        #The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N' or 'P'
        #"--" represent and empty space with no piece
        self.board = [
            [Square('bR'), Square('bN'), Square('bB'), Square('bQ'), Square('bK'), Square('bB'), Square('bN'), Square('bR')],
            [Square('bp'), Square('bp'), Square('bp'), Square('bp'), Square('bp'), Square('bp'), Square('bp'), Square('bp')],
            [Square(), Square(), Square(), Square(), Square(), Square(), Square(), Square()],
            [Square(), Square(), Square(), Square(), Square(), Square(), Square(), Square()],
            [Square(),      Square(),       Square(),       Square(),       Square(),       Square(),       Square(),       Square()],
            [Square(),      Square(),       Square(),       Square(),       Square(),       Square(),       Square(),       Square()],
            [Square('wp'), Square('wp'), Square('wp'), Square('wp'), Square('wp'), Square('wp'), Square('wp'), Square('wp')],
            [Square('wR'), Square('wN'), Square('wB'), Square('wQ'), Square('wK'), Square('wB'), Square('wN'), Square('wR')],
        ]
        self.moveLog = []
        self.whiteToMove = True

    def getLastMove(self):
        if len(self.moveLog) != 0:
            return self.moveLog[-1]
        return None

    def encode_board(self, board):
        encoded = np.zeros([8, 8, 22]).astype(int)
        encoder_dict = {"bR":0, "bN":1, "bB":2, "bQ":3, "bK":4, "bp":5, "wR":7, "wN":8, "wB":9, "wQ":10, "wK":11, "wp":12}
        for i in range(8):
            for j in range(8):
                if board[i][j] != None:
                    encoded[i,j,encoder_dict[board[i][j]]] = 1
        encoded[:,:,12] = 1
        return encoded
    
    def makeMove(self, move, gameController):
        move.pieceMoved.makeMove(move, self.board, gameController)
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if not self.isSpecialCase(move):
            gameController.drawGameState()
            gameController.animatedMove(move)

    def undoMove(self, gameController):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            move.pieceMoved.undoMoves(move, self.board, gameController) 
            self.whiteToMove = not self.whiteToMove
            gameController.drawGameState()

    def isSpecialCase(self, move):
        if isinstance(move, Pawn.Move):
            if move.pawnPromotion:
                return True
        return False

    def getValidMoves(self, gameController):
        # 1. 0:00:00.000997  Hours
        # 2. 0:00:00.005020  Hours
        self.resetRange(gameController)
        self.getAllEnemysMoves(gameController)
        moves = self.getAllPlayerMoves()
        for move in reversed(moves):
            if self.isSpecialCase(move):
                continue
            move.pieceMoved.makeMove(move, self.board, gameController)
            self.whiteToMove = not self.whiteToMove
            enemyMoves = self.getAllPlayerMoves()
            if self.validateDanger(enemyMoves):
                moves.remove(move)
            move.pieceMoved.undoMoves(move, self.board, gameController) 
            self.whiteToMove = not self.whiteToMove
        if len(moves) == 0:
            gameController.gameOver = True

        return moves

    def validateDanger(self, enemyMoves):
        for move in enemyMoves:
            if move.enemyKingInRange:
                return True
        return False
    
    def getAllPlayerMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] != None: 
                    turn = self.board[r][c].piece.playerColor
                    if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                        moves += self.board[r][c].piece.getMoves(r, c, self.board, self)
        return moves
    
    def getAllEnemysMoves(self, gameController):
        moves = []
        self.whiteToMove = not self.whiteToMove
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] != None: 
                    turn = self.board[r][c].piece.playerColor
                    if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                        moves += self.board[r][c].piece.getMoves(r, c, self.board, self)
        for move in moves:
            self.board[move.endRow][move.endCol].inDanger = True
            if move.enemyKingInRange:
                move.pieceCaptured.kingInDanger = True
                gameController.drawGameState()
        self.whiteToMove = not self.whiteToMove
        
    def resetRange(self, gameController):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                self.board[r][c].inDanger = False
                if isinstance(self.board[r][c].piece, King):
                    self.board[r][c].piece.kingInDanger = False
        gameController.drawGameState()

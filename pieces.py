from abc import ABC, abstractmethod

class Square():
    def __init__(self, piece=None):
        if piece == None:
            self.piece = None
        elif piece[1] == 'p':
            self.piece = Pawn(piece)
        elif piece[1] == 'R':
            self.piece = Rook(piece)
        elif piece[1] == 'N':
            self.piece = Knight(piece)
        elif piece[1] == 'B':
            self.piece = Bishop(piece)
        elif piece[1] == 'Q':
            self.piece = Queen(piece)
        elif piece[1] == 'K':
            self.piece = King(piece)
        self.inDanger = False
    
    def __eq__(self, value) -> bool:
        return self.piece == value
    
    def __repr__(self) -> str:
        return self.piece.__repr__()
    
    def resetSquare(self):
        self.inDanger = False

class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1":7, "2":6, "3":5, "4":4,
                   "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                   "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol].piece
        self.pieceCaptured = board[self.endRow][self.endCol].piece
        self.enemyKingInRange = self.checkKing()
        self.moveID = '{}{}{}{}'.format(self.startRow,self.startCol,self.endRow,self.endCol)

    def __eq__(self, other) -> bool:
        if isinstance(other, Move):
            return int(self.moveID) == int(other.moveID)
        
    def __repr__(self) -> str:
        return str(self.moveID)

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def checkKing(self):
        if isinstance(self.pieceCaptured, King):
            return True
        return False

class Pieces(ABC):
    def __init__(self, name):
        self.playerColor = name[0]
        self.pieceName = name[1]
        self.pieceMoves = []

    @abstractmethod
    def getMoves(self, r, c, board, gameState):
        pass

    def createMoves(self, r, c, board, direction, player_color, enemy_color):
        i = direction[0]
        j = direction[1]
        condition = False
        while not condition:
            condition = 0 > (r + i) or (r + i) > 7 or 0 > (c + j) or (c + j) > 7

            if condition:
                break

            if board[r+i][c+j] != None and board[r+i][c+j].piece.playerColor == player_color:
                break

            self.pieceMoves.append(Move((r,c), (r+i,c+j), board))
            if board[r+i][c+j] != None and board[r+i][c+j].piece.playerColor == enemy_color:
                break

            i += direction[0]
            j += direction[1]

    def makeMove(self, move, board, gameController):
        board[move.startRow][move.startCol].piece = None
        board[move.endRow][move.endCol].piece = move.pieceMoved

    def undoMoves(self, move, board, gameController):
        board[move.startRow][move.startCol].piece = move.pieceMoved
        board[move.endRow][move.endCol].piece = move.pieceCaptured

    def __repr__(self) -> str:
        return self.playerColor + self.pieceName

class Pawn(Pieces):
    def __init__(self, name):
        super().__init__(name)

    class Move(Move):
        def __init__(self, startSq, endSq, board):
            super().__init__(startSq, endSq, board)
            # En passant Move
            self.enPassant = False
            self.passantRow = None
            self.passantCol = None
            # Pawn promotion Move
            self.pawnPromotion = self.canPawnPromoted()
            self.piecePromoted = None

        def canPawnPromoted(self):
            if (self.endRow == 0 and self.pieceMoved == 'wp') or (self.endRow == 7 and self.pieceMoved == 'bp'):
                return True
            return False    

    def getMoves(self, r, c, board, gameState):
        self.pieceMoves = []

        if gameState.whiteToMove:
            if r-1 >= 0 and board[r-1][c] == None:
                self.pieceMoves.append(self.Move((r, c), (r-1, c), board))

                if r == 6 and board[r-2][c] == None:
                    self.pieceMoves.append(self.Move((r,c), (r-2, c), board))

            if c-1 >= 0 and r-1 >= 0:
                canEnPassant = self.canEnPassant(r, c-1, gameState)
                if board[r-1][c-1] != None:
                    if board[r-1][c-1].piece.playerColor == 'b':
                        self.pieceMoves.append(self.Move((r, c), (r-1, c-1), board))
                elif canEnPassant:
                    move = self.Move((r, c), (r-1, c-1), board)
                    self.pieceMoves.append(self.enPassant(r,c-1, board[r][c-1].piece, move))

            if c+1 <= 7 and r-1 >= 0:
                canEnPassant = self.canEnPassant(r, c+1, gameState)
                if board[r-1][c+1] != None:
                    if board[r-1][c+1].piece.playerColor == 'b':
                        self.pieceMoves.append(self.Move((r, c), (r-1,c+1), board))
                elif canEnPassant:
                    move = self.Move((r, c), (r-1, c+1), board)
                    self.pieceMoves.append(self.enPassant(r, c+1, board[r][c+1].piece, move))

        elif not gameState.whiteToMove:
            if r+1 <= 7 and board[r+1][c] == None:
                self.pieceMoves.append(self.Move((r, c), (r+1, c), board))

                if r == 1 and board[r+2][c] == None:
                    self.pieceMoves.append(self.Move((r,c), (r+2, c), board))

            if c-1 >= 0 and r+1 <= 7:
                canEnPassant = self.canEnPassant(r, c-1, gameState)
                if board[r+1][c-1] != None:
                    if board[r+1][c-1].piece.playerColor == 'w':
                        self.pieceMoves.append(self.Move((r, c), (r+1, c-1), board))
                elif canEnPassant:
                    move = self.Move((r, c), (r+1, c-1), board)
                    self.pieceMoves.append(self.enPassant(r, c-1, board[r][c-1].piece, move))

            if c+1 <= 7 and r+1 <= 7:
                canEnPassant = self.canEnPassant(r, c+1, gameState)
                if board[r+1][c+1] != None:
                    if board[r+1][c+1].piece.playerColor == 'w':
                        self.pieceMoves.append(self.Move((r, c), (r+1,c+1), board))
                elif canEnPassant:
                    move = self.Move((r, c), (r+1, c+1), board)
                    self.pieceMoves.append(self.enPassant(r, c+1, board[r][c+1].piece, move))

        return self.pieceMoves 
    
    def pawnPromotion(self, move, board, piece):
        r = move.endRow
        c = move.endCol
        move.piecePromoted = piece
        board[r][c].piece = piece

    def canEnPassant(self, r, c, gameState):
        lastMove = gameState.getLastMove()
        if lastMove == None:
            return False
        lastMoveCondition = abs(lastMove.endRow - lastMove.startRow) == 2 and lastMove.pieceMoved.pieceName == 'p'
        currentMoveCondition = lastMove.endRow == r and c == lastMove.endCol
        playerCondition = 'b' if gameState.whiteToMove else 'w'
        if lastMoveCondition and currentMoveCondition and lastMove.pieceMoved.playerColor == playerCondition:
            return True
        return False
    
    def enPassant(self, r, c, piece, move):
        move.pieceCaptured = piece
        move.passantRow = r
        move.passantCol = c
        move.enPassant = True
        return move
    
    def makeMove(self, move, board, gameController):
        super().makeMove(move, board, gameController)
        if move.enPassant:
            board[move.passantRow][move.passantCol].piece = None
        if move.canPawnPromoted():
            gameController.loadButtons((move.endRow, move.endCol), self.playerColor)
            gameController.createButton()

    def undoMoves(self, move, board, gameController):
        super().undoMoves(move, board, gameController)
        if move.enPassant:
            board[move.endRow][move.endCol].piece = None
            board[move.passantRow][move.passantCol].piece = move.pieceCaptured

    def __eq__(self, value) -> bool:
        return self.playerColor + self.pieceName == value
    
    def __str__(self) -> str:
        return self.playerColor + self.pieceName


class Rook(Pieces):
    def __init__(self, name):
        super().__init__(name)
        self.rookMovements = []    

    def getMoves(self, r, c, board, gameState):
        self.pieceMoves = []
        directions = ((1,0),(-1,0),(0,1),(0,-1))

        if gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'w', 'b')

        elif not gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'b', 'w')

        return self.pieceMoves
    
    def hasRookMove(self):
        if len(self.rookMovements) >= 1:
            return True
        return False
    
    def makeMove(self, move, board, gameController):
        super().makeMove(move, board, gameController)
        self.rookMovements.append(move)

    def undoMoves(self, move, board, gameController):
        super().undoMoves(move, board, gameController)
        self.rookMovements.remove(move)

    def __eq__(self, value) -> bool:
        return self.playerColor + self.pieceName == value
    
    def __str__(self) -> str:
        return self.playerColor + self.pieceName

class Knight(Pieces):
    def __init__(self, name):
        super().__init__(name)

    def getMoves(self, r, c, board, gameState):
        self.pieceMoves = []
        directions = ((1,2),(-1,2),(1,-2),(-1,-2),(2,1),(-2,1),(2,-1),(-2,-1))

        if gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'w', 'b')

        elif not gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'b', 'w')

        return self.pieceMoves

    def createMoves(self, r, c, board, direction, player_color, enemy_color):
        i = direction[0]
        j = direction[1]
        condition = 0 > (r + i) or (r + i) > 7 or 0 > (c + j) or (c + j) > 7
        if not condition and (board[r+i][c+j] == None or board[r+i][c+j].piece.playerColor != player_color):
            self.pieceMoves.append(Move((r,c), (r+i, c+j), board))
    
    def makeMove(self, move, board, gameController):
        super().makeMove(move, board, gameController)

    def undoMoves(self, move, board, gameController):
        super().undoMoves(move, board, gameController)

    def __eq__(self, value) -> bool:
        return self.playerColor + self.pieceName == value
    
    def __str__(self) -> str:
        return self.playerColor + self.pieceName
    
class Bishop(Pieces):
    def __init__(self, name):
        super().__init__(name)

    def getMoves(self, r, c, board, gameState):
        self.pieceMoves = []
        directions = ((1, 1), (-1, 1), (1, -1), (-1, -1))

        if gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'w', 'b')

        elif not gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'b', 'w')

        return self.pieceMoves
    
    def makeMove(self, move, board, gameController):
        super().makeMove(move, board, gameController)

    def undoMoves(self, move, board, gameController):
        super().undoMoves(move, board, gameController)

    def __eq__(self, value) -> bool:
        return self.playerColor + self.pieceName == value
    
    def __str__(self) -> str:
        return self.playerColor + self.pieceName

class Queen(Pieces):
    def __init__(self, name):
        super().__init__(name)

    def getMoves(self, r, c, board, gameState):
        self.pieceMoves = []
        directions = ((1, 1), (-1, 1), (1, -1), (-1, -1), (1,0), (-1,0), (0,1), (0,-1))

        if gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'w', 'b')

        elif not gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'b', 'w')

        return self.pieceMoves
    
    def makeMove(self, move, board, gameController):
        super().makeMove(move, board, gameController)

    def undoMoves(self, move, board, gameController):
        super().undoMoves(move, board, gameController)

    def __eq__(self, value) -> bool:
        return self.playerColor + self.pieceName == value
    
    def __str__(self) -> str:
        return self.playerColor + self.pieceName
    
class King(Pieces):
    def __init__(self, name):
        super().__init__(name)
        self.kingMovements = []
        self.kingInDanger = False

    class Move(Move):
        def __init__(self, startSq, endSq, board, kingSq=None, rookSq=None):
            super().__init__(startSq, endSq, board)
            # Castling Move
            self.realKingRow, self.realKingCol, self.realRookRow, self.realRookCol = self.canCastling(kingSq, rookSq)

        def canCastling(self, kingSq, rookSq):
            if kingSq == None or rookSq == None:
                return None, None, None, None
            return kingSq[0], kingSq[1], rookSq[0], rookSq[1]

    def getMoves(self, r, c, board, gameState):
        self.pieceMoves = []
        directions = ((1, 1), (-1, 1), (1, -1), (-1, -1), (1,0), (-1,0), (0,1), (0,-1))

        if gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'w', 'b')

        elif not gameState.whiteToMove:
            for d in directions:
                self.createMoves(r, c, board, d, 'b', 'w')
            
        self.castlingKing(r, c, board, gameState.whiteToMove)

        return self.pieceMoves

    def createMoves(self, r, c, board, direction, player_color, enemy_color):
        i = direction[0]
        j = direction[1]
        if (0 <= (r + i) <= 7 and 0 <= (c + j) <= 7) and (board[r+i][c+j] == None or board[r+i][c+j].piece.playerColor != player_color):
            self.pieceMoves.append(self.Move((r, c), (r+i, c+j), board))

    def castlingKing(self,r, c, board, whiteToMove):
        def checkMove(j:int, finishCol, kingRow, rookRow):
            for i in range(c+j,finishCol,j):
                square = board[r][i]
                if square.inDanger:
                    return
                if square.piece == None:
                    continue
                return
            piece = board[r][finishCol].piece
            if piece == None or piece.playerColor != playerColor or piece.hasRookMove():
                return
            self.pieceMoves.append(self.Move((r, c), (r, finishCol), board, (r,kingRow),(r,rookRow)))

        if self.hasKingMove() or self.kingInDanger or c != 4:
            return
        
        playerColor = 'w' if whiteToMove else 'b'
        checkMove(1, 7, 6, 5)
        checkMove(-1, 0, 2, 3)
            
    def hasKingMove(self):
        if len(self.kingMovements) >= 1:
            return True
        return False
    
    def makeMove(self, move, board, gameController):
        self.kingMovements.append(move)
        if move.realKingRow != None and move.realRookRow != None:
            board[move.realKingRow][move.realKingCol].piece = move.pieceMoved
            board[move.realRookRow][move.realRookCol].piece = move.pieceCaptured
            board[move.startRow][move.startCol].piece = None
            board[move.endRow][move.endCol].piece = None
        else:
            super().makeMove(move, board, gameController)

    def undoMoves(self, move, board, gameController):
        super().undoMoves(move, board, gameController)
        self.kingMovements.remove(move)
        if move.realKingRow != None and move.realRookRow != None:
            board[move.realKingRow][move.realKingCol].piece = None
            board[move.realRookRow][move.realRookCol].piece = None 

    def __eq__(self, value) -> bool:
        return self.playerColor + self.pieceName == value
    
    def __str__(self) -> str:
        return self.playerColor + self.pieceName
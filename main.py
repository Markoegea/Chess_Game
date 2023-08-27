import pygame as p
import game
import pieces

class Button:
    def __init__(self, value, image, width, height, position):
        self.value = value
        self.image = image
        self.width = width
        self.height = height
        self.position = position
        self.drawed = False

    def draw(self, screen):
        self.drawed = True
        p.draw.rect(screen, (255,255,255), (self.position[0], self.position[1], self.width, self.height))
        screen.blit(self.image, p.Rect(self.position[0]-5, self.position[1]-10, self.width, self.height))

    def is_clicked(self, mouse_pos):
        if self.position[0] < mouse_pos[0] < self.position[0] + self.width and \
            self.position[1] < mouse_pos[1] < self.position[1] + self.height:
            return True
        return False
    
    def create_piece(self, color):
        if self.value[1] == 'B':
            return pieces.Bishop(color+self.value[1])
        elif self.value[1] == 'Q':
            return pieces.Queen(color+self.value[1])
        elif self.value[1] == 'N':
            return pieces.Knight(color+self.value[1])
        elif self.value[1] == 'R':
            return pieces.Rook(color+self.value[1])
        else:
            return None

class GameController():
    
    def __init__(self):
        self.WIDTH = 512
        self.HEIGHT = 512
        self.DIMENSION = 8
        self.SQ_SIZE = self.HEIGHT // self.DIMENSION
        self.MAX_FPS = 15 # for animation later on
        self.IMAGES = {}
        self.promotion_buttons = {}
        self.screen = p.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = p.time.Clock()
        self.screen.fill(p.Color('white'))
        self.gs = game.GameState()
        self.board = self.gs.board
        self.gameOver = False
        self.loadImages()
        p.init()

    def resetGame(self):
        self.promotion_buttons = {}
        self.gs = game.GameState()
        self.board = self.gs.board
        self.gameOver = False

    def loadImages(self):
        pieces = ['bB', 'bK', 'bN', 'bp', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wp', 'wQ', 'wR']
        for piece in pieces:
            self.IMAGES[piece] = p.transform.scale(p.image.load('pixel_chess/pieces/'+ piece + ".png"), (self.SQ_SIZE, self.SQ_SIZE))

    def run(self):
        moves = self.gs.getValidMoves(self)
        running = True
        moveMade = False
        sqSelected = ()
        playerClicks = []
        self.drawGameState()
        while running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False

                elif e.type == p.MOUSEBUTTONDOWN and not self.gameOver:
                    location = p.mouse.get_pos() # (x, y) location of mouse

                    if len(self.promotion_buttons) <= 0:
                        col = location[0] // self.SQ_SIZE
                        row = location[1] // self.SQ_SIZE

                        if sqSelected == (row, col): # the user clicked the same square twice
                            sqSelected = ()
                            playerClicks = []

                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)

                            if len(playerClicks) == 2: # after 2nd click
                                move = '{}{}{}{}'.format(playerClicks[0][0], playerClicks[0][1], playerClicks[1][0], playerClicks[1][1])
                                for validMove in moves:
                                    if validMove.moveID == move:
                                        print(validMove.getChessNotation())
                                        self.gs.makeMove(validMove, self)
                                        moveMade = True
                                        sqSelected = ()
                                        playerClicks = []
                                        break
                            if not moveMade:
                                playerClicks = [sqSelected]

                        if len(playerClicks) == 1:
                            r, c = playerClicks[0][0], playerClicks[0][1]
                            self.drawGameState(r, c,self.board[r][c].piece)
            
                    else:
                        lastMove = self.gs.getLastMove()
                        moveMade = self.promotionBehavior(lastMove.pieceMoved, location, lastMove)

                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z: 
                        self.gs.undoMove(self)
                        moveMade = True
                        if self.gameOver:
                            self.gameOver = False
                    if e.key == p.K_r:
                        self.resetGame()
                        moves = self.gs.getValidMoves(self)
                        moveMade = False
                        sqSelected = ()
                        playerClicks = []

            if moveMade and len(self.promotion_buttons) <= 0:
                moves = self.gs.getValidMoves(self)
                moveMade = False
                if self.gameOver:
                    if self.gs.whiteToMove:
                        text = 'Black Wins by CheckMate'
                    else:
                        text = 'White Wins by CheckMate'
                    self.drawText(text)

            self.clock.tick(self.MAX_FPS)
            p.display.flip()

    def drawText(self, text):
        font = p.font.SysFont('Helvetica', 32, True, False)
        textObject = font.render(text, 0, p.Color('orange'))
        textLocation = p.Rect(0, 0, self.WIDTH, self.HEIGHT).move(self.WIDTH/2 - textObject.get_width()/2, self.HEIGHT/2 - textObject.get_height()/2)
        self.screen.blit(textObject, textLocation)
        textObject = font.render(text, 0, p.Color('yellow'))
        self.screen.blit(textObject, textLocation.move(2, 2))

    def drawGameState(self, r=None, c=None, piece=None):
        self.drawBoard() # draw squares on the board
        self.drawMoveSuggestions(r, c, piece)
        self.drawPieces() # draw pieces on top of those squares

    def drawMoveSuggestions(self, r, c, piece):
        if piece == None:
            return
        if piece.playerColor == ('w' if self.gs.whiteToMove else 'b'):
            color = p.Color('orange')
            s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
            s.set_alpha(100)
            s.fill(color)
            self.screen.blit(s, (c*self.SQ_SIZE, r*self.SQ_SIZE))
            for move in piece.pieceMoves:
                p.draw.circle(self.screen, color, ((self.SQ_SIZE*move.endCol)+self.SQ_SIZE//2, (move.endRow*self.SQ_SIZE)+self.SQ_SIZE//2), 17.25)

    def drawBoard(self):
        colors = [p.Color('blue'), p.Color('white')]
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                color = colors[((r + c) % 2)]
                p.draw.rect(self.screen, color, p.Rect(c*self.SQ_SIZE, r*self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))

    def drawPieces(self):
        color = p.Color('red')
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                piece = self.board[r][c]
                if piece.piece != None:
                    if isinstance(piece.piece, pieces.King):
                        if piece.piece.kingInDanger:
                            p.draw.rect(self.screen, color, p.Rect(c*self.SQ_SIZE, r*self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
                    self.screen.blit(self.IMAGES[str(piece)], p.Rect(c*self.SQ_SIZE, r*self.SQ_SIZE - 10, self.SQ_SIZE, self.SQ_SIZE))

    def animatedMove(self, move):
        colors = [p.Color('blue'), p.Color('white')]
        dR = move.endRow - move.startRow
        dC = move.endCol - move.startCol
        frameCount = (abs(dR) + abs(dC)) * self.MAX_FPS
        for frame in range(frameCount + 1):
            r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
            self.drawBoard()
            self.drawPieces()
            color = colors[(move.endRow + move.endCol) % 2]
            endSquare = p.Rect(move.endCol*self.SQ_SIZE, move.endRow*self.SQ_SIZE - 10, self.SQ_SIZE, self.SQ_SIZE)
            p.draw.rect(self.screen, color, endSquare)
            if move.pieceCaptured != None:
                self.screen.blit(self.IMAGES[str(move.pieceCaptured)], endSquare)
            self.screen.blit(self.IMAGES[str(move.pieceMoved)], p.Rect(c*self.SQ_SIZE, r*self.SQ_SIZE - 10, self.SQ_SIZE, self.SQ_SIZE))
            p.display.flip()
            self.clock.tick(60)
            
    def loadButtons(self, position, player):
        if len(self.IMAGES) <= 0:
            return
        pieces = ['wB', 'wQ', 'wN', 'wR', 'bB', 'bQ', 'bN', 'bR']
        if self.gs.whiteToMove:
            i, j = 0, 1
        else:
            i, j = 7, -1
        for piece in pieces:
            if (piece[0] == player):
                self.promotion_buttons[piece] = Button(piece, self.IMAGES[piece], self.SQ_SIZE, self.SQ_SIZE,\
                                                        (position[1]*self.SQ_SIZE, i*self.SQ_SIZE))
                i += j

    def createButton(self):
        for button in self.promotion_buttons.values():
            button.draw(self.screen)

    def promotionBehavior(self, piece, location, move):
        for button in self.promotion_buttons.values():
            if button.is_clicked(location):
                piece.pawnPromotion(move, self.board, button.create_piece(button.value[0]))
                self.promotion_buttons.clear()
                self.drawGameState()
                return True
        return False

if __name__ == '__main__':
    chess = GameController()
    chess.run()
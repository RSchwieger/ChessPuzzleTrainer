import pygame
import os
import chess
import math


class MyChessBoard:
    """
    Gui for the chess.board
    """
    def __init__(self, sizeX, cryptic_board, screen, moveValidation=None, game=None):
        self.sizeRect = sizeX/8 # init size of square
        self.White = (255, 255, 255)
        self.Black = (0, 120, 0)
        self.screen = screen # some pyGame stuff

        # store the squares where the user clicked
        self.firstClick = None
        self.secondClick = None

        self.board = cryptic_board # the chess.board =)
        self.draw_board()
        self.game = game # optional variable for storing solutions or games

        self.moveCount = 0 # count moves
        self.moveList = []

        # Load chess engine
        self.engine = chess.uci.popen_engine("/usr/games/stockfish")
        self.engine.uci()
        self.engine.position(self.board)

    def suggestMove(self):
        """
        Suggests a move based on a PGN description.
        :return:
        """
        if self.game != None: # if there is PGN data available
            if not self.game.is_end():
                self.next_node = self.game.variation(0) # choose always the main line.
                return self.next_node.move
            else:
                print("No more moves in PGN description")
                return None
        else:
            self.engine.position(self.board)
            best, ponder = self.engine.go(depth=15)
            return best
        return None

    def __moveValidation(self, move):
        """
        If moves were specified in a pgn string include that into the move validation process.
        :param move:
        :return:
        """
        if True: # if there is PGN data available
            suggested_move = self.suggestMove() # suggest a move based on the PGN Data
            if suggested_move == None:
                print("No more moves. Puzzle solved.")
                return False
            if suggested_move != move: # User makes a different move
                print("Wrong move")
                print("Play instead "+str(suggested_move))
                return False
            else:
                #print("Correct move")
                if self.game != None:
                    self.game = self.next_node # traverse to the next node
                return True
        return True

    def loadNewPosition(self, board, game=None):
        """
        Loads a new position with an optional move tree
        :param board: instance of chess.format
        :param game: PGN data stored in a py-chess specific format
        :return:
        """
        self.board = board
        # reset moves
        self.firstClick = None
        self.secondClick = None
        self.moveCount = 0
        self.moveList = []
        self.game = game

    def draw_board(self):
        """
        Draws the chess board saved in self.board
        :return:
        """
        self.__drawEmptyBoard()
        for i in range(64):
            # There is some mess with different chess notations
            (letter, number) = self.__convertArrayNotationToChessHuman(i)
            piece = self.board.piece_at(i) # check if in chess.board is a piece at the specified coordinate
            if piece is not None:
                coordinate = str(letter)+str(number)
                self.__drawFigure(coordinate, str(piece))

    def __convertArrayNotationToChessHuman(self, number):
        """
        Converts the notation of self.board to a human readable notation.
        :param number: in [0,...,64] which is converted to smth. like "a8"
        :return: tuple, eg. (a,8) representing the square "a8"
        """
        dict = {0.0: "a", 1.0: "b", 2.0: "c", 3.0: "d", 4.0: "e", 5.0: "f", 6.0: "g", 7.0: "h"}
        letter = number%8
        num  = (number-letter)/8+1
        return (dict[letter],int(num))

    def __drawEmptyBoard(self):
        """
        Just an empty board
        :return: None
        """
        for j in range(8):
            for i in range(8):
                if (i+j)%2==0:
                    pygame.draw.rect(self.screen, self.White, pygame.Rect(i*self.sizeRect, j*self.sizeRect, self.sizeRect, self.sizeRect))
                else:
                    pygame.draw.rect(self.screen, self.Black, pygame.Rect(i*self.sizeRect, j*self.sizeRect, self.sizeRect, self.sizeRect))

    def __drawFigureIn2DCoordinates(self, y, x, whichFigure):
        """
        Inserts the figures
        :param y: square coordinates
        :param x: square coordinates
        :param whichFigure: see dictionary in function
        :return:
        """
        figure_pngs = {"n": 'SpringerSchwarz.png', "N": "SpringerWeiß.png", "r": "TurmSchwarz.png", "R": "TurmWeiß.png",
                "k": "KönigSchwarz.png", "K": "KönigWeiß.png", "b": "LäuferSchwarz.png", "B": "LäuferWeiß.png", "p":
                "BauerSchwarz.png", "P": "BauerWeiß.png", "q": "KöniginSchwarz.png", "Q": "KöniginWeiß.png"}
        figure = pygame.image.load(os.path.join('chessPictures', figure_pngs[whichFigure]))

        figure = pygame.transform.scale(figure, (int(self.sizeRect), int(self.sizeRect)) )

        #some pyGame stuff
        self.screen.blit(figure, pygame.Rect(y*self.sizeRect, x*self.sizeRect, self.sizeRect, self.sizeRect))

    def __drawFigure(self, coordinate, whichFigure):
        """
        Convenience method for __drawFigureIn2DCoordinates
        :param coordinate: in human chess format (e.g. "a8")
        :param whichFigure: see dictionary in __drawFigureIn2DCoordinates
        :return:
        """
        dictLetter = {'a': 0, 'b': 1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
        dictNumber = {'1': 7, '2': 6, '3':5, '4':4, '5':3, '6':2, '7':1, '8':0}
        self.__drawFigureIn2DCoordinates(dictLetter[coordinate[0]],dictNumber[coordinate[1]], whichFigure)

    def __selectField(self, position):
        """
        Selects a field of the chess board according to the mouse position
        :param position: an (x,y) coordinate of the screen
        :return:
        """
        # find the square where the user clicked
        x,y = position
        intx = math.floor(x/self.sizeRect)
        inty = 8-math.floor(y/self.sizeRect) # pyGame coordinates are starting from the left upper corner...
        dict = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7:"h"}
        return dict[intx]+str(inty)

    def detectMove(self, position):
        """
        Saves the clicks of the user and checks if it makes sense,
        :param position: (x,y) coordinate of the pyGame screen
        :return: True for move, False for no move or illegal moves
        """
        if self.firstClick is None:
            self.firstClick = self.__selectField(position)
            return False
        else:
            self.secondClick = self.__selectField(position)
            move = chess.Move.from_uci(self.firstClick+self.secondClick)
            # print(self.board.legal_moves)
            self.move_figure(move)
            self.firstClick = None
            self.secondClick = None
            return True

    def move_figure(self, move):
        """
        moves a figure in chess.board
        :param move: chess.board specific command
        :return:
        """
        if move in self.board.legal_moves and self.__moveValidation(move):
                self.board.push(move) # here the "movement" happens.
                self.moveCount += 1
                self.moveList += [move]
                # print(move)

    def __convertHumanReadableTopyBoardCoordinate(self, coordinateString):
        """
        Converts a human chess coordinate into a pychess coordinate
        :param coordinateString:
        :return:
        """
        dictLetter = {'a': 0, 'b': 1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
        dictNumber = {'1': 0, '2': 1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7}
        letter_num = dictLetter[coordinateString[0]]
        number_num = dictNumber[coordinateString[1]]
        fin_num = letter_num+number_num*8
        return fin_num
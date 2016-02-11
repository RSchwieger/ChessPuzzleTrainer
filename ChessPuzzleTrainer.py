import pygame
import chess
from chess import uci
from MyChessBoard import MyChessBoard
import time
from PuzzleCollection import PuzzleCollection, ChessPuzzle, ScheduledPuzzleCollection
import os.path
import datetime

def returnCurrentFile(folder):
    """
    For a given folder it searches for the latest problem file
    :param folder:
    :return: None if no file found otherwise the name
    """
    counter = 1
    current_filename = None
    while True:
        if os.path.exists(folder+str(counter)) == True:
            current_filename = folder+str(counter)
        else:
            break
        counter += 1
    if current_filename == None:
        return None
    else:
        return (current_filename, folder+str(counter))

screenSize = 500
pygame.init()
screen = pygame.display.set_mode((screenSize, screenSize))
pygame.display.set_caption("Chess Puzzles")
done = False
trainingTime = time.time()

folder = input("Name of folder: ")
infile, outfile = returnCurrentFile(folder+"/"+folder)
print("Loading file")
time.sleep(10)

try:
    puzzleCollection = ScheduledPuzzleCollection(infile, outfile)
    puzzleIterator = iter(puzzleCollection)
    currentChessPuzzle = next(puzzleIterator)
except StopIteration:
    print("No puzzle_collection to solve")
    raise SystemExit

pygame.display.set_caption(currentChessPuzzle.puzzleDict["description"])
boardGUI = MyChessBoard(screenSize, chess.Board(currentChessPuzzle.FEN), screen)

# Load chess engine
engine = chess.uci.popen_engine("/usr/games/stockfish")
engine.uci()
engine.position(boardGUI.board)

def loadNextPuzzle():
    try:
        currentChessPuzzle = next(puzzleIterator)
        boardGUI.loadNewPosition(chess.Board(currentChessPuzzle.FEN), currentChessPuzzle.game)
        boardGUI.draw_board()
        if 'description' in currentChessPuzzle.puzzleDict:
            pygame.display.set_caption(currentChessPuzzle.puzzleDict["description"])
        else:
            pygame.display.set_caption("No description")
        return (False, currentChessPuzzle)
    except StopIteration:
        return (True, None)

while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
                        print("Hier")
                        puzzleCollection.savePuzzlesIntoFile() # save results
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    is_moved = boardGUI.detectMove(pos)
                    boardGUI.draw_board()

                    if is_moved:
                        pygame.display.flip()
                        time.sleep(0.5)
                        best = boardGUI.suggestMove() # returns the node with the move
                        boardGUI.move_figure(best)
                        boardGUI.draw_board()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        print("Reset position")
                        boardGUI.loadNewPosition(chess.Board(currentChessPuzzle.FEN)) # load the old position again
                        boardGUI.draw_board()
                    if event.key == pygame.K_c:
                        currentChessPuzzle.markPuzzleAsSolvedCorrectly()
                        (done, currentChessPuzzle) = loadNextPuzzle()

                    if event.key == pygame.K_w:
                        print("Puzzle not solved")
                        currentChessPuzzle.markPuzzleAsSolvedIncorrectly()
                        (done, currentChessPuzzle) = loadNextPuzzle()

                    if event.key == pygame.K_d:
                        print("Delete puzzle")
                        puzzleCollection.removeCurrentPuzzleFromCollection()
                        (done, currentChessPuzzle) = loadNextPuzzle()

                    if event.key == pygame.K_h:
                        print("h - Help")
                        print("r - reset position")
                        print("c - correctly solved")
                        print("d - delete the current puzzle")
                        print("w - wrongly solved")

        pygame.display.flip()

file_for_trainingTimes = open(folder+"/"+"trainingTimes", 'a')
print(folder+"/"+"trainingTimes")
trainingTime = time.time()-trainingTime
file_for_trainingTimes.write(str(datetime.date.today())+": "+str(trainingTime)+" seconds"+"\n")
file_for_trainingTimes.close()

import json
import random
import datetime
import time
import chess.pgn
from io import StringIO

class ChessPuzzle:
    """
    This class represents one chess puzzle. It mainly is just a json string with additional information about the
    solving time
    """
    def __init__(self, puzzleAsString):
        """
        Reads the string containing the chess puzzle and additional information.
        :param puzzleAsString: string
        :return:-
        """
        self.puzzleDict = json.loads(puzzleAsString) # each line of the file represents a puzzle represented in json format
        self.FEN = self.puzzleDict["FEN"] # see WIKI for informations of the chess FEN format
        # Create a list of solving times if necessary
        if 'previousSolvingTimes' not in self.puzzleDict:
            self.puzzleDict['previousSolvingTimes'] = []

        # Check if there is some information about solutions given
        if 'PGN' in self.puzzleDict and self.puzzleDict['PGN'] != "":
            pgnString = "[FEN \""+self.FEN+"\"]\n"
            pgnString += self.puzzleDict['PGN']
            #print(pgnString)
            self.PGN = StringIO(pgnString)
            self.game = chess.pgn.read_game(self.PGN)
            # print(self.game)
        else:
            self.puzzleDict['PGN'] = ""
            self.game = None

        # measure the time needed to solve the puzzle
        self.start_time = time.time()
        self.time_for_solving = -1

    def __str__(self):
        return json.dumps(self.puzzleDict)

    def markPuzzleAsSolvedCorrectly(self):
        """
        Save the time necessary to solve the puzzle.
        :return:
        """
        self.puzzleDict['previousSolvingTimes'] += [[str(datetime.date.today()), time.time()-self.start_time]]
        print(str(time.time()-self.start_time))
        self.start_time = time.time() # reset time, if the puzzle gets asked again in this round due to much time
        self.time_for_solving = -1

    def markPuzzleAsSolvedIncorrectly(self):
        """
        Mark the puzzle as unsolved
        :return:
        """
        self.puzzleDict['previousSolvingTimes'] += [[str(datetime.date.today()), "not solved"]]
        self.start_time = time.time() # reset time, if the puzzle gets asked again in this round due to much time
        self.time_for_solving = -1

#############################################################################################################

class PuzzleCollection:
    """
    Essentially a list of ChessPuzzle instances. This list can be loaded from a file and saved to a file. Is afterwards shuffled.
    The class also provides an iterator.
    """
    def __init__(self, filename_in, filename_out):
        self.listOfPuzzles = self.__readFileIntoPuzzleList(filename_in) # the puzzle_collection.
        random.shuffle(self.listOfPuzzles)
        self.puzzleIterator = iter(self.listOfPuzzles) # Provides some way to iterate over the collection
        self.saveInFile = filename_out
        self.currentPuzzle = None

    def __readFileIntoPuzzleList(self, filename):
        """
        Reads the puzzle list from a file
        :param filename:
        :return: list of puzzle_collection
        """
        puzzlesFile = open(filename)
        puzzles = [ChessPuzzle(line) for line in puzzlesFile]
        puzzlesFile.close()
        return puzzles

    def __iter__(self):
        return self

    def __next__(self):
        """
        Iterate over all puzzle_collection without any criteria
        :return:
        """
        try:
            self.currentChessPuzzle = next(self.puzzleIterator)
            self.currentChessPuzzle.start_time = time.time()
            return self.currentChessPuzzle
        except StopIteration:
            self.closePuzzleCollection()
            raise StopIteration

    def savePuzzlesIntoFile(self):
        """
        Saves the puzzle_collection and their attributes to a file
        :param filename:
        :param puzzle_collection: list of puzzle_collection
        :return:
        """
        print("Saving results...")
        file_for_saving = open(self.saveInFile, 'w')
        file_for_saving_solvingtimes = open(self.saveInFile+"_solvingtimes", 'w')
        for puzzle in self.listOfPuzzles:
            file_for_saving.write(str(puzzle)+"\n")
            file_for_saving_solvingtimes.write(str(puzzle.puzzleDict['previousSolvingTimes'])+"\n")

        file_for_saving.close()
        file_for_saving_solvingtimes.close()

    def closePuzzleCollection(self):
        """
        Convenience method
        """
        print("No more puzzle_collection.")
        self.savePuzzlesIntoFile()

##############################################################################################################

class ScheduledPuzzleCollection(PuzzleCollection):
    """
    This class is a refinement of 'PuzzleCollection'. The main diffrence is that it provides an iterator for
    puzzle_collection which should be learned according to a schedule specified in the constructor,
    The puzzle_collection are iterated in such a way that puzzle_collection solved previously are presented to the user first.
    Only afterwards new puzzle_collection are (randomly) chosen for the user.
    """
    def __init__(self, filename_in, filename_out):
        PuzzleCollection.__init__(self, filename_in, filename_out)
        self.schedule = {1:1, 2:2, 3:10, 4:30, 5:90, 6:300} # level:days between two repetitions
        self.treshold = 120.0 # after 3 min the problem is more frequently shown in future

    def __next__(self):
        """
        Iterate first over all problems which are due and solved before and then over all problems which are due
        :return:
        """
        # First we iterate over all problems which are due and solved previously
        # Afterwards we iterate over all problems which were not solved previously
        # The method '__problemIsCurrent' indicates if a problem should be solved
        # After the fist 'StopIteration' we replace this method by '__problemIsDue' and reset the iterator
        # The second time 'StopIteration' occurs we stop the iteration
        try:
            self.currentChessPuzzle = next(self.puzzleIterator)
            self.currentChessPuzzle.start_time = time.time()
        except StopIteration:
            if self.__problemIsCurrent != self.__problemIsDue:
                self.puzzleIterator = iter(self.listOfPuzzles)
                self.__problemIsCurrent = self.__problemIsDue
                print("You solved all previously presented puzzles.")
                return self.__next__()
            else:
                self.closePuzzleCollection()
                raise StopIteration
        previousSolvingTimes = self.currentChessPuzzle.puzzleDict['previousSolvingTimes']

        if self.__problemIsCurrent(previousSolvingTimes):
            return self.currentChessPuzzle
        else:
            return self.__next__()

    def __problemWasSolvedBefore(self, previousSolvingTimes):
        """
        Checks if the problem was solved before
        :param previousSolvingTimes:
        :return:
        """
        if previousSolvingTimes == []:
           return False
        else:
           return True

    def getLevel(self, previousSolvingTimes):
        """
        Returns the current level
        :param previousSolvingTimes:
        :return:
        """
        if previousSolvingTimes == None:
            return 0
        level = 1
        for i in range(len(previousSolvingTimes)):
            (date, solved) = previousSolvingTimes[i]
            if solved == "not solved":
                level = 0
            else:
                # if the puzzle was solved before, the level is bigger than 1 but the solving time is higher
                # than the treshold then reduce the level by one
                if i>1 and solved >= self.treshold and level > 1:
                    level -= 1
                # if the puzzle was solved fast enough increase the level by one
                elif solved <= self.treshold:
                    level += 1
                # if the puzzle the level is zero and the time for solving is higher than the treshold
                # increase the level nevertheless by one
                elif solved >= self.treshold and level == 0:
                    level += 1
                # if the solving time is longer than the treshold time and the level is 1, don't change the level
                elif solved >= self.treshold and level == 1:
                    pass
        # print("level "+str(level)+"  "+str((date,solved)))
        return level

    def __problemIsDue(self, previousSolvingTimes):
        if previousSolvingTimes == None or previousSolvingTimes == []:
            return True

        level = self.getLevel(previousSolvingTimes)
        #print(previousSolvingTimes)
        #print(level)
        (date, solved) = previousSolvingTimes[-1]
        previousDate = datetime.datetime.strptime(date, "%Y-%m-%d") # parse next date
        temp = datetime.date.today()-previousDate.date() # how long was it since the problem was solved the last time
        # checks if it is time to present the
        # puzzle again according to schedule

        if level == 0:
            return True
        if self.schedule[level]<=temp.days:
            return True
        else:
            return False


    def __problemIsCurrent(self, previousSolvingTimes):
        """
        Convenience method.
        :param previousSolvingTimes:
        :return:
        """
        if self.__problemIsDue(previousSolvingTimes) and self.__problemWasSolvedBefore(previousSolvingTimes):
            return True
        else:
            False

    def removeCurrentPuzzleFromCollection(self):
        """
        Don't save the current puzzle later
        :return:
        """
        self.listOfPuzzles.remove(self.currentChessPuzzle)
        self.puzzleIterator =  iter(self.listOfPuzzles) # reset iterator to circumvent problems
        print("Puzzle removed")
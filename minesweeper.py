import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"
    @property
    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:"""
            # mark the cell as a move that has been made
        self.moves_made.add(cell)

            #mark the cell as safe
        self.mark_safe(cell)

        neighbour_move = set()

            #add a new sentence to the AI's knowledge base
               #based on the value of `cell` and `count`
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                       #move within board range
                  if (0 <= i < 8) and (0 <= j <8):
                        if(i, j) not in self.moves_made:
                              neighbour_move.add((i, j))
        if Sentence(neighbour_move, count) not in self.knowledge:
            self.knowledge.append(Sentence(neighbour_move, count))

                # mark any additional cell as safe or as mines if it can be conclude based on AI knowledge base
            for sentence in self.knowledge:
                    #sentence having all mine
                    if len(sentence.cells) == sentence.count:
                        all_mines = copy.deepcopy(sentence.cells)
                        for mine in all_mines:
                            self.mark_mine(mine)
                        self.knowledge.remove(sentence)
                        #print(sentence full of mine)
                    elif sentence.count == 0:
                        all_safe = copy.deepcopy(sentence.cells)
                        for safe in all_safe:
                            self.mark_safe(safe)
                        self.knowledge.remove(sentence)
                    else:
                        pass
            # add any new sentence to the AI's knowledge
            static_knowledge_base = copy.deepcopy(self.knowledge)
            for sentence1 in static_knowledge_base:
                if len(sentence1.cells) != 0:
                    for sentence2 in static_knowledge_base:
                       if len(sentence2.cells) != 0 and sentence2 != sentence1:
                            # If found any subset
                            if sentence2.cells.issubset(sentence1.cells):
                                new_cells = sentence1.cells - sentence2.cells
                                new_count = sentence1.count - sentence2.count
                                for cell in self.moves_made:
                                    if cell in new_cells:
                                        new_cells.remove(cell)
                                for sentence in static_knowledge_base:
                                    if set(new_cells) == sentence.cells:
	                                    # pre exsiting knowledge , hence skipped
	                                    continue
                                # Add sentence to knowledge
                                if Sentence(new_cells, new_count) not in self.knowledge:
                                    self.knowledge.append(Sentence(new_cells, new_count))


    def make_safe_move(self):
        # return a safe cell to choose on minesweeper board.
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None


    def make_random_move(self):
        for i in range(8):
            for j in range(8):
                cell = (i, j)
                if (cell not in self.moves_made) and (cell not in self.mines):
                    return cell
        return None



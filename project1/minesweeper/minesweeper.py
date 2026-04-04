import itertools
import random


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
        self.mines = set()
        self.safes = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if self.count == len(self.cells):
            return set(self.cells)
        return set()
        
    def known_safes(self):
        if self.count == 0:
            return set(self.cells)
        return set()
        
    def mark_mine(self, cell):
        cells = {c for c in self.cells}
        
        if cell in cells:
            self.mines.add(cell)
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        cells = {c for c in self.cells}
        
        if cell in cells:
            self.safes.add(cell)
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

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        cell_i, cell_j = cell
        if cell_i not in range(self.height) or cell_j not in range(self.width):
            return

        self.moves_made.add(cell)
        self.mark_safe(cell)

        neighbors = set()
        adjusted_count = count

        for i in range(max(0, cell_i - 1), min(self.height - 1, cell_i + 1) + 1):
            for j in range(max(0, cell_j - 1), min(self.width - 1, cell_j + 1) + 1):
                neighbor = (i, j)

                if neighbor == cell:
                    continue
                if neighbor in self.mines:
                    adjusted_count -= 1
                elif neighbor not in self.safes and neighbor not in self.moves_made:
                    neighbors.add(neighbor)

        if len(neighbors) > 0:
            new_sentence = Sentence(neighbors, adjusted_count)
            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence)

        changed = True
        while changed:
            changed = False

            new_safes = set()
            new_mines = set()
            for sentence in self.knowledge:
                new_safes |= sentence.known_safes()
                new_mines |= sentence.known_mines()

            for safe in new_safes - self.safes:
                self.mark_safe(safe)
                changed = True

            for mine in new_mines - self.mines:
                self.mark_mine(mine)
                changed = True

            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

            inferred_sentences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 == s2:
                        continue
                    if not s1.cells.issubset(s2.cells):
                        continue

                    diff_cells = s2.cells - s1.cells
                    diff_count = s2.count - s1.count

                    if len(diff_cells) == 0 or diff_count < 0:
                        continue

                    candidate = Sentence(diff_cells, diff_count)
                    if candidate not in self.knowledge and candidate not in inferred_sentences:
                        inferred_sentences.append(candidate)

            if len(inferred_sentences) > 0:
                self.knowledge.extend(inferred_sentences)
                changed = True
        
    def infer_safe_cells(self, sentence):
        sentence_cells = {c for c in sentence.cells}
        # for every sentence in knowledge where count is 0, we can mark all cells in it as safe
        if sentence.count == 0:
            for sentence_cell in sentence_cells:
                self.mark_safe(sentence_cell)
                
    def infer_mine_cells(self, sentence):
        sentence_cells = {c for c in sentence.cells}
        # for every sentence in knowledge where count is equal to the number of cells, we can mark all cells in it as mines
        if sentence.count == len(sentence_cells):
            for sentence_cell in sentence_cells:
                self.mark_mine(sentence_cell)

    def make_safe_move(self):
        for safe_cell in self.safes:
            if safe_cell not in self.moves_made:
                return safe_cell

    def make_random_move(self):
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                
                if cell not in self.moves_made and cell not in self.mines:
                    return cell

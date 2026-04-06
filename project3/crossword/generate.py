import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        for variable, possible_words in self.domains.items():
            self.domains[variable] = {word for word in possible_words if len(word) == variable.length}
            
    def revise(self, x, y):
        result = False
        
        for (first, second), overlap in self.crossword.overlaps.items():
            if not overlap:
                continue
            
            if x not in (first, second) or y not in (first, second):
                continue
            
            if x == first:
                x_character = overlap[0]
                y_character = overlap[1]
            else:
                x_character = overlap[1]
                y_character = overlap[0]
                
            new_domains = set()
            for word in self.domains[x]:
                if any(y_word for y_word in self.domains[y] if word[x_character] == y_word[y_character]):
                    new_domains.add(word)
                else:
                    result = True
                    
            self.domains[x] = new_domains
            
        return result
            

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is not None:
            queue = list(arcs)
        else:
            queue = [(x,y) for x in self.domains.keys() for y in self.crossword.neighbors(x)]
            
        while len(queue) > 0:
            (x, y) = queue.pop(0)
            
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                
                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        queue.append((neighbor, x))
                    
        return True
            
    def assignment_complete(self, assignment):
        for variable in self.domains.keys():
            if not assignment.get(variable):
                return False
        return True

    def consistent(self, assignment):
        for variable, value in assignment.items():
            if len(value) != variable.length:
                return False
            
            for neighbor in self.crossword.neighbors(variable):
                overlap = self.crossword.overlaps.get((variable, neighbor))
                if not overlap:
                    continue
                
                if not assignment.get(neighbor):
                    continue
                
                if value[overlap[0]] != assignment.get(neighbor)[overlap[1]]:
                    return False
            
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        conflicts = dict()
        
        for word in self.domains[var]:
            conflicts[word] = 0
            
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue

                overlap = self.crossword.overlaps.get((var, neighbor))
                if overlap:
                    conflicting_words = [w for w in self.domains[neighbor] if word[overlap[0]] != w[overlap[1]]]
                    conflicts[word] += len(conflicting_words)
                    
        return sorted(conflicts.keys(), key=lambda word: conflicts[word])

    def select_unassigned_variable(self, assignment):
        sorted_list = sorted([var for var in self.domains.keys() if var not in assignment], key=lambda var: len(self.domains[var]))
        
        return sorted_list[0] if len(sorted_list) > 0 else None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value

            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result

            del assignment[var]

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # has to be either a knight or a knave, and not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    
    # if he's a knight, he's telling the truth so he's both
    # if he's a knave, he's telling a lie so he's not both
    Implication(AKnight, And(AKnight, AKnave)),
    Implication(AKnave, Not(And(AKnight, AKnave))),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # both A and B have to be either a knight or a knave, and not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    
    # if A is a knight, both him and B are knaves
    # if A is a knave, they're not both knaves
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Not(And(AKnave, BKnave)))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    
    # if A is a knight, they're both the same kind
    # if A is a knave, they're not the same kind
    
    # if B is a knight, they're not the same kind
    # if B is a knave, they're the both the same kind
    
    Implication(Or(AKnight, BKnave), Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Implication(Or(AKnave, BKnight), Not(Or(And(AKnight, BKnight), And(AKnave, BKnave))))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),
    
    # if b is a knight, we consider that A said 'I am a knave'
    # he can't be a knight, because he would have to be telling the truth
    # he could be a knave but in that case he would have to be lying so he's a knight
    # we conclude that if b is a knight, then a is a knight
    
    # if b is a knight, C is a knave
    # if b is a knave, c is a knight
    
    # if c is a knight, a is a knight
    # if c is a knave, a is a knave
    
    Implication(BKnight, And(AKnight, CKnave)),
    Implication(BKnave, CKnight),
    Implication(CKnight, AKnight),
    Implication(CKnave, AKnave)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()

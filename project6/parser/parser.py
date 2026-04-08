import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | NP VP Conj VP | NP VP Conj NP VP

NP -> N | Det NP | AdjP NP | NP PP
VP -> V | V NP | AdvP VP | AdvP VP | V PP
AdjP -> Adj | Adj Adj
AdvP -> Adv
PP -> P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)

def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))

def preprocess(sentence):
    words = nltk.tokenize.word_tokenize(sentence)
    result = []
    for word in words:
        if word.isalpha():
            result.append(word.lower())
    return result

def np_chunk(tree):
    def has_np_child(subtree):
        for child_subtree in subtree.subtrees():
            if child_subtree == subtree:
                continue
            if child_subtree.label() == "NP":
                return True
        return False

    result = []

    for subtree in tree.subtrees(lambda x: x.label() == "NP"):
        if not has_np_child(subtree):
            result.append(subtree)

    return result


if __name__ == "__main__":
    main()

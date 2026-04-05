import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loophave the gene over all sets of people who might 
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * A: everyone in set `one_gene` has one copy of the gene, and
        * B: everyone in set `two_genes` has two copies of the gene, and
        * C: everyone not in `one_gene` or `two_gene` does not have the gene, and
        * D: everyone in set `have_trait` has the trait, and
        * E: everyone not in set` have_trait` does not have the trait.
    """
    
    p = 1
    
    for person in people:
        mother = people[person]['mother']
        father = people[person]['father']
        
        num_genes = 0
        if person in one_gene:
            num_genes = 1
        elif person in two_genes:
            num_genes = 2
        
        if not mother or not father:
            prob_genes = PROBS['gene'][num_genes]
        else:
            if mother in two_genes:
                prob_mother_transmits = 1 - PROBS['mutation']
            elif mother in one_gene:
                prob_mother_transmits = 0.5
            else:
                prob_mother_transmits = PROBS['mutation']
            
            if father in two_genes:
                prob_father_transmits = 1 - PROBS['mutation']
            elif father in one_gene:
                prob_father_transmits = 0.5
            else:
                prob_father_transmits = PROBS['mutation']
                
            if num_genes == 2:
                # both have to transmit
                prob_genes = prob_mother_transmits * prob_father_transmits
            elif num_genes == 1:
                # one transmits and the other doesn't
                prob_genes = prob_mother_transmits * (1 - prob_father_transmits) + (1 - prob_mother_transmits) * prob_father_transmits
            else:
                # none transmits
                prob_genes = (1 - prob_mother_transmits) * (1 - prob_father_transmits)
            
            
        has_trait = person in have_trait
        
        prob_trait = PROBS['trait'][num_genes][has_trait]
        
        p *= prob_genes * prob_trait
            
    return p


def update(probabilities, one_gene, two_genes, have_trait, p):
    for person in probabilities:
        num_genes = 2 if person in two_genes else 1 if person in one_gene else 0
        has_trait = person in have_trait
        
        probabilities[person]['gene'][num_genes] += p
        probabilities[person]['trait'][has_trait] += p
            
def normalize(probabilities):
    for person in probabilities:
        sum_genes = sum(probabilities[person]['gene'][num] for num in range(3))
        sum_trait = sum(probabilities[person]['trait'][boolean] for boolean in [True, False])
        
        for num in range(3):
            probabilities[person]['gene'][num] /= sum_genes
            
        for boolean in [True, False]:
            probabilities[person]['trait'][boolean] /= sum_trait

if __name__ == "__main__":
    main()

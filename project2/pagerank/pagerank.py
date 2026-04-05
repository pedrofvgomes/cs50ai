import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    
    Para cada key, o valor é um set dos links todos que a página tem
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )
        
    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    
    Return dict
    keys: pages
    values: dict with page-probability
    
    if page has no links, equal probability for all pages
    """
    all_pages = {key for key in corpus.keys()}
    
    linked_pages = corpus.get(page, set())
    
    # links to itself are ignored
    if page in linked_pages:
        linked_pages.remove(page)
    
    non_linked_pages = all_pages - linked_pages
        
    result = {}
    
    for page in all_pages:
        probability = 0
            
        if len(linked_pages) == 0:
            probability = 1 / len(all_pages)
        elif page in linked_pages:
            probability = damping_factor / len(linked_pages)
        else:
            probability = (1 - damping_factor) / len(non_linked_pages)
        
        result[page] = probability
        
    return result

def sample_pagerank(corpus, damping_factor, n):
    result = {page: 0 for page in corpus.keys()}
    
    total_visits = 0

    sample = random.choice([key for key in corpus.keys()])
    
    while True:
        # increment the current sample's visit counter and the total visits
        result[sample] += 1
        total_visits += 1

        if total_visits == n:
            break
        
        model = transition_model(corpus, sample, damping_factor)
        
        population = []
        weights = []
        
        for page, probability in model.items():
            population.append(page)
            weights.append(probability)
            
        sample = random.choices(population=population, weights=weights)[0]
        
    for page, visits in result.items():
        result[page] = visits / total_visits
    
    return result

def iterate_pagerank(corpus, damping_factor):
    all_pages = [page for page in corpus.keys()]
    results = {page: 1/len(all_pages) for page in all_pages}
    
    pages_linked = {page: [] for page in all_pages}
    pages_that_link_to = {page: [] for page in all_pages}
    
    for page, links in corpus.items():
        if len(links) == 0:
            links = all_pages
            
        for link in links:
            pages_that_link_to[link].append(page)

        pages_linked[page] = links
            
    previous_results = {}
    
    while True:
        if all(abs(results.get(page, 0) - previous_results.get(page, -1) <= 0.001) for page in all_pages):
            break
        
        new_results = {}
        
        for page in all_pages:
            first_condition = (1 - damping_factor) / len(all_pages)
            
            i_pages = pages_that_link_to[page]
            
            sum_result = 0
            
            for i in i_pages:
                pr = results.get(i)
                num_links = len(pages_linked.get(i))
                
                if num_links > 0:
                    sum_result += pr / num_links
                    
            second_condition = damping_factor * sum_result

            new_results[page] = first_condition + second_condition
            
        previous_results = {k:v for k,v in results.items()}
        results = {k:v for k,v in new_results.items()}
                
    return results

if __name__ == "__main__":
    main()

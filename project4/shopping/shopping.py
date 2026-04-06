import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4

INT_HEADERS = [
    'Administrative',
    'Informational',
    'ProductRelated',
    'Month',
    'OperatingSystems',
    'Browser',
    'Region',
    'TrafficType',
    'VisitorType',
    'Weekend'
]

FLOAT_HEADERS = [
    'Administrative_Duration',
    'Informational_Duration',
    'ProductRelated_Duration',
    'BounceRates',
    'ExitRates',
    'PageValues',
    'SpecialDay'
]

MONTH_STR_TO_INT = {
    'Jan': 0,
    'Feb': 1,
    'Mar': 2,
    'Apr': 3,
    'May': 4,
    'June': 5,
    'Jul': 6,
    'Aug': 7,
    'Sep': 8,
    'Oct': 9,
    'Nov': 10,
    'Dec': 11
}

VISITOR_TYPE_STR_TO_INT = {
    'New_Visitor': 0,
    'Other': 0,
    'Returning_Visitor': 1,
}

WEEKEND_STR_TO_INT = {
    'TRUE': 1,
    'FALSE': 0
}

REVENUE_STR_TO_INT = {
    'TRUE': 1,
    'FALSE': 0
}

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")




def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []
    
    with open(filename, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            skip = False
            
            revenue = REVENUE_STR_TO_INT[row['Revenue']]
            
            evidence_for_user = []
            labels_for_user = [revenue]*17
            
            for header in row.keys():
                if header == 'Revenue':
                    continue
                
                value = row[header]
                    
                if header == 'Month':
                    if value not in MONTH_STR_TO_INT:
                        print(f'Month {value} not in {MONTH_STR_TO_INT}')
                        skip = True
                        break
                    
                    value = MONTH_STR_TO_INT[value]
                    
                if header == 'VisitorType':
                    if value not in VISITOR_TYPE_STR_TO_INT:
                        print(f'Value {value} not in {VISITOR_TYPE_STR_TO_INT}')
                        skip = True
                        break
                    
                    value = VISITOR_TYPE_STR_TO_INT[value]
                    
                if header == 'Weekend':
                    if value not in WEEKEND_STR_TO_INT:
                        print(f'Value {value} not in {WEEKEND_STR_TO_INT}')
                        skip = True
                        break
                        
                    value = WEEKEND_STR_TO_INT[value]
                
                if header in INT_HEADERS:
                    try:
                        value = int(value)
                    except ValueError:
                        print(f'Value {value} is not an int')
                        skip = True
                        break
                
                if header in FLOAT_HEADERS:
                    try:
                        value = float(value)
                    except ValueError:
                        print(f'Value {value} is not a float')
                        skip = True
                        break
                    
                evidence_for_user.append(value)

            if skip:
                continue
            
            evidence.append(evidence_for_user)
            labels.append(labels_for_user)      

    result = (evidence, labels)
    return result

def train_model(evidence, labels):
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    true_positive = 0
    total_positive = 0
    true_negative = 0
    total_negative = 0
    
    for label, prediction in zip(labels, predictions):
        if label:
            total_positive += 1
            if prediction:
                true_positive += 1

        else:
            total_negative += 1
            if not prediction:
                true_negative += 1

    return (true_positive / total_positive, true_negative / total_negative)

if __name__ == "__main__":
    main()

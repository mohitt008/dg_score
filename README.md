# Cataloguing

## Feature Vectors
To create feature vectors for each product in a particular category, input the delhivery category ID.

### Process:
1. Joins the abstracts for a particular category to form a paragraph.
2. Creates a new object with the joined abstracts as input to the class.
3. Removes the HTML tags from the abstract using utilities.py
4. Removes special characters from output of step 3.
5. Performs stemming on the tokens.
6. Post tag the tokens and select only commom nouns
7. Counts the frequency of nouns.


## Generate Product Information 
Calls the function getProducts with input as delhivery category ID(INTEGER) and count of products required (INTEGER)

### Process
1. Collects the associated children category ID for the delhivery category ID.
2. For the categories selected in step 1, get vendor category IDs.
3. Generate list of random numbers to select the sequence of document to be selected.
4. Map the vendor category ids with set of sequence numbers.
5. From products table, extract the product information in a json. 
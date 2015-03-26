## Cataloguing 
-------------------------

What is Cataloguing?
The objective of Cataloguing is to maintain a universal product catalogue for the various items that we receive in order to make better decisions in the future. Example: Whether the product is dangerous with respect to shipment in the air. 
This would help to compare actual/client given/manifest weights versus predicted weights.

-------------------------
How to use the service?
-------------------------
### Predictions
To create feature vectors for each product in a particular category, provide input the delhivery category ID.
Or
Create an object of class Sentence with input as a string and call the function getNouns on it.

#### Example Usage:
tokenize = Sentence("Moto G 2nd Generation, a brilliant display, stereo sound.......")
tokenize.getNouns()

### Products
The function getProducts takes input as delhivery category ID(INTEGER) and count of products required (INTEGER)

#### Example Usage:
getProducts(20,10)

----------------------------
### Prerequisites
----------------------------
Products table should exist in the database.
Run Products/database/InitialiseDB.py to perform following operations:
1. Create and Insert data into Channel_Category_Mapping and Category Tables.
2. Update Products table

----------------------------
### Database
----------------------------
To change or add database details, go to database folder under Products/ and modify dbInfo.py:

1. Database

2. Collections
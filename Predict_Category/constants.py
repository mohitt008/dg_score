import re

second_level_cat_names = \
            ["Beauty Products and Personal Care",
                  "Camera and Photos",
                  "Mobile Phone, Tablets and Accesories",
                  "Apparel & Accessories",
                  "Watches, Eyewear and Jewellery",
                  "Electronics and Appliances",
                  "Home and Kitchen",
                  "Computers and Laptops",
                  "Shoes and Footwear"
            ]

CLEAN_PRODUCT_NAME_REGEX = re.compile('[0-9.]+(?=[a-zA-Z]{1}[0-9]+)|[0-9.]+[a-zA-Z}{1}|[0-9.]+|[a-zA-Z]+')
VOLUME_ML_REGEX = re.compile('[0-9]+[\s]*ml')

# Alpha-num. Remove all punctuation, spaces etc
ALPHA_NUM_REGEX = re.compile('[\W_]+')

# Redis cache expiry 15 days (in sec)
CACHE_EXPIRY = 1296000


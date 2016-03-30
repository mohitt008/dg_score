__author__ = 'delhivery'
import os
ROOT_PATH = os.path.abspath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                      os.path.pardir)), os.path.pardir))

words_to_remove = \
    [
        'new', 'item new', "item"
    ]
second_level_cat_names =\
    ["Apparel and Accessories",
     "Automotive",
     "Beauty Products and Personal Care",
     "Books, Software and E-learning",
     "Camera and Photos",
     "Computers, Laptops and Accessories",
     "Electronics and Appliances",
     "Handbags, Bags and Luggage",
     "Health and Wellness",
     "Home and Kitchen",
     "Mobile Phone, Tablets and Accessories",
     "Shoes and Footwear",
     "Sports and Outdoors",
     "Watches, Eyewear and Jewellery"
     ]
#
# second_level_cat_names_nb=\
#     ["Apparel and Accessories",
#      "Automotive",
#      "Beauty Products and Personal Care",
#      "Books, Software and E-learning",
#      "Camera and Photos",
#      "Computers, Laptops and Accessories",
#      "Electronics and Appliances",
#      "Handbags, Bags and Luggage",
#      "Health and Wellness",
#      "Home and Kitchen",
#      "Shoes and Footwear",
#      "Sports and Outdoors",
#      "Watches, Eyewear and Jewellery",
#
#     ]
#
#
# second_level_cat_names_rf=\
#     [ "Mobile Phone, Tablets and Accessories"]


"""
This file includes the database,collection names to be used in the scripts.
"""
database = 'cat_identification'
vendor_table = 'vendors'
product_table = 'products_new'
delhivery_category_table = 'delhivery_categories'
vendor_category_table = 'vendor_categories'
vendor_delhivery_mapping = 'vendor_delhivery_mapping'
json_dir_prefix = ROOT_PATH + '/' + 'data/pc_data'

"""
Specify the files/folder to import here
"""

folder_to_import = 'xyz'
delhivery_category_file = ''
vendor_category_file = ''

# Load_Settings Folder

# Train_Test_Settings

# Predict_Paths


cnn_params = {
    # Data Cleaning Parameters
    'num_feature': 10000,  # Number of feature to be chosen after feature selection (default: None)
    'min_word_count': 3,  # Minimum occurrence of a word in input data for the word to be considered
    'max_title_length': 100,  # Max length of input product title to be considered

    # Model Hyperparameters
    'embedding_dim': 128,  # Dimensionality of character embedding
    'filter_sizes': [2, 3, 4, 5],  # Filter sizes for CNN
    'num_filters': 128,  # Number of filters per filter size
    'dropout_keep_prob': 0.5,  # Dropout keep probability
    'l2_reg_lambda': 0.0,  # L2 regularizaion lambda

    # Training parameters
    'batch_size': 100,  # Batch Size
    'num_epochs': 10,  # Number of training epochs

    # Testing parameters
    'confidence_threshold': 0.1,  # Use CNN result only if confidence is above this value

    # Misc Parameters
    'allow_soft_placement': True,  # Allow soft device placement
    'log_device_placement': False  # Log placement of ops on devices
}

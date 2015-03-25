from pymongo import MongoClient,ASCENDING
from dbInfo import *

client = MongoClient()
db = client[database]

delhiveryCategories = {0: {'category': 'Software and E-learning'},
     5: {'category': 'Musical Instruments'},
     10: {'category': 'Books'},
     15: {'category': 'Industrial and Scientific Goods'},
     20: {'category': 'Computers and Laptops'},
     25: {'category': 'Shoes and Footwear'},
     30: {'category': 'Movies, Music and Video Games'},
     35: {'category': 'Home and Kitchen'},
     40: {'category': 'Grocery and Gourmet Food'},
     45: {'category': 'Mobile Phone, Tablets and Accesories'},
     50: {'category': 'Toys and Games'},
     55: {'category': 'Health and Wellness'},
     60: {'category': 'Electronics and Appliances'},
     65: {'category': 'Handbags, Bags and Luggage'},
     70: {'category': 'Sports and Outdoors'},
     75: {'category': 'Apparel & Accessories'},
     80: {'category': 'Tools and Hardware'},
     85: {'category': 'Automotive'},
     90: {'category': 'Watches, Eyewear and Jewellery'},
     95: {'category': 'Beauty Products and Personal Care'},
     100: {'category': 'Camera and Photos'},
     105: {'category': 'Pet Supplies'},
     110: {'category': 'Office Products'},
     115: {'category': 'Baby Care'},
     120: {'category': 'Gifts'},
     125: {'category': 'KitchenWare'},
     130: {'category': 'Uncategorized'},
     201: {'category': 'Computers and Laptops',
      'sub_category': 'Routers and Modems'},
     202: {'category': 'Computers and Laptops', 'sub_category': 'Laptop'},
     203: {'category': 'Computers and Laptops',
      'sub_category': 'Computer Components'},
     204: {'category': 'Computers and Laptops',
      'sub_category': 'Computer Accessories'},
     205: {'category': 'Computers and Laptops', 'sub_category': 'Desktops'},
     206: {'category': 'Computers and Laptops',
      'sub_category': 'Pen Drives and Data Card'},
     207: {'category': 'Computers and Laptops',
      'sub_category': 'External Hard Drives'},
     208: {'category': 'Computers and Laptops', 'sub_category': 'Monitor'},
     209: {'category': 'Computers and Laptops', 'sub_category': 'Speakers'},
     210: {'category': 'Computers and Laptops',
      'sub_category': 'Headphones & Mic'},
     211: {'category': 'Computers and Laptops',
      'sub_category': 'Printers and Scanners'},
     251: {'category': 'Shoes and Footwear', 'sub_category': "Kids' Footwear"},
     252: {'category': 'Shoes and Footwear', 'sub_category': "Women's Footwear"},
     253: {'category': 'Shoes and Footwear', 'sub_category': "Men's Footwear"},
     351: {'category': 'Home and Kitchen', 'sub_category': 'Furniture'},
     352: {'category': 'Home and Kitchen', 'sub_category': 'Kitchenware'},
     353: {'category': 'Home and Kitchen', 'sub_category': 'Home Decor'},
     354: {'category': 'Home and Kitchen', 'sub_category': 'Home Furnishing'},
     401: {'category': 'Grocery and Gourmet Food',
      'sub_category': 'Frozen Food Items'},
     451: {'category': 'Mobile Phone, Tablets and Accesories',
      'sub_category': 'Powerbanks'},
     452: {'category': 'Mobile Phone, Tablets and Accesories',
      'sub_category': 'Tablets'},
     453: {'category': 'Mobile Phone, Tablets and Accesories',
      'sub_category': 'Mobiles'},
     454: {'category': 'Mobile Phone, Tablets and Accesories',
      'sub_category': 'Case, Cover and Screenguards'},
     455: {'category': 'Mobile Phone, Tablets and Accesories',
      'sub_category': 'Mobile Accessories'},
     456: {'category': 'Mobile Phone, Tablets and Accesories',
      'sub_category': 'Digital Goods'},
     551: {'category': 'Health and Wellness', 'sub_category': 'Pharmacy Products'},
     552: {'category': 'Health and Wellness',
      'sub_category': 'E-Ciggarettes and E-Sheesha'},
     553: {'category': 'Health and Wellness',
      'sub_category': 'Massage and Pain Relief'},
     554: {'category': 'Health and Wellness',
      'sub_category': 'Hospital and Medical Equipment'},
     555: {'category': 'Health and Wellness', 'sub_category': 'Diabetic Care'},
     556: {'category': 'Health and Wellness', 'sub_category': 'Sexual Wellness'},
     557: {'category': 'Health and Wellness',
      'sub_category': 'Protein and Health Supplements'},
     558: {'category': 'Health and Wellness',
      'sub_category': 'Bp and Heart Rate Monitors'},
     559: {'category': 'Health and Wellness', 'sub_category': 'Health Devices'},
     560: {'category': 'Health and Wellness', 'sub_category': 'Homeopathy'},
     561: {'category': 'Health and Wellness',
      'sub_category': 'Woman Care and Motherhood'},
     601: {'category': 'Electronics and Appliances', 'sub_category': 'Projectors'},
     602: {'category': 'Electronics and Appliances',
      'sub_category': 'Portable Audio Players'},
     603: {'category': 'Electronics and Appliances',
      'sub_category': 'Headphones and Earphones'},
     604: {'category': 'Electronics and Appliances',
      'sub_category': 'Home Appliances'},
     605: {'category': 'Electronics and Appliances', 'sub_category': 'TV'},
     606: {'category': 'Electronics and Appliances', 'sub_category': 'Speakers'},
     607: {'category': 'Electronics and Appliances',
      'sub_category': 'Audio and Video Accessories'},
     608: {'category': 'Electronics and Appliances',
      'sub_category': 'Washing Machine'},
     701: {'category': 'Sports and Outdoors', 'sub_category': 'Sports Clothing'},
     702: {'category': 'Sports and Outdoors', 'sub_category': 'Outdoor Gear'},
     703: {'category': 'Sports and Outdoors', 'sub_category': 'Sports Equipment'},
     704: {'category': 'Sports and Outdoors',
      'sub_category': 'Exercise and Fitness'},
     751: {'category': 'Apparel & Accessories',
      'sub_category': "Women's Clothing"},
     752: {'category': 'Apparel & Accessories', 'sub_category': "Men's Clothing"},
     801: {'category': 'Tools and Hardware',
      'sub_category': 'Bathroom Fittings and Accesories'},
     802: {'category': 'Tools and Hardware', 'sub_category': 'Other Tools'},
     803: {'category': 'Tools and Hardware',
      'sub_category': 'Paint and Paint Tools'},
     851: {'category': 'Automotive', 'sub_category': 'Bike Accessories'},
     852: {'category': 'Automotive', 'sub_category': 'Automobiles'},
     853: {'category': 'Automotive', 'sub_category': 'Tyres and Spares'},
     854: {'category': 'Automotive', 'sub_category': 'Car Audio and GPS'},
     855: {'category': 'Automotive', 'sub_category': 'Car Accesories'},
     901: {'category': 'Watches, Eyewear and Jewellery',
      'sub_category': 'Watches'},
     902: {'category': 'Watches, Eyewear and Jewellery',
      'sub_category': 'Jewellery'},
     903: {'category': 'Watches, Eyewear and Jewellery',
      'sub_category': 'Eyewear'},
     951: {'category': 'Beauty Products and Personal Care',
      'sub_category': 'Bath'},
     952: {'category': 'Beauty Products and Personal Care',
      'sub_category': 'Hair Care'},
     953: {'category': 'Beauty Products and Personal Care',
      'sub_category': 'Deodrants and Fragrances'},
     954: {'category': 'Beauty Products and Personal Care',
      'sub_category': 'Women Hygiene'},
     955: {'category': 'Beauty Products and Personal Care',
      'sub_category': 'Shaving and Grooming'},
     956: {'category': 'Beauty Products and Personal Care',
      'sub_category': 'Oral Care'},
     957: {'category': 'Beauty Products and Personal Care',
      'sub_category': 'Skin Care'},
     958: {'category': 'Beauty Products and Personal Care',
      'sub_category': 'Everyday Makeup'},
     1001: {'category': 'Camera and Photos', 'sub_category': 'Camera Lens'},
     1002: {'category': 'Camera and Photos', 'sub_category': 'Digital Camera'},
     1003: {'category': 'Camera and Photos',
      'sub_category': ' Binoculars and Telescopes'},
     1004: {'category': 'Camera and Photos', 'sub_category': 'Camcoders'},
     1005: {'category': 'Camera and Photos',
      'sub_category': 'Digital Photo Frames'},
     1006: {'category': 'Camera and Photos', 'sub_category': 'DSLR'},
     1007: {'category': 'Camera and Photos', 'sub_category': 'Memory Cards'},
     1008: {'category': 'Camera and Photos', 'sub_category': 'Camera Accesories'},
     1101: {'category': 'Office Products', 'sub_category': 'Desk Accesories'},
     1102: {'category': 'Office Products', 'sub_category': 'Office Stationary'},
     1103: {'category': 'Office Products',
      'sub_category': 'Ink Cartridges and Toners'}
}

snapdealCategories=[{
        'Toys & Games': {
            'Education & School Supplies': (67,50),
            'Ride On & Scooters': (702,50),
            'Party Supplies': (513,50),
            'Bicycles & Tricycles': (700,50),
            'Die Cast Vehicle': (10,50),
            'Board Games': (698,50),
            'Soft Toys': (73,50),
            'Kids Room Decor': (71,353),
            'Puzzles & Cubes': (699,50),
            'Indoor Games': (68,50),
            'Outdoor & Sports': (72,70),
            'Dolls & Doll Houses': (355,50),
            'Activity Sets': (459,50),
            'Action Toys & Figures': (460,50),
            'id': (66,-1),
            'Prams & Strollers': (361,50),
            'Electronic Toys': (132,50)
        },
        'Movies & Music': {
            'Bollywood Movies': (518,30),
            'World Cinema': (519,30),
            'Hollywood Movies': (517,30),
            'id': (516,-1),
            'International Music': (522,30),
            'Indian Music': (523,30),
            'TV Shows': (521,30),
            'Regional Movies': (520,30)
        },
        'Cameras & Accessories': {
            'Camera Lenses': (615,1001),
            'DSLR': (292,1006),
            'Digital Photo Frames': (294,1005),
            'Camera Accessories': (296,1008),
            'id': (290,-1),
            'Digital Cameras': (291,1002),
            'Memory Cards': (304,1007),
            'Binoculars & Telescopes': (295,1003),
            'Camcorders': (293,1004)
        },
        'Automotive': {
            'Vehicle Services & Security Solutions': (2337,85),
            'Car Audio & GPS': (311,854),
            'Car Accessories': (313,855),
            'id': (310,-1),
            'Helmets': (2354,851),
            'Biker Gear & Accessories': (317,851),
            'Tyres & Alloys': (335,853),
            'Cars & Bikes': (590,852),
            'Parts & Spares': (738,853),
            'Car Care & Fresheners': (312,855)
        },
        'Chocolates & Snacks': {
            'id': (403,-1),
            'Chocolates & Cookies': (404,40),
            'Gift Packs': (405,40)
        },
        'Baby Care': {
            'Imported Products': (716,115),
            'Bath, Skin & Health Care': (69,115),
            'Gifting & Super Savers': (719,115),
            'Baby Gear & Safety': (717,115),
            'Diapers & Potty Training': (429,115),
            'id': (715,-1),
            'Moms & Maternity': (718,115),
            'Feeding & Nursing': (430,115),
            'Baby Bedding': (431,115)
        },
        'Hobbies': {
            'Crafts & Hobbies': (684,50),
            'Antiques & Collectibles': (687,50),
            'Outdoor Hobbies': (688,50),
            'id': (682,-1),
            'Science Kits': (686,50),
            'Remote Control Models': (683,50),
            'Art & Hobbies': (685,50),
            'Indoor Games & Hobbies': (689,50)
        },
        'Gifting & Events': {
            'Gifts For Him': (645,120),
            'Gift Vouchers': (648,120),
            'Gift For Kids': (646,120),
            'id': (643,-1),
            'Event Essentials': (653,120),
            'Dry Fruits & Chocolates': (652,120),
            'Sweets': (727,120)
        },
        'Computers & Peripherals': {
            'Headphones & Mics': (154,210),
            'Data Cards': (334,206),
            'Laptop Batteries': (326,204),
            'Routers & Modems': (286,201),
            'Mouse': (151,203),
            'Value Added Services': (705,20),
            'Speakers': (153,209),
            'Webcams': (282,204),
            'Pen Drives': (52,206),
            'Printers & Scanners': (58,211),
            'RAM': (703,203),
            'id': (21,-1),
            'Computer Accessories': (150,204),
            'External Hard Disks': (53,207),
            'Adapters': (327,204),
            'Processor': (704,203),
            'Graphics Card': (305,203),
            'Internal Hard Drives': (283,203),
            'Keyboard': (152,203),
            'Desktops': (55,205),
            'Software': (59,0),
            'Laptops': (57,202),
            'Computer Components': (56,203),
            'Monitors': (121,208)
        },
        "Men's Clothing": {
            'Innerwear & Sleepwear': (196,752),
            'Jeans': (194,752),
            'Sweatshirts': (358,752),
            'Shirts': (191,752),
            'Shorts & 3/4ths': (201,752),
            'Sweaters': (359,752),
            'Trackpants & Tracksuits': (357,752),
            'Suits & Blazers': (362,752),
            'Suitings & Shirtings': (195,752),
            'Kurtas, Pyjamas & Sherwanis': (110,752),
            'Jackets': (200,752),
            'id': (17,-1),
            'Trousers & Chinos': (192,752),
            'Polo T Shirts': (470,752),
            'T Shirts': (193,752)
        },
        'Mobiles & Tablets': {
            'Mobile Screen Guards': (677,454),
            'Bluetooth Devices': (675,455),
            'Mobile Accessories': (29,455),
            'Cables&Chargers': (868,455),
            'Tablet Accessories': (336,455),
            'Earphones': (851,603),
            'Memory Cards': (228,455),
            'Value Added Services': (574,45),
            'Mobile Cases & Covers': (676,454),
            'Batteries': (678,455),
            'Power Banks': (679,451),
            'International SIM Cards': (2234,455),
            'id': (12,-1),
            'Digital Goods': (2241,456),
            'Mobile Phones': (175,453),
            'Mobile Spare Parts': (735,455),
            'Tablets': (133,452)
        },
        'Hardware & Sanitary Fittings': {
            'Paints and Paint Tools': (789,803),
            'Door & Door Fittings': (856,80),
            'Kitchen Fittings & Sinks': (869,80),
            'Faucets': (695,801),
            'Wall and Floorings': (859,80),
            'Bathroom Accessories & Fittings': (786,801),
            'Sanitaryware': (697,801),
            'Tools & Hardware': (93,80),
            'id': (694,-1),
            'Taps & Faucets': (853,801),
            'Building Material': (892,80),
            'Electrical Fixtures': (790,80),
            'Showers': (696,801),
            'Bathroom Accessories': (600,801)
        },
        'Home Improvement': {
            'Pet Supplies': (225,105),
            'Innovative Products': (888,35),
            'id': (864,-1),
            'Home Utility': (865,35),
            'Home Cleaning': (95,35),
            'Plants & Gardening': (215,35)
        },
        'Fragrances': {
            "Women's Perfumes": (729,953),
            "Men's Perfumes": (728,953),
            'Deodorants': (136,953),
            'id': (31,-1),
            'Body Mists': (587,953),
            'Air Freshners': (138,953),
            'Attars': (881,953),
            'Teens Perfume': (2273,953)
        },
        'Kids Clothing': {
            'Boys Clothing (8-14 Yrs)': (814,752),
            'Girls Clothing (8-14 Yrs)': (830,751),
            'id': (2373,-1),
            'Infant Wear': (557,75),
            'Boys Clothing (2-8 Yrs)': (524,752),
            'Girls Clothing (2-8 Yrs)': (539,751)
        },
        'Kitchenware': {
            'Cookware & Bakeware': (89,125),
            'Flasks & Tiffins': (208,125),
            'Dining & Serving': (205,125),
            'Kitchen Storage': (207,125),
            'Bar & Glassware': (88,125),
            'id': (5,-1),
            'Disposables': (883,125),
            'Hotel & Catering Supplies': (638,125),
            'Tea & Coffee Serveware': (206,125),
            'Kitchen Tools': (204,125),
            'Microwave Cooking': (203,125)
        },
        'Stationery': {
            'Art & Craft Supplies': (465,1102),
            'Office Supplies & Machines': (464,1102),
            'School Supplies': (601,1102),
            'id': (461,-1),
            'Pens & Markers': (462,1102),
            'Calculators': (625,1102),
            'Stationery Supplies': (463,1102),
            'Personalized Products': (626,1102)
        },
        'Real Estate': {
            'id': (897,-1),
            'Apartments': (898,130)
        },
        'Office Equipment': {
            'Photocopiers': (756,110),
            'Vending Machines & Supplies': (761,110),
            'Lab Equipment': (2332,110),
            'Janitorial Supplies': (762,110),
            'id': (753,-1),
            'Security Systems': (755,110),
            'Note Counters & Paper Shredders': (754,110),
            'Other Machines': (763,110),
            'POS Equipment': (760,110),
            'Labeling & Stamping Machine': (757,110)
        },
        'Furniture': {
            'Tables': (616,351),
            'Prefabricated Homes': (2302,351),
            'Bean Bags': (418,351),
            'Living Room ': (581,351),
            'Space Saving Furniture': (2338,351),
            'id': (580,-1),
            'Bedroom ': (582,351),
            'Outdoor & Garden': (620,351),
            'Chairs': (619,351)
        },
        'Online Education': {
            'Study Abroad': (919,0),
            'Online Magazines': (916,0),
            'E-books': (915,0),
            'Counselling': (862,0),
            'id': (746,-1),
            'Educational Devices': (752,0),
            'School Education': (861,0),
            'Value Added Services': (918,0),
            'Professional Courses & Certifications': (748,0)
        },
        "Women's Ethnic Wear": {
            'Kurtis': (178,751),
            'Blouses and Petticoats': (692,751),
            'Lehengas': (417,751),
            'Dupattas & Shawls': (189,751),
            'Dress Material': (179,751),
            'id': (691,-1),
            'Burqas': (190,751),
            'Salwar Suits': (416,751),
            'Salwars & Churidhars': (187,751),
            'Sarees': (176,751)
        },
        'Sports & Fitness': {
            'id': (159,-1),
            'Sports': (2371,70),
            'Fitness': (2372,704)
        },
        'Bags & Luggage': {
            'Womens Handbags': (16,65),
            'School Bags': (436,65),
            'Travel Accessories': (435,65),
            'Utility Bags': (572,65),
            'Laptop Bags': (434,65),
            'Briefcases': (876,65),
            'Luggage & Suitcases': (38,65),
            'Clutches': (573,65),
            'Hiking Bags & Rucksacks': (873,65),
            'Laptop Sleeves & Cases': (874,65),
            'Travel Duffles': (438,65),
            'id': (474,-1),
            'Backpacks': (402,65)
        },
        'Watches': {
            'Couple Watches': (480,901),
            "Men's Watches": (477,901),
            "Women's Watches": (478,901),
            'Kids Watches': (479,901),
            'id': (476,-1),
            'Smart Watches': (592,901),
            'Watch Accessories': (593,901)
        },
        'Home Furnishing': {
            'Fabrics': (606,354),
            'Bath Linen': (209,354),
            'Kids Bedding & More': (721,354),
            'Mattresses': (579,354),
            'Mats & Carpets': (220,354),
            'Cushions & Covers': (337,354),
            'Curtains & Accessories': (214,354),
            'id': (475,-1),
            'Table & Kitchen Linen': (221,354),
            'Pillows & Covers': (866,354),
            'Bed Linen': (211,354),
            'Blankets & Quilts': (607,354)
        },
        'Fashion Jewellery': {
            'Rings': (342,902),
            'Designer Jewelry': (134,902),
            'Mangalsutra': (345,902),
            'The Craft Collective': (2209,902),
            'Necklaces & Sets': (344,902),
            'Silver Jewellery': (42,902),
            'Wedding Accessories': (674,902),
            'Idols & Articles': (351,902),
            'Pendant & Sets': (343,902),
            'Earrings': (341,902),
            'Jewellery Boxes & Cleaning Kits': (353,902),
            'Kids Jewellery': (354,902),
            'Chains': (348,902),
            'Mens Jewellery': (49,902),
            'Bangles & Bracelets': (346,902),
            "God's Jewellery": (2336,902),
            'id': (6,-1),
            'Anklets, Toe-rings & More': (48,902)
        },
        'Beauty & Personal Care': {
            'Makeup': (11,958),
            'Hair Loss Treatments': (741,952),
            'Shaving & Grooming': (144,955),
            'Beauty Accessories': (588,95),
            'Kits & Combos': (589,95),
            'Skin Care': (34,95),
            'Bath & Body': (32,951),
            'Hair Care': (20,952),
            'Imported Products': (739,95),
            'Razors and Cartridges': (743,955),
            'id': (586,-1),
            'Bath Soaps and Salts': (742,951),
            'Feminine Care': (306,954),
            'Oral Care': (223,956)
        },
        'The Designer Studio': {
            'Preeti Jhawar': (2268,75),
            'Indian by Manish Arora': (930,75),
            '5 Elements': (2263,75),
            'SAMOR by Pragya and Megha Samor': (2267,75),
            'Rajesh Pratap Singh': (2374,75),
            'Varun Bahl': (2227,75),
            'Samant Chauhan': (931,75),
            'id': (2224,-1),
            'Ashish N Soni': (926,75),
            'Nida Mehmood': (2249,75),
            'Malini Ramani': (2231,75)
        },
        'Gourmet': {
            'Oils, Vinegars, Sauces': (901,40),
            'Beverages': (904,40),
            'Nuts & Dry Fruits': (907,40),
            'International Groceries': (900,40),
            'id': (899,-1),
            'Dips, Spreads & Jams': (903,40),
            'Snacks': (908,40),
            'Ready to Cook/Eat': (906,40)
        },
        'Books': {
            'Self-Help': (388,10),
            'Religion and Spirituality': (386,10),
            'Literature and Fiction': (365,10),
            'History and Politics': (381,10),
            'Biographies and Autobiographies': (398,10),
            'Comics and Graphic Novels': (374,10),
            'id': (364,-1),
            'Reference': (385,10),
            'Academic and Professional': (366,10),
            'Children and Young Adults': (372,10)
        },
        'Footwear': {
            'id': (18,-1),
            'Kids Footwear': (493,251),
            "Men's Footwear ": (226,253),
            "Women's Footwear": (227,252)
        },
        'Precious Jewellery': {
            'Nosepins & Noserings': (665,90),
            'Loose Diamonds': (669,90),
            'Precious Gifts & Articles': (671,90),
            'Rings': (659,90),
            'Necklaces & Sets': (668,90),
            'Loose Gemstones': (670,90),
            'Pendants': (661,90),
            'Anklets & Toe-rings': (672,90),
            'Earrings': (660,90),
            'Mangalsutra': (663,90),
            'Kids Jewellery': (673,90),
            'Chains': (664,90),
            'id': (658,-1),
            'Bangles & Bracelets': (667,90),
            'Silver Coins & Bars': (2363,90),
            'Gold Coins & Bars': (349,90),
            'Mens Jewellery': (666,90)
        },
        'Eyewear': {
            'Sunglasses': (15,903),
            'Eyeglasses & Frames': (140,903),
            'Reading Glasses': (713,903),
            'id': (473,-1),
            'Contact Lenses': (319,903),
            'Power Eyeglasses': (594,903)
        },
        'TVs, Audio & Video': {
            'Stereo Components': (632,60),
            'Projectors': (629,601),
            'DJ & Karaoke': (634,60),
            'Video Players': (628,60),
            'Audio & Video Accessories': (635,607),
            'Speakers': (631,606),
            'Televisions': (64,605),
            'Home Theatre Systems': (630,607),
            'Headphones & Earphones': (288,603),
            'id': (7,-1),
            'Landline Phones': (63,60),
            'MP3 & Media Players': (627,602)
        },
        'Nutrition & Supplements': {
            'Family Nutrition': (597,557),
            'id': (764,-1),
            'Pet Wellness': (2243,557),
            'Vitamins & Minerals': (433,557),
            'Proteins & Sports Nutrition': (322,557),
            'Ayurveda & Organic Products': (339,557)
        },
        "Women's Clothing": {
            'Trackpants & Track Suits': (423,751),
            'Plus & Maternity': (424,751),
            'Lingerie & Sleepwear': (2251,751),
            'id': (23,-1),
            'Top Wear': (2304,751),
            'Bottom Wear': (2301,751),
            'Winter Wear': (2240,751),
            'Dresses': (724,751)
        },
        'Home Decoratives': {
            'Candles & Fragrances': (212,353),
            'Clocks': (213,353),
            'id': (217,-1),
            'Wall Decor': (222,353),
            'Lamps & Lighting': (218,353),
            'Religion & Spirituality': (129,353),
            'Home Decor': (96,353),
        },
        'Health, Wellness & Medicine': {
            'Health Devices': (321,559),
            'Imported Products': (596,55),
            'Health Checkup': (736,55),
            'Respiratory Care': (768,55),
            'Massager & Pain Relief': (767,553),
            'Hospital & Medical Equipment': (774,554),
            'E-Cigarette & E-Shisha': (773,552),
            'Sexual Wellness': (324,556),
            'Homeopathy': (769,560),
            'Women Care & Motherhood': (770,55),
            'Combos for Bulk Buy': (515,55),
            'Alternative Health Therapies': (693,55),
            'Yoga & Meditation': (885,55),
            'id': (318,-1),
            'Weighing Scales & Daily Needs': (772,55),
            'Supports & Rehabilitation': (323,55),
            'BP & Heart Rate Monitors': (791,558),
            'Diabetic Care': (595,555),
            'Pharmacy Products': (709,551)
        },
        'Fashion Accessories': {
            'Cufflinks': (399,75),
            'Pocket Squares': (490,75),
            'Suspenders': (489,75),
            'Party Accessories': (884,75),
            'Card Holders': (598,75),
            'Headwraps': (485,75),
            'Socks': (455,75),
            'Mufflers': (482,75),
            'Key Chains': (491,75),
            'Umbrella': (486,75),
            'Wallets': (300,75),
            'id': (481,-1),
            'Stoles & Scarves': (363,75),
            'Mobile Pouches': (487,75),
            'Handkerchiefs': (483,75),
            'Trims': (886,75),
            'Hair Accessories': (714,75),
            'Necktie': (400,75),
            'Flags': (654,75),
            'Gift Sets': (401,75),
            'Cravats': (484,75),
            'Belts': (328,75),
            'Shawls': (657,75)
        },
        'TV Shop': {
            'TV Shop Kids Toys': (2300,50),
            'TV Shop Appliances': (2277,60),
            'TV Shop Home & Kitchen': (2296,35),
            'TV Shop Fashion': (2220,75),
            'TV Shop Home Furnishing': (2297,354),
            'id': (2218,-1),
            'TV Shop Mobiles & Tablets': (2291,45),
            'TV Shop H W & Industrials': (2298,80),
            "TV Shop Men's Footwear": (2284,253),
            "TV Shop Men's Apparel": (2279,752),
            "TV Shop Women's Apparel": (2293,751),
        },
        'Musical Instruments': {
            'Keyboards,MIDI & Accessories': (505,5),
            'Other Instruments': (510,5),
            'Brass & Wind Instruments': (732,5),
            'DJ Equipment': (733,5),
            'Indian Instruments & Accessories': (506,5),
            'Drums, Percussion & Accessories': (507,5),
            'id': (502,-1),
            'Effects & Amplifiers': (731,5),
            'Guitars & Accessories': (503,5),
            'Public Address Systems': (2210,5),
            'Live & Recording': (509,5)
        },
        'Gaming': {
            'Gaming Accessories': (577,30),
            'Gaming Imports': (681,30),
            'Gaming Merchandise': (776,30),
            'id': (575,-1),
            'Gaming Titles': (578,30),
            'Gaming Consoles': (576,30),
            'Digital Games': (775,30)
        },
        'Appliances': {
            'Home Appliances': (97,604),
            'Kitchen Appliances': (98,604),
            'Imported Appliances': (468,60),
            'id': (9,-1),
            'Large Appliances': (2369,60),
            'Personal Care Appliances': (229,60)
        }
}]

def createChannelCategoryMapping(channelCategoryMappingTable):

    """
    Input: Channel-Category-Mapping-Table Name (String)
    Process: Loops around snapdealCategories to fetch snapdeal_id and delhivery category ID
    and inserts into the table 
    """
    channelCategory = db[channelCategoryMappingTable]
    for category in snapdealCategories[0]:
        # print category
        for snapdeal_ids in snapdealCategories[0][category]:
            snapdeal_id =  snapdealCategories[0][category][snapdeal_ids][0]
            delhivery_id = snapdealCategories[0][category][snapdeal_ids][1]
            channelCategory.insert({"Channel_Id":1,"Channel_Category_Id":snapdeal_id,"Category_Id":delhivery_id})

def updateProductCount(ProductsTable,channelCategoryMappingTable):

    """
    Input: Product Table Name (String), Channel-Category-Mapping-Table Name (String)
    Process: Groups product table based on product_category_id and counts 
    the sum of each category. Update Channel-Category-Mapping-Table to 
    include a new field "count", calculated from above. 
    """
    products = db[ProductsTable]
    channelCategory = db[channelCategoryMappingTable]
    countProducts = products.aggregate([{"$group":{"_id":"$product_category_id","count":{"$sum":1}}}])

    for categories in countProducts['result']:
        channelCategory.update({"Channel_Category_Id":categories["_id"]},{"$set":{"count":categories["count"]}})

    channelCategory.update({"count":{"$exists":False}},{"$set":{"count":0}},multi=True)

def updateSequenceProdTable(ProductsTable):

    """
    Input: Product Table Name (String)
    Process: Update product table to include a new field "seq" to have
    sequence number in eah category. 
    """
    products = db[ProductsTable]
    categories = products.distinct("product_category_id")

    for category in categories:
        count  = 1
        for product in products.find({"product_category_id":category}):
            products.update({"_id":product["_id"]},{"$set":{"seq":count}})
            count = count + 1

def getParent(categoryName):

    """
    Input: Category Name (String)
    Return parent of the category from delhiveryCategories declared above.
    """
  for key,value in delhiveryCategories.iteritems():
    if delhiveryCategories[key]['category'] == categoryName and 'sub_category' not in delhiveryCategories[key]:
      return key

def createCategoryTable(categoryTable):

    """
    Input: category Table Name (String)
    Process: Computes ID for each delhivery category defined above and it's parent.
    """
    catTable = db[categoryTable]
    category_table = {}
    for key,value in delhiveryCategories.iteritems():
      if 'sub_category' in delhiveryCategories[key]:
        category_table[delhiveryCategories[key]['sub_category']] = {"Category_Id":key,"Category_Parent":getParent(delhiveryCategories[key]['category'])}
      else:
        category_table[delhiveryCategories[key]['category']] = {"Category_Id":key,"Category_Parent":-1}
      
    for key in category_table:
      catTable.insert({"Category_Id":category_table[key]['Category_Id'],"Category_Name":key,"Category_Parent":category_table[key]["Category_Parent"]})


if __name__ == '__main__':
    createChannelCategoryMapping(channelCategoryTable)
    # print "created ChannelCategoryMapping"
    createCategoryTable(categoryTable)
    # print "created categoryTable"
    updateProductCount(productTable,channelCategoryTable)
    # print "updated Channel Category Table"
    updateSequenceProdTable(productTable)
    # print "updated ProductsTable"
Categories = []

data=[
("Software and E-learning",[]),
("Musical Instruments",[]),
("Books",[]),
("Industrial and Scientific Goods",[]),
("Computers and Laptops",["Routers and Modems","Laptop","Computer Components","Computer Accessories","Desktops","Pen Drives and Data Card","External Hard Drives","Monitor","Speakers","Headphones & Mic","Printers and Scanners"]),
("Shoes and Footwear",["Kids' Footwear","Women's Footwear","Men's Footwear"]),
("Movies, Music and Video Games",[]),
("Home and Kitchen",["Furniture","Kitchenware","Home Decor","Home Furnishing"]),
("Grocery and Gourmet Food",["Frozen Food Items"]),
("Mobile Phone, Tablets and Accesories",["Powerbanks","Tablets","Mobiles","Case, Cover and Screenguards","Mobile Accessories","Digital Goods"]),
("Toys and Games",[]),
("Health and Wellness",["Pharmacy Products","E-Ciggarettes and E-Sheesha","Massage and Pain Relief","Hospital and Medical Equipment","Diabetic Care","Sexual Wellness","Protein and Health Supplements","Bp and Heart Rate Monitors","Health Devices","Homeopathy","Woman Care and Motherhood"]),
("Electronics and Appliances",["Projectors","Portable Audio Players","Headphones and Earphones","Home Appliances","TV","Speakers","Audio and Video Accessories","Washing Machine"]),
("Handbags, Bags and Luggage",[]),
("Sports and Outdoors",["Sports Clothing","Outdoor Gear","Sports Equipment","Exercise and Fitness"]),
("Apparel & Accessories",["Women's Clothing","Men's Clothing"]),
("Tools and Hardware",["Bathroom Fittings and Accesories","Other Tools","Paint and Paint Tools"]),
("Automotive",["Bike Accessories","Automobiles","Tyres and Spares","Car Audio and GPS","Car Accesories"]),
("Watches, Eyewear and Jewellery",["Watches","Jewellery","Eyewear"]),
("Beauty Products and Personal Care",["Bath","Hair Care","Deodrants and Fragrances","Women Hygiene","Shaving and Grooming","Oral Care","Skin Care","Everyday Makeup"]),
("Camera and Photos",["Camera Lens","Digital Camera"," Binoculars and Telescopes","Camcoders","Digital Photo Frames","DSLR","Memory Cards","Camera Accesories"]),
("Pet Supplies",[]),
("Office Products",["Desk Accesories","Office Stationary","Ink Cartridges and Toners"]),
("Baby Care",[]),
("Gifts",[]),
("KitchenWare",[]),
("Uncategorized",[])
]


id_cat_dict={}
for i,x in enumerate(data):
#     print (x)
    id_cat_dict[5*i]={'category':x[0]}
    for j,y in enumerate(x[1]):
        id_cat_dict[50*i+j+1]={'category':x[0],'sub_category':y}

import json
f=open("category_tree.json",'w')
json.dump(id_cat_dict,f)
f.close()
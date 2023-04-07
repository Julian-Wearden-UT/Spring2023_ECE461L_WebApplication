import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient("<PLACE YOUR CONNECTION CODE THING HERE>")
# The database to store the collection in (HardwareSet is the name, it is created if not existing already)
db = client.HardwareSet
# The collection to store the items in (HWSet1 is the name, it is created if not existing already)
collection = db.HWSet1
itemName = input("What hardware set do you want to modify? Enter the exact name: ")
query = collection.find_one({"Description": itemName})
print(query)
if(query == None):
        print("Looks like that doesn't exist in the database!")

else:
        print("We found it in the database!")
        for thing in query:
                value = query[thing];
                print(value)

        cap = input("Enter the new capacity: " )
        avail = input("Enter the new availability: " )
        newvalues = {"$set": {"Capacity": cap}}
        collection.update_one(query, newvalues)
        newvalues = {"$set": {"Availability": avail}}
        collection.update_one(query, newvalues)
#post = {"Description": "Screwdrivers","Capacity": "100","Availability": "200"}
#post_id = collection.insert_one(post).inserted_id
#print(post)
#query = collection.find_one({"Description": "Hammers"})
#newvalues = { "$set": { "Capacity": "300" } }
#collection.update_one(collection.find_one({"Description": "Hammers"}), newvalues)


import pymongo
from flask import Flask, request

app = Flask(__name__)

# Returns a query for hardware set 1 or 2, depending on which number is passed through.
# This is mainly an internal function.
# Please use the other getters and setters to access data.
# Inputs: 1 or 2 depending on which set is being accessed
# Outputs: A query featuring the hardware of the set (there is only one hardware per collection)
@app.route('/get_hardware')
def get_hardware(whichSet):
    if (whichSet == 1):
        return HWSet1.find_one()
    else:
        return HWSet2.find_one()


# This just gets the capacity of the set.
# Inputs: 1 or 2 depending on which set you want to access
# Outputs: A number representing the capacity of the set
@app.route('/get_capacity')
def get_capacity():
    whichSet = request.args.to_dict().get("whichSet", 1)
    return {"Capacity": get_hardware(whichSet)['Capacity']}


# This just gets the availability of the set.
# Inputs: 1 or 2 depending on which set you want to access
# Outputs: A number representing the availability of the set
@app.route('/get_availability')
def get_availability(whichSet):
    return get_hardware(whichSet)['Availability']


# This just gets the description of the set.
# Inputs: 1 or 2 depending on which set you want to access
# Outputs: A string representing the description of the set
@app.route('/get_description')
def get_description(whichSet):
    return get_hardware(whichSet)['Description']


# This checks in hardware into a set.
# Inputs: 1 or 2 depending on which set you want to access, and the amount of hardware you're checking in
# Outputs: 0 if the check-in was successful, -1 if there was not enough space to check in all hardware
# Note: No hardware will be checked in if there is not enough room for all checked-in hardware
# Another note: -1 should basically never happen, but it could if the hardware capacity is manually decreased
@app.route('/check_in')
def check_in(whichSet, amount):
    capacity = get_capacity(whichSet)
    availability = get_availability(whichSet)
    if (amount + availability) > capacity:
        return -1
    else:
        newTotal = amount + availability
        newAmount = {"$set": {"Availability": newTotal}}
        if whichSet == 1:
            HWSet1.update_one(get_hardware(whichSet), newAmount)
        else:
            HWSet2.update_one(get_hardware(whichSet), newAmount)
    return 0


# This checks out hardware from a set.
# Inputs: 1 or 2 depending on which set you want to access, and the amount of hardware you're checking out
# Outputs: 0 if the check-out was successful, -1 if there was not enough hardware to check out
# Note: No hardware will be checked out if there is not enough hardware to check out
# Another note: this can and will happen in production
@app.route('/check_out')
def check_out(whichSet, amount):
    availability = get_availability(whichSet)
    if amount > availability:
        return -1
    else:
        newTotal = availability - amount
        newAmount = {"$set": {"Availability": newTotal}}
        if whichSet == 1:
            HWSet1.update_one(get_hardware(whichSet), newAmount)
        else:
            HWSet2.update_one(get_hardware(whichSet), newAmount)
    return 0


client = pymongo.MongoClient(
    "mongodb+srv://EvanRosenthal:Password1@cluster0.5hkhflb.mongodb.net/?retryWrites=true&w=majority")
DB = client.HardwareSet
HWSet1 = DB.HWSet1
HWSet2 = DB.HWSet2

if __name__ == '__main__':
    app.run(debug = True)

# Some tests
# print("Description of set 1:", get_description(1))
# print("Availability of set 1:", get_availability(1))
# print("Capacity of set 1:", get_capacity(1))
# print("Status of checking in hardware to set 1:", check_in(1, 200))
# print("Availability of set 1:", get_availability(1))
# print("Status of checking out hardware to set 1:", check_out(1, 500))
# print("Availability of set 1:", get_availability(1))

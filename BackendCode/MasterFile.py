import pymongo
from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
#THIS IS THE MASTER FILE: IT CONTAINS ALL OF THE FUNCTIONS!!!
# --------------------------------------------BEGIN HARDWARESET FUNCTIONS-----------------------------------------------
# Returns a query for hardware set 1 or 2, depending on which number is passed through.
# This is mainly an internal function.
# Please use the other getters and setters to access data.
# Inputs: 1 or 2 depending on which set is being accessed
# Outputs: A query featuring the hardware of the set (there is only one hardware per collection)
def get_hardware(whichSet):
    if (whichSet == 1):
        return HWSet1.find_one()
    else:
        return HWSet2.find_one()

@app.route('/get_hardware_set_data/<int:whichSet>')
def get_hardware_set_data(whichSet):
    hardwareSet = get_hardware(whichSet)
    return {"Capacity": hardwareSet['Capacity'],
            "Availability" : hardwareSet['Availability'],
            "Description": hardwareSet['Description']}

# This just gets the capacity of the set.
# Inputs: 1 or 2 depending on which set you want to access
# Outputs: A number representing the capacity of the set
@app.route('/get_capacity/<int:whichSet>')
def get_capacity(whichSet):
    return {"Capacity": get_hardware(whichSet)['Capacity']}


# This just gets the availability of the set.
# Inputs: 1 or 2 depending on which set you want to access
# Outputs: A number representing the availability of the set
@app.route('/get_availability/<int:whichSet>')
def get_availability(whichSet):
    return {"Availability" : get_hardware(whichSet)['Availability']}


# This just gets the description of the set.
# Inputs: 1 or 2 depending on which set you want to access
# Outputs: A string representing the description of the set
@app.route('/get_description/<int:whichSet>')
def get_description(whichSet):
    return {"Description": get_hardware(whichSet)['Description']}


# This checks in hardware into a set.
# Inputs: 1 or 2 depending on which set you want to access, and the amount of hardware you're checking in
# Outputs: 0 if the check-in was successful, Error message if there was not enough space to check in all hardware
# Note: No hardware will be checked in if there is not enough room for all checked-in hardware
# Another note: Erroring should basically never happen, but it could if the hardware capacity is manually decreased
def check_in(whichSet, amount):
    capacity = get_capacity(whichSet)['Capacity']
    availability = get_availability(whichSet)['Availability']
    if (amount + availability) > capacity:
        return {"Status" : "Not enough room for all checked-in hardware!"}
    else:
        newTotal = amount + availability
        newAmount = {"$set": {"Availability": newTotal}}
        if whichSet == 1:
            HWSet1.update_one(get_hardware(whichSet), newAmount)
        else:
            HWSet2.update_one(get_hardware(whichSet), newAmount)
    return {"Status" : 0}


# This checks out hardware from a set.
# Inputs: 1 or 2 depending on which set you want to access, and the amount of hardware you're checking out
# Outputs: 0 if the check-out was successful, Error message if there was not enough hardware to check out
# Note: No hardware will be checked out if there is not enough hardware to check out
# Another note: this can and will happen in production
def check_out(whichSet, amount):
    availability = get_availability(whichSet)['Availability']
    if amount > availability:
        return {"Status" : "Not enough hardware to check out!"}
    else:
        newTotal = availability - amount
        newAmount = {"$set": {"Availability": newTotal}}
        if whichSet == 1:
            HWSet1.update_one(get_hardware(whichSet), newAmount)
        else:
            HWSet2.update_one(get_hardware(whichSet), newAmount)
    return {"Status" : 0}

# ---------------------------------------BEGIN PROJECT FUNCTIONS--------------------------------------------------------
# Gets a project in the form of a query. This is an internal function, mainly. It gets used by other functions here.
# Inputs: A project's unique ID in the form of a string.
# Outputs: A query object representing the project, or -1 if the project does not exist. (Thanks, dynamic types!)
def get_project(projectID):
    query = Projects.find_one({"ID": projectID})
    if query is None:
        return -1
    return query


# Creates a new empty project with no users and no hardware
# Inputs: The unique ID of the project, and the Name of the project
# Outputs: Error Message if the ID is not unique (already exists in database), 0 if the creation was successful
# Note: Since these functions are not user specific, the user who created the project will not be added to the project.
@app.route('/create_project/<string:projectID>/<string:Name>')
def create_project(projectID, Name):
    query = get_project(projectID)
    if query != -1:
        return {"Status" : "The ID is not unique!"}
    else:
        post = {'Name': Name, 'ID': projectID, 'Users': [], 'HW1': 0, 'HW2': 0}
        Projects.insert_one(post)
    return {"Status": 0}


# Deletes a project (!)
# Inputs: The unique ID of the project to be deleted
# Outputs: Error Message if the ID of the project does not exist, 0 if the deletion was successful
# Note: If this is implemented, please password protect the functionality. I can hardcode an admin password if you want.
@app.route('/delete_project/<string:projectID>')
def delete_project(projectID):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    else:
        Projects.delete_one(query)
    return {"Status" : 0}


# Checks hardware back into the database
# Inputs: The unique project ID, the amount of hardware, and which set to pull from (1 or 2)
# Outputs: Error Message if the project ID does not exist, if hardware DB is full, or if not enough hardware in the project
# Extra outputs: 0 if the checkin was successful
@app.route('/check_in/<string:projectID>/<int:amount>/<int:whichSet>')
def check_in_project(projectID, amount, whichSet):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    if whichSet == 1:
        available = query['HW1']
        if amount > available:
            return {"Status": "Not enough hardware in the project to check in!"}
        else:
            newTotal = available - amount
            newAmount = {"$set": {"HW1": newTotal}}
    else:
        available = query['HW2']
        if amount > available:
            return {"Status" : "Not enough hardware in the project to check in!"}
        else:
            newTotal = available - amount
            newAmount = {"$set": {"HW2": newTotal}}
    if check_in(whichSet, amount)['Status'] != 0:
        return {"Status" : "Hardware DB is full!"}
    Projects.update_one(query, newAmount)
    return {"Status" : 0}


# Checks hardware out from the database.
# Inputs: The unique project ID, the amount of hardware, and which set to push to (1 or 2)
# Outputs: Error Message if the project ID does not exist or if there is not enough hardware in DB to checkout, 0 if successful
@app.route('/check_out/<string:projectID>/<int:amount>/<int:whichSet>')
def check_out_project(projectID, amount, whichSet):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    if whichSet == 1:
        available = query['HW1']
        newTotal = available + amount
        newAmount = {"$set": {"HW1": newTotal}}
    else:
        available = query['HW2']
        newTotal = available + amount
        newAmount = {"$set": {"HW2": newTotal}}
    if check_out(whichSet, amount)['Status'] != 0:
        return {"Status" : "Not enough hardware in the DB to check out!"}
    Projects.update_one(query, newAmount)
    return {"Status" : 0}


# Adds a user to a project.
# Inputs: The unique Project ID, and the unique User ID
# Outputs: Error message if the project ID does not exist or if the user is already a part of the project
# Note: There is no need to check the database to see if the user exists, since this will get called with a
# user that most certainly exists.
# Don't use this, user user_join_project instead
def join_project(projectID, userID):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    else:
        users = query['Users']
        try:
            dex = users.index(userID)
        except ValueError:
            newUsers = {"$push": {"Users": userID}}
            Projects.update_one(query, newUsers)
            return {"Status" : 0}
        else:
            return {"Status" : "The user is already a part of that project!"}


# Removes a user from a project.
# Inputs: The unique Project ID, and the unique User ID
# Outputs: Error message if the project ID does not exist or if the user is not a part of the project
# Note: Same as before, we assume the user exists already
# Don't use this, use user_leave_project instead
def leave_project(projectID, userID):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    else:
        users = query['Users']
        try:
            dex = users.index(userID)
        except ValueError:
            return {"Status" : "The user is not a part of that project!"}
        else:
            newUsers = {"$pull": {"Users": userID}}
            Projects.update_one(query, newUsers)
            return {"Status" : 0}


# The following functions are getters. They should be used by the frontend to display info about the projects.
# There is no GetID function because the ID should have been specified by the frontend (ID is used as the "key")
# They will all return Error Message if the project ID does not exist, otherwise they return the corresponding piece of info
@app.route('/get_project_name/<string:projectID>')
def get_project_name(projectID):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    return {"Name" : query['Name']}

@app.route('/get_users/<string:projectID>')
def get_users(projectID):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    return {"Users": query['Users']}

@app.route('/get_HW1/<string:projectID>')
def get_HW1(projectID):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    return {"HW1" : query['HW1']}

@app.route('/get_HW2/<string:projectID>')
def get_HW2(projectID):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    return {"HW2" : query['HW2']}

@app.route('/get_HWAvail/<string:projectID>/<int:whichSet>')
def get_HWAvail(projectID, whichSet):
    query = get_project(projectID)
    if query == -1:
        return{"Status" : "The project ID does not exist!"}
    setQuery = 'HW' + str(whichSet)
    return {"key": whichSet, "name": get_description(whichSet)["Description"], "available": query[setQuery]}
# -----------------------------------------------BEGIN USER FUNCTIONS--------------------------------------------------
# Gets a user in the form of a query. This is an internal function, mainly. It gets used by other functions here.
# Inputs: A user's unique ID in the form of a string.
# Outputs: A query object representing the user, or -1 if the user does not exist. (Thanks, dynamic types!)
def get_user(userID):
    query = Users.find_one({"ID": userID})
    if query is None:
        return -1
    return query


# Creates a user, adding them to the database
# Inputs: the user's unique ID, username, and encrypted password
# Outputs: Error Message if the user ID already exists in the database, or 0 if the creation was successful
@app.route('/create_user/<string:userID>/<string:name>/<string:password>')
def create_user(userID, name, password):
    query = get_user(userID)
    if query != -1:
        return {"Status" : "The user ID already exists!"}
    else:
        post = {'Name': name, 'ID': userID, 'Password': password, 'Projects': []}
        Users.insert_one(post)
    return {"Status" : 0}


# Compares a password attempt to the password stored in the database
# Inputs: the user's unique ID and the password attempt
# Outputs: Error Message if the passwords do not match or if the user ID does not exist, and 0 if the passwords match
@app.route('/log_in/<string:userID>/<string:passwordAttempt>')
def log_in(userID, passwordAttempt):
    query = get_user(userID)
    if query == -1:
        return {"Status": "The user ID does not exist!"}
    else:
        password = query['Password']
        if password != passwordAttempt:
            return {"Status" : "The password is incorrect!"}
    return {"Status" : 0}


# Deletes a user from the database, with password required
# Inputs: the user's unique ID and their password
# Outputs: Error Message if the user ID does not exist or if the passwords is incorrect, and 0 if the deletion was successful
@app.route('/delete_user/<string:userID>/<string:password>')
def delete_user(userID, password):
    query = get_user(userID)
    if query == -1:
        return {"Status" : "The user ID does not exist!"}
    else:
        if log_in(userID, password)['Status'] != 0:
            return {"Status":"The password is incorrect!"}
        else:
            Users.delete_one(query)
    return {"Status" : 0}


# Adds the user to a project
# Inputs: the user's unique ID and the project's unique ID
# Outputs: Error Message if the user ID does not exist, if the user is already a part of that project, or if the project ID does not exist
# Additional Outputs: 0 if all is well
@app.route('/user_join_project/<string:userID>/<string:projectID>')
def user_join_project(userID, projectID):
    query = get_user(userID)
    if query == -1:
        return {"Status":"The user ID does not exist!"}
    else:
        status = join_project(projectID, userID)
        if status['Status'] == 0:
            print("Updated user's projects")
            newProjects = {"$push": {"Projects": projectID}}
            Users.update_one(query, newProjects)
        return status


# Removes a user from a project
# Inputs: the user's unique ID and the project's unique ID
# Outputs: Error Message if the user ID does not exist, if the user is not a part of the project, or if the project ID does not exist
# Additional Outputs: 0 if all is well
@app.route('/user_leave_project/<string:userID>/<string:projectID>')
def user_leave_project(userID, projectID):
    query = get_user(userID)
    if query == -1:
        return {"Status":"The user ID does not exist!"}
    else:
        status = leave_project(projectID, userID)
        if status['Status'] == 0:
            newProjects = {"$pull": {"Projects": projectID}}
            Users.update_one(query, newProjects)
        return status


# The following functions are getters, they will get information for your pleasure.
# Note: For security reasons there is no getter for the password.
@app.route('/get_user_name/<string:userID>')
def get_user_name(userID):
    query = get_user(userID)
    if query == -1:
        return {"Status":"The user ID does not exist!"}
    return {"Name":query['Name']}

@app.route('/get_users_name_id/<string:projectID>')
def get_users_name_id(projectID):
    query = get_project(projectID)
    if query == -1:
        return {"Status" : "The project ID does not exist!"}
    else:
        TheUsers = []
        for userID in query['Users']:
            query = get_user_name(userID)
            if query == {"Status":"The user ID does not exist!"}:
                print(userID, "does not exist")
                leave_project(projectID, userID)
            TheUsers.append({"userID": userID, "userName": query.get("Name")})
        return {"Users": TheUsers, "Status": 0}

@app.route('/get_projects/<string:userID>')
def get_projects(userID):
    query = get_user(userID)
    if query == -1:
        return {"Status":"The user ID does not exist!"}
    return {"Projects":query['Projects']}


@app.route('/get_projects_name_id/<string:userID>')
def get_projects_name_id(userID):
    query = get_user(userID)
    if query == -1:
        return {"Status": "The user ID does not exist!"}
    else:
        Projects = []
        for projectID in query['Projects']:
            query = get_project(projectID)
            if query == {"Status" : "The project ID does not exist!"}:
                # Delete the project from the user's list if the project no longer exists
                newProjects = {"$pull": {"Projects": projectID}}
                Users.update_one(query, newProjects)
            Projects.append({"Id": projectID, "Name": query['Name']})
        return {"Projects": Projects, "Status": 0}

client = pymongo.MongoClient(
    "mongodb+srv://EvanRosenthal:Password1@cluster0.5hkhflb.mongodb.net/?retryWrites=true&w=majority")
UserProjDB = client.Users_And_Projects
Projects = UserProjDB.Projects
Users = UserProjDB.Users
HardwareDB = client.HardwareSet
HWSet1 = HardwareDB.HWSet1
HWSet2 = HardwareDB.HWSet2

if __name__ == '__main__':
    app.run(debug = True)

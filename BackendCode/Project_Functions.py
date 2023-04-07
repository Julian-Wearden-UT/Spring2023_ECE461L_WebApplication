import pymongo
import HardwareSet_Functions


# Error Codes (for Projects)
# 0: All good, no error
# -1: The project ID does not exist
# -2: The User ID is not unique
# -3: Hardware DB is full, cannot check in
# -4: Not enough Hardware in the project to check in
# -5: Not enough Hardware in the Hardware DB to check out
# -6: The User ID is already a part of that project
# -7: The User ID is not a part of that project
# -8: The project ID is not unique


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
# Outputs: -2 if the ID is not unique (already exists in database), 0 if the creation was successful
# Note: Since these functions are not user specific, the user who created the project will not be added to the project.
def create_project(projectID, Name):
    query = get_project(projectID)
    if query != -1:
        return -8
    else:
        post = {'Name': Name, 'ID': projectID, 'Users': [], 'HW1': 0, 'HW2': 0}
        Projects.insert_one(post)
    return 0


# Deletes a project (!)
# Inputs: The unique ID of the project to be deleted
# Outputs: -1 if the ID of the project does not exist, 0 if the deletion was successful
# Note: If this is implemented, please password protect the functionality. I can hardcode an admin password if you want.
def delete_project(projectID):
    query = get_project(projectID)
    if query == -1:
        return -1
    else:
        Projects.delete_one(query)
    return 0


# Checks hardware back into the database
# Inputs: The unique project ID, the amount of hardware, and which set to pull from (1 or 2)
# Outputs: -1 if the project ID does not exist, -3 if hardware DB is full, -4 if not enough hardware in the project
# Extra outputs: 0 if the checkin was successful
def check_in(projectID, amount, whichSet):
    query = get_project(projectID)
    if query == -1:
        return -1
    if whichSet == 1:
        available = query['HW1']
        if amount > available:
            return -4
        else:
            newTotal = available - amount
            newAmount = {"$set": {"HW1": newTotal}}
    else:
        available = query['HW2']
        if amount > available:
            return -4
        else:
            newTotal = available - amount
            newAmount = {"$set": {"HW2": newTotal}}
    if HardwareSet_Functions.check_in(whichSet, amount) == -1:
        return -3
    Projects.update_one(query, newAmount)
    return 0


# Checks hardware out from the database.
# Inputs: The unique project ID, the amount of hardware, and which set to push to (1 or 2)
# Outputs: -1 if the project ID does not exist, -5 if there is not enough hardware in DB to checkout, 0 if successful
def check_out(projectID, amount, whichSet):
    query = get_project(projectID)
    if query == -1:
        return -1
    if whichSet == 1:
        available = query['HW1']
        newTotal = available + amount
        newAmount = {"$set": {"HW1": newTotal}}
    else:
        available = query['HW2']
        newTotal = available - amount
        newAmount = {"$set": {"HW2": newTotal}}
    if HardwareSet_Functions.check_out(whichSet, amount) == -1:
        return -5
    Projects.update_one(query, newAmount)
    return 0


# Adds a user to a project.
# Inputs: The unique Project ID, and the unique User ID
# Outputs: -1 if the project ID does not exist, -6 if the user is already a part of the project
# Note: There is no need to check the database to see if the user exists, since this will get called with a
# user that most certainly exists.
def join_project(projectID, userID):
    query = get_project(projectID)
    if query == -1:
        return -1
    else:
        users = query['Users']
        try:
            dex = users.index(userID)
        except ValueError:
            newUsers = {"$push": {"Users": userID}}
            Projects.update_one(query, newUsers)
            return 0
        else:
            return -6


# Removes a user from a project.
# Inputs: The unique Project ID, and the unique User ID
# Outputs: -1 if the project ID does not exist, -7 if the user is not a part of the project
# Note: Same as before, we assume the user exists already
def leave_project(projectID, userID):
    query = get_project(projectID)
    if query == -1:
        return -1
    else:
        users = query['Users']
        try:
            dex = users.index(userID)
        except ValueError:
            return -7
        else:
            newUsers = {"$pull": {"Users": userID}}
            Projects.update_one(query, newUsers)
            return 0


# The following functions are getters. They should be used by the frontend to display info about the projects.
# There is no GetID function because the ID should have been specified by the frontend (ID is used as the "key")
# They will all return -1 if the project ID does not exist, otherwise they return the corresponding piece of info
def get_name(projectID):
    query = get_project(projectID)
    if query == -1:
        return -1
    return query['Name']


def get_users(projectID):
    query = get_project(projectID)
    if query == -1:
        return -1
    return query['Users']


def get_HW1(projectID):
    query = get_project(projectID)
    if query == -1:
        return -1
    return query['HW1']


def get_HW2(projectID):
    query = get_project(projectID)
    if query == -1:
        return -1
    return query['HW2']


client = pymongo.MongoClient(
    "mongodb+srv://EvanRosenthal:Password1@cluster0.5hkhflb.mongodb.net/?retryWrites=true&w=majority")
DB = client.Users_And_Projects
Projects = DB.Projects

# Some tests
# print(get_project("UntitledProject_1"))
# print(create_project("ChessRobot", "ChessBot"))
# print(get_project("ChessRobot"))
# print(check_in("PoopBot", 200, 1))
# print(check_in("ChessRobot", 200, 2))
# print(check_out("ElectricalScooter", 500, 1))
# print(join_project("ChessRobot", "xX_Gamer_Xx"))
# print(leave_project("ChessRobot", "PoopLoser67"))
# print(join_project("ElectricalScooter", "PeeHead96"))
# print(get_name("ElectricalScooter"))
# print(get_HW2("ChessRobot"))
# print(delete_project("ChessRobot"))

import pymongo
import Project_Functions


# Error codes (For Users)
# 0: No errors here, all good!
# -1: The user ID does not exist
# -2: The user ID is not unique
# -3: The passwords do not match
# -4: The project ID does not exist
# -5: N/A
# -6: The user is already a part of the project
# -7: The user is not a part of the project

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
# Outputs: -2 if the user ID already exists in the database, or 0 if the creation was successful
def create_user(userID, name, password):
    query = get_user(userID)
    if query != -1:
        return -2
    else:
        post = {'Name': name, 'ID': userID, 'Password': password, 'Projects': []}
        Users.insert_one(post)
    return 0


# Compares a password attempt to the password stored in the database
# Inputs: the user's unique ID and the password attempt
# Outputs: -3 if the passwords do not match, -1 if the user ID does not exist, and 0 if the passwords match
def log_in(userID, passwordAttempt):
    query = get_user(userID)
    if query == -1:
        return -1
    else:
        password = query['Password']
        if password != passwordAttempt:
            return -3
    return 0


# Deletes a user from the database, with password required
# Inputs: the user's unique ID and their password
# Outputs: -1 if the user ID does not exist, -3 if the passwords is incorrect, and 0 if the deletion was successful
def delete_user(userID, password):
    query = get_user(userID)
    if query == -1:
        return -1
    else:
        if log_in(userID, password) == -3:
            return -3
        else:
            Users.delete_one(query)
    return 0


# Adds the user to a project
# Inputs: the user's unique ID and the project's unique ID
# Outputs: -1 if the user ID does not exist, -6 if the user is already a part of that project, 0 if all is well
# Additional Outputs: -4 if the project ID does not exist
def join_project(userID, projectID):
    query = get_user(userID)
    if query == -1:
        return -1
    else:
        status = Project_Functions.join_project(projectID, userID)
        if status == 0:
            newProjects = {"$push": {"Projects": projectID}}
            Users.update_one(query, newProjects)
        elif status == -1:
            return -4
        return status


# Removes a user from a project
# Inputs: the user's unique ID and the project's unique ID
# Outputs: -1 if the user ID does not exist, -7 if the user is not a part of the project, 0 if all is well
# Additional Outputs: -4 if the project ID does not exist
def leave_project(userID, projectID):
    query = get_user(userID)
    if query == -1:
        return -1
    else:
        status = Project_Functions.leave_project(projectID, userID)
        if status == 0:
            newProjects = {"$pull": {"Projects": projectID}}
            Users.update_one(query, newProjects)
        elif status == -1:
            return -4
        return status


# The following functions are getters, they will get information for your pleasure.
# Note: For security reasons there is no getter for the password.
def get_name(userID):
    query = get_user(userID)
    if query == -1:
        return -1
    return query['Name']


def get_projects(userID):
    query = get_user(userID)
    if query == -1:
        return -1
    return query['Projects']


client = pymongo.MongoClient(
    "mongodb+srv://EvanRosenthal:Password1@cluster0.5hkhflb.mongodb.net/?retryWrites=true&w=majority")
DB = client.Users_And_Projects
Users = DB.Users

# Some tests
# print(get_user("PoopLoser67"))
# print(create_user("PeeHead69", "PeeHead69", "p00pie"))
# print(log_in("PeeHead69", "p00pie"))
# print(log_in("PeeHole42", "p00pie"))
# print(log_in("PeeHead69", "shitfart609"))
# # print(delete_user("PeeHead69","p00pie"))
# print(create_user("PeePeehead69", "PeeHead69", "d00kie"))
# print(join_project("PeeHead69", "ChessRobot"))
# print(join_project("PeeHead69", "ElectricalScooter"))
# # print(leave_project("PeeHead69", "ChessRobot"))
# print(leave_project("xX_Gamer_Xx", "ChessRobot"))

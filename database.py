import mysql.connector
from mysql.connector import Error
import sys
import bcrypt

from functools import wraps

class Login:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.user_permissions = None

    def authenticate_user(self, username, password):
        # Authenticate the user
        if self.db_manager.authenticate_user(username, password):
            self.user_permissions = self.db_manager.get_user_role_and_permissions(username)
            return True
        return False

    def has_permission(self, permission):
        if self.user_permissions:
            return permission in self.user_permissions
        return False

class Database:
 
    def __init__(self,host,port,username,password,database_name,unix_socket, verbose = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database_name = database_name
        self.connection = None
        self.unix_socket = unix_socket
        self.verbose = verbose
    
    ############################################################################
    ####### Basic database mangement methods
    def connect(self):
        try:
            if sys.platform == 'win32':
                self.connection = mysql.connector.connect(host=self.host,
                                                      database=self.database_name,
                                                      user=self.username,
                                                      password=self.password,
                                                      port=self.port)
            elif sys.platform == 'linux':
                self.connection = mysql.connector.connect(host=self.host,
                                                    database=self.database_name,
                                                    user=self.username,
                                                    password=self.password,
                                                    unix_socket=self.unix_socket
                                                    )
            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                if self.verbose:
                    print("Connected to MySQL Server version ", db_Info)
 
 
        except Error as e:
            print("Error while connecting to MySQL", e)

    def is_connected(self):
        return self.connection.is_connected()

    def disconnect(self):

        if self.connection.is_connected():
            self.connection.close()
            #print("MySQL connection is closed")

    def permission_required(permission):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if not self.login_manager or not self.login_manager.has_permission(permission):
                    raise PermissionError("Insufficient permissions")
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    # Password hashing methods
    def hash_password(self, password: str) -> str:
        # Hash a password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        # Verify a password
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    ############################################################################
    ####### Users
    def add_user(self, name: str, password: str, role_name: str):
        try:
            cursor = self.connection.cursor()
            
            # Hash the password
            hashed_password = self.hash_password(password)
            
            # Check if role exists
            cursor.execute("SELECT id FROM Roles WHERE role_name = %s", (role_name,))
            role_result = cursor.fetchone()
            if not role_result:
                raise ValueError(f"Role '{role_name}' does not exist. Please insert it first.")
            role_id = role_result[0]
            
            # Insert the user
            cursor.execute("INSERT INTO Users (name, password, role_id) VALUES (%s, %s, %s)", (name, hashed_password, role_id))
            self.connection.commit()
            return cursor.lastrowid

        except Error as e:
            print(f"Error adding user: {e}")
            self.connection.rollback()
        except ValueError as e:
            print(e)
    
    def authenticate_user(self, name: str, password: str) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT password FROM Users WHERE name = %s", (name,))
            result = cursor.fetchone()
            if result:
                hashed_password = result[0]
                return self.verify_password(password, hashed_password)
            else:
                print("User does not exist.")
                return False
        except Error as e:
            print(f"Error authenticating user: {e}")
            return False

    def get_users(self):
        try:
            cursor = self.connection.cursor(dictionary=True)  # Using dictionary=True for better readability
            sql = """
                SELECT 
                    u.id AS user_id, 
                    u.name AS name, 
                    r.role_name, 
                    GROUP_CONCAT(p.name SEPARATOR ', ') AS permissions
                FROM 
                    Users u
                JOIN 
                    Roles r ON u.role_id = r.id
                LEFT JOIN 
                    RolePermissions rp ON r.id = rp.role_id
                LEFT JOIN 
                    Permissions p ON rp.permission_id = p.id
                GROUP BY 
                    u.id, r.role_name;
            """
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error fetching users: {e}")
            return []
        finally:
            cursor.close()

    def delete_user(self, name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Users WHERE name = %s", (name,))
            if cursor.rowcount == 0:
                raise ValueError(f"User '{name}' does not exist.")
            self.connection.commit()
        except Error as e:
            print(f"Error deleting user: {e}")
            self.connection.rollback()
        except ValueError as e:
            print(e)

    def update_user_role(self, user_name, new_role_name):
        try:
            cursor = self.connection.cursor()
            
            # Check if new role exists
            cursor.execute("SELECT id FROM Roles WHERE role_name = %s", (new_role_name,))
            role_result = cursor.fetchone()
            if not role_result:
                raise ValueError(f"Role '{new_role_name}' does not exist.")
            role_id = role_result[0]
            
            # Update the user role
            cursor.execute("UPDATE Users SET role_id = %s WHERE name = %s", (role_id, user_name))
            if cursor.rowcount == 0:
                raise ValueError(f"User '{user_name}' does not exist.")
            self.connection.commit()
        except Error as e:
            print(f"Error updating user role: {e}")
            self.connection.rollback()
        except ValueError as e:
            print(e)

    def get_user_role_and_permissions(self, user_name):
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get user role
            cursor.execute("SELECT u.id, r.role_name FROM Users u JOIN Roles r ON u.role_id = r.id WHERE u.name = %s", (user_name,))
            role_result = cursor.fetchone()
            if not role_result:
                raise ValueError(f"User '{user_name}' does not exist.")
            role_name = role_result['role_name']
            
            # Get permissions for the role
            cursor.execute("""
                SELECT p.name 
                FROM RolePermissions rp 
                JOIN Permissions p ON rp.permission_id = p.id 
                WHERE rp.role_id = (SELECT id FROM Roles WHERE role_name = %s)
            """, (role_name,))
            permissions = cursor.fetchall()
            permission_names = [perm['name'] for perm in permissions]
            
            return {
                'role': role_name,
                'permissions': permission_names
            }
        except Error as e:
            print(f"Error getting user role and permissions: {e}")
        except ValueError as e:
            print(e)

    ####### user helper functions
    def get_rooms_by_user(self, user_id: int):

        """
        Retrieve all rooms associated with a user.
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Select rooms associated with the user
            cursor.execute("""
                SELECT r.id As room_id, 
                       r.room_name
                FROM Rooms r
                JOIN UsersRooms ur ON r.id = ur.room_id
                WHERE ur.user_id = %s
            """, (user_id,))
            
            rooms = cursor.fetchall()
            return rooms
        except Error as e:
            print(f"Error retrieving rooms for user {user_id}: {e}")
            return []
    
    def get_rooms_accessories_by_user(self, user_id):
        """
        Retrieves all rooms for a specific user and their associated accessories.

        :param user_id: The ID of the user whose rooms and accessories are being retrieved.
        :return: A list of dictionaries containing room details and accessory details.
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # SQL query to get rooms and accessories for a specific user
            sql = """
            SELECT 
                r.id AS room_id,
                r.room_name,
                a.id AS accessory_id,
                a.name AS accessory_name,
                a.position AS accessory_position,
                a.accessory_key,
                a.field,
                a.type AS accessory_type,
                a.communication_protocol_name
            FROM 
                Rooms r
            JOIN 
                AccessoriesDetails a ON a.room_id = r.id
            JOIN 
                UsersRooms ur ON ur.room_id = r.id
            JOIN 
                Users u ON u.id = ur.user_id
            WHERE 
                u.id = %s;
            """
            
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
        
        except Error as e:
            print(f"Error retrieving data: {e}")
            return []
        
        finally:
            cursor.close()

    def get_rooms_accessories_latest_records_by_user(self, user_id):
        """
        Retrieves all rooms for a specific user, their accessories, and the latest records for each accessory.

        :param user_id: The ID of the user whose data is being retrieved.
        :return: A list of dictionaries containing room details, accessory details, and the latest record for each accessory.
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # SQL query to get the latest accessory records details for a specific user
            sql = """
            SELECT 
                r.room_id,
                r.room_name,
                ar.id AS accessory_id,
                ar.name AS accessory_name,
                ar.position AS position,
                ar.accessory_key AS accessory_key,
                ar.field AS field,
                ar.type AS accessory_type,
                ar.communication_protocol_name AS communication_protocol_name,
                
                -- Latest Record details
                ar.value,
                ar.category,
                ar.date_time,
                ar.value_type,
                ar.battery_level

            FROM 
                LatestAccessoryRecordsDetails ar
            JOIN 
                RoomsWithAccessoriesForUser r ON ar.id = r.accessory_id
            WHERE 
                r.user_id = %s;
            """
            
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
        
        except Error as e:
            print(f"Error retrieving data: {e}")
            return []
        
        finally:
            cursor.close() 
    
    def get_automations_by_user(self, user_id):
        """
        Retrieve all automations associated with a user.
        """
        message = None
        is_sucess = False
        automations = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT DISTINCT
                    a.id AS automation_id,
                    a.execute_actions AS execute_actions,
                    a.time_from AS time_from,
                    a.time_to AS time_to
                FROM
                    Automations a
                JOIN
                    Events e ON a.id = e.automation_id
                JOIN
                    Accessories acc ON e.sensor_id = acc.id
                JOIN
                    Rooms r ON acc.room_id = r.id
                JOIN
                    UsersRooms ur ON r.id = ur.room_id
                WHERE
                    ur.user_id = %s
            """
            
            cursor.execute(query, (user_id,)) # (user_id,)
            
            # Fetch results
            automations = cursor.fetchall()
            # print(len(automations))
            
            if not automations:
                message = f"No automations found for user {user_id}"
            
            # return automations
        
        except mysql.connector.Error as e:
            message = f"Error retrieving automations for user {user_id}: {e}"
            # return []
        
        finally:
            if self.verbose:
                print(message)
            cursor.close()
            return {"status": is_sucess, "message": message, "output": automations}

    ############################################################################
    ####### Permissions
    def insert_permission(self, name, description):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO Permissions (name, description) VALUES (%s, %s)"
            cursor.execute(query, (name, description))
            self.connection.commit()
        except Error as e:
            print(f"Error inserting permission: {e}")
            self.connection.rollback()

    def delete_permission(self, name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Permissions WHERE name = %s", (name,))
            if cursor.rowcount == 0:
                raise ValueError(f"Permission '{name}' does not exist.")
            # Remove associated role permissions
            cursor.execute("DELETE FROM RolePermissions WHERE permission_id = (SELECT id FROM Permissions WHERE name = %s)", (name,))
            self.connection.commit()
        except Error as e:
            print(f"Error deleting permission: {e}")
            self.connection.rollback()
        except ValueError as e:
            print(e)

    def update_permission(self, old_name, new_name, new_description):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Permissions SET name = %s, description = %s WHERE name = %s", (new_name, new_description, old_name))
            if cursor.rowcount == 0:
                raise ValueError(f"Permission '{old_name}' does not exist.")
            # Update associated role permissions if necessary
            self.connection.commit()
        except Error as e:
            print(f"Error updating permission: {e}")
            self.connection.rollback()
        except ValueError as e:
            print(e)
    
    def get_permissions(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT p.id, p.name, p.description
                FROM Permissions p
            """)
            
            permissions = cursor.fetchall()
            
            return permissions
        
        except Error as e:
            print(f"Error fetching permissions: {e}")
            return None

    ############################################################################
    ####### Roles
    def delete_role(self, role_name):
        try:
            cursor = self.connection.cursor()

            # Get the role_id for the given role_name
            cursor.execute("SELECT id FROM Roles WHERE role_name = %s", (role_name,))
            role = cursor.fetchone()
            
            if role is None:
                print(f"Role '{role_name}' does not exist.")
                return
            
            role_id = role[0]

            # Remove all references to this role_id from RolePermissions
            cursor.execute("DELETE FROM RolePermissions WHERE role_id = %s", (role_id,))
            
            # Remove the role from Roles
            cursor.execute("DELETE FROM Roles WHERE id = %s", (role_id,))
            
            self.connection.commit()
            print(f"Role '{role_name}' and associated permissions have been deleted.")
        
        except Error as e:
            print(f"Error deleting role: {e}")
            self.connection.rollback()

    def update_role_name(self, old_role_name, new_role_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Roles SET role_name = %s WHERE role_name = %s", (new_role_name, old_role_name))
            if cursor.rowcount == 0:
                raise ValueError(f"Role '{old_role_name}' does not exist.")
            # Update associated users and permissions if necessary
            self.connection.commit()
        except Error as e:
            print(f"Error updating role name: {e}")
            self.connection.rollback()
        except ValueError as e:
            print(e)

    def update_role_permissions(self, role_name, permissions):
        try:
            cursor = self.connection.cursor()
            
            # Check if the role exists
            cursor.execute("SELECT id FROM Roles WHERE role_name = %s", (role_name,))
            role_id = cursor.fetchone()
            if not role_id:
                raise ValueError(f"Role '{role_name}' does not exist.")
            role_id = role_id[0]
            
            # Check if all permissions exist
            permission_ids = []
            for permission in permissions:
                cursor.execute("SELECT id FROM Permissions WHERE name = %s", (permission,))
                permission_id = cursor.fetchone()
                if not permission_id:
                    raise ValueError(f"Permission '{permission}' does not exist.")
                permission_ids.append(permission_id[0])
            
            # Remove existing permissions for the role
            cursor.execute("DELETE FROM RolePermissions WHERE role_id = %s", (role_id,))
            
            # Add new permissions
            for permission_id in permission_ids:
                cursor.execute("INSERT INTO RolePermissions (role_id, permission_id) VALUES (%s, %s)", (role_id, permission_id))
            
            self.connection.commit()
        
        except Error as e:
            print(f"Error updating role permissions: {e}")
            self.connection.rollback()
        except ValueError as e:
            print(e)

    def insert_role_with_permissions(self, role_name, permissions):
        try:
            cursor = self.connection.cursor()
            
            # Check if all permissions exist
            permission_ids = []
            for perm_name in permissions:
                cursor.execute("SELECT id FROM Permissions WHERE name = %s", (perm_name,))
                result = cursor.fetchone()
                if result:
                    permission_ids.append(result[0])
                else:
                    raise ValueError(f"Permission '{perm_name}' does not exist. Please insert it first.")
            
            # Insert the role
            cursor.execute("INSERT INTO Roles (role_name) VALUES (%s)", (role_name,))
            role_id = cursor.lastrowid
            
            # Insert role permissions
            for perm_id in permission_ids:
                cursor.execute("INSERT INTO RolePermissions (role_id, permission_id) VALUES (%s, %s)", (role_id, perm_id))
            
            self.connection.commit()
        except Error as e:
            print(f"Error inserting role with permissions: {e}")
            self.connection.rollback()
        except ValueError as e:
            print(e)

    def get_roles(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT r.id, r.role_name
                FROM Roles r
            """)
            
            roles = cursor.fetchall()
            
            return roles
        
        except Error as e:
            print(f"Error fetching roles: {e}")
            return None

    def get_role_permissions(self, role_name):
        try:
            cursor = self.connection.cursor()
            
            # Get the role_id for the given role_name
            cursor.execute("SELECT id FROM Roles WHERE role_name = %s", (role_name,))
            role = cursor.fetchone()
            
            if role is None:
                print(f"Role '{role_name}' does not exist.")
                return
            
            role_id = role[0]
            
            # Fetch permissions associated with the role_id
            cursor.execute("""
                SELECT p.id, p.name, p.description
                FROM Permissions p
                INNER JOIN RolePermissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = %s
            """, (role_id,))
            
            permissions = cursor.fetchall()
            
            if not permissions:
                print(f"No permissions found for role '{role_name}'.")
                return
            
            return permissions
        
        except Error as e:
            print(f"Error retrieving role permissions: {e}")

    ############################################################################
    ####### Rooms management methods
    def add_room(self, room_name: str, user_id: int):
        """
        Add a new room to the Rooms table and associate it with a user in UsersRooms table.
        """
        room_id = None
        message = None
        is_sucess = False
        try:
            cursor = self.connection.cursor()
            
            # Insert the room into the Rooms table
            cursor.execute("INSERT INTO Rooms (room_name) VALUES (%s)", (room_name,))
            room_id = cursor.lastrowid
            
            # Associate the room with the user in UsersRooms table
            cursor.execute("INSERT INTO UsersRooms (user_id, room_id) VALUES (%s, %s)", (user_id, room_id))
            
            self.connection.commit()
            message = f"Room '{room_name}' added successfully with ID {room_id} and associated with user {user_id}."
            is_sucess = True
        except Error as e:
            message = f"Error adding room: {e}"
            self.connection.rollback()
        finally:
            cursor.close()
            if self.verbose:
                print(message)
            return {"room_id": room_id, "message": message, "status": is_sucess}

    def update_room(self, room_id: int = None, old_room_name: str = None, new_room_name: str = None, user_id: int = None):
        """
        Update the room name in the Rooms table.
        Can update based on either room_id or old_room_name.
        """
        if not new_room_name:
            print("New room name is required to update the room.")
            return

        if room_id is None and old_room_name is None:
            print("Either room_id or old_room_name must be provided to update the room.")
            return

        try:
            cursor = self.connection.cursor()

            if room_id:
                # Update using room_id
                cursor.execute("UPDATE Rooms SET room_name = %s WHERE id = %s", (new_room_name, room_id))
            else:
                # Update using old_room_name
                cursor.execute("UPDATE Rooms SET room_name = %s WHERE room_name = %s", (new_room_name, old_room_name))

            # Check if the update was successful
            if cursor.rowcount == 0:
                print("No room was found with the given criteria.")
                return

            # Optionally, insert/update the user-room association if user_id is provided
            if user_id is not None:
                if room_id is None:
                    # Fetch the room_id if it wasn't provided, using old_room_name
                    cursor.execute("SELECT id FROM Rooms WHERE room_name = %s", (new_room_name,))
                    result = cursor.fetchone()
                    if result:
                        room_id = result[0]
                    else:
                        print("Error fetching the room ID after update.")
                        return

                # Insert the user-room association if it does not exist
                cursor.execute("SELECT 1 FROM UsersRooms WHERE user_id = %s AND room_id = %s", (user_id, room_id))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO UsersRooms (user_id, room_id) VALUES (%s, %s)", (user_id, room_id))

            self.connection.commit()
            print(f"Room updated successfully to '{new_room_name}'.")
        except Error as e:
            print(f"Error updating room: {e}")
            self.connection.rollback()

    def delete_room(self, room_id: int = None, room_name: str = None):
        """
        Delete a room from the Rooms table and its associated foreign keys in the UsersRooms table.
        The room can be deleted using either room_id or room_name.
        """
        if room_id is None and room_name is None:
            print("Either room_id or room_name must be provided to delete the room.")
            return

        try:
            cursor = self.connection.cursor()

            # First, identify the room to delete
            if room_id:
                # If room_id is provided, use it to delete
                cursor.execute("SELECT id FROM Rooms WHERE id = %s", (room_id,))
            else:
                # If room_name is provided, use it to delete
                cursor.execute("SELECT id FROM Rooms WHERE room_name = %s", (room_name,))
            
            result = cursor.fetchone()
            if not result:
                print("No room found with the given criteria.")
                return
            
            room_id_to_delete = result[0]

            # Delete from UsersRooms table first to maintain referential integrity
            cursor.execute("DELETE FROM UsersRooms WHERE room_id = %s", (room_id_to_delete,))

            # Then delete from the Rooms table
            cursor.execute("DELETE FROM Rooms WHERE id = %s", (room_id_to_delete,))

            self.connection.commit()
            print(f"Room with ID {room_id_to_delete} deleted successfully.")
        
        except Error as e:
            print(f"Error deleting room: {e}")
            self.connection.rollback()
    
    ############################################################################
    ####### Types CRUD
    def insert_type(self, field, type_name):
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO Types (field, type) VALUES (%s, %s)"
            cursor.execute(sql, (field, type_name))
            self.connection.commit()
        except Error as e:
            print(f"Error inserting type: {e}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def get_types(self, type_id=None, type_name=None):
        try:
            cursor = self.connection.cursor(dictionary=True)
            if type_id:
                # If type_id is provided, filter by type_id
                sql = "SELECT * FROM Types WHERE id = %s"
                cursor.execute(sql, (type_id,))
            elif type_name:
                # If type_name is provided, filter by type_name
                sql = "SELECT * FROM Types WHERE type = %s"
                cursor.execute(sql, (type_name,))
            else:
                # If neither type_id nor type_name is provided, return all types
                sql = "SELECT * FROM Types"
                cursor.execute(sql)
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error retrieving types: {e}")
            return None
 
    def update_type(self, id=None, type_old_name=None, type_new_name=None, field=None):
        try:
            cursor = self.connection.cursor()
            if type_new_name and field:
                if id:
                    sql = "UPDATE Types SET type = %s, field = %s WHERE id = %s"
                    cursor.execute(sql, (type_new_name, field, id))
                elif type_old_name:
                    sql = "UPDATE Types SET type = %s, field = %s WHERE type = %s"
                    cursor.execute(sql, (type_new_name, field, type_old_name))
            elif field:
                if id:
                    sql = "UPDATE Types SET field = %s WHERE id = %s"
                    cursor.execute(sql, (field, id))
                elif type_old_name:
                    sql = "UPDATE Types SET field = %s WHERE type = %s"
                    cursor.execute(sql, (field, type_old_name))
            elif type_new_name:
                if id:
                    sql = "UPDATE Types SET type = %s WHERE id = %s"
                    cursor.execute(sql, (type_new_name, id))
                elif type_old_name:
                    sql = "UPDATE Types SET type = %s WHERE type = %s"
                    cursor.execute(sql, (type_new_name, type_old_name))
            else:
                print("No valid update parameters provided.")
                return
            self.connection.commit()
            print("Type updated successfully")
        except Error as e:
            print(f"Error updating type: {e}")
            self.connection.rollback()
    
    def delete_type(self, id=None, type_name=None):
        try:
            cursor = self.connection.cursor()
            if id:
                sql = "DELETE FROM Types WHERE id = %s"
                cursor.execute(sql, (id,))
            elif type_name:
                sql = "DELETE FROM Types WHERE type = %s"
                cursor.execute(sql, (type_name,))
            else:
                print("No identifier provided for deletion.")
                return
            self.connection.commit()
        except Error as e:
            print(f"Error deleting type: {e}")
            self.connection.rollback()

    ############################################################################
    ####### communication protocol CRUD #######
    def insert_communication_protocol(self, name):
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO CommunicationProtocol (name) VALUES (%s)"
            cursor.execute(sql, (name,))
            self.connection.commit()
            print("Communication protocol inserted successfully")
        except Error as e:
            print(f"Error inserting communication protocol: {e}")
            self.connection.rollback()
        # finally:
        #     cursor.close()

    def get_communication_protocols(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            sql = "SELECT * FROM CommunicationProtocol"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error fetching communication protocols: {e}")
            return []
        # finally:
        #     cursor.close()

    def update_communication_protocol(self, id=None, name_old=None, name_new=None):
        try:
            cursor = self.connection.cursor()
            if name_new:
                if id:
                    sql = "UPDATE CommunicationProtocol SET name = %s WHERE id = %s"
                    cursor.execute(sql, (name_new, id))
                elif name_old:
                    sql = "UPDATE CommunicationProtocol SET name = %s WHERE name = %s"
                    cursor.execute(sql, (name_new, name_old))
            else:
                print("No valid update parameters provided.")
                return
            self.connection.commit()
            print("Communication protocol updated successfully")
        except Error as e:
            print(f"Error updating communication protocol: {e}")
            self.connection.rollback()
        # finally:
        #     cursor.close()
    
    def delete_communication_protocol(self, id=None, name=None):
        try:
            cursor = self.connection.cursor()
            if id:
                sql = "DELETE FROM CommunicationProtocol WHERE id = %s"
                cursor.execute(sql, (id,))
            elif name:
                sql = "DELETE FROM CommunicationProtocol WHERE name = %s"
                cursor.execute(sql, (name,))
            else:
                print("No valid delete parameters provided.")
                return
            self.connection.commit()
            print("Communication protocol deleted successfully")
        except Error as e:
            print(f"Error deleting communication protocol: {e}")
            self.connection.rollback()
        # finally:
        #     cursor.close()
      
    ############################################################################
    ####### Accessories CRUD #######
    def insert_accessory(self, id=None, name=None, position=0, accessory_key=None, 
                     type_id=None, communication_protocol_id=None, room_id=None,
                     type_name=None, communication_protocol_name=None, room_name=None, user_id=None):
        is_sucess = False
        message = None
        try:
            cursor = self.connection.cursor()

            if id:
                if room_name and user_id:
                    room_id = self.get_room_id_by_name_for_user(room_name, user_id)
                
                if room_id:
                    if type_id is None and type_name:
                        type_id = self.get_type_id_by_name(type_name)
                    if communication_protocol_id is None and communication_protocol_name:
                        communication_protocol_id = self.get_communication_protocol_id_by_name(communication_protocol_name)

                    if type_id and communication_protocol_id and room_id:
                        sql = """
                            INSERT INTO Accessories (id, name, position, accessory_key, type_id, communication_protocol_id, room_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (id, name, position, accessory_key, type_id, communication_protocol_id, room_id))
                        self.connection.commit()
                        message = "Accessory inserted successfully"
                        is_sucess = True
                    else:
                        message = "Check the values of (type, room, or communication protocol)"
                else:
                    message = "Room ID could not be determined or is invalid."
            else:
                message = "No ID provided for accessory insertion."
        except Error as e:
            message = f"Error inserting accessory: {e}"
            self.connection.rollback()
        finally:
            if self.verbose:
                print(message)
            cursor.close()
            return{"status": is_sucess, "message": message}

    def update_accessory(self, id=None, name=None, position=0, accessory_key=None, 
                     type_id=None, communication_protocol_id=None, room_id=None,
                     type_name=None, communication_protocol_name=None, room_name=None, user_id=None):
        try:
            cursor = self.connection.cursor()

            if type_name and type_id is None:
                type_id = self.get_type_id_by_name(type_name)
            if communication_protocol_name and communication_protocol_id is None:
                communication_protocol_id = self.get_communication_protocol_id_by_name(communication_protocol_name)
            if room_name and room_id is None and user_id:
                room_id = self.get_room_id_by_name_for_user(room_name, user_id)

            sql = "UPDATE Accessories SET "
            updates = []
            parameters = []

            if name is not None:
                updates.append("name = %s")
                parameters.append(name)
            if position != 0:
                updates.append("position = %s")
                parameters.append(position)
            if accessory_key is not None:
                updates.append("accessory_key = %s")
                parameters.append(accessory_key)
            if type_id is not None:
                updates.append("type_id = %s")
                parameters.append(type_id)
            if communication_protocol_id is not None:
                updates.append("communication_protocol_id = %s")
                parameters.append(communication_protocol_id)
            if room_id is not None:
                updates.append("room_id = %s")
                parameters.append(room_id)

            if updates:
                sql += ", ".join(updates)
                sql += " WHERE id = %s"
                parameters.append(id)
                cursor.execute(sql, tuple(parameters))
                self.connection.commit()
                print("Accessory updated successfully")
            else:
                print("No update parameters provided.")
        except Error as e:
            print(f"Error updating accessory: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def get_accessories(self, id=None, room_id=None):
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Base query
            sql = """SELECT id AS accessory_id,
                            name AS accessory_name,
                            position AS accessory_position,
                            accessory_key AS accessory_key,
                            field AS field, 
                            type AS accessory_type,
                            communication_protocol_name,
                            room_name AS room_name,
                            room_id FROM AccessoriesDetails"""
            parameters = []
            
            if id:
                # Filter by accessory ID
                sql += " WHERE id = %s ORDER BY position"
                parameters.append(id)
                cursor.execute(sql, tuple(parameters))
                result = cursor.fetchone()  # Fetch only one row for the specific accessory

            elif room_id:
                # Filter by room ID
                sql += " WHERE room_id = %s"
                parameters.append(room_id)
                cursor.execute(sql, tuple(parameters))
                result = cursor.fetchall()  # Fetch all rows for the specified room

            else:
                # Fetch all accessories if no filters are provided
                cursor.execute(sql)
                result = cursor.fetchall()  # Fetch all rows
            
            return result

        except Error as e:
            print(f"Error fetching accessories: {e}")
            return []

        finally:
            cursor.close()

    def delete_accessory(self, id=None):
        # Records will delete automatically when accessory is deleted due to ON DELETE CASCADE

        is_success = False
        message = None
        try:
            cursor = self.connection.cursor(dictionary=True)

            if id:
                # Step 1: Retrieve the room_id of the accessory before deleting it
                cursor.execute("SELECT room_id FROM Accessories WHERE id = %s", (id,))
                result = cursor.fetchone()

                if result:
                    room_id = result['room_id']

                    # Step 2: Delete the accessory
                    sql_delete = "DELETE FROM Accessories WHERE id = %s"
                    cursor.execute(sql_delete, (id,))
                    self.connection.commit()

                    # Step 3: Fetch remaining accessories in the same room ordered by current position
                    cursor.execute("SELECT id FROM Accessories WHERE room_id = %s ORDER BY position", (room_id,))
                    accessories = cursor.fetchall()

                    # Step 4: Rearrange positions of remaining accessories
                    for index, accessory in enumerate(accessories):
                        sql_rearrange = "UPDATE Accessories SET position = %s WHERE id = %s"
                        cursor.execute(sql_rearrange, (index, accessory['id']))

                    self.connection.commit()

                    message = "Accessory deleted and positions rearranged successfully"
                    is_success = True
                else:
                    message = "Accessory not found."
            else:
                message = "No valid delete parameters provided."

        except Error as e:
            message = f"Error deleting accessory: {e}"
            self.connection.rollback()
        finally:
            if self.verbose:
                print(message)
            cursor.close()
            return {"status": is_success, "message": message}

    ## Helper Methods for Fetching IDs
    def get_type_id_by_name(self, type_name):
        try:
            cursor = self.connection.cursor()
            sql = "SELECT id FROM Types WHERE type = %s"
            cursor.execute(sql, (type_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching type ID: {e}")
            return None
        finally:
            cursor.close()

    def get_communication_protocol_id_by_name(self, name):
        try:
            cursor = self.connection.cursor()
            sql = "SELECT id FROM CommunicationProtocol WHERE name = %s"
            cursor.execute(sql, (name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching communication protocol ID: {e}")
            return None
        finally:
            cursor.close()

    def get_room_id_by_name_for_user(self, room_name, user_id):
        try:
            cursor = self.connection.cursor()
            sql = """
                SELECT r.id
                FROM Rooms r
                JOIN UsersRooms ur ON r.id = ur.room_id
                WHERE r.room_name = %s AND ur.user_id = %s
            """
            cursor.execute(sql, (room_name, user_id))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching room ID for user: {e}")
            return None
        finally:
            cursor.close()

    ############################################################################
    ####### Records CRUD #######
    def insert_record(self, accessory_id, value, date_time, value_type, battery_level, category):
        """
        Inserts a new record into the Records table.

        :param value: The value of the record.
        :param date_time: The date and time of the record.
        :param value_type: The type of the value.
        :param battery_level: The battery level (if applicable).
        :param category: The category of the value ex. status, distance, frequency..
        :param accessory_id: The ID of the accessory associated with the record.
        """
        is_success = False
        message = None
        try:
            cursor = self.connection.cursor()
            sql = """
                INSERT INTO Records (value, date_time, value_type, battery_level, category, accessory_id) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (value, date_time, value_type, battery_level, category, accessory_id))
            self.connection.commit()
            message = "Record inserted successfully"
            is_success = True
        except Error as e:
            message = f"Error inserting record: {e}"
            self.connection.rollback()
        finally:
            if self.verbose:
                print(message)
            cursor.close()
            
            return {"status": is_success, "message": message}

    def get_records(self, accessory_id=None, category=None, value_type=None, start_date=None, end_date=None, latest_per_accessory=False):
        """
        Retrieves records from the Records table based on given filters.

        :param accessory_id: Filter by accessory ID.
        :param category: Filter by category.
        :param value_type: Filter by value type.
        :param start_date: Filter records from this date.
        :param end_date: Filter records up to this date.
        :param latest_per_accessory: If True, fetches only the latest record for each accessory.
        :return: List of records matching the criteria.
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            if latest_per_accessory:
                # Query to get the latest record for each accessory
                sql = """
                    SELECT r.*
                    FROM Records r
                    INNER JOIN (
                        SELECT accessory_id, MAX(date_time) AS max_date_time
                        FROM Records
                        GROUP BY accessory_id
                    ) latest_records ON r.accessory_id = latest_records.accessory_id AND r.date_time = latest_records.max_date_time
                    WHERE 1=1
                """
            else:
                # Standard query to get records based on filters
                sql = "SELECT * FROM Records r WHERE 1=1"
            
            parameters = []

            if accessory_id:
                sql += " AND r.accessory_id = %s"
                parameters.append(accessory_id)
            if category:
                sql += " AND category = %s"
                parameters.append(category)
            if value_type:
                sql += " AND value_type = %s"
                parameters.append(value_type)
            if start_date:
                sql += " AND date_time >= %s"
                parameters.append(start_date)
            if end_date:
                sql += " AND date_time <= %s"
                parameters.append(end_date)
            
            cursor.execute(sql, tuple(parameters))
            records = cursor.fetchall()
            return records
        except Error as e:
            print(f"Error fetching records: {e}")
            return []
        finally:
            cursor.close()

    def update_record(self, date_time, accessory_id, value=None, value_type=None, battery_level=None, category=None):
        """
        Updates an existing record in the Records table.

        :param date_time: The date and time of the record to update.
        :param accessory_id: The ID of the accessory associated with the record.
        :param value: The new value of the record.
        :param value_type: The new type of the value.
        :param battery_level: The new battery level (if applicable).
        :param category: The new category of the value.
        """
        try:
            cursor = self.connection.cursor()
            sql = "UPDATE Records SET "
            updates = []
            parameters = []

            if value is not None:
                updates.append("value = %s")
                parameters.append(value)
            if value_type is not None:
                updates.append("value_type = %s")
                parameters.append(value_type)
            if battery_level is not None:
                updates.append("battery_level = %s")
                parameters.append(battery_level)
            if category is not None:
                updates.append("category = %s")
                parameters.append(category)

            if updates:
                sql += ", ".join(updates)
                sql += " WHERE date_time = %s AND accessory_id = %s"
                parameters.extend([date_time, accessory_id])
                cursor.execute(sql, tuple(parameters))
                self.connection.commit()
                print("Record updated successfully")
            else:
                print("No update parameters provided.")
        except Error as e:
            print(f"Error updating record: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def delete_record(self, accessory_id, date_time=None):
        """
        Deletes records from the Records table.

        :param accessory_id: The ID of the accessory associated with the record(s).
        :param date_time: The date and time of the record to delete. If None, all records for the accessory_id are deleted.
        """
        try:
            cursor = self.connection.cursor()
            
            # SQL query to delete a specific record or all records for an accessory
            if date_time is None:
                sql = "DELETE FROM Records WHERE accessory_id = %s"
                parameters = (accessory_id,)
            else:
                sql = "DELETE FROM Records WHERE date_time = %s AND accessory_id = %s"
                parameters = (date_time, accessory_id)

            cursor.execute(sql, parameters)
            self.connection.commit()
            print("Record(s) deleted successfully")
        except Error as e:
            print(f"Error deleting record: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    ############################################################################
    ####### Automations CRUD #######
    def is_valid_accessory_id(self, accessory_id, expected_field):
        """
        Validates whether a given accessory ID corresponds to the expected field ('sensor' or 'actuator') in AccessoriesDetails.

        :param accessory_id: The accessory ID to validate.
        :param expected_field: The expected field value ('sensor' or 'actuator').
        :return: True if the accessory ID is valid for the expected field, False otherwise.
        """
        try:
            cursor = self.connection.cursor()
            sql = """
                SELECT 1
                FROM Accessories a
                JOIN Types t ON a.type_id = t.id
                WHERE a.id = %s AND t.field = %s
            """
            cursor.execute(sql, (accessory_id, expected_field))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error validating accessory ID: {e}")
            return False

    def create_automation(self, events, actions, time_from=None, time_to=None):
        """
        Creates a new automation in the database with the provided events and actions.

        :param events: A list of event dictionaries with 'sensor_id' and 'status' keys.
        :param actions: A list of action dictionaries with 'actuator_id', 'duration', and 'sequence' keys.
        :param time_from: The start time for the automation (optional).
        :param time_to: The end time for the automation (optional).
        :return: The ID of the created automation or None if an error occurred.
        """
        # Check if events and actions have at least one element
        if not events or not actions:
            raise ValueError("Events and actions must each have at least one element.")

        try:
            cursor = self.connection.cursor()

            # Validate sensor IDs in events
            seen_sensor_ids = set()
            for event in events:
                sensor_id = event.get('sensor_id')
                if sensor_id in seen_sensor_ids:
                    print(f"Error: Duplicate sensor ID '{sensor_id}' found in events.")
                    return None
                if not self.is_valid_accessory_id(sensor_id, 'sensor'):
                    print(f"Error: Invalid sensor ID '{sensor_id}' for event.")
                    return None
                seen_sensor_ids.add(sensor_id)

            # Validate actuator IDs in actions
            seen_actuator_ids = set()
            for action in actions:
                actuator_id = action.get('actuator_id')
                if actuator_id in seen_actuator_ids:
                    print(f"Error: Duplicate actuator ID '{actuator_id}' found in actions.")
                    return None
                if not self.is_valid_accessory_id(actuator_id, 'actuator'):
                    print(f"Error: Invalid actuator ID '{actuator_id}' for action.")
                    return None
                seen_actuator_ids.add(actuator_id)

            # Insert into Automations table
            sql_automation = """
                INSERT INTO Automations (execute_actions, time_from, time_to)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql_automation, (False, time_from, time_to))
            automation_id = cursor.lastrowid

            # Insert into Events table
            for event in events:
                sql_event = """
                    INSERT INTO Events (status, `trigger`, automation_id, sensor_id)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_event, (event['status'], False, automation_id, event['sensor_id']))

            # Insert into Actions table
            for action in actions:
                sql_action = """
                    INSERT INTO Actions (duration, sequence, automation_id, actuator_id)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_action, (action['duration'], action['sequence'], automation_id, action['actuator_id']))

            self.connection.commit()
            print(f"Automation created successfully with ID: {automation_id}")
            return automation_id

        except Exception as e:
            self.connection.rollback()
            print(f"Error creating automation: {e}")
            return None
        finally:
            cursor.close()

    def update_automation(self, automation_id, automation_data=None, events_data=None, actions_data=None):
        """
        Updates an automation, its events, or its actions with the provided data.
        
        :param automation_id: ID of the automation to update
        :param automation_data: Dictionary containing fields to update in the Automations table
        :param events_data: List of dictionaries, each containing an 'id' and fields to update in the Events table
        :param actions_data: List of dictionaries, each containing an 'id' and fields to update in the Actions table
        """

        try:
            cursor = self.connection.cursor()
            # Update the Automations table if automation_data is provided
            if automation_data:
                update_fields = ", ".join([f"{key} = %s" for key in automation_data.keys()])
                update_values = list(automation_data.values())
                sql = f"UPDATE Automations SET {update_fields} WHERE id = %s"
                cursor.execute(sql, (*update_values, automation_id))

            # Update the Events table if events_data is provided
            if events_data:
                for event in events_data:
                    sensor_id = event.pop('sensor_id', None)  # Get event ID and remove it from the update dict
                    if sensor_id:
                        update_fields = ", ".join([f"`{key}` = %s" if key == "trigger" else f"{key} = %s" for key in event.keys()])
                        update_values = list(event.values())
                        sql = f"UPDATE Events SET {update_fields} WHERE sensor_id = %s AND automation_id = %s"
                        cursor.execute(sql, (*update_values, str(sensor_id), automation_id))

            # Update the Actions table if actions_data is provided
            if actions_data:
                for action in actions_data:
                    actuator_id = action.pop('actuator_id', None)  # Get action ID and remove it from the update dict
                    if actuator_id:
                        update_fields = ", ".join([f"{key} = %s" for key in action.keys()])
                        update_values = list(action.values())
                        sql = f"UPDATE Actions SET {update_fields} WHERE actuator_id = %s AND automation_id = %s"
                        cursor.execute(sql, (*update_values, actuator_id, automation_id))

            self.connection.commit()
            print(f"Automation {automation_id} updated successfully.")

        except Exception as e:
            self.connection.rollback()
            print(f"Error updating automation: {e}")
        finally:
            cursor.close()

    def delete_automation(self, automation_id):
        try:
            cursor = self.connection.cursor()
            # Delete from Events table
            cursor.execute("DELETE FROM Events WHERE automation_id = %s", (automation_id,))

            # Delete from Actions table
            cursor.execute("DELETE FROM Actions WHERE automation_id = %s", (automation_id,))

            # Delete from Automations table
            cursor.execute("DELETE FROM Automations WHERE id = %s", (automation_id,))

            self.connection.commit()
            print("Automation and related records deleted successfully.")

        except Exception as e:
            self.connection.rollback()
            print("Error deleting automation:", e)
        finally:
            cursor.close()

    def get_automation(self, automation_id=None):
        """
        Retrieves automations along with their related events and actions.

        :param automation_id: Optional ID of a specific automation to retrieve. If None, retrieves all automations.
        :return: A list of dictionaries containing automation details, events, and actions.
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            # SQL to select automations and their related events and actions
            if automation_id:
                # Retrieve a specific automation and its details
                sql = """
                    SELECT 
                        a.id AS automation_id, 
                        a.execute_actions, 
                        a.time_from, 
                        a.time_to,
                        e.id AS event_id, 
                        e.status AS event_status, 
                        e.`trigger` AS event_trigger, 
                        e.sensor_id AS event_sensor_id,
                        act.id AS action_id,
                        act.duration AS action_duration,
                        act.sequence AS action_sequence,
                        act.actuator_id AS action_actuator_id
                    FROM Automations a
                    LEFT JOIN Events e ON a.id = e.automation_id
                    LEFT JOIN Actions act ON a.id = act.automation_id
                    WHERE a.id = %s
                """
                cursor.execute(sql, (automation_id,))
            else:
                # Retrieve all automations and their details
                sql = """
                    SELECT 
                        a.id AS automation_id, 
                        a.execute_actions, 
                        a.time_from, 
                        a.time_to,
                        e.id AS event_id, 
                        e.status AS event_status, 
                        e.`trigger` AS event_trigger, 
                        e.sensor_id AS event_sensor_id,
                        act.id AS action_id,
                        act.duration AS action_duration,
                        act.sequence AS action_sequence,
                        act.actuator_id AS action_actuator_id
                    FROM Automations a
                    LEFT JOIN Events e ON a.id = e.automation_id
                    LEFT JOIN Actions act ON a.id = act.automation_id
                """
                cursor.execute(sql)

            results = cursor.fetchall()

            # Organize data into a structured format
            automations = {}
            for row in results:
                automation_id = row['automation_id']
                if automation_id not in automations:
                    automations[automation_id] = {
                        'id': automation_id,
                        'execute_actions': row['execute_actions'],
                        'time_from': row['time_from'],
                        'time_to': row['time_to'],
                        'events': [],
                        'actions': []
                    }

                # Add events if they exist
                if row['event_id']:
                    event = {
                        'event_id': row['event_id'],
                        'status': row['event_status'],
                        'trigger': row['event_trigger'],
                        'sensor_id': row['event_sensor_id']
                    }
                    automations[automation_id]['events'].append(event)

                # Add actions if they exist
                if row['action_id']:
                    action = {
                        'action_id': row['action_id'],
                        'duration': row['action_duration'],
                        'sequence': row['action_sequence'],
                        'actuator_id': row['action_actuator_id']
                    }
                    automations[automation_id]['actions'].append(action)

            return list(automations.values())

        except Exception as e:
            print(f"Error retrieving automations: {e}")
            return None
        finally:
            cursor.close()


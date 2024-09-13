from database import Database
from globals import database_configuration, accessories_configuration, GLOBAL_VERBOSE
import sys
from datetime import datetime
# from functools import wraps

class Controller:
    session = None
    db_manager = None  # Class attribute to hold the database manager
    
    def __init__(self, session):
        Controller.session = session
    
    @staticmethod
    def get_db_connection():
        # Establish the database connection based on the platform
        db_manager = None
        
        if sys.platform == 'win32':
            db_manager = Database(
                database_configuration['host'], 
                database_configuration['port'], 
                database_configuration['username'],
                database_configuration['password'], 
                database_configuration['database_name'], 
                None,
                GLOBAL_VERBOSE
            )
        elif sys.platform == 'linux':
            db_manager = Database(
                database_configuration['host'], 
                database_configuration['port'], 
                database_configuration['username'],
                database_configuration['password'], 
                database_configuration['database_name'], 
                database_configuration['unix_socket'],
                GLOBAL_VERBOSE
            )
       
        return db_manager

    @staticmethod
    def with_db_connection():
        # Context manager to handle opening and closing the connection
        class DatabaseContext:
            def __enter__(self):
                Controller.db_manager = Controller.get_db_connection()
                Controller.db_manager.connect()
                return Controller.db_manager

            def __exit__(self, exc_type, exc_value, traceback):
                Controller.db_manager.disconnect()
        
        return DatabaseContext()
 
    def convert_record_value(self, record = None):
        if record:
            record_type = record["value_type"]
            if record_type == "str" or record_type == "s":
                record["value"] = str(record["value"])
            elif record_type == "float" or record_type == "f":
                try:
                    record["value"] = float(record["value"])
                except ValueError:
                    # Handle the case where conversion to float fails
                    record["value"] = None
                    print("Warning: Value could not be converted to float.")
            elif record_type == "int" or record_type == "i":
                try:
                    record["value"] = int(record["value"])
                except ValueError:
                    # Handle the case where conversion to int fails
                    record["value"] = None
                    print("Warning: Value could not be converted to int.")
            elif record_type == "bool" or record_type == "b":
                if isinstance(record["value"], str):
                    # Handle boolean values expressed as "true"/"false" or "1"/"0"
                    record["value"] = record["value"].lower() in ["true", "1"]
                else:
                    # Handle boolean values expressed as True/False
                    record["value"] = bool(record["value"])
            else:
                # Handle unknown record types or set default behavior
                print(f"Unknown record type: {record_type}")
                record["value"] = record["value"]
            return record
        else:
            print("No record found")
    
    @staticmethod
    def get_defalut_status(accessory_type):
            status = None
            if accessory_type:
                defalut_status = accessories_configuration["Items Status"][accessory_type][0]
                if defalut_status == "FLOAT" or defalut_status == "INT":
                    status = 0
                else:
                    status = defalut_status  
            return status
           
    def check_session_parameters(self):
        if 'first_load' not in Controller.session.data:
            Controller.session.set('first_load', False)
        if 'user_id' not in Controller.session.data:
            print("The user not exist")

        user_id = Controller.session.get('user_id')
        
        with Controller.with_db_connection() as db_manager:
            # accessories = db_manager.get_rooms_accessories_by_user(user_id)
            
            # Communication Protocols
            Controller.session.set("communication_protocols", [c['name'] for c in db_manager.get_communication_protocols()])
            
            # Accessories Types
            Controller.session.set("accessories_types", [t['type'] for t in db_manager.get_types()])

            # Accessories in rooms
            rooms = db_manager.get_rooms_by_user(user_id)
            rooms_details = {}
            for room in rooms:
                room_id = room["room_id"]
                room_name = room["room_name"]
                rooms_details[room_id] = {   
                        "room_name": room_name,
                        "accessories": []
                }     
                accessories = db_manager.get_accessories(room_id = room_id)
                for acc in accessories:
                    acc.pop("room_id")
                    acc.pop("room_name")
    
                    accessory_id = acc["accessory_id"]
                    statuses = db_manager.get_records(accessory_id=accessory_id)
                    record = None if len(statuses) == 0 else statuses[0]
                    position = acc.get("accessory_position", 0)
                    if record:
                        record = self.convert_record_value(record)
                        acc["current_status"] = record["value"]
                    else:
                        acc["current_status"] = Controller.get_defalut_status(acc.get("accessory_type", None))
                    
                    if rooms_details.get(room_id, None):
                        rooms_details[room_id]["accessories"].insert(position, acc)
                       
            # Controller.session.set("accessories_data", accessories)
            # rooms_details = self.restructure_accessories_with_rooms(accessories)


            Controller.session.set("rooms_data", rooms_details)
            

            automations = db_manager.get_automations_by_user(user_id)["output"]
            automations_details = []
            for automation in automations:
                automation_id = automation["automation_id"]
                automations_details.append(db_manager.get_automation(automation_id)[0])

            Controller.session.set("automations", automations_details)

    def start(self):
        # This function should reposiable for validation of the user at the begining 
        # 1- login the user name and password 
        
        # 2- check this role of this user 

        # 3- If login valid should push basic data to session
       
        # if not it should keep the user in the login page
        # if 'username' not in Controller.session.data:
        #     return {'redirect': '/login'}  # Example of redirect data
        
        self.check_session_parameters()

    @staticmethod
    def check_item(item_type, item_id):
        is_exist = False
        rooms_data = Controller.session.get("rooms_data")
        if rooms_data:
            for room_id in rooms_data:
                room = rooms_data[room_id]
                for accessory in room["accessories"]:
                    if accessory['accessory_type'] == item_type and accessory['accessory_id'] == item_id:
                        is_exist = True
                        return is_exist
        return is_exist

    @staticmethod
    def check_item_totally(type, id, status):
        if Controller.check_item(type, id):
            if status in accessories_configuration["Items Status"].get(type, None):
                return True
        return False

    @staticmethod
    def validations(db_manager = None):
        user_id = Controller.session.get("user_id")
        if user_id is None:
            return "Invalid user: No user ID in session"
        
        if isinstance(db_manager, Database):
            for user in db_manager.get_users():
                if user["user_id"] == user_id:
                    return True
            return False
        else:
            return "Invalid Connection: connect to the database first"

    @staticmethod
    def delete_accessory(accessory_id):
        # Records will delete automatically when accessory deleted
        # Because there is relation "ON DELETE CASCADE" between them

        with Controller.with_db_connection() as db_manager:
            # Step 1: Validate user
            if not Controller.validations(db_manager):
                return "Invalid User"
        
            # Step 2: Delete Accessory
            delete_data = db_manager.delete_accessory(accessory_id)

            
            if delete_data.get("status", False):
                # Step 3: Update Session
                rooms_data = Controller.session.get('rooms_data')
                for room_id in rooms_data:
                    room = rooms_data[room_id]
                    for accessory in room["accessories"]:
                        if accessory['accessory_id'] == accessory_id:
                            room["accessories"].remove(accessory)
                Controller.session.set("rooms_data", rooms_data)

            return delete_data

    @staticmethod
    def add_room(room_name):

        with Controller.with_db_connection() as db_manager:
            # Step 1: Validate user
            if not Controller.validations(db_manager):
                return {"message": "Invalid User", "status": False, "room_id": None}

            user_id = Controller.session.get("user_id")

            # Step 2: Add Room
            room_data = Controller.db_manager.add_room(room_name, user_id)
            room_id = room_data["room_id"]

            if room_data.get("status", False):
                Controller.session.data["rooms_data"][room_id] = {
                    "room_name": room_name,
                    "accessories": []
                }

            return room_data

    @staticmethod
    def add_accessory(accessory = {}):
        user_id = Controller.session.get("user_id")

        
        with Controller.with_db_connection() as db_manager:
            
            # Step 1: Validate user
            if not Controller.validations(db_manager):
                return {"message": "Invalid User", "status": False}
            
            # Step 2: Update the room with sensors and actuators

            accessory_id = accessory['id']
            accessory_type = accessory['type']
            name = accessory.get('name', "Unknown")
            cp = accessory.get('cp', "LoRa")
            position = accessory.get('position', 0)
            accessory_key = accessory.get('key', None)
            room_name = accessory.get('room_name', None)
            current_status = accessory.get('status', None)
            
            # validations
            # Check if the room exists for the user
            room_id = db_manager.get_room_id_by_name_for_user(room_name, user_id)
            
            if room_id is None:
                return "Invalid room for User"
        
            # Insert the accessory
            accessory_data = db_manager.insert_accessory(id= accessory_id, type_name= accessory_type, 
                                        name= name, communication_protocol_name= cp, position= position,
                                        accessory_key= accessory_key, room_id = room_id)

            if accessory_data.get("status", False):
                # Update Session
                types = db_manager.get_types(type_name = accessory_type)
                field = None
                if types:
                    if len(types) > 0 :
                        field = types[0]["field"]

                new_accory = {
                    'accessory_id': accessory_id,
                    'accessory_name': name,
                    'accessory_position': position,
                    'accessory_key': accessory_key,
                    'field': field,
                    'accessory_type': accessory_type,
                    'communication_protocol_name': cp,  
                    'current_status': current_status}

                rooms_data = Controller.session.get("rooms_data")
                
                if rooms_data.get(room_id, None):
                    rooms_data[room_id]["room_name"] = room_name
                    rooms_data[room_id]["accessories"].append(new_accory)
                else:
                    rooms_data[room_id] = {   
                        "room_name": room_name,
                        "accessories": [new_accory]
                            }

                
                Controller.session.set("rooms_data", rooms_data)
                
            return accessory_data
    
    @staticmethod
    def add_record(record_details = None):
        with Controller.with_db_connection() as db_manager:
            
            # Step 1: Validate user
            if not Controller.validations(db_manager):
                return {"message": "Invalid User", "status": False}
            
            # Step 2: Add record for sensors and actuators
            current_time = datetime.now()
            accessory_id = record_details['id']
            value = record_details['value']
            value_type = type(value).__name__
            
            battery_level = record_details.get('battery_level', None)
            category = record_details.get('category', "status")

            record_data = db_manager.insert_record(accessory_id, value, current_time, str(value_type),  battery_level, category)
            
            if record_data.get("status", False):
                for room_id in Controller.session.data["rooms_data"]:
                    room = Controller.session.data["rooms_data"][room_id]
                    for acc in room.get("accessories", None):
                        if acc["accessory_id"] == accessory_id:
                            acc["current_status"] = value
            
            return record_data

    @staticmethod
    def get_accessory_details(id):
        with Controller.with_db_connection() as db_manager:
            
            # Step 1: Validate user
            if not Controller.validations(db_manager):
                return {"message": "Invalid User", "status": False}
            
            # Step 2: Get Accessory
            return db_manager.get_accessories(id=id)

    @staticmethod
    def get_alerts(user_id):
        Alerts = []
        with Controller.with_db_connection() as db_manager:
            
            # # Step 1: Validate user
            if not Controller.validations(db_manager):
                return {"message": "Invalid User", "status": False}

            # Step 2: Get Alerts
            
            for automation in db_manager.get_automations_by_user(user_id)["output"]:
                if automation["execute_actions"] == 1:
                    automation_id = automation["automation_id"]
                    # return db_manager.get_automation(automation_id)[0]
                    Alerts.append(automation_id)
            return Alerts

    @staticmethod        
    def reset_alert(id):
        with Controller.with_db_connection() as db_manager:
        
            # Step 1: Validate user
            if not Controller.validations(db_manager):
                return {"message": "Invalid User", "status": False}  
            
            # Step 2: reset Alert
            ### TODO


# from globals import session
# import pprint

# obj = Controller(session)
# obj.start()
# # Pretty-print the data
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(Controller.session.get('rooms_data'))
# print(Controller.session.get('automations'))
# print(Controller.session.get('communication_protocols'))
# print(Controller.session.get('types'))









# print(Controller.delete_accessory("sensor1"))
# print(Controller.session.get('accessories_data'))

# Define accessory data to test the function
# accessories_data = [
#     {
#         'id': "sensor5",
#         'type': 'glass break sensor',
#         'name': 'sayed sensor',
#         'cp': 'WiFi',
#         'position': 3,
#         'key': 'sensor_key_1',
#         'room_name': 'Hall'
#     }
# ]

# # Call the function
# response = obj.add_accessories(accessories_data)

# Print the results
# print("Response from add_accessory:", response)
# print(Controller.session.get('accessories_data'))

# rec = {
#         'id': "sensor5",
#         'value': 'Opened',
#         'battery_level': 95,
#         'category': 'status'
#     }
# response = Controller.add_record(rec)
# # Print the results
# print("Response from add_record:", response)
# print(Controller.session.get('accessories_data'))
import unittest
from database import Database
from datetime import datetime, timedelta
import sys
from globals import database_configuration, GLOBAL_VERBOSE

"""
Before Using these tests you should create the database by running the sql commands (every time test failded or there an error)

running:
python test_database.py 
"""

class TestDatabaseManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize the database connection once for all tests."""
        if sys.platform == 'win32':
            cls.db_manager = Database(
                database_configuration['host'], 
                database_configuration['port'], 
                database_configuration['username'],
                database_configuration['password'], 
                database_configuration['database_name'], 
                None,
                GLOBAL_VERBOSE
            )
        elif sys.platform == 'linux':
            cls.db_manager = Database(
                database_configuration['host'], 
                database_configuration['port'], 
                database_configuration['username'],
                database_configuration['password'], 
                database_configuration['database_name'], 
                database_configuration['unix_socket'],
                GLOBAL_VERBOSE
            )
        cls.db_manager.connect()
        cls.user_id = cls.db_manager.add_user('john_doe', 'securepassword', 'User') # add this user to test the rooms
        room_data = cls.db_manager.add_room("Testing Room test", user_id=cls.user_id)
        cls.room_id = room_data["room_id"]
        print(f"User Id: {cls.user_id} room ID: {cls.room_id}")
        
        # sensor
        cls.db_manager.insert_accessory(
            id="A1",
            name="Accessory 1",
            position=1,
            accessory_key="key1",
            type_id=1,
            communication_protocol_id=1,
            room_id=cls.room_id 
        )
        
        # Acuator
        cls.db_manager.insert_accessory(
            id="A2",
            name="Accessory 2",
            position=5,
            accessory_key="key2",
            type_id=4,
            communication_protocol_id=1,
            room_id=cls.room_id 
        )

        # sensor
        cls.db_manager.insert_accessory(
            id="A3",
            name="Accessory 3",
            position=3,
            accessory_key="key3",
            type_id=1,
            communication_protocol_id=1,
            room_id=cls.room_id 
        )

        # cls.automation_id = cls.db.create_automation(events=[], actions=[], time_from="08:00:00", time_to="17:00:00")

    @classmethod
    def tearDownClass(cls):
        cls.db_manager.delete_accessory(id="A3")
        cls.db_manager.delete_accessory(id="A2")
        cls.db_manager.delete_accessory(id="A1")
        cls.db_manager.delete_room(room_name="Testing Room test")
        cls.db_manager.delete_user('john_doe')

        cls.db_manager.disconnect()

    def setUp(self):
        """Run before every test."""
        # Add setup code if needed, like resetting specific parts of the DB or state.
        
    def tearDown(self):
        """Run after every test."""
        # Add teardown code if needed, like clearing test data from the DB.



    def test_permissions(self):
        """Test cases for permissions."""
        self.db_manager.insert_permission('test1', 'Allows writing 1 new records.')
        permissions = self.db_manager.get_permissions()
        self.assertTrue(any(p['name'] == 'test1' for p in permissions))
        self.db_manager.update_permission('test1', 'test', 'Allows writing new records.')
        permissions = self.db_manager.get_permissions()
        self.assertTrue(any(p['name'] == 'test' for p in permissions))
        self.db_manager.delete_permission("test")
        permissions = self.db_manager.get_permissions()
        self.assertFalse(any(p['name'] == 'test' for p in permissions))

    def test_roles(self):
        """Test cases for roles."""
        self.db_manager.insert_role_with_permissions('Editor', ['update', 'read'])
        roles = self.db_manager.get_roles()
        self.assertIn('Editor', [role['role_name'] for role in roles])
        self.db_manager.update_role_permissions('Editor', ['read'])
        permissions = self.db_manager.get_role_permissions('Editor')
        self.assertEqual(permissions[0][1], 'read')
        self.db_manager.delete_role('Editor')
        roles = self.db_manager.get_roles()
        self.assertNotIn('Editor', [role['role_name'] for role in roles])

    def test_users(self):
        """Test cases for users."""
        self.db_manager.add_user('test_name', 'securepassword', 'User')
        user_info = self.db_manager.get_user_role_and_permissions('test_name')
        self.assertEqual(user_info['role'], 'User')
        self.db_manager.update_user_role('test_name', 'Admin')
        user_info = self.db_manager.get_user_role_and_permissions('test_name')
        self.assertEqual(user_info['role'], 'Admin')
        self.db_manager.delete_user('test_name')
        users = self.db_manager.get_users()
        self.assertNotIn('test_name', [user['name'] for user in users])

    def test_rooms(self):
        """Test cases for rooms."""
        self.db_manager.add_room("Testing Room", user_id=self.user_id)
        rooms = self.db_manager.get_rooms_by_user(user_id=self.user_id)
        self.assertIn("Testing Room", [room['room_name'] for room in rooms])
        self.db_manager.update_room(old_room_name="Testing Room", new_room_name="Main Testing Room", user_id=self.user_id)
        rooms = self.db_manager.get_rooms_by_user(user_id=self.user_id)
        self.assertIn("Main Testing Room", [room['room_name'] for room in rooms])
        self.db_manager.delete_room(room_name="Main Testing Room")
        rooms = self.db_manager.get_rooms_by_user(user_id=self.user_id)
        self.assertNotIn("Main Testing Room", [room['room_name'] for room in rooms])

    def test_types(self):
        """Test cases for types."""
        self.db_manager.insert_type("field1", "type1")
        self.db_manager.insert_type("field2", "type2")
        types = self.db_manager.get_types()
        self.assertIn("type1", [t['type'] for t in types])
        self.db_manager.update_type(type_old_name="type1", type_new_name="type3", field="field3")
        types = self.db_manager.get_types()
        self.assertIn("type3", [t['type'] for t in types])
        self.db_manager.delete_type(type_name="type3")
        self.db_manager.delete_type(type_name="type2")
        types = self.db_manager.get_types()
        self.assertNotIn("type3", [t['type'] for t in types])
        self.assertNotIn("type2", [t['type'] for t in types])

    def test_communication_protocols(self):
        """Test cases for communication protocols."""
        self.db_manager.insert_communication_protocol("Protocol1")
        protocols = self.db_manager.get_communication_protocols()
        self.assertIn("Protocol1", [p['name'] for p in protocols])
        self.db_manager.update_communication_protocol(name_old="Protocol1", name_new="Protocol3")
        protocols = self.db_manager.get_communication_protocols()
        self.assertIn("Protocol3", [p['name'] for p in protocols])
        self.db_manager.delete_communication_protocol(name="Protocol3")
        protocols = self.db_manager.get_communication_protocols()
        self.assertNotIn("Protocol3", [p['name'] for p in protocols])

    def test_accessories(self):
        """Test cases for accessories."""
        self.db_manager.insert_accessory(
            id="acc1",
            name="Accessory 1",
            position=1,
            accessory_key="key1",
            type_id=1,
            communication_protocol_id=1,
            room_id=self.room_id
        )
        accessories = self.db_manager.get_accessories()
        self.assertIn("acc1", [a['accessory_id'] for a in accessories])
        self.db_manager.update_accessory(
            id="acc1",
            name="Updated Accessory 1",
            position=10,
            accessory_key="updated_key",
            type_id=4,
            room_id=self.room_id
        )
        accessories = self.db_manager.get_accessories()
        self.assertIn("Updated Accessory 1", [a['accessory_name'] for a in accessories])
        self.db_manager.delete_accessory(id="acc1")
        accessories = self.db_manager.get_accessories()
        self.assertNotIn("acc1", [a['accessory_id'] for a in accessories])

    def test_records(self):
        """Test cases for records."""
        self.db_manager.insert_record(
            value="25.5",
            date_time="2024-08-28 15:00:00",
            value_type="float",
            battery_level=85,
            category="status",
            accessory_id="A1"
        )
        self.db_manager.insert_record(
            value="20.2",
            date_time="2024-08-28 13:00:00",
            value_type="float",
            battery_level=85,
            category="temp",
            accessory_id="A1"
        )
        records = self.db_manager.get_records(accessory_id="A1")
        self.assertEqual(len(records), 2)
        self.db_manager.delete_record(accessory_id="A1")
        records = self.db_manager.get_records(accessory_id="A1")
        self.assertEqual(len(records), 0)

    def test_automations(self):
        """Test cases for automations."""
        # Insert accessories for testing purposes (you may have these in your setup or elsewhere)
        """
        Before the test
        INSERT INTO Accessories (id, name, position, accessory_key, type_id, communication_protocol_id, room_id) VALUES ('A1', 'Accessory 4', 4, 'key4', 1, 1, 1), ('A2', 'Accessory 5', 5, 'key5', 4, 1, 1);
        """
        
        # Define events and actions for the automation
        events = [{"sensor_id": "A1", "status": "active"}]
        actions = [{"actuator_id": "A2", "duration": "00:05:00", "sequence": 1}]
        
        # Create an automation with the specified events and actions
        automation_id = self.db_manager.create_automation(events, actions, "13:00:00", "14:00:00")
        
        # Retrieve the created automation and its details
        automation = self.db_manager.get_automation(automation_id)
        
        # Check if the automation is not None
        self.assertIsNotNone(automation)
        
        # Check if the automation has events and actions
        if automation:
            automation = automation[0]
            self.assertEqual(len(automation['events']), 1)  # Expecting 1 event
            self.assertEqual(len(automation['actions']), 1)  # Expecting 1 action

            # Validate the event details
            event = automation['events'][0]
            self.assertEqual(event['sensor_id'], "A1")
            self.assertEqual(event['status'], "active")

            # Validate the action details
            action = automation['actions'][0]
            self.assertEqual(action['actuator_id'], "A2")
            self.assertEqual(str(action['duration']), "0:05:00")
            self.assertEqual(action['sequence'], 1)
        
        # Update the automation details
        self.db_manager.update_automation(automation_id, {"time_from": "14:00:00"}, events, actions)
        
        # Retrieve the updated automation details
        updated_automation = self.db_manager.get_automation(automation_id)
        
        # Check if the updated automation time has been set correctly
        if updated_automation:
            updated_automation = updated_automation[0]
            self.assertEqual(str(updated_automation['time_from']), "14:00:00")
            
            # Again, check if the events and actions are still correctly linked
            self.assertEqual(len(updated_automation['events']), 1)  # Expecting 1 event
            self.assertEqual(len(updated_automation['actions']), 1)  # Expecting 1 action

        # Delete the automation
        self.db_manager.delete_automation(automation_id)
        
        # Check if the automation has been deleted
        automation = self.db_manager.get_automation(automation_id)
        self.assertEqual(len(automation), 0)

    def test_trigger_with_null_time(self):
        # Create automation with events where time_from and time_to are NULL
        events = [{"sensor_id": "A1", "status": "active"}]
        actions = [{"actuator_id": "A2", "duration": "00:05:00", "sequence": 1}]
        automation_id = self.db_manager.create_automation(events, actions, time_from=None, time_to=None)

        # Insert record to trigger the event
        self.db_manager.insert_record( "A1", "inactive", datetime.now(), "str", 100, "status")

        # Retrieve the created automation and its details
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]
            print(automation)

            # Validate the event details
            event = automation['events'][0]
            self.assertEqual(event['sensor_id'], "A1")
            self.assertEqual(event['status'], "active")
            self.assertEqual(event['trigger'], 0, "Trigger should be set to 0 when events(status) != records(value) not equal each others")

        self.db_manager.insert_record("A1", "active", datetime.now(), "str", 100, "status")
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]

            # Validate the event details
            event = automation['events'][0]
            self.assertEqual(event['sensor_id'], "A1")
            self.assertEqual(event['trigger'], 1, "Trigger should be set to 1 when time_from and time_to are NULL")

        self.db_manager.insert_record("A1", "inactive", datetime.now(), "str", 100, "status")
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]

            # Validate the event details
            event = automation['events'][0]
            self.assertEqual(event['sensor_id'], "A1")
            self.assertEqual(event['trigger'], 1, "Trigger should be keep to 1 when is set before as 1 when time_from and time_to are NULL")
        
        self.db_manager.delete_record("A1")
        self.db_manager.delete_automation(automation_id)

    def test_trigger_within_time_range(self):
        # Get current time and calculate a time range within which the trigger should activate
        current_time = datetime.now()
        time_from = (current_time - timedelta(hours=1)).strftime('%H:%M:%S')
        time_to = (current_time + timedelta(hours=1)).strftime('%H:%M:%S')

        # Create automation with events where the current time is within the time_from and time_to range
        events = [{"sensor_id": "A1", "status": "active"}]
        actions = [{"actuator_id": "A2", "duration": "00:05:00", "sequence": 1}]
        automation_id = self.db_manager.create_automation(events, actions, time_from=time_from, time_to=time_to)

        # Insert record to trigger the event
        self.db_manager.insert_record("A1", "inactive", datetime.now(), "str", 100, "status")

        # Retrieve the created automation and its details
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]

            # Validate the event details
            event = automation['events'][0]
            self.assertEqual(event['sensor_id'], "A1")
            self.assertEqual(event['status'], "active")
            self.assertEqual(event['trigger'], 0, "Trigger should be set to 0 when records(value) != events(status)")

        self.db_manager.insert_record("A1", "active", datetime.now(), "str", 100, "status")

        # Retrieve the created automation and its details
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]

            # Validate the event details
            event = automation['events'][0]
            self.assertEqual(event['sensor_id'], "A1")
            self.assertEqual(event['trigger'], 1, "Trigger should be set to 1 when records(value) matches events(status) within time range")
        
        self.db_manager.delete_record("A1")
        self.db_manager.delete_automation(automation_id)

    def test_trigger_outside_time_range(self):
        # Get current time and calculate a time range outside which the trigger should not activate
        current_time = datetime.now()
        time_from = (current_time - timedelta(hours=2)).strftime('%H:%M:%S')
        time_to = (current_time - timedelta(hours=1)).strftime('%H:%M:%S')

        # Create automation with events where the current time is outside the time_from and time_to range
        events = [{"sensor_id": "A1", "status": "active"}]
        actions = [{"actuator_id": "A2", "duration": "00:05:00", "sequence": 1}]
        automation_id = self.db_manager.create_automation(events, actions, time_from=time_from, time_to=time_to)

        # Insert record to trigger the event
        self.db_manager.insert_record("A1", "inactive", datetime.now(), "str", 100, "status")

        # Retrieve the created automation and its details
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]

            # Validate the event details
            event = automation['events'][0]
            self.assertEqual(event['sensor_id'], "A1")
            self.assertEqual(event['status'], "active")
            self.assertEqual(event['trigger'], 0, "Trigger should be set to 0 when current time is outside time range")

        self.db_manager.insert_record("A1", "active", datetime.now(), "str", 100, "status")

        # Retrieve the created automation and its details
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]

            # Validate the event details
            event = automation['events'][0]
            self.assertEqual(event['sensor_id'], "A1")
            self.assertEqual(event['trigger'], 0, "Trigger should be set to 0 when current time is outside time range")
        
        self.db_manager.delete_record("A1")
        self.db_manager.delete_automation(automation_id)

    def test_trigger_update_events(self):
        # Create an automation with a set of events
        events = [{"sensor_id": "A1", "status": "active"}, 
                  {"sensor_id": "A3", "status": "inactive"}]
        actions = [{"actuator_id": "A2", "duration": "00:05:00", "sequence": 1}]
        automation_id = self.db_manager.create_automation(events, actions, time_from=None, time_to=None)

        # Retrieve the created automation
        automation = self.db_manager.get_automation(automation_id)
        self.assertIsNotNone(automation, "Failed to create automation")
        automation = automation[0]

        # Check the initial state of excute_actions
        self.assertFalse(automation['execute_actions'], "Initial excute_actions should be FALSE")

        # Update the status of events to match the trigger condition
        self.db_manager.insert_record("A1", "active", datetime.now(), "str", 100, "status")
        self.db_manager.insert_record("A3", "active", datetime.now(), "str", 100, "status")

        # Check the excute_actions column after updates
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]
            self.assertFalse(automation['execute_actions'], "excute_actions should be FALSE as not all events are triggered")

        # Update the status of the remaining event
        self.db_manager.insert_record("A3", "inactive", datetime.now(), "str", 100, "status")

        # Check the excute_actions column again
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]
            self.assertTrue(automation['execute_actions'], "excute_actions should be TRUE as all events are triggered")

        self.db_manager.update_automation(automation_id= automation_id, events_data=[{"sensor_id": "A3", "trigger": False}])

        # Check the excute_actions column after updates
        automation = self.db_manager.get_automation(automation_id)
        if automation:
            automation = automation[0]
            event = automation['events']
            print(event)
            self.assertFalse(automation['execute_actions'], "excute_actions should be FALSE as not all events are triggered")
        
        # Cleanup
        self.db_manager.delete_record("A1")
        self.db_manager.delete_automation(automation_id)



if __name__ == '__main__':
    unittest.main()


# db_manager = Database(host='localhost', port = 3306, username='root', password='1234', database_name='home_kit', unix_socket=None)
# db_manager.connect()
# ## permission test
# # db_manager.insert_permission('test1', 'Allows writing 1 new records.')
# # db_manager.update_permission('test1', 'test', 'Allows writing new records.')
# # print(db_manager.get_permissions())
# # db_manager.delete_permission("test")
# # print(db_manager.get_permissions())

# ## Roles test
# # db_manager.insert_role_with_permissions('Editor', ['update', 'read'])
# # print(db_manager.get_roles())
# # db_manager.update_role_permissions('Editor', [ 'read'])
# # print(db_manager.get_role_permissions('Editor'))
# # print(db_manager.get_roles())
# # db_manager.delete_role('Editor')
# # print(db_manager.get_roles())


# ### User test
# # db_manager.add_user('john_doe', 'securepassword', 'user')
# # print(db_manager.get_user_role_and_permissions('john_doe'))
# # print(db_manager.get_users())
# # db_manager.update_user_role('john_doe', 'Admin')
# # print(db_manager.get_user_role_and_permissions('john_doe'))
# # db_manager.delete_user('john_doe')


# # Rooms test
# # db_manager.add_room("Living Room", user_id=1)
# # rooms = db_manager.get_rooms_by_user(user_id=1)
# # print(rooms)
# # db_manager.update_room(old_room_name="Living Room", new_room_name="Main Living Room", user_id=5)
# # rooms = db_manager.get_rooms_by_user(user_id=1)
# # print(rooms)
# # db_manager.delete_room(room_id=6)
# # db_manager.delete_room(room_name="Living Room")
# # rooms = db_manager.get_rooms_by_user(user_id=1)
# # print(rooms)

# ## Types test
# # Test insert
# # db_manager.insert_type("field1", "type1")
# # db_manager.insert_type("field2", "type2")
# # db_manager.insert_type("field5", "type5")

# # # Test get
# # types = db_manager.get_types()
# # print("Types after insert:")
# # for type_row in types:
# #     print(type_row)

# # # Test update with type_new_name and field
# # db_manager.update_type(type_old_name="type1", type_new_name="type3", field="field3")

# # # Test update with only type_new_name
# # db_manager.update_type(id=2, type_new_name="type_updated")

# # # Test update with only field
# # db_manager.update_type(type_old_name="type_updated", field="field_updated")

# # # Test update with only field
# # db_manager.update_type(type_old_name="type5", type_new_name="type4")

# # # Test get after update
# # types = db_manager.get_types()
# # print("Types after update:")
# # for type_row in types:
# #     print(type_row)

# # # Test delete
# # db_manager.delete_type(type_name="type3")
# # # db_manager.delete_type(id=2)
# # db_manager.delete_type(type_name="type4")
# # db_manager.delete_type(type_name="type2")

# # # Test get after delete
# # types = db_manager.get_types()
# # print("Types after delete:")
# # for type_row in types:
# #     print(type_row)



#  # Test insert
# # db_manager.insert_communication_protocol("Protocol1")
# # db_manager.insert_communication_protocol("Protocol2")

# # # Test get
# # protocols = db_manager.get_communication_protocols()
# # print("Protocols after insert:")
# # for protocol in protocols:
# #     print(protocol)

# # # Test update with name_new
# # db_manager.update_communication_protocol(name_old="Protocol1", name_new="Protocol3")

# # # Test update with id
# # db_manager.update_communication_protocol(id=5, name_new="Protocol_updated")

# # # Test get after update
# # protocols = db_manager.get_communication_protocols()
# # print("Protocols after update:")
# # for protocol in protocols:
# #     print(protocol)

# # # Test delete
# # db_manager.delete_communication_protocol(name="Protocol3")
# # db_manager.delete_communication_protocol(id=5)

# # # Test get after delete
# # protocols = db_manager.get_communication_protocols()
# # print("Protocols after delete:")
# # for protocol in protocols:
# #     print(protocol)


# # test accessories table

# # 1. Test Insert Accessory with ID
# # try:
# #     db_manager.insert_accessory(
# #         id="acc1",
# #         name="Accessory 1",
# #         position=1,
# #         accessory_key="key1",
# #         type_id=1,
# #         communication_protocol_id=1,
# #         room_id=2
# #     )
# #     print("Insert with ID successful")
# # except Exception as e:
# #     print(f"Error during insert with ID: {e}")

# # # 2. Test Insert Accessory with Names
# # try:
# #     db_manager.insert_accessory(
# #         id="acc2",
# #         name="Accessory 2",
# #         position=2,
# #         accessory_key="key2",
# #         type_name="glass break sensor",
# #         communication_protocol_name="WiFi",
# #         room_name="Living Room"
# #     )
# #     print("Insert with names successful")
# # except Exception as e:
# #     print(f"Error during insert with names: {e}")

# # try:
# #     accessories = db_manager.get_accessories()
# #     print("Get Accessories successful")
# #     for accessory in accessories:
# #         print(accessory)
# # except Exception as e:
# #     print(f"Error during get accessories: {e}")

# # # 3. Test Update Accessory with ID
# # try:
# #     db_manager.update_accessory(
# #         id="acc1",
# #         name="Updated Accessory 1",
# #         position=10,
# #         accessory_key="updated_key",
# #         type_id= 4,
# #         room_id=2
# #     )
# #     print("Update with ID successful")
# # except Exception as e:
# #     print(f"Error during update with ID: {e}")


# # # 4. Test Update Accessory with Names
# # try:
# #     db_manager.update_accessory(
# #         id="acc2",
# #         name="Updated Accessory 2",
# #         position=20,
# #         accessory_key="updated_key2",
# #         type_name="Updated Type 2",
# #         communication_protocol_name="Updated Protocol 2",
# #         room_name="Updated Room 2"
# #     )
# #     print("Update with names successful")
# # except Exception as e:
# #     print(f"Error during update with names: {e}")

# # # 5. Test Get Accessories
# # try:
# #     accessories = db_manager.get_accessories()
# #     print("Get Accessories successful")
# #     for accessory in accessories:
# #         print(accessory)
# # except Exception as e:
# #     print(f"Error during get accessories: {e}")

# # # 6. Test Delete Accessory with ID
# # try:
# #     db_manager.delete_accessory(id="acc1")
# #     print("Delete with ID successful")
# # except Exception as e:
# #     print(f"Error during delete with ID: {e}")

# # # 7. Test Delete Accessory with Name
# # # Since delete requires ID, you would need to ensure the accessory exists first.
# # try:
# #     db_manager.delete_accessory(id="acc2")
# #     print("Delete with ID successful")
# # except Exception as e:
# #     print(f"Error during delete with ID: {e}")
# # try:
# #     accessories = db_manager.get_accessories()
# #     print("Get Accessories successful")
# #     for accessory in accessories:
# #         print(accessory)
# # except Exception as e:
# #     print(f"Error during get accessories: {e}")

# # test Records table

# # # Test inserting records
# # db_manager.insert_record(
# #     value="25.5",
# #     date_time="2024-08-28 15:00:00",
# #     value_type="temperature",
# #     battery_level=85,
# #     category="status",
# #     accessory_id="A1"
# # )

# # db_manager.insert_record(
# #     value="26.0",
# #     date_time="2024-09-15 15:10:00",
# #     value_type="temperature",
# #     battery_level=80,
# #     category="status",
# #     accessory_id="A1"
# # )

# # db_manager.insert_record(
# #     value="30.0",
# #     date_time="2024-08-29 15:30:00",
# #     value_type="temperature",
# #     battery_level=75,
# #     category="status",
# #     accessory_id="A2"
# # )

# # # Test getting all records
# # records = db_manager.get_records()
# # print("All Records:", records)

# # # Test getting records for a specific accessory
# # records_a1 = db_manager.get_records(accessory_id="A1")
# # print("Records for A1:", records_a1)

# # # Test getting latest record for each accessory
# # latest_records = db_manager.get_records(latest_per_accessory=True)
# # print("Latest records for each accessory:", latest_records)

# # # Test deleting a specific record
# # db_manager.delete_record(accessory_id="A1", date_time="2024-08-30 14:00:00")

# # # Verify delete operation
# # records_after_delete_specific = db_manager.get_records(accessory_id="A1")
# # print("Records for A1 after deleting a specific record:", records_after_delete_specific)

# # # Test deleting all records for a specific accessory
# # db_manager.delete_record(accessory_id="A2")

# # # Verify delete operation
# # records_after_delete_all = db_manager.get_records(accessory_id="A2")
# # print("Records for A2 after deleting all records:", records_after_delete_all)




# # 1. Test Create Automation
# # """
# # Before run the test insert these data:
# # INSERT INTO Accessories (id, name, position, accessory_key, type_id, communication_protocol_id, room_id) VALUES ('sensor1', 'Accessory 3', 3, 'key3', 1, 1, 1), ('sensor2', 'Accessory 4', 4, 'key4', 1, 1, 1), ('sensor3', 'Accessory 5', 5, 'key5', 1, 1, 1), ('sensor4', 'Accessory 7', 6, 'key6', 1, 1, 1), ('actuator1', 'Accessory 8', 6, 'key6', 5, 1, 1), ('actuator2', 'Accessory 9', 6, 'key6', 4, 1, 1), ('actuator3', 'Accessory 10', 6, 'key6', 4, 1, 1), ('actuator4', 'Accessory 11', 6, 'key6', 5, 1, 1);
# # """
# # print("Testing create_automation...")
# # events = [
# #     {"sensor_id": "sensor1", "status": "active"},
# #     # {"sensor_id": "sensor2", "status": "inactive"},
# #     # {"sensor_id": "sensor3", "status": "active"},
# #     # {"sensor_id": "sensor4", "status": "inactive"}
# # ]
# # actions = [
# #     {"actuator_id": "actuator1", "duration": "00:05:00", "sequence": 1},
# #     # {"actuator_id": "actuator2", "duration": "00:05:00", "sequence": 2},
# #     # {"actuator_id": "actuator3", "duration": "00:05:00", "sequence": 3},
# #     # {"actuator_id": "actuator4", "duration": "00:05:00", "sequence": 4}
# # ]
# # automation_id = db_manager.create_automation(events, actions, "13:00:00", "14:00:00")
# # print(f"Created automation with ID: {automation_id}")

# # # Get specific automation
# # automation = db_manager.get_automation(automation_id)
# # print(f"Retrieved specific automation before update: {automation}")

# # # 2. Test Update Automation
# # print("Testing update_automation...")
# # update_automation_data = {"time_from": "14:00:00"}
# # update_events_data = [{"sensor_id": "sensor1", "status": "inactive"}]  # Assume event with ID 1 exists
# # update_actions_data = [{"actuator_id": "actuator1", "duration": "00:15:00"}]  # Assume action with ID 1 exists

# # db_manager.update_automation(automation_id, update_automation_data, update_events_data, update_actions_data)
# # print("Updated automation successfully.")

# # # 3. Test Get Automation
# # # Get specific automation
# # automation = db_manager.get_automation(automation_id)
# # print(f"Retrieved specific automation After update: {automation}")

# # # Get all automations
# # all_automations = db_manager.get_automation()
# # print(f"Retrieved all automations: {all_automations}")

# # # # 4. Test Delete Automation
# # print("Testing delete_automation...")
# # db_manager.delete_automation(automation_id)
# # print(f"Deleted automation with ID: {automation_id}")


# # print("Testing get_automation...")
# # # Get specific automation
# # automation = db_manager.get_automation(automation_id)
# # print(f"Retrieved specific automation after delete: {automation}")



# db_manager.disconnect()





#################### tesing automations per user #############
# db_manager = Database(host='localhost', port = 3306, username='root', password='1234', database_name='home_kit', unix_socket=None)
# db_manager.connect()
# # print(db_manager.get_automations_by_user(43))


# print(db_manager.add_user('sayed testing', 'pass', 'user'))
# # db_manager.add_room("sayed Room 1", user_id=43)
# # db_manager.add_room("sayed Room 2", user_id=43)
# # db_manager.insert_accessory("ss1", "sayed sensor", 1, "sayedkey", 1, 2, 37)
# # db_manager.insert_accessory("sa1", "sayedacc", 1, "sayedkey", 4, 2, 38)

# # print("Testing create_automation...")
# # events = [
# #     {"sensor_id": "ss1", "status": "active"},
# # ]
# # actions = [
# #     {"actuator_id": "sa1", "duration": "00:05:00", "sequence": 1},
# # ]
# # automation_id = db_manager.create_automation(events, actions)
# # print(f"Created automation with ID: {automation_id}")
# # print(db_manager.get_automation(automation_id))
# db_manager.disconnect()
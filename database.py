from datetime import datetime

import mysql.connector
from mysql.connector import Error
# from PyQt5.QtCore import QThread
from globals import *

"""
host='localhost',
database='gateway',
user='root',
password='0000',
port='9999'
"""


class Database:
 
    def __init__(self,host,port,username,password,database_name,unix_socket):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database_name = database_name
        self.connection = None
        self.unix_socket = unix_socket
 
    def connect(self):
        try:
            self.connection = mysql.connector.connect(host=self.host,
                                                 database=self.database_name,
                                                 user=self.username,
                                                 password=self.password,
                                                 unix_socket=self.unix_socket
                                                 )
            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                #print("Connected to MySQL Server version ", db_Info)
 
 
        except Error as e:
            print("Error while connecting to MySQL", e)
 
    def is_connected(self):
        return self.connection.is_connected()

    def disconnect(self):

        if self.connection.is_connected():
            self.connection.close()
            #print("MySQL connection is closed")

    def ckeck_connection(self):

        if self.connection.is_connected():
            return True
        else:
            return False

    def insert_dashboard(self, dashboard_id, dashboard_name, user_id):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO dashboards (id, name, user_id) VALUES (%s, %s, %s)"
            cursor.execute(query, (dashboard_id, dashboard_name, user_id))
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert dashboard: {}".format(error))
            return False
        return True

    def insert_new_sensor(self, sensorid, cp, type, name):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO sensors(sensorid, cp, type, name) VALUES (%s, %s, %s, %s)"""
            records_to_insert = (sensorid, cp, type, name)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_new_actuator(self, actuatorid, cp, type, name):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO actuators(actuatorid, cp, type, name) VALUES (%s, %s, %s, %s)"""
            records_to_insert = (actuatorid, cp, type, name)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_temperature_sensor_reading(self, sensorid, temp, hum, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO temperature_sensor(sensorid,temperature,humidty,date_time) VALUES (%s,%s,%s,%s)"""
            records_to_insert = (sensorid, temp, hum, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_door_sensor_reading(self, sensorid, status, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO door_sensor(sensorid,door_status,date_time) VALUES (%s,%s,%s)"""
            records_to_insert = (sensorid, status, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_smoke_sensor_reading(self, sensorid, status, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO smoke_sensor(sensorid,fire_status,date_time) VALUES (%s,%s,%s)"""
            records_to_insert = (sensorid, status, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_glass_sensor_reading(self, sensorid, status, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO glass_sensor(sensorid,glass_status,date_time) VALUES (%s,%s,%s)"""
            records_to_insert = (sensorid, status, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_motion_sensor_reading(self, sensorid, status, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO motion_sensor(sensorid,motion_status,date_time) VALUES (%s,%s,%s)"""
            records_to_insert = (sensorid, status, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_polution_sensor_reading(self, sensorid, polution, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO polution_sensor(sensorid,polution,date_time) VALUES (%s,%s,%s)"""
            records_to_insert = (sensorid, polution, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_power_reading(self, power, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO power(power,date_time) VALUES (%s,%s)"""
            records_to_insert = (power, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_relay_switch_reading(self, actuatorid, status, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO relay_switch(actuatorid,status,date_time) VALUES (%s,%s,%s)"""
            records_to_insert = (actuatorid, status, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_siren_reading(self, actuatorid, status, datetime):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO siren(actuatorid,status,date_time) VALUES (%s,%s,%s)"""
            records_to_insert = (actuatorid, status, datetime)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def check_sensorid(self, sensorid):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query = "SELECT * FROM sensors WHERE sensorid = %s"
            cursor.execute(check_query, (sensorid,))
            result = cursor.fetchone()
            #self.connection.commit()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def check_actuatorid(self, actuatorid):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query = "SELECT * FROM actuators WHERE actuatorid = %s"
            cursor.execute(check_query, (actuatorid,))
            result = cursor.fetchone()
            #self.connection.commit()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error
    
    def check_user_exists(self, user_id):
        try:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result[0] > 0
        except mysql.connector.Error as error:
            print("Failed to check user existence: {}".format(error))
            return False

    def check_dashboard_exists(self, dashboard_id):
        try:
            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM dashboards WHERE id = %s"
            cursor.execute(query, (dashboard_id,))
            result = cursor.fetchone()
            return result[0] > 0
        except mysql.connector.Error as error:
            print("Failed to check dashboard existence: {}".format(error))
            return False

    def insert_sensors_to_dashboard(self, dashboard_id, sensor_id):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO dashboard_sensors (dashboard_id,sensor_id) VALUES (%s,%s)"""
            records_to_insert = (int(dashboard_id), int(sensor_id))
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_actuators_to_dashboard(self, dashboard_id, actuators_id):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO dashboard_actuators (dashboard_id,actuator_id) VALUES (%s,%s)"""
            records_to_insert = (int(dashboard_id), int(actuators_id))
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_sensors_by_user(self, user_id):
        try:
            cursor = self.connection.cursor()
            # Query to fetch sensor and actuator details with type
            query = """
                SELECT id, name, type
                FROM (
                    SELECT s.sensorid AS id, s.name, s.type
                    FROM sensors s
                    JOIN dashboard_sensors ds ON s.sensorid = ds.sensor_id
                    JOIN dashboards d ON ds.dashboard_id = d.id
                    WHERE d.user_id = %s
                ) AS sensor_result
                UNION
                SELECT id, name, type
                FROM (
                    SELECT a.actuatorid AS id, a.name, a.type
                    FROM actuators a
                    JOIN dashboard_actuators da ON a.actuatorid = da.actuator_id
                    JOIN dashboards d ON da.dashboard_id = d.id
                    WHERE d.user_id = %s
                ) AS actuator_result;
            """
            # Execute the query and fetch the results
            cursor.execute(query, (user_id, user_id))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to fetch data from MySQL table {}".format(error))
            return error

    def insert_positions_into_dashboard(self, positions, dashboard_id, user_id):
        try:
            cursor = self.connection.cursor()
            for item in positions:
                item_id = item['itemId']
                partition_id = item['partitionId']
                item_type = item['type']

                insert_query = """
                    INSERT INTO dashboard_items (dashboard_id, item_id, partition_id, item_type,user_id)
                    VALUES (%s, %s, %s, %s,%s)
                    ON DUPLICATE KEY UPDATE partition_id = VALUES(partition_id)
                """

                insert_data = (dashboard_id, item_id, partition_id, item_type, user_id)  # Using dashboard ID 1
                cursor.execute(insert_query, insert_data)

            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_positions(self, user_id, dashboard_id):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            select_query = """
                SELECT item_id, partition_id, item_type
                FROM dashboard_items
                WHERE user_id = %s AND dashboard_id = %s
            """  # Execute the query and fetch the results
            cursor.execute(select_query, (user_id, dashboard_id))
            result = cursor.fetchall()
            # data = []
            # Iterate over the rows and extract the required values
            data = [{'itemId': row[0], 'partitionId': row[1], 'type': row[2]} for row in result]
            # for row in result:
            #     item_id, partition_id, item_type = row
            #     data.append({
            #         'itemId': item_id,
            #         'partitionId': partition_id,
            #         'type': item_type
            #     })
            return data
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def delete_sensor(self, sensorid, type):
        try:
            cursor = self.connection.cursor()
            print(sensorid)
            print(type)
            sensorid = str(sensorid)
            if type == 'glass_break':
                type = "glass_sensor"

            if type == 'temperature':
                type = "temperature_sensor"

            # Delete from dashboard_items
            command = """DELETE FROM dashboard_items WHERE item_id = %s"""
            cursor.execute(command, (sensorid,))

            # Delete from dashboard_sensors
            command = """DELETE FROM dashboard_sensors WHERE sensor_id = %s"""
            cursor.execute(command, (sensorid,))

            # Delete from sensor data table
            command = f"DELETE FROM {type} WHERE sensorid = %s"
            cursor.execute(command, (sensorid,))

            # Delete from sensors table
            command = """DELETE FROM sensors WHERE sensorid = %s"""
            cursor.execute(command, (sensorid,))

            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to delete from MySQL table: {}".format(error))
            return error

    def delete_actuator(self, actuatorid, type):
        try:
            cursor = self.connection.cursor()
            print(actuatorid)
            print(type)
            actuatorid = str(actuatorid)

            # Delete from dashboard_items
            command = """DELETE FROM dashboard_items WHERE item_id = %s"""
            cursor.execute(command, (actuatorid,))

            # Delete from dashboard_actuators
            command = """DELETE FROM dashboard_actuators WHERE actuator_id = %s"""
            cursor.execute(command, (actuatorid,))

            # Delete from sensor data table
            command = f"DELETE FROM {type} WHERE actuatorid = %s"
            cursor.execute(command, (actuatorid,))

            # Delete from sensors table
            command = """DELETE FROM actuators WHERE actuatorid = %s"""
            cursor.execute(command, (actuatorid,))

            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to delete from MySQL table: {}".format(error))
            return error

    def get_actions(self, action_id):
        try:
            result = {}
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            select_query = """
                SELECT siren_id, siren_status, order_number
                FROM action_siren
                WHERE action_id = %s 
            """  # Execute the query and fetch the results
            cursor.execute(select_query, (action_id,))
            result['siren'] = cursor.fetchall()

            select_query = """
                SELECT switch_id, switch_status, order_number
                FROM action_switch
                WHERE action_id = %s 
            """  # Execute the query and fetch the results
            cursor.execute(select_query, (action_id,))
            result['switch'] = cursor.fetchall()

            select_query = """
                SELECT duration , order_number
                FROM delay 
                WHERE action_id = %s 
            """  # Execute the query and fetch the results
            cursor.execute(select_query, (action_id,))
            result['time'] = cursor.fetchall()

            return result


        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_push_alert(self, ):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query = "SELECT event_id, action_id FROM push_alert"
            cursor.execute(check_query)
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def delete_push_alert(self, action_id):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            cursor.execute("DELETE FROM push_alert WHERE action_id = %s", (action_id,))
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_events_by_user(self, userid):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query = """SELECT a.`event_id`,
                            GROUP_CONCAT(DISTINCT CONCAT( '[' , d.`door_sensor_id`, ',', d.`door_sensor_status`, ']'  )) AS event_door,
                            GROUP_CONCAT(DISTINCT CONCAT( '[', m.`motion_sensor_id`, ',', m.`motion_sensor_status` , ']' )) AS event_motion
                            FROM
                                `automation` a
                            JOIN
                                `event_door` d ON a.`event_id` = d.`event_id`
                            JOIN
                                `event_motion` m ON a.`event_id` = m.`event_id`
                            WHERE
                                a.`user_id` = %s
                                AND a.`event_id` IN (SELECT `event_id` FROM `automation` WHERE `user_id` = %s )
                            GROUP BY
                                a.`event_id`;
                            """
            cursor.execute(check_query, [str(userid), str(userid)], )
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_actions_by_user(self, userid):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query = """SELECT
                                    a.`action_id`,
                                    GROUP_CONCAT(DISTINCT CONCAT( '[',s.`siren_id`, ',', s.`siren_status`, ',', s.`order_number` , ']')) AS action_siren,
                                    GROUP_CONCAT(DISTINCT CONCAT('[', sw.`switch_id`, ',', sw.`switch_status`, ',', sw.`order_number`, ']')) AS action_switch,
                                    GROUP_CONCAT(DISTINCT CONCAT('[' , d.`duration`, ',', d.`order_number`, ']')) AS delay
                                FROM
                                    `automation` a
                                LEFT JOIN
                                    `action_siren` s ON a.`action_id` = s.`action_id`
                                LEFT JOIN
                                    `action_switch` sw ON a.`action_id` = sw.`action_id`
                                LEFT JOIN
                                    `delay` d ON a.`action_id` = d.`action_id`
                                WHERE
                                    a.`user_id` = %s
                                    AND a.`action_id` IN (SELECT `action_id` FROM `automation` WHERE `user_id` = %s )
                                GROUP BY
                                    a.`action_id`;
                                """
            cursor.execute(check_query, [str(userid), str(userid)])
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def check_insert_event_id(self, event_id, user_id):
        try:
            cursor = self.connection.cursor()
            check_query = "SELECT event_id FROM automation WHERE user_id = %s"
            cursor.execute(check_query, (user_id,))
            result = cursor.fetchone()
            if event_id in result:
                return False
            else:
                return True

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def check_insert_action_id(self, action_id, user_id):
        try:
            cursor = self.connection.cursor()
            check_query = "SELECT action_id FROM automation WHERE user_id = %s"
            cursor.execute(check_query, (user_id,))
            result = cursor.fetchone()
            if action_id in result:
                return False
            else:
                return True

        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_new_automation(self, event_id, action_id, user_id):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO automation (event_id, user_id, action_id) VALUES (%s, %s, %s)"
            # Data to be inserted
            data = (event_id, user_id, action_id)
            cursor.execute(insert_query, data)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_door_event(self, event_id, door_sensor_id, door_status):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO event_door (  event_id , door_sensor_id , door_sensor_status , triggerr ) VALUES (%s,%s,%s, %s) """
            records_to_insert = (event_id, door_sensor_id, door_status, 0)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_motion_event(self, event_id, motion_sensor_id, motion_status):
        try:
            cursor = self.connection.cursor()
            command = """INSERT INTO event_motion (event_id , motion_sensor_id , motion_sensor_status , triggerr ) VALUES ( %s,%s,%s,%s )"""
            records_to_insert = (event_id, motion_sensor_id, motion_status, 0)
            cursor.execute(command, records_to_insert)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error
     
    def get_lastest_status_test(self):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query =''' WITH LatestSiren AS (
                            SELECT actuatorid, status, date_time,
                                ROW_NUMBER() OVER (PARTITION BY actuatorid ORDER BY date_time DESC) AS rn
                            FROM siren
                        ),
                        LatestRelaySwitch AS (
                            SELECT actuatorid, status, date_time,
                                ROW_NUMBER() OVER (PARTITION BY actuatorid ORDER BY date_time DESC) AS rn
                            FROM relay_switch
                        ),
                        LatestMotionSensor AS (
                            SELECT sensorid, motion_status, date_time,
                                ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY date_time DESC) AS rn
                            FROM motion_sensor
                        ),
                        LatestGlassSensor AS (
                            SELECT sensorid, glass_status, date_time,
                                ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY date_time DESC) AS rn
                            FROM glass_sensor
                        ),
                        LatestDoorSensor AS (
                            SELECT sensorid, door_status, date_time,
                                ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY date_time DESC) AS rn
                            FROM door_sensor
                        )
                        SELECT 'siren' AS type, actuatorid AS id, status AS status, date_time
                        FROM LatestSiren
                        WHERE rn = 1
                        UNION ALL
                        SELECT 'switch' AS type, actuatorid AS id, status AS status, date_time
                        FROM LatestRelaySwitch
                        WHERE rn = 1
                        UNION ALL
                        SELECT 'motion_sensor' AS type, sensorid AS id, motion_status AS status, date_time
                        FROM LatestMotionSensor
                        WHERE rn = 1
                        UNION ALL
                        SELECT 'glass_sensor' AS type, sensorid AS id, glass_status AS status, date_time
                        FROM LatestGlassSensor
                        WHERE rn = 1
                        UNION ALL
                        SELECT 'door_sensor' AS type, sensorid AS id, door_status AS status, date_time
                        FROM LatestDoorSensor
                        WHERE rn = 1;

                            '''

            cursor.execute(check_query)
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error
    def get_events_and_action_by_user(self, userid):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query = """
        SELECT
            a.`event_id`,
            GROUP_CONCAT(DISTINCT CONCAT('[', d.`door_sensor_id`, ',', d.`door_sensor_status`, ']')) AS event_door,
            GROUP_CONCAT(DISTINCT CONCAT('[', m.`motion_sensor_id`, ',', m.`motion_sensor_status`, ']')) AS event_motion,
            a.`action_id`,
            GROUP_CONCAT(DISTINCT CONCAT('[', s.`siren_id`, ',', s.`siren_status`, ',', s.`order_number`, ']')) AS action_siren,
            GROUP_CONCAT(DISTINCT CONCAT('[', sw.`switch_id`, ',', sw.`switch_status`, ',', sw.`order_number`, ']')) AS action_switch,
            GROUP_CONCAT(DISTINCT CONCAT('[', dl.`duration`, ',', dl.`order_number`, ']')) AS delay
        FROM
            `automation` a
        LEFT JOIN
            `event_door` d ON a.`event_id` = d.`event_id`
        LEFT JOIN
            `event_motion` m ON a.`event_id` = m.`event_id`
        LEFT JOIN
            `action_siren` s ON a.`action_id` = s.`action_id`
        LEFT JOIN
            `action_switch` sw ON a.`action_id` = sw.`action_id`
        LEFT JOIN
            `delay` dl ON a.`action_id` = dl.`action_id`
        WHERE
            a.`user_id` = %s
            AND a.`event_id` IN (SELECT `event_id` FROM `automation` WHERE `user_id` = %s)
        GROUP BY
            a.`event_id`, a.`action_id`
    """
            cursor.execute(check_query, (userid, userid))
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_sensor_id_by_type(self, type):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query = "SELECT sensorid FROM sensors WHERE name =%s"
            cursor.execute(check_query, [type])
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_actuator_id_by_type(self, type):
        try:
            cursor = self.connection.cursor()
            # Check if the sensor ID already exists in the sensors table
            check_query = "SELECT actuatorid FROM actuators WHERE name = %s"
            cursor.execute(check_query, [type])
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    # Actions
    def insert_action_siren(self, order, action_id, siren_id, status):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO action_siren (action_id,siren_id,siren_status,order_number) VALUES (%s, %s, %s, %s)"
            # Data to be inserted
            data = (action_id, siren_id, status, order)
            cursor.execute(insert_query, data)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_action_switch(self, order, action_id, switch_id, status):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO action_switch (action_id,switch_id,switch_status,order_number ) VALUES (%s, %s, %s, %s)"
            # Data to be inserted
            data = (action_id, switch_id, status, order)
            cursor.execute(insert_query, data)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def insert_action_delay(self, order, action_id, duration):
        try:
            cursor = self.connection.cursor()
            insert_query = "INSERT INTO delay (action_id,duration,order_number) VALUES (%s, %s,%s)"
            # Data to be inserted
            data = (action_id, duration, order)
            cursor.execute(insert_query, data)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def delete_automation(self, event_id, action_id):
        try:
            cursor = self.connection.cursor()

            delete_event_door_query = "DELETE FROM event_door WHERE event_id = %s"
            cursor.execute(delete_event_door_query, (event_id,))

            delete_event_motion_query = "DELETE FROM event_motion WHERE event_id = %s"
            cursor.execute(delete_event_motion_query, (event_id,))

            delete_action_siren_query = "DELETE FROM action_siren WHERE action_id = %s"
            cursor.execute(delete_action_siren_query, (action_id,))

            delete_action_switch_query = "DELETE FROM action_switch WHERE action_id = %s"
            cursor.execute(delete_action_switch_query, (action_id,))

            delete_delay_query = "DELETE FROM delay WHERE action_id = %s"
            cursor.execute(delete_delay_query, (action_id,))

            delete_automation_query = "DELETE FROM automation WHERE event_id = %s AND action_id = %s"
            cursor.execute(delete_automation_query, (event_id, action_id))

            self.connection.commit()

        except mysql.connector.Error as error:
            print("Failed to delete from MySQL tables:", error)
            return error

    def insert_trigger(self, event_id, action_id):
        try:
            cursor = self.connection.cursor()

            trigger_door_name = f"{'door' + str(event_id)}"
            trigger_motion_name = f"{'motion' + str(event_id)}"

            door_query = f"""
            CREATE TRIGGER {trigger_door_name}
            AFTER INSERT ON door_sensor
            FOR EACH ROW
            BEGIN
            DECLARE event_triggerr INT;
            DECLARE event_id_param INT;
            DECLARE action_id_param INT;
            DECLARE door_triggerr INT;
            DECLARE motion_triggerr INT;
            DECLARE door_row_count INT;
            DECLARE motion_row_count INT;

            -- Get the event_id and action_id parameters
            SET event_id_param = %s; -- Replace <event_id_value> with the actual event ID parameter
            SET action_id_param = %s; -- Replace <action_id_value> with the actual action ID parameter
            -- Check if the inserted row is a door sensor
            IF NEW.sensorid IN (
            SELECT door_sensor_id
            FROM event_door
            WHERE event_id = event_id_param AND door_sensor_id = NEW.sensorid AND door_sensor_status = NEW.door_status
            ) THEN
            -- Update the trigger value for the corresponding event and action
            UPDATE event_door
            SET triggerr = 1
            WHERE event_id = event_id_param AND door_sensor_id = NEW.sensorid;
            END IF;
            
            
            -- Get the row counts for event_door and event_motion
            SELECT COUNT(*) INTO door_row_count
            FROM event_door
            WHERE event_id = event_id_param;

            SELECT COUNT(*) INTO motion_row_count
            FROM event_motion
            WHERE event_id = event_id_param;

            -- Check if all triggers (door, motion, and switch) are set to 1 for the given event and action
            SET door_triggerr = (
            SELECT MIN(triggerr)
            FROM event_door
            WHERE event_id = event_id_param
            GROUP BY event_id
            );

            SET motion_triggerr = (
            SELECT MIN(triggerr)
            FROM event_motion
            WHERE event_id = event_id_param
            GROUP BY event_id
            );

            -- If all triggers are set to 1
            IF (door_triggerr = 1 AND motion_triggerr = 1) OR (door_triggerr = 1 AND motion_row_count = 0) OR (motion_triggerr = 1 AND door_row_count = 0) THEN
            UPDATE event_door SET triggerr = 0 WHERE event_id = event_id_param;
            UPDATE event_motion SET triggerr = 0 WHERE event_id = event_id_param;
            INSERT INTO push_alert VALUES (event_id_param , action_id_param );

            END IF;
  
            END
            """
            door_data = (event_id, action_id)
            cursor.execute(door_query, door_data)
            motion_query = f"""
            CREATE TRIGGER {trigger_motion_name}
AFTER INSERT ON motion_sensor
FOR EACH ROW
BEGIN
  DECLARE event_triggerr INT;
  DECLARE event_id_param INT;
  DECLARE action_id_param INT;
  DECLARE door_triggerr INT;
  DECLARE motion_triggerr INT;
  DECLARE door_row_count INT;
  DECLARE motion_row_count INT;

  -- Get the event_id and action_id parameters
  SET event_id_param = %s ; -- Replace <event_id_value> with the actual event ID parameter
  SET action_id_param = %s ; -- Replace <action_id_value> with the actual action ID parameter
  
  -- Check if the inserted row is a motion sensor
  IF NEW.sensorid IN (
      SELECT motion_sensor_id
      FROM event_motion
      WHERE event_id = event_id_param AND motion_sensor_id = NEW.sensorid AND motion_sensor_status = NEW.motion_status
    ) THEN
    -- Update the trigger value for the corresponding event and action
    UPDATE event_motion
    SET triggerr = 1
    WHERE event_id = event_id_param AND motion_sensor_id = NEW.sensorid;
  END IF;

  -- Check if all triggers (door, motion, and switch) are set to 1 for the given event and action
  SET door_triggerr = (
    SELECT MIN(triggerr)
    FROM event_door
    WHERE event_id = event_id_param
    GROUP BY event_id
  );

  SET motion_triggerr = (
    SELECT MIN(triggerr)
    FROM event_motion
    WHERE event_id = event_id_param
    GROUP BY event_id
  );
  
  -- Get the row counts for event_door and event_motion
    SELECT COUNT(*) INTO door_row_count
    FROM event_door
    WHERE event_id = event_id_param;

    SELECT COUNT(*) INTO motion_row_count
    FROM event_motion
    WHERE event_id = event_id_param;


  -- If all triggers are set to 1, execute the Python script
  IF (door_triggerr = 1 AND motion_triggerr = 1) OR (door_triggerr = 1 AND motion_row_count = 0) OR (motion_triggerr = 1 AND door_row_count = 0) THEN

      UPDATE event_door SET triggerr = 0 WHERE event_id = event_id_param;
      UPDATE event_motion SET triggerr = 0 WHERE event_id = event_id_param;
      INSERT INTO push_alert VALUES (event_id_param , action_id_param );
  	


  END IF;
END
            """
            motion_data = (event_id, action_id)
            cursor.execute(motion_query, motion_data)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def delete_trigger(self, event_id):
        try:
            cursor = self.connection.cursor()
            trigger_door_name = 'door' + str(event_id)
            trigger_motion_name = 'motion' + str(event_id)
            query_door = f'DROP TRIGGER {trigger_door_name};'
            query_motion = f'DROP TRIGGER {trigger_motion_name};'

            cursor.execute(query_door)
            cursor.execute(query_motion)
            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_sensor_data_by_time(self, type, id, start_time, end_time):
        try:
            cursor = self.connection.cursor()
            check_query = f"SELECT * FROM {type} WHERE sensorid = %s AND date_time BETWEEN %s AND %s "

            cursor.execute(check_query, (id, start_time, end_time))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error

    def get_actuator_data_by_time(self, type, id, start_time, end_time):
        try:
            cursor = self.connection.cursor()
            check_query = f"SELECT * FROM {type} WHERE actuatorid = %s AND date_time BETWEEN %s AND %s "

            cursor.execute(check_query, (id, start_time, end_time))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table {}".format(error))
            return error
    
    def get_dashboard_by_user_id(self, user_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = '''
                SELECT 
                    d.id AS dashboard_id, 
                    d.name AS dashboard_name, 
                    u.id AS user_id, 
                    u.name AS user_name 
                FROM 
                    dashboards d
                JOIN 
                    users u ON d.user_id = u.id
                WHERE 
                    d.user_id = %s;
            '''
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to fetch data from MySQL table: {}".format(error))
            return error

    def get_latest_status(self, dashboard_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = '''
                WITH LatestSiren AS (
                    SELECT actuatorid, status, date_time,
                        ROW_NUMBER() OVER (PARTITION BY actuatorid ORDER BY date_time DESC) AS rn
                    FROM siren
                    JOIN dashboard_actuators ON siren.actuatorid = dashboard_actuators.actuator_id
                    WHERE dashboard_actuators.dashboard_id = %s
                ),
                LatestRelaySwitch AS (
                    SELECT actuatorid, status, date_time,
                        ROW_NUMBER() OVER (PARTITION BY actuatorid ORDER BY date_time DESC) AS rn
                    FROM relay_switch
                    JOIN dashboard_actuators ON relay_switch.actuatorid = dashboard_actuators.actuator_id
                    WHERE dashboard_actuators.dashboard_id = %s
                ),
                LatestMotionSensor AS (
                    SELECT sensorid, motion_status, date_time,
                        ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY date_time DESC) AS rn
                    FROM motion_sensor
                    JOIN dashboard_sensors ON motion_sensor.sensorid = dashboard_sensors.sensor_id
                    WHERE dashboard_sensors.dashboard_id = %s
                ),
                LatestGlassSensor AS (
                    SELECT sensorid, glass_status, date_time,
                        ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY date_time DESC) AS rn
                    FROM glass_sensor
                    JOIN dashboard_sensors ON glass_sensor.sensorid = dashboard_sensors.sensor_id
                    WHERE dashboard_sensors.dashboard_id = %s
                ),
                LatestDoorSensor AS (
                    SELECT sensorid, door_status, date_time,
                        ROW_NUMBER() OVER (PARTITION BY sensorid ORDER BY date_time DESC) AS rn
                    FROM door_sensor
                    JOIN dashboard_sensors ON door_sensor.sensorid = dashboard_sensors.sensor_id
                    WHERE dashboard_sensors.dashboard_id = %s
                )
                SELECT 'siren' AS type, actuatorid AS id, status AS status, date_time
                FROM LatestSiren
                WHERE rn = 1
                UNION ALL
                SELECT 'switch' AS type, actuatorid AS id, status AS status, date_time
                FROM LatestRelaySwitch
                WHERE rn = 1
                UNION ALL
                SELECT 'motion_sensor' AS type, sensorid AS id, motion_status AS status, date_time
                FROM LatestMotionSensor
                WHERE rn = 1
                UNION ALL
                SELECT 'glass_sensor' AS type, sensorid AS id, glass_status AS status, date_time
                FROM LatestGlassSensor
                WHERE rn = 1
                UNION ALL
                SELECT 'door_sensor' AS type, sensorid AS id, door_status AS status, date_time
                FROM LatestDoorSensor
                WHERE rn = 1;
            '''
            cursor.execute(query, (dashboard_id, dashboard_id, dashboard_id, dashboard_id, dashboard_id))
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as error:
            print("Failed to fetch data from MySQL table: {}".format(error))
            return error



        
    def get_user_dashboards_and_status(self, user_id):
        try:
            user_dashboards = []
            dashboards = self.get_dashboard_by_user_id(user_id)
            if isinstance(dashboards, Exception):
                return dashboards

            for dashboard in dashboards:
                dashboard_id = dashboard['dashboard_id']
                accessories_data = self.get_latest_status(dashboard_id)
                if isinstance(accessories_data, Exception):
                    return accessories_data
                positions = self.get_positions(user_id, dashboard_id)
                if isinstance(positions, Exception):
                    return positions

                accessories_with_positions = []
                for accessory in accessories_data:
                    position = next((pos for pos in positions if pos['itemId'] == accessory['id']), None)
                    accessories_with_positions.append({
                        'type': accessory['type'],
                        'id': accessory['id'],
                        'status': accessory['status'],
                        'date_time': accessory['date_time'],
                        'position': position["partitionId"] if position else None
                    })

                user_dashboards.append({
                    'dashboard': dashboard,
                    'accessories_data': accessories_with_positions
                })

            return user_dashboards
        
        except mysql.connector.Error as error:
            print("Failed to fetch data from MySQL table: {}".format(error))
            return error
        
    def insert_position_into_dashboard(self, item, dashboard_id, user_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            max_partition_id_query = """
                SELECT partition_id
                FROM dashboard_items 
                WHERE dashboard_id = %s AND user_id = %s
            """
            cursor.execute(max_partition_id_query, (dashboard_id, user_id))
            results = cursor.fetchall()
            
            max_partition_id = max(
                (int(pos['partition_id']) for pos in results if pos['partition_id']), 
                default=0
            )
            if max_partition_id == 0:
                next_partition_id = 0
            else:
                next_partition_id = max_partition_id + 1

            item_id = item['itemId']
            item_type = item['type']
            partition_id = item.get('partitionId', None)

            if partition_id is None:
                # prefix = "partitionId-" # dashboard_id
                partition_id = f"{next_partition_id}"
                next_partition_id += 1

            insert_query = """
                INSERT INTO dashboard_items (dashboard_id, item_id, partition_id, item_type, user_id)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE partition_id = VALUES(partition_id)
            """

            insert_data = (dashboard_id, item_id, partition_id, item_type, user_id)
            cursor.execute(insert_query, insert_data)

            self.connection.commit()
        except mysql.connector.Error as error:
            print("Failed to insert into MySQL table: {}".format(error))
            return error



def create_database_object():
    obj = Database(database_configuration['host'], database_configuration['port'], database_configuration['username'],
                   database_configuration['password'], database_configuration['database_name'] ,database_configuration['unix_socket'] )  # (host, 3306, "grafana", "pwd123", "grafanadb")
    obj.connect()
    return obj

def actions_of_acuators_to_list(siren, switch, time):
    list_of_Actions = []
    siren = str(siren).split('],[')
    siren = [x.replace('[', '').replace(']', '') for x in siren]
    siren = [x.split(',') for x in siren]

    switch = str(switch).split('],[')
    switch = [x.replace('[', '').replace(']', '') for x in switch]
    switch = [x.split(',') for x in switch]

    time = str(time).split('],[')
    time = [x.replace('[', '').replace(']', '') for x in time]
    time = [x.split(',') for x in time]

    for sirenAcrion in siren:
        if sirenAcrion[0] == 'None':
            break
        list_of_Actions.append([int(sirenAcrion[2]), 'siren', sirenAcrion[1], int(sirenAcrion[0])])
    for switchAcrion in switch:
        if switchAcrion[0] == 'None':
            break
        list_of_Actions.append([int(switchAcrion[2]), 'switch', switchAcrion[1], int(switchAcrion[0])])
    for t in time:
        if t[0] == 'None':
            break
        list_of_Actions.append([int(t[1]), 'delay', t[0] + ' sec', None])

    actions_dict = {item[0]: {"type": item[1], "id": item[3], "status": item[2]} for item in list_of_Actions}

    # Sort the dictionary by keys (the order)
    sorted_actions = sorted(actions_dict.items())

    # Convert the sorted dictionary back to a list of dictionaries
    sorted_data = [{"order": order, **values} for order, values in sorted_actions]

    # Convert the sorted data to JSON format
    # json_data = json.dumps(sorted_data, indent=2)

    # Print the JSON data
    return sorted_data

def str_to_data(data_string):
    if data_string == "None" or not data_string:
        return []
    
    data_list = []
    if '],[' in str(data_string):
        for item in data_string.split('],['):
            id, status = item.strip('[]').split(',')
            data_list.append({'id': int(id), 'status': status})
    elif ']' in data_string:
        id, status = str(data_string).replace('[', '').replace(']', '').split(',')
        data_list.append({'id': int(id), 'status': status})
    
    return data_list

def update_process_location(item_locations, object):
    object.insert_positions_into_dashboard(item_locations, session.get('dashboard_id'), session.get('user_id'))

class Controller:
    session = None
    def __init__(self, session):
        Controller.session = session
    
    def get_items_locations(self, object):
        result = object.get_positions(Controller.session.get('user_id'), Controller.session.get('dashboard_id'))
        result = sorted(result, key=lambda x: int(x['partitionId']))
        return result
    
    def get_data_from_dashboard(self, object):
        user_id = Controller.session.get('user_id')  # Assuming user ID is 1, replace with the actual user ID retrieval logic
        sensor_counts = {key: [] for key in sensor_types}
        result = object.get_sensors_by_user(user_id)
        data = [{'id': row[0], 'name': row[1], 'type': row[2]} for row in result]
        for row in data:
            if row['type'] != 'temp':
                sensor_counts[row['type']].append(row['id'])
        sensor_counts = {key: value for key, value in sensor_counts.items() if value}
        Controller.session.set("sensor_counts", sensor_counts)
        return sensor_counts
    
    def check_session_parameters(self):
        if 'first_load' not in Controller.session.data:
            Controller.session.set('first_load', False)
        if 'user_id' not in Controller.session.data or 'dashboard_id' not in Controller.session.data:
            print("The user not exist")
    
        obj = create_database_object()
        # obj.delete_actuator(4967, "relay_switch")
        # obj.delete_actuator(55, "siren")
        Controller.session.set('sensor_counts', self.get_data_from_dashboard(obj))
        Controller.session.set('item_locations', self.get_items_locations(obj))
        Controller.session.set('rooms_data', obj.get_user_dashboards_and_status(Controller.session.get('user_id')))
        # print(Controller.session.get("rooms_data"))
        if not Controller.session.get('item_locations'):
            counter = 0
            items = []
            for x in Controller.session.get('sensor_counts').keys():
                for n in Controller.session.get('sensor_counts')[x]:
                    items.append({'itemId': n, 'partitionId':  str(counter), 'type': str(x)})
                    counter += 1
            Controller.session.set('item_locations', items)
            update_process_location(Controller.session.get('item_locations'), obj)
        
        Controller.session.set('count', len(Controller.session.get('item_locations')))
        
        max_partition = max(int(d['partitionId']) for d in Controller.session.get('item_locations'))
        sensor_counts = Controller.session.get('sensor_counts')
        item_locations = Controller.session.get('item_locations')
        list_of_ids = []
        list_of_typeids = []
        
        for dic in item_locations:
            list_of_ids.append(dic['itemId'])
            list_of_typeids.append(dic['type'])
        
        for type in sensor_counts.keys():
            for id in sensor_counts[type]:
                if id not in list_of_ids:
                    max_partition += 1
                    Controller.session.get('item_locations').append(
                        {'itemId': id, 'partitionId':  str(max_partition), 'type': str(type)})
                    update_process_location(Controller.session.get('item_locations'), obj)
                    Controller.session.set('count', Controller.session.get('count') + 1)
        
        Controller.session.set('events_and_actions', obj.get_events_and_action_by_user(Controller.session.get('user_id')))
        Controller.session.set("items_status", obj.get_lastest_status_test())
        obj.disconnect()
    
    def start(self):
        self.check_session_parameters()
        if 'username' not in Controller.session.data:
            return {'redirect': '/login'}  # Example of redirect data
        
        count = Controller.session.get('count')
        partition_width = 200
        partition_height = 200
        padding = 50
        numPerRow = 4
        numItems = (count // numPerRow) + 1
        len_items = count  # Replace with the actual number of items
        
        door_event_data = []
        motion_event_data = []
        actions_data = []
        
        for i in range(len(Controller.session.get('events_and_actions'))):
            door_event_data.append(str_to_data(Controller.session.get('events_and_actions')[i][1]))
            motion_event_data.append(str_to_data(Controller.session.get('events_and_actions')[i][2]))
            actions_data.append({'actions_data': actions_of_acuators_to_list(Controller.session.get('events_and_actions')[i][4],
                                                                 Controller.session.get('events_and_actions')[i][5],
                                                                 Controller.session.get('events_and_actions')[i][6])})
        
        # This part aims to get all action in just one dict 
        # it should be like this: actions = {'sensors': {'sensor_name': [{'id': xx, 'status': xx}, ]}, 'acuators': {'acuator_name': [{'id': xx, 'status': xx}, ]}}}
        acuators_actions = {}
        acuators_actions["siren"] = []
        acuators_actions["delay"] = []
        acuators_actions["switch"] = []

        for action in actions_data:
            d = action['actions_data']
            for ele in d:
                if ele["type"] == "siren":
                    acuators_actions["siren"].append({'id': ele['id'], 'status': ele['status']})
                elif ele["type"] == "switch":
                    acuators_actions["switch"].append({'id': ele['id'], 'status': ele['status']})
                elif ele["type"] == "delay":
                    acuators_actions["delay"].append({'id': ele['id'], 'status': ele['status']})
    
        
        sensors_actions = {}
        sensors_actions['door'] = [door for door in door_event_data][0]
        sensors_actions['motion'] = [motion for motion in motion_event_data][0]
        actions = {'sensors': sensors_actions, 
               'acuators': acuators_actions}
        
        # Create a dictionary from items_location
        location_dict = {item['itemId']: item for item in Controller.session.get('item_locations')}

        combined_data = []

        for item in Controller.session.get("items_status"):
            item_type, item_id, status, timestamp = item
            if item_id in location_dict:
                combined_item = {
                    'type': item_type,
                    'itemId': item_id,
                    'status': status,
                    'timestamp': timestamp,
                    'partitionId': location_dict[item_id]['partitionId']
        }
                combined_data.append(combined_item)
            else:
                print(f"Item with ID {item_id} Item type ({item_type}) is missing in items_location list.")

        if 'username' in Controller.session.data:
            return {
                'rooms_data': Controller.session.get('rooms_data'),
                # 'events_and_actions': Controller.session.get('events_and_actions'),
                'items_data': combined_data,
                # 'actions': actions
            }
        else:
            return {'usnername': None}  # Example of redirect data
        
    # @staticmethod
    # def insert_reading(sensor_type, sensor_id, status):
    #     sensor_id = int(sensor_id)
    #     obj = create_database_object()
    #     current_time = datetime.now()
    #     if sensor_type == 'door_sensor':
    #         obj.insert_door_sensor_reading(sensor_id, status, current_time)
    #     elif sensor_type == 'motion_sensor':
    #         obj.insert_motion_sensor_reading(sensor_id, status, current_time)
    #     elif sensor_type == 'temperature':
    #         obj.insert_temperature_sensor_reading(sensor_id, status, status, current_time)
    #     elif sensor_type == 'polution':
    #         obj.insert_polution_sensor_reading(sensor_id, status, current_time)
    #     elif sensor_type == 'switch':
    #         obj.insert_relay_switch_reading(sensor_id, status, current_time)
    #     elif sensor_type == 'siren':
    #         obj.insert_siren_reading(sensor_id, status, current_time)
    #     elif sensor_type == 'smoke':
    #         obj.insert_smoke_sensor_reading(sensor_id, status, current_time)
        
    #     # Controller.session.set("items_status", obj.get_lastest_status())
    #     # print(Controller.session.get("items_status"))
        
    #     ## Remove the item with old status form the session 
    #     items_status = [tup for tup in Controller.session.get("items_status") if tup[1] != sensor_id]
        
    #     ## append the item with new status to the session 
    #     items_status.append((sensor_type, sensor_id, status, current_time))
    #     Controller.session.set("items_status", items_status)
        
    #     # print(Controller.session.get("items_status"))
    #     obj.disconnect()

    def general_insert(self, user_id, dashboard_id, dashboard_name, accessory_data = []):
        """
        if accessory_data is empty that means you need to just insert new room
        """
        obj = create_database_object()
        
        # Step 1: Validate user
        user_exists = obj.check_user_exists(user_id)
        if not user_exists:
            return "Invalid user"

        # Step 2: Check if the dashboard exists, if not, create it
        dashboard_exists = obj.check_dashboard_exists(dashboard_id)
        if not dashboard_exists:
            obj.insert_dashboard(dashboard_id, dashboard_name, user_id)
        
        # Step 3: Update the dashboard with sensors and actuators
        if len(accessory_data) != 0:
            for accessory in accessory_data:
                sensor_id = int(accessory['id'])
                sensor_type = accessory['type']
                status = accessory['status']
                name = accessory.get('name', "Unkown") # defalut Unkown
                cp = accessory.get('cp', "LoRa") # defalut LoRa
                current_time = datetime.now()
                position = accessory.get('position', None)

                if sensor_type in ['door_sensor', 'motion_sensor', 'temperature', 'polution', 'smoke']:
                    # Check if sensor exists
                    existing_sensor = obj.check_sensorid(sensor_id)
                    print(existing_sensor)
                    if not existing_sensor:
                        obj.insert_new_sensor(sensor_id, cp, sensor_type, name)
                    obj.insert_sensors_to_dashboard(dashboard_id, sensor_id)

                    # Insert the sensor reading
                    if sensor_type == 'door_sensor':
                        obj.insert_door_sensor_reading(sensor_id, status, current_time)
                    elif sensor_type == 'motion_sensor':
                        obj.insert_motion_sensor_reading(sensor_id, status, current_time)
                    elif sensor_type == 'temperature':
                        obj.insert_temperature_sensor_reading(sensor_id, status, status, current_time)
                    elif sensor_type == 'polution':
                        obj.insert_polution_sensor_reading(sensor_id, status, current_time)
                    elif sensor_type == 'smoke':
                        obj.insert_smoke_sensor_reading(sensor_id, status, current_time)

                elif sensor_type in ['switch', 'siren']:
                    # Check if actuator exists
                    existing_actuator = obj.check_actuatorid(sensor_id)
                    if not existing_actuator:
                        obj.insert_new_actuator(sensor_id, cp, sensor_type, name)
                    obj.insert_actuators_to_dashboard(dashboard_id, sensor_id)

                    # Insert the actuator reading
                    if sensor_type == 'switch':
                        obj.insert_relay_switch_reading(sensor_id, status, current_time)
                    elif sensor_type == 'siren':
                        obj.insert_siren_reading(sensor_id, status, current_time)
                # Insert position
                obj.insert_position_into_dashboard({
                    'itemId': sensor_id,
                    'type': sensor_type,
                    'partitionId': position
                }, dashboard_id, user_id)
        # Update session with latest status
        # items_status = Controller.session.get("items_status", [])
        # for accessory in accessory_data:
        #     sensor_id = int(accessory['id'])
        #     sensor_type = accessory['type']
        #     status = accessory['status']
        #     current_time = datetime.now()
        #     items_status = [tup for tup in items_status if tup[1] != sensor_id]
        #     items_status.append((sensor_type, sensor_id, status, current_time))
        # Controller.session.set("items_status", items_status)
        
        obj.disconnect()
        return "Success"

    
    @staticmethod
    def update_session():
        obj = create_database_object()
        Controller.session.set("items_status", obj.get_lastest_status())
        obj.disconnect()

    @staticmethod
    def check_item(type, id):
        is_exist = False
        items = Controller.session.get("items_status")
        if items and items != {}:
            for t, i, s, d in Controller.session.get("items_status"):
                if t == type and id == i:
                    is_exist = True
                    return is_exist
        return is_exist
    @staticmethod
    def check_item_totally(type, id, status):
        if Controller.check_item(type, id):
            if status in items_configuration["Items Status"][type]:
                return True
        return False
            
DROP DATABASE IF EXISTS home_kit;
CREATE DATABASE IF NOT EXISTS home_kit;

-- Use the 'home_kit' database
USE home_kit;

-- tables
-- Table: Accessories
CREATE TABLE Accessories (
    id varchar(255)  NOT NULL,
    name varchar(255)  NULL,
    position int  NOT NULL DEFAULT 0,
    accessory_key varchar(255) NULL,
    type_id bigint  UNSIGNED NOT NULL,
    communication_protocol_id bigint  UNSIGNED NOT NULL,
    room_id bigint  UNSIGNED NOT NULL,
    UNIQUE INDEX Accessories_ak_1 (id),
    CONSTRAINT Accessories_pk PRIMARY KEY (id)
);

-- Table: Actions
CREATE TABLE Actions (
    id bigint  UNSIGNED NOT NULL AUTO_INCREMENT,
    duration time  NOT NULL DEFAULT '0',
    sequence int  UNSIGNED NOT NULL,
    automation_id bigint  UNSIGNED NOT NULL,
    actuator_id varchar(255)  NOT NULL,
    CONSTRAINT Actions_pk PRIMARY KEY (id)
);

-- Table: Automations
CREATE TABLE Automations (
    id bigint  UNSIGNED NOT NULL AUTO_INCREMENT,
    execute_actions boolean  NOT NULL DEFAULT '0',
    time_from time  NULL,
    time_to time  NULL,
    CONSTRAINT Automations_pk PRIMARY KEY (id)
);

-- Table: CommunicationProtocol
CREATE TABLE CommunicationProtocol (
    id bigint  UNSIGNED NOT NULL AUTO_INCREMENT,
    name varchar(255)  NOT NULL,
    UNIQUE INDEX name (name),
    CONSTRAINT CommunicationProtocol_pk PRIMARY KEY (id)
);

INSERT INTO CommunicationProtocol (name) VALUES
('LoRa'),
('BLE'),
('WiFi');;

-- Table: Events
CREATE TABLE Events (
    id bigint  UNSIGNED NOT NULL AUTO_INCREMENT,
    status varchar(255)  NOT NULL,
    `trigger` boolean  NOT NULL,
    automation_id bigint  UNSIGNED NOT NULL,
    sensor_id varchar(255)  NOT NULL,
    CONSTRAINT Events_pk PRIMARY KEY (id)
);

-- Table: Permissions
CREATE TABLE Permissions (
    id bigint  NOT NULL AUTO_INCREMENT,
    name varchar(255)  NOT NULL,
    description varchar(255)  NOT NULL,
    UNIQUE INDEX name (name),
    CONSTRAINT id PRIMARY KEY (id)
);

INSERT INTO permissions (name, description) VALUES
('update', 'Allows updating existing records.'),
('edit', 'Allows editing records but not necessarily updating all fields.'),
('delete', 'Allows deleting records from the system.'),
('read', 'Allows reading or viewing records.');;

-- Table: Records
CREATE TABLE Records (
    value varchar(255)  NOT NULL,
    date_time datetime  NOT NULL,
    value_type varchar(255)  NOT NULL,
    battery_level int  NULL,
    category varchar(50)  NOT NULL COMMENT 'the type of value ex. status, distance, frequency.',
    accessory_id varchar(255)  NOT NULL
);

-- Table: RolePermissions
CREATE TABLE RolePermissions (
    role_id bigint  NOT NULL,
    permission_id bigint  NOT NULL
);

-- For Admin (assuming role_id = 1)
INSERT INTO RolePermissions (role_id, permission_id) VALUES
(1, 1),  -- update
(1, 2),  -- edit
(1, 3),  -- delete
(1, 4);  -- read

-- For Technician (assuming role_id = 2)
INSERT INTO RolePermissions (role_id, permission_id) VALUES
(2, 1),  -- update
(2, 2),  -- edit
(2, 4);  -- read

-- For User (assuming role_id = 3)
INSERT INTO RolePermissions (role_id, permission_id) VALUES
(3, 4);  -- read;

-- Table: Roles
CREATE TABLE Roles (
    id bigint  NOT NULL AUTO_INCREMENT,
    role_name varchar(255)  NOT NULL,
    UNIQUE INDEX role_name (role_name),
    CONSTRAINT id PRIMARY KEY (id)
);

INSERT INTO Roles (role_name) VALUES
('Admin'),
('Technician'),
('User');;

-- Table: Rooms
CREATE TABLE Rooms (
    id bigint  UNSIGNED NOT NULL AUTO_INCREMENT,
    room_name varchar(255)  NOT NULL,
    CONSTRAINT Rooms_pk PRIMARY KEY (id)
);
    --UNIQUE INDEX room_name (room_name),

-- Table: Types
CREATE TABLE Types (
    id bigint  UNSIGNED NOT NULL AUTO_INCREMENT,
    field varchar(255)  NOT NULL,
    type varchar(255)  NOT NULL,
    UNIQUE INDEX type (type),
    CONSTRAINT Types_pk PRIMARY KEY (id)
);

-- Insert sensor types
INSERT INTO Types (field, type) VALUES
('sensor', 'motion sensor'),
('sensor', 'door sensor'),
('sensor', 'glass break sensor');

-- Insert actuator types
INSERT INTO Types (field, type) VALUES
('actuator', 'siren'),
('actuator', 'lamp');;

-- Table: Users
CREATE TABLE Users (
    id bigint  UNSIGNED NOT NULL AUTO_INCREMENT,
    name varchar(255)  NOT NULL,
    password varchar(255)  NOT NULL,
    role_id bigint  NOT NULL,
    UNIQUE INDEX name (name),
    CONSTRAINT Users_pk PRIMARY KEY (id)
);

-- Table: UsersRooms
CREATE TABLE UsersRooms (
    user_id bigint  UNSIGNED NOT NULL,
    room_id bigint  UNSIGNED NOT NULL
);

-- views
-- View: AccessoriesDetails
CREATE VIEW AccessoriesDetails AS
SELECT 
    a.id AS id,
    a.name AS name,
    a.position AS position,
    a.accessory_key AS accessory_key,
    t.field AS field, 
    t.type AS type,
    cp.name AS communication_protocol_name,
    r.room_name AS room_name,
    r.id AS room_id
FROM 
    Accessories a
JOIN 
    Types t ON a.type_id = t.id
JOIN 
    CommunicationProtocol cp ON a.communication_protocol_id = cp.id
JOIN 
    Rooms r ON a.room_id = r.id;
-- View: AutomationDetails
CREATE VIEW AutomationDetails AS
SELECT 
    a.id AS automation_id,
    a.execute_actions AS execute_actions,
    a.time_from AS time_from,
    a.time_to AS time_to, 
    e.id AS event_id,
    e.status AS event_status,
    e.trigger AS event_trigger,
    aact.id AS action_id,
    aact.duration AS action_duration,
    aact.sequence AS action_sequence,
    e.sensor_id AS event_sensor_id,
    aact.actuator_id AS action_actuator_id
FROM 
    Automations a
LEFT JOIN 
    Events e ON a.id = e.automation_id
LEFT JOIN 
    Actions aact ON a.id = aact.automation_id;

-- View: AutomationWithAccessoriesDetails
CREATE VIEW AutomationWithAccessoriesDetails AS
-- Create or replace the view to include accessory details
SELECT 
    a.id AS automation_id,
    a.execute_actions AS execute_actions,
    a.time_from AS time_from, 
    a.time_to AS time_to,    
    
    -- Event details
    e.id AS event_id,
    e.status AS event_status,
    e.trigger AS event_trigger,
    
    -- Accessory details for the event sensor
    e.sensor_id AS event_sensor_id,
    ad_sensor.name AS event_sensor_name,
    ad_sensor.position AS event_sensor_position,
    ad_sensor.accessory_key AS event_sensor_key,
    ad_sensor.field AS event_sensor_field,
    ad_sensor.type AS event_sensor_type,
    ad_sensor.communication_protocol_name AS event_sensor_communication_protocol_name,
    ad_sensor.room_name AS event_sensor_room_name,

    -- Action details
    aact.id AS action_id,
    aact.duration AS action_duration,
    aact.sequence AS action_sequence,
    
    -- Accessory details for the action actuator
    aact.actuator_id AS action_actuator_id,
    ad_actuator.name AS action_actuator_name,
    ad_actuator.position AS action_actuator_position,
    ad_actuator.accessory_key AS action_actuator_key,
    ad_actuator.field AS action_actuator_field,
    ad_actuator.type AS action_actuator_type,
    ad_actuator.communication_protocol_name AS action_actuator_communication_protocol_name,
    ad_actuator.room_name AS action_actuator_room_name

FROM 
    Automations a
LEFT JOIN 
    Events e ON a.id = e.automation_id
LEFT JOIN 
    Actions aact ON a.id = aact.automation_id
LEFT JOIN 
    AccessoriesDetails ad_sensor ON e.sensor_id = ad_sensor.id
LEFT JOIN 
    AccessoriesDetails ad_actuator ON aact.actuator_id = ad_actuator.id;

-- View: AccessoryRecordsDetails
-- CREATE VIEW AccessoryRecordsDetails AS
-- SELECT 
--     a.id AS id,
--     a.name AS name,
--     a.position AS position,
--     a.accessory_key AS accessory_key,
--     a.field AS field,
--     a.type AS type,
--     a.communication_protocol_name AS accessory_communication_protocol_name,
--     a.room_name AS room_name,

--     -- Record details
--     r.value AS value,
--     r.category AS category,
--     r.date_time AS date_time,
--     r.value_type AS value_type,
--     r.battery_level AS battery_level
-- FROM 
--     Records r
-- JOIN 
--     AccessoriesDetails a ON r.accessory_id = a.id
-- WHERE 
--     r.accessory_id = @accessory_id; -- Replace @accessory_id with the specific accessory ID or use it as a parameter;

-- View: LatestAccessoryRecordsDetails
CREATE VIEW LatestAccessoryRecordsDetails AS
SELECT 
    a.id AS id,
    a.name AS name,
    a.position AS position,
    a.accessory_key AS accessory_key,
    a.field AS field,
    a.type AS type,
    a.communication_protocol_name AS communication_protocol_name,
    a.room_name AS room_name,

    -- Record details
    r.value AS value,
    r.category AS category,
    r.date_time AS date_time,
    r.value_type AS value_type,
    r.battery_level AS battery_level
FROM 
    Records r
JOIN 
    AccessoriesDetails a ON r.accessory_id = a.id
WHERE 
    r.date_time = (
        SELECT MAX(r2.date_time)
        FROM Records r2
        WHERE r2.accessory_id = r.accessory_id
    );

-- View: UserLatestAccessoryRecords
-- CREATE VIEW UserLatestAccessoryRecords AS
-- -- Get the latest accessory records details for a specific user
-- SELECT 
--     r.room_id,
--     r.room_name,
--     ar.id AS id,
--     ar.name AS name,
--     ar.position position,
--     ar.accessory_key AS accessory_key,
--     ar.field AS field,
--     ar.type AS type,
--     ar.communication_protocol_name AS communication_protocol_name,
    
--     -- Latest Record details
--     ar.value,
--     ar.category,
--     ar.date_time,
--     ar.value_type,
--     ar.battery_level

-- FROM 
--     LatestAccessoryRecordsDetails ar
-- JOIN 
--     RoomsWithAccessoriesForUser r ON ar.id = r.id
-- WHERE 
--     r.user_id = @user_id; -- Replace @user_id with the specific user ID or use it as a parameter;

-- -- View: UserAutomationDetails
-- CREATE VIEW UserAutomationDetails AS
-- SELECT 
--     a.id AS automation_id,
--     a.execute_actions AS execute_actions,
--     a.time_from AS time_from,
--     a.time_to AS time_to, 

--     -- Event details
--     e.id AS event_id,
--     e.status AS event_status,
--     e.trigger AS event_trigger,

--     -- Accessory details for the event sensor
--     e.sensor_id AS event_sensor_id,
--     ad_sensor.name AS event_sensor_name,
--     ad_sensor.position AS event_sensor_position,
--     ad_sensor.accessory_key AS event_sensor_key,
--     ad_sensor.field AS event_sensor_field,
--     ad_sensor.type AS event_sensor_type,
--     ad_sensor.communication_protocol_name AS event_sensor_communication_protocol_name,
--     ad_sensor.room_name AS event_sensor_room_name,

--     -- Action details
--     ac.id AS action_id,
--     ac.duration AS action_duration,
--     ac.sequence AS action_sequence,
    
--     -- Accessory details for the action actuator
--     ac.actuator_id AS action_actuator_id,
--     ad_actuator.name AS action_actuator_name,
--     ad_actuator.position AS action_actuator_position,
--     ad_actuator.accessory_key AS action_actuator_key,
--     ad_actuator.field AS action_actuator_field,
--     ad_actuator.type AS action_actuator_type,
--     ad_actuator.communication_protocol_name AS action_actuator_communication_protocol_name,
--     ad_actuator.room_name AS action_actuator_room_name,

--     -- Room details
--     r.id AS room_id,
--     r.room_name AS room_name

-- FROM 
--     Automations a
-- LEFT JOIN 
--     Events e ON a.id = e.automation_id
-- LEFT JOIN 
--     Actions ac ON a.id = ac.automation_id
-- LEFT JOIN 
--     AccessoriesDetails ad_sensor ON e.sensor_id = ad_sensor.id
-- LEFT JOIN 
--     AccessoriesDetails ad_actuator ON ac.actuator_id = ad_actuator.id
-- JOIN 
--     Rooms r ON ad_sensor.room_id = r.id OR ad_actuator.room_id = r.id
-- JOIN 
--     UsersRooms ur ON r.id = ur.room_id
-- WHERE 
--     ur.user_id = @user_id;

-- -- View: RoomsWithAccessoriesForUser
-- CREATE VIEW RoomsWithAccessoriesForUser AS
CREATE VIEW RoomsWithAccessoriesForUser AS
SELECT 
    -- user details
    u.id AS user_id,
    u.name AS user_name,
    
    r.id AS room_id,
    r.room_name AS room_name,
    
    -- Accessory details
    a.id AS accessory_id,
    a.name AS name,
    a.position AS position,
    a.accessory_key AS accessory_key,
    t.field AS field,
    t.type AS type,
    cp.name AS communication_protocol_name

FROM 
    Rooms r
JOIN 
    UsersRooms ur ON r.id = ur.room_id
JOIN 
    Accessories a ON r.id = a.room_id
JOIN 
    Types t ON a.type_id = t.id
JOIN 
    CommunicationProtocol cp ON a.communication_protocol_id = cp.id
JOIN
    Users u ON u.id = ur.user_id;

-- foreign keys
-- Reference: Records_Accessories (table: Records)
ALTER TABLE Records ADD CONSTRAINT Records_Accessories FOREIGN KEY Records_Accessories (accessory_id)
    REFERENCES Accessories (id)
    ON DELETE CASCADE;

-- Reference: RolePermissions_Permissions (table: RolePermissions)
ALTER TABLE RolePermissions ADD CONSTRAINT RolePermissions_Permissions FOREIGN KEY RolePermissions_Permissions (permission_id)
    REFERENCES Permissions (id);

-- Reference: RolePermissions_Roles (table: RolePermissions)
ALTER TABLE RolePermissions ADD CONSTRAINT RolePermissions_Roles FOREIGN KEY RolePermissions_Roles (role_id)
    REFERENCES Roles (id);

-- Reference: Users_Roles (table: Users)
ALTER TABLE Users ADD CONSTRAINT Users_Roles FOREIGN KEY Users_Roles (role_id)
    REFERENCES Roles (id);

-- Reference: accessories_communication_protocol_id_foreign (table: Accessories)
ALTER TABLE Accessories ADD CONSTRAINT accessories_communication_protocol_id_foreign FOREIGN KEY accessories_communication_protocol_id_foreign (communication_protocol_id)
    REFERENCES CommunicationProtocol (id);

-- Reference: accessories_room_id_foreign (table: Accessories)
ALTER TABLE Accessories ADD CONSTRAINT accessories_room_id_foreign FOREIGN KEY accessories_room_id_foreign (room_id)
    REFERENCES Rooms (id);

-- Reference: accessories_type_id_foreign (table: Accessories)
ALTER TABLE Accessories ADD CONSTRAINT accessories_type_id_foreign FOREIGN KEY accessories_type_id_foreign (type_id)
    REFERENCES Types (id);

-- Reference: actions_actuator_id_foreign (table: Actions)
ALTER TABLE Actions ADD CONSTRAINT actions_actuator_id_foreign FOREIGN KEY actions_actuator_id_foreign (actuator_id)
    REFERENCES Accessories (id);

-- Reference: actions_automation_id_foreign (table: Actions)
ALTER TABLE Actions ADD CONSTRAINT actions_automation_id_foreign FOREIGN KEY actions_automation_id_foreign (automation_id)
    REFERENCES Automations (id);

-- Reference: events_automation_id_foreign (table: Events)
ALTER TABLE Events ADD CONSTRAINT events_automation_id_foreign FOREIGN KEY events_automation_id_foreign (automation_id)
    REFERENCES Automations (id);

-- Reference: events_sensor_id_foreign (table: Events)
ALTER TABLE Events ADD CONSTRAINT events_sensor_id_foreign FOREIGN KEY events_sensor_id_foreign (sensor_id)
    REFERENCES Accessories (id);

-- Reference: usersrooms_room_id_foreign (table: UsersRooms)
ALTER TABLE UsersRooms ADD CONSTRAINT usersrooms_room_id_foreign FOREIGN KEY usersrooms_room_id_foreign (room_id)
    REFERENCES Rooms (id);

-- Reference: usersrooms_user_id_foreign (table: UsersRooms)
ALTER TABLE UsersRooms ADD CONSTRAINT usersrooms_user_id_foreign FOREIGN KEY usersrooms_user_id_foreign (user_id)
    REFERENCES Users (id);


--DELIMITER //

--CREATE TRIGGER update_events_trigger
--AFTER INSERT ON Records
--FOR EACH ROW
--BEGIN
--    -- Update the trigger column in the Events table if the status matches the inserted value
--    UPDATE Events 
--    SET `trigger` = 1
--    WHERE 
--        status = NEW.value AND 
--        sensor_id = NEW.accessory_id;
--END //

--DELIMITER ;

--DELIMITER //

--CREATE TRIGGER update_events_trigger_on_update
--AFTER UPDATE ON Records
--FOR EACH ROW
--BEGIN
--    -- Update the trigger column in the Events table if the status matches the updated value
--    UPDATE Events 
--   SET `trigger` = 1
--    WHERE 
--        status = NEW.value AND 
--        sensor_id = NEW.accessory_id;
--END //

--DELIMITER ;


DELIMITER //

CREATE OR REPLACE TRIGGER update_events_trigger
AFTER INSERT ON Records
FOR EACH ROW
BEGIN
    DECLARE v_time_from TIME;
    DECLARE v_time_to TIME;
    DECLARE v_current_time TIME;
    DECLARE v_automation_id BIGINT UNSIGNED;
    DECLARE v_trigger_value BOOLEAN;
    
    -- Get the current time
    SET v_current_time = CURTIME();
    
    -- Find all matching events for the sensor_id
    BEGIN
        DECLARE done INT DEFAULT FALSE;
        DECLARE cur CURSOR FOR
            SELECT e.automation_id, a.time_from, a.time_to
            FROM Events e
            JOIN Automations a ON e.automation_id = a.id
            WHERE e.sensor_id = NEW.accessory_id;
        DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
        
        OPEN cur;
        
        read_loop: LOOP
            FETCH cur INTO v_automation_id, v_time_from, v_time_to;
            IF done THEN
                LEAVE read_loop;
            END IF;
            
            -- Determine the trigger value
            IF v_time_from IS NULL OR v_time_to IS NULL THEN
                SET v_trigger_value = 1;
            ELSE
                SET v_trigger_value = 
                    CASE WHEN (v_time_from <= v_time_to AND v_current_time BETWEEN v_time_from AND v_time_to) OR
                              (v_time_from > v_time_to AND (v_current_time >= v_time_from OR v_current_time <= v_time_to))
                         THEN 1
                         ELSE 0
                    END;
            END IF;
            
            -- Update the Events table
            UPDATE Events 
            SET `trigger` = v_trigger_value
            WHERE automation_id = v_automation_id AND sensor_id = NEW.accessory_id AND status = NEW.value;
        END LOOP;
        
        CLOSE cur;
    END;
END //

DELIMITER ;



DELIMITER //

CREATE TRIGGER after_event_update
AFTER UPDATE ON Events
FOR EACH ROW
BEGIN
    DECLARE event_count INT;
    DECLARE triggered_count INT;

    -- Count the total number of events with the same automation_id
    SELECT COUNT(*) INTO event_count
    FROM Events
    WHERE automation_id = NEW.automation_id;

    -- Count the number of events with trigger set to 1 for the same automation_id
    SELECT COUNT(*) INTO triggered_count
    FROM Events
    WHERE automation_id = NEW.automation_id AND `trigger` = 1;

    -- Update the execute_actions column in the Automations table
    IF event_count = triggered_count THEN
        UPDATE Automations
        SET execute_actions = TRUE
        WHERE id = NEW.automation_id;
    ELSE
        UPDATE Automations
        SET execute_actions = FALSE
        WHERE id = NEW.automation_id;
    END IF;
END //

DELIMITER ;

-- update position after delete
--  DELIMITER $$

-- CREATE PROCEDURE rearrange_positions(IN roomId INT)
-- BEGIN
--     DECLARE pos INT DEFAULT -1;

--     UPDATE accessories
--     SET pos = (@pos := @pos + 1)
--     WHERE room_id = roomId
--     ORDER BY position;
-- END$$

-- DELIMITER ;

-- DELIMITER $$

-- CREATE TRIGGER rearrange_positions_after_delete
-- AFTER DELETE ON accessories
-- FOR EACH ROW
-- BEGIN
--     -- Call the stored procedure to rearrange positions
--     CALL rearrange_positions(OLD.room_id);
-- END$$

-- DELIMITER ;


-- End of file.
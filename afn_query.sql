CREATE SCHEMA military_schema;
SET search_path TO military_schema;


CREATE TABLE ArmOfService (
    arm_of_service_id SERIAL PRIMARY KEY,
    arm_of_service_name VARCHAR(100) NOT NULL
);

CREATE TABLE Headquarters (
    headquarters_id SERIAL PRIMARY KEY,
    headquarters_name VARCHAR(100) NOT NULL,
    arm_of_service_id INT REFERENCES ArmOfService(arm_of_service_id)
);

CREATE TABLE Directorates (
    directorate_id SERIAL PRIMARY KEY,
    directorate_name VARCHAR(100) NOT NULL,
    headquarters_id INT REFERENCES Headquarters(headquarters_id)
);

CREATE TABLE Teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    directorate_id INT REFERENCES Directorates(directorate_id)
);

CREATE TABLE Course (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL
);

CREATE TABLE Rank (
    rank_id SERIAL PRIMARY KEY,
    rank_name VARCHAR(100) NOT NULL
);

CREATE TABLE Personnel (
    personnel_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    rank_id INT REFERENCES Rank(rank_id),
    course_id INT REFERENCES Course(course_id),
    directorate_id INT REFERENCES Directorates(directorate_id),
    arm_of_service_id INT REFERENCES ArmOfService(arm_of_service_id)  -- Foreign Key if needed
);

CREATE TABLE Appointment (
    appointment_id SERIAL PRIMARY KEY,
    appointment_name VARCHAR(100) NOT NULL,
    personnel_id INT REFERENCES Personnel(personnel_id),
    headquarters_id INT REFERENCES Headquarters(headquarters_id)
);

CREATE TABLE PersonnelTeams (
    personnel_id INT REFERENCES Personnel(personnel_id),
    team_id INT REFERENCES Teams(team_id),
    PRIMARY KEY (personnel_id, team_id)
);

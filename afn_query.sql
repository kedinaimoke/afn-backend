CREATE TABLE headquarters (
    headquarter_id SERIAL PRIMARY KEY,
    headquarter_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE directorates (
    directorate_id SERIAL PRIMARY KEY,
    headquarter_id INT REFERENCES headquarters(headquarter_id) ON DELETE CASCADE,
    directorate_name VARCHAR(255) NOT NULL
);

CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    directorate_id INT REFERENCES directorates(directorate_id) ON DELETE CASCADE,
    team_name VARCHAR(255) NOT NULL
);

CREATE TABLE staff (
    staff_id SERIAL PRIMARY KEY,
    service_number VARCHAR(15) UNIQUE NOT NULL,
    official_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    last_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    headquarter_id INT REFERENCES headquarters(headquarter_id) ON DELETE SET NULL, -- a staff can only belong to one headquarter at a time
	directorate_id INT REFERENCES directorates(directorate_id) ON DELETE SET NULL -- a staff can only belong to one directorate at a time
);

CREATE TABLE staff_teams (
    staff_id INT REFERENCES staff(staff_id) ON DELETE CASCADE,
    team_id INT REFERENCES teams(team_id) ON DELETE CASCADE,
    PRIMARY KEY (staff_id, team_id)
);

-- CREATE EXTENSION system_stats;

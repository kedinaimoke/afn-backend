INSERT INTO headquarters (headquarter_name)
VALUES ('Defence Space Administration');

INSERT INTO directorates (headquarter_id, directorate_name)
VALUES
((SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), 'Directorate of Communication Satellite'),
((SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), 'Directorate of Cybersecurity'),
((SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), 'Directorate of Earth Observation');

INSERT INTO teams (directorate_id, team_name)
VALUES
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'Software Development Team'),
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'EMail/Website/Social Media'),
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'DSTV/CCTV/Multimedia Display');

INSERT INTO staff (service_number, official_name, first_name, middle_name, last_name, phone_number, email, headquarter_id, directorate_id)
VALUES (
    'CIV/123/12344',
    'JQ Doe',
    'John',
    'Quest',
    'Doe',
    '1234567890',
    'jd@mail.com',
    (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'),
    (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')
);

INSERT INTO staff_teams (staff_id, team_id)
VALUES 
    ((SELECT staff_id FROM staff WHERE service_number = 'CIV/123/12344'),
    (SELECT team_id FROM teams WHERE team_name = 'Software Development Team')),

	 ((SELECT staff_id FROM staff WHERE service_number = 'CIV/123/12344'),
     (SELECT team_id FROM teams WHERE team_name = 'DSTV/CCTV/Multimedia Display')
);

-- ALTER TABLE staff
-- ALTER COLUMN service_number TYPE VARCHAR(20);

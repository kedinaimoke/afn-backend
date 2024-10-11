INSERT INTO headquarters (headquarter_name)
VALUES ('Defence Space Administration');

INSERT INTO directorates (headquarter_id, directorate_name)
VALUES
((SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), 'Directorate of Communication Satellite'),
((SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), 'Directorate of Cybersecurity'),
((SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), 'Directorate of Earth Observation');

INSERT INTO teams (directorate_id, team_name)
VALUES
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'EMAIL/WEBSITE/SOCIAL MEDIA'),
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'INVERTER/SERVERS/SYSTEM REPAIRS'),
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'IP PHONE/ACCESS CONTROL/SCANNING MACHINE'),
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'DSTV/CCTV/MULTI MEDIA DISPLAY'),
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'INTERNET'),
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'SOFTWARE DEVELOPMENT TEAM')
((SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'), 'SECRETARIAT/REGISTRY');

INSERT INTO staff (service_number, official_name, first_name, middle_name, last_name, phone_number, email, headquarter_id, directorate_id)
VALUES
('DSA/CIV/0008', 'J Alawiye', 'Joshua', '', 'Alawiye', '', 'J.TEMMY4EVER@YAHOO.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0022', 'DA Jekennu', 'Daniel', 'A.', 'Jekennu', '', 'DANIELJEKENNU@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0030', 'OC Oroge', 'Olaoluwa', 'C.', 'Oroge', '', 'O.OROGE@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0031F', 'EC Nkechinyere', 'Eneh', 'Chioma', 'Nkechinyere', '', NULL, (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0034', 'AM Yerima', 'Abdullahi', 'M.', 'Yerima', '', 'YERIMAABDULLAHI@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0036', 'OD Ali', 'Odiba', 'David', 'Ali', '', 'ODIBAALI@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0042', 'N Musa', 'Nasiru', '', 'Musa', '', NULL, (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0049', 'AA Bashir', 'Ahmed', 'A.', 'Bashir', '', 'BASHMAD872@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0055', 'NI Mukhtar', 'Najeeb', 'Ibrahim', 'Mukhtar', '', 'MNIDAMBATTA@HOTMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0060', 'AO', 'Abdullahi', '', 'Othman', '', 'OTHY1059@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0067', 'MS Bello', 'Mu’awiya', 'Sali', 'Bello', '', 'MUAWEEYASB1960@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0075', 'YD Aluke', 'Yahaya', 'David', 'Aluke', '', NULL, (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0076', 'YS Magashi', 'Yahaya', 'Shehu', 'Magashi', '', 'YAHAYA843@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0083', 'IH Ijoma', 'Ijomanta', 'Hyacinth', 'Ijoma', '', 'HYCINTHIJOMANTA@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0091', 'IM Guri', 'Ibrahim', 'Muhammed', 'Guri', '', NULL, (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0093', 'AD Idris', 'Abdulhakeem', 'D.', 'Idris', '', 'ABDULHAKEEMIDRIZ@YAHOO.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0098', 'R Samuel', 'Rotimi', '', 'Samuel', '', NULL, (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0116', 'O Demien', 'Onoberhie', '', 'Demien', '', NULL, (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0139F', 'EM Etta', 'Edem', 'Mary', 'Etta', '', 'MARYEDEM94@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0147', 'AM Khalifa', 'Abdulhameed', 'M.', 'Khalifa', '', 'MAHMOODABDULHAMEED62@YAHOO.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0185', 'S Abdullahi', 'Shehu', '', 'Abdullahi', '', 'SHEHUMIDO@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0201', 'DS Shadrach', 'Danjuma', 'S.', 'Shadrach', '', 'SHADRACH.DANJUMA@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0213', 'AI Aderibigbe', 'Adeniji', 'Ismaeel', 'Aderibigbe', '', 'HERDEYNIG@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0215', 'SB Bala', 'Samaila', 'Bilal', 'Bala', '', 'BILALSAMAILABALA@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0245', 'UO Udofia', 'Ubong', 'Okon', 'Udofia', '', 'UDOFIAUBONG10@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0254', 'AA Bukar', 'Abubakar', 'A.', 'Bukar', '', 'ABBAABDUL850@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0273', 'OT Olabode', 'Omoleye', 'T.', 'Olabode', '', 'TOMIOMOLEYE@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0286', 'LE Seun', 'Lucas', 'Emmanuel', 'Seun', '', 'ELUCAS052@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0299', 'HM Saghir', 'Hussaini', 'M.', 'Saghir', '', 'ENGRHMSAGHIR@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0304F', 'M Maryam', 'Muhammad', '', 'Maryam', '', 'MRIAMDKYOM@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0322', 'AA Ashiru', 'Ashiru', 'Abdulrashid', 'Ashiru', '', 'ASHEERKUDAN@ICLOUD.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0332', 'UM Inuwa', 'Usman', 'Mohammed', 'Inuwa', '', 'USMANINUWA77@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0350', 'L Auwal', 'Lawal', '', 'Auwal', '', 'LAWALAUWAL550@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0351', 'OT Precious', 'Olawale', 'Timilehin', 'Precious', '', 'TIMIOLAWALE@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0355', 'ON Opeyemi', 'Odunbaku', 'Nurudeen', 'Opeyemi', '', 'NURUDEENODUN25@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0218', 'AE Abiodun', 'Adebanjo', 'Emmanuel', 'Abiodun', '', 'EMMACULATE789@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0317', 'IP Ngozi', 'Ikeh', 'Paul', 'Ngozi', '', 'PAULIKEH99@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/JNR/CIV/0050', 'AF Onyekachi', 'Agbo', 'Francis', 'Onyekachi', '', 'FONYEKACHI7@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0280', 'OC Chigozie', 'Okoro', 'Caleb', 'Chigozie', '', 'OKOROCALEB25@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite')),
('DSA/CIV/0326', 'MO Wilfred', 'Mustapha', 'Oluwatobi', 'Wilfred', '', 'ORION4585@GMAIL.COM', (SELECT headquarter_id FROM headquarters WHERE headquarter_name = 'Defence Space Administration'), (SELECT directorate_id FROM directorates WHERE directorate_name = 'Directorate of Communication Satellite'));

INSERT INTO staff_teams (staff_id, team_id)
VALUES 
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0022'), (SELECT team_id FROM teams WHERE team_name = 'DSTV/CCTV/MULTI MEDIA DISPLAY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0030'), (SELECT team_id FROM teams WHERE team_name = 'INVERTER/SERVERS/SYSTEM REPAIRS')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0031F'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0034'), (SELECT team_id FROM teams WHERE team_name = 'INTERNET')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0036'), (SELECT team_id FROM teams WHERE team_name = 'IP PHONE/ACCESS CONTROL/SCANNING MACHINE')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0042'), (SELECT team_id FROM teams WHERE team_name = 'SECRETARIAT/REGISTRY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0049'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0055'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0060'), (SELECT team_id FROM teams WHERE team_name = 'INVERTER/SERVERS/SYSTEM REPAIRS')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0067'), (SELECT team_id FROM teams WHERE team_name = 'INTERNET')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0075'), (SELECT team_id FROM teams WHERE team_name = 'DSTV/CCTV/MULTI MEDIA DISPLAY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0076'), (SELECT team_id FROM teams WHERE team_name = 'DSTV/CCTV/MULTI MEDIA DISPLAY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0083'), (SELECT team_id FROM teams WHERE team_name = 'INTERNET')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0091'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0093'), (SELECT team_id FROM teams WHERE team_name = 'IP PHONE/ACCESS CONTROL/SCANNING MACHINE')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0098'), (SELECT team_id FROM teams WHERE team_name = 'TRAINING OFFICERS')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0116'), (SELECT team_id FROM teams WHERE team_name = 'SECRETARIAT/REGISTRY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0139F'), (SELECT team_id FROM teams WHERE team_name = 'INVERTER/SERVERS/SYSTEM REPAIRS')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0147'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0185'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0201'), (SELECT team_id FROM teams WHERE team_name = 'TRAINING OFFICERS')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0213'), (SELECT team_id FROM teams WHERE team_name = 'IP PHONE/ACCESS CONTROL/SCANNING MACHINE')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0215'), (SELECT team_id FROM teams WHERE team_name = 'DSTV/CCTV/MULTI MEDIA DISPLAY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0245'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0254'), (SELECT team_id FROM teams WHERE team_name = 'INTERNET')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0273'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0286'), (SELECT team_id FROM teams WHERE team_name = 'DSTV/CCTV/MULTI MEDIA DISPLAY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0299'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0304F'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0322'), (SELECT team_id FROM teams WHERE team_name = 'INVERTER/SERVERS/SYSTEM REPAIRS')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0332'), (SELECT team_id FROM teams WHERE team_name = 'INTERNET')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0350'), (SELECT team_id FROM teams WHERE team_name = 'INVERTER/SERVERS/SYSTEM REPAIRS')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0351'), (SELECT team_id FROM teams WHERE team_name = 'INTERNET')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0355'), (SELECT team_id FROM teams WHERE team_name = 'INTERNET')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0218'), (SELECT team_id FROM teams WHERE team_name = 'SECRETARIAT/REGISTRY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0317'), (SELECT team_id FROM teams WHERE team_name = 'TRAINING OFFICERS')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/JNR/CIV/0050'), (SELECT team_id FROM teams WHERE team_name = 'SECRETARIAT/REGISTRY')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0280'), (SELECT team_id FROM teams WHERE team_name = 'SOFTWARE DEVELOPMENT TEAM')),
    ((SELECT staff_id FROM staff WHERE service_number = 'DSA/CIV/0326'), (SELECT team_id FROM teams WHERE team_name = 'SECRETARIAT/REGISTRY'));

-- ALTER TABLE staff;
-- ALTER COLUMN service_number TYPE VARCHAR(20);

import sqlite3

# Initialize db.sqlite3 connection
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

# Create tables matching bincom_test schema
cursor.executescript("""
CREATE TABLE IF NOT EXISTS agentname (
  name_id INTEGER PRIMARY KEY AUTOINCREMENT,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  email TEXT DEFAULT NULL,
  phone CHAR(13) NOT NULL,
  pollingunit_uniqueid INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS announced_lga_results (
  result_id INTEGER PRIMARY KEY AUTOINCREMENT,
  lga_name TEXT NOT NULL,
  party_abbreviation CHAR(4) NOT NULL,
  party_score INTEGER NOT NULL,
  entered_by_user TEXT NOT NULL,
  date_entered TEXT NOT NULL,
  user_ip_address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS announced_pu_results (
  result_id INTEGER PRIMARY KEY AUTOINCREMENT,
  polling_unit_uniqueid TEXT NOT NULL,
  party_abbreviation CHAR(4) NOT NULL,
  party_score INTEGER NOT NULL,
  entered_by_user TEXT NOT NULL,
  date_entered TEXT NOT NULL,
  user_ip_address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lga (
  uniqueid INTEGER PRIMARY KEY AUTOINCREMENT,
  lga_id INTEGER NOT NULL,
  lga_name TEXT NOT NULL,
  state_id INTEGER NOT NULL,
  lga_description TEXT,
  entered_by_user TEXT NOT NULL,
  date_entered TEXT NOT NULL,
  user_ip_address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS polling_unit (
  uniqueid INTEGER PRIMARY KEY AUTOINCREMENT,
  polling_unit_id INTEGER NOT NULL,
  ward_id INTEGER NOT NULL,
  lga_id INTEGER NOT NULL,
  uniquewardid INTEGER,
  polling_unit_number TEXT,
  polling_unit_name TEXT,
  polling_unit_description TEXT,
  lat TEXT,
  long TEXT,
  entered_by_user TEXT,
  date_entered TEXT,
  user_ip_address TEXT
);
""")

# Seed Sample LGAs and Polling Units for Assessment Views
cursor.executescript("""
INSERT OR IGNORE INTO lga (uniqueid, lga_id, lga_name, state_id, lga_description, entered_by_user, date_entered, user_ip_address)
VALUES 
(1, 1, 'Aniocha North', 25, '', 'admin', '2011-04-27 09:49:55', '127.0.0.1'),
(2, 2, 'Aniocha South', 25, '', 'admin', '2011-04-27 09:58:33', '127.0.0.1'),
(3, 8, 'Ethiope East', 25, '', 'admin', '2011-04-27 13:54:57', '127.0.0.1');

INSERT OR IGNORE INTO polling_unit (uniqueid, polling_unit_id, ward_id, lga_id, polling_unit_number, polling_unit_name, entered_by_user)
VALUES 
(8, 1, 1, 8, 'PU001', 'Otorho Primary School', 'Bose'),
(9, 2, 1, 8, 'PU002', 'Town Hall Center', 'Joseph'),
(10, 3, 1, 8, 'PU003', 'Market Square Unit', 'Kingsley');

INSERT OR IGNORE INTO announced_pu_results (result_id, polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address)
VALUES 
(111, '8', 'PDP', 802, 'Bose', '2011-04-26 15:44:03', '127.0.0.1'),
(112, '8', 'DPP', 719, 'Bose', '2011-04-26 15:44:03', '127.0.0.1'),
(113, '8', 'ACN', 416, 'Bose', '2011-04-26 15:44:03', '127.0.0.1'),
(114, '8', 'PPA', 939, 'Bose', '2011-04-26 15:44:03', '127.0.0.1'),
(117, '9', 'PDP', 285, 'Joseph', '2011-04-26 16:20:49', '127.0.0.1'),
(118, '9', 'DPP', 1254, 'Joseph', '2011-04-26 16:20:49', '127.0.0.1');
""")

conn.commit()
conn.close()
print("Tables and election data created successfully!")
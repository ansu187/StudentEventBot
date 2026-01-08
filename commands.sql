


CREATE TABLE Events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL,
    creator_name TEXT,  -- For display purposes
    name TEXT,
    start_time TEXT,
    end_time TEXT,
    ticket_sell_time TEXT,
    location TEXT,
    description_fi TEXT,
    description_en TEXT,
    ticket_link TEXT,
    other_link TEXT,
    accessibility_fi TEXT,
    accessibility_en TEXT,
    price REAL,
    dc TEXT,
    accepted BOOLEAN DEFAULT 0,
    tags TEXT,
    stage INTEGER,
    FOREIGN KEY (creator_id) REFERENCES Users(id)
);

INSERT INTO Events_new (
    id, creator_id, creator_name, name, start_time, end_time, ticket_sell_time, location,
    description_fi, description_en, ticket_link, other_link,
    accessibility_fi, accessibility_en, price, dc, accepted, tags, stage
)
SELECT 
    e.id, u.id AS creator_id, u.username AS creator_name, e.name, e.start_time, e.end_time, e.ticket_sell_time, e.location,
    e.description_fi, e.description_en, e.ticket_link, e.other_link,
    e.accessibility_fi, e.accessibility_en, e.price, e.dc, e.accepted, e.tags, e.stage
FROM Events AS e
JOIN Users AS u ON e.creator = u.username;


CREATE TRIGGER UpdateCreatorName
AFTER UPDATE OF username ON Users
BEGIN
    UPDATE Events
    SET creator_name = NEW.username
    WHERE creator_id = OLD.id;
END;

UPDATE Events SET start_time = "2025-02-27 21:00:00", end_time = "2025-02-27 22:00:00" WHERE id = "213";

UPDATE Events SET stage = 50 WHERE id = 252;

UPDATE Users SET user_type = 4 WHERE username = "ansu187";
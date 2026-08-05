#============================================================================
# Database schema and seed data configuration
#============================================================================


#----------------------------------------------------------------------------
# Table definitions
#----------------------------------------------------------------------------
# Define your tables with a name, a schema and optional seed/sample data,
# using this format, and then add the tables to the Table Registry below:
#
# class TableName:
#     NAME      = "name"
#     SCHEMA    = "CREATE TABLE name (...)"
#     SEED_DATA = "INSERT INTO name (...)" or None
#----------------------------------------------------------------------------

class userTable:

    NAME = "user"

    SCHEMA = """
        CREATE TABLE user (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            forename        TEXT NOT NULL,
            surname     TEXT NOT NULL,
            username        TEXT NOT NULL, 
            reportedHunts   INT DEFAULT 0,
            bio    TEXT,
            passwordHash         TEXT NOT NULL,
            ghostHunter             BOOLEAN, 
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """

    SEED_DATA = """
        INSERT INTO user (forename, surname, username, reportedHunts, bio, passwordHash, ghostHunter)
        VALUES
            ("Sharon", "Paratrack", "sharontracksghosts", 4, "Hey! I'm Sharon Paratrack. A fun fact about me: I can smell ghosts!", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", false),
            ("Hugh", "Findghost", "hughfindsghosts", 2, "Hey! I'm Hugh Findghost. A fun fact about me: I know the best ghost locations!", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", false),
            ("Ryan", " Banishspirit", "ryanbanishesspirits", 0, "I'm not entirely sure what I'm doing here but I keep finding ghosts in new world.", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", false),
            ("John", "Ghosthunter", "JohnGhosthunter", 1, "Hey! I'm John Ghostunter. After my creepy uncles disapearence, I've been fascinated in hunting ghosts.", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252", false)
            
    """



class messagesTable:

    NAME = "message"

    SCHEMA = """
        CREATE TABLE message (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            sender     INTEGER NOT NULL REFERENCES user(id),
            body     TEXT NOT NULL,
            sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """

    SEED_DATA = """
        INSERT INTO message (sender, body)
        VALUES
           (2, "Where's the milk?"),
           (1, "For the last time this isn't a New World, it's just an abandoned building"),
           (1, "But I met someones nice uncle :(" )
    """

class reportedHuntTable:

    NAME = "reportedHunt"

    SCHEMA = """
        CREATE TABLE reportedHunt (
            id      INTEGER PRIMARY KEY AUTOINCREMENT ,
            reportedBy    ID REFERENCES user(id) ,
            details             TEXT NOT NULL,  
            dateReported TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            location TEXT NOT NULL
        )
    """
    # Reported by
    # string

    SEED_DATA = """
        INSERT INTO reportedHunt (reportedBy, details, location)
        VALUES
            (3, "I was sleeping, and then I saw my uncle, Dan Ghosthunter, standing in my window. My house is on the 2nd Floor, surrounded by trees, so it had to be a ghost 👻. Then, the next day, they found my dear Uncle Dan dead from head trauma after a significant fall outside my house. The ghost teleported him as punishment. And to think, he just got out of jail for stalking too. Poor Dan. He didn't deserve this.", "10 Ridgeview Court"),
            (1, "TEST DATA PLEASE IGNORE", "test")

    """

class participantTable:

    NAME = "participant"

    SCHEMA = """
        CREATE TABLE participant (
           ghostHunterID        INTEGER NOT NULL REFERENCES user(id),
            huntID      INTEGER NOT NULL REFERENCES reportedHunt(id)
        )
    """

    SEED_DATA = """
        INSERT INTO participant (ghostHunterID, huntID)
        VALUES
            (0,0),
            (1,0),
            (2,0),
            (3,0)
    """



#----------------------------------------------------------------------------
# Table registry
#----------------------------------------------------------------------------
# Register all of your tables by adding them to the TABLES list here:
#
# TABLES = [
#     Table1Name,
#     Table2Name,
#     etc.
# ]
#
# Note: The table order is important - Create the tables that have
# foreign keys *after* the tables they link to have been created
#----------------------------------------------------------------------------

TABLES = [
    userTable,
    participantTable,
    messagesTable,
    reportedHuntTable
    # Add more tables here...
]


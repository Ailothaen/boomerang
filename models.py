# Standard libs
import datetime, os, sqlite3

class Database():
    """
    Class representing the database and its methods to interact with it.
    """
    def __init__(self):
        # Checking if the DB already exists; if not, create the schema
        if not os.path.exists("data/boomerang.sqlite3"):
            self.create_db()

        self.base = sqlite3.connect("data/boomerang.sqlite3")
        self.base.row_factory = sqlite3.Row # having column names! cf https://stackoverflow.com/a/18788347
        self.cursor = self.base.cursor()


    def create_db(self):
        """
        Function creating the DB if it does not exist
        """
        base = sqlite3.connect("data/boomerang.sqlite3")
        cursor = base.cursor()
        cursor.execute('CREATE TABLE "people" ("id" INTEGER NOT NULL UNIQUE, "name" TEXT, "timezone" TEXT, PRIMARY KEY("id"))')
        cursor.execute('CREATE TABLE "reminders" ("id" INTEGER NOT NULL UNIQUE, "author" INTEGER NOT NULL, "date_creation" INTEGER NOT NULL, "date_next" INTEGER NOT NULL, "recurrence" TEXT, "recurrence_limit" INTEGER, "text" TEXT, "color" INTEGER, PRIMARY KEY("id" AUTOINCREMENT))')
        cursor.execute('CREATE INDEX "i_people_id" ON "people" ("id" ASC)')
        cursor.execute('CREATE INDEX "i_reminders_id" ON "reminders" ("id" ASC)')
        base.commit()
        base.close()


    def select_reminder(self, id):
        """
        Returns a specific reminder.

        Args:
            id (int): Reminder ID

        Returns:
            dict: Reminder
        """
        self.cursor.execute("SELECT * FROM reminders WHERE id=?", (id,))
        r = self.cursor.fetchone()
        if r is None:
            raise IndexError("Reminder does not exist in database")
        else:
            return r


    def count_reminders(self):
        """
        Counts reminders.

        Returns:
            int: Reminder count
        """
        self.cursor.execute("SELECT COUNT(*) AS len FROM reminders")
        return self.cursor.fetchone()["len"]


    def select_reminders_user(self, author):
        """
        Returns all the reminders belonging to someone.

        Args:
            author (discord.User): User requesting the select

        Returns:
            list: All reminders belonging to someone. Can be empty.
        """
        self.cursor.execute("SELECT * FROM reminders WHERE author=?", (author.id,))
        return self.cursor.fetchall()


    def select_user_timezone(self, author):
        """
        Returns the timezone of someone.

        Args:
            author (discord.User): User requesting the select

        Returns:
            str: IANA timezone
        """
        self.cursor.execute("SELECT * FROM people WHERE id=?", (author.id,))

        try:
            return self.cursor.fetchone()["timezone"]
        except TypeError:
            raise IndexError("User does not exist in database")


    def select_reminders_now(self):
        """
        Returns all the reminders that must be fired now.

        Returns:
            list: List of reminders. Can be empty.
        """
        now = datetime.datetime.now(datetime.timezone.utc).replace(second=59, microsecond=0)
        self.cursor.execute("SELECT * FROM reminders WHERE date_next < ?", (int(datetime.datetime.timestamp(now)),))

        reminders = []
        for reminder in self.cursor.fetchall():
            reminders.append({
                "id": reminder["id"],
                "author": reminder["author"],
                "date_creation": reminder["date_creation"],
                "text": reminder["text"],
                "color": reminder["color"]
            })
        return reminders


    def insert_reminder(self, author, date_creation, date_next, text, color, recurrence=None, recurrence_limit=None):
        """
        Insert a new reminder in database

        Args:
            author (discord.User): Reminder author
            date_creation (datetime): When the reminder was created
            date_next (datetime): When is the next occurrence of the reminder
            text (str): Text of the reminder
            color (Discord Color object): Color associated with the reminder
            recurrence (str, optional): Expression ("4d", "3h"...) telling how often the reminder should be fired. If None, no recurrence.
            recurrence_limit (int, optional): For recurrence-enabled events: how many times the reminder should be fired. If None, no limit. (Not implemented yet)
        """
        self.cursor.execute("INSERT INTO reminders (author, date_creation, date_next, recurrence, recurrence_limit, text, color) VALUES (?, ?, ?, ?, ?, ?, ?)", (author.id, datetime.datetime.timestamp(date_creation), datetime.datetime.timestamp(date_next), recurrence, recurrence_limit, text, color))
        self.base.commit()


    def update_reminder_recurrence(self, id, date_next, recurrence_limit):
        """
        Updates a reminder to set its next occurrence.

        Args:
            id (int): Reminder ID
            date_next (datetime.datetime): Datetime object of the next reminder datetime 
            recurrence_limit (int): How many times should the reminder be fired again. (Not implemented yet)
        """
        self.cursor.execute("UPDATE reminders SET date_next=?, recurrence_limit=? WHERE id=?", (int(date_next.timestamp()), recurrence_limit, id))
        self.base.commit()


    def update_user_timezone(self, author, tz):
        """
        Updates the timezone of someone in the database.
        If user does not exist, creates it as well

        Args:
            author (Discord User/Member object): Requestor
            tz (pytz timezone): pytz timezone
        """
        self.cursor.execute("SELECT * FROM people WHERE id=?", (author.id,))

        if self.cursor.fetchone() is not None:
            self.cursor.execute("UPDATE people SET name=?, timezone=? WHERE id=?", ((author.name+'#'+str(author.discriminator)), str(tz), author.id))
        else:
            self.cursor.execute("INSERT INTO people VALUES (?, ?, ?)", (author.id, author.name+'#'+str(author.discriminator), str(tz)))
        
        self.base.commit()


    def delete_reminder(self, id):
        """
        Delete a reminder from the database.

        Args:
            id (int): Reminder ID
        """
        self.cursor.execute("DELETE FROM reminders WHERE id=?", (id,))
        self.base.commit()

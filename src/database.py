import sqlite3
import os
import json
from datetime import datetime
from enum import Enum, unique


USER_LAST_INTERACTION = "last_interaction"
USER_FOLLOWING_STATUS = "following_status"
FILENAME_INTERACTED_USERS = "interacted_users.json"


class Database:
    def __init__(self, username):
        if username is None:
            print(COLOR_FAIL + "No username, thus the script won't get access to interacted users and sessions data" +
                  COLOR_ENDC)
            return

        if not os.path.exists(username):
            os.makedirs(my_username)
        self.conn = sqlite3.connect(f'{username}/data.db')
        self.c = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS interaction
                        (username text, last_interaction text, following_status text)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS session
                (
                    total_interactions real, successful_interactions real,
                    total_followed, real, total_likes real, total_unfollowed real,
                    start_time text, end_time text, followers real, interacted text
                )''')
        self.conn.commit()

    def get_interacted(self, username):
        t = (username,)
        self.c.execute('SELECT * from interaction where username = ? ', t)
        return self.c.fetchone()

    def add_interacted(self, username, last_interaction, following_status):
        t = (username, last_interaction, following_status)
        self.c.execute('INSERT INTO interaction VALUES(?,?,?)', t)
        self.conn.commit()

    def check_user_was_interacted(self, username):
        t = (username,)
        self.c.execute('SELECT 1 from interaction where username = ? ', t)
        return self.c.fetchone()

    def check_user_was_interacted_recently(self, username):
        user = self.get_interacted(username)
        if user is None:
            return False

        last_interaction = datetime.strptime(user[USER_LAST_INTERACTION], '%Y-%m-%d %H:%M:%S.%f')
        return datetime.now() - last_interaction <= timedelta(days=3)

    def get_following_status(self, username):
        user = self.get_interacted(username)
        return user is None and FollowingStatus.NONE or FollowingStatus[user[USER_FOLLOWING_STATUS].upper()]

    def add_interacted_user(self, username, followed=False, unfollowed=False):
        user = self.get_interacted(username)
        following_status = FollowingStatus.NONE.name.lower()
        if followed:
            following_status = FollowingStatus.FOLLOWED.name.lower()
        elif unfollowed:
            following_status = FollowingStatus.UNFOLLOWED.name.lower()

        self.add_interacted(username, str(datetime.now()), following_status)

@unique
class FollowingStatus(Enum):
    NONE = 0
    FOLLOWED = 1
    UNFOLLOWED = 2

# if __name__ == "__main__":
#     db = Database('streetsmtl')
#     interacted_users_path = 'streetsmtl' + "/" + FILENAME_INTERACTED_USERS
#     if os.path.exists(interacted_users_path):
#             with open(interacted_users_path) as json_file:
#                 interacted_users = json.load(json_file)
#     db.c.execute("SELECT * FROM interaction where username='cvagphoto'")
#     print(db.c.fetchone())
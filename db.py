import os
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash

def get_connection():
    dsn = os.environ.get('DATABASE_URL')
    return psycopg2.connect(dsn)

def get_user(username):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT * FROM Users WHERE UserName = %s
            """, (username,))
            user = cur.fetchone()
    return user

def get_user_id(username):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT UserID FROM Users WHERE UserName = %s
            """, (username,))
            user = cur.fetchone()
    return user['userid'] if user else None

def get_tweets():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT Users.UserName, Tweets.Content, Tweets.Timestamp
                FROM Tweets
                JOIN Users ON Tweets.UserID = Users.UserID
                ORDER BY Tweets.Timestamp DESC
            """)
            tweets = cur.fetchall()
    return tweets

def create_user(username, email, password):
    with get_connection() as conn:
        with conn.cursor() as cur:
            hashed_password = generate_password_hash(password)  # パスワードをハッシュ化
            cur.execute("""
                INSERT INTO Users (UserName, Email, HashedPassword)
                VALUES (%s, %s, %s)
                """, (username, email, hashed_password))
            conn.commit()

def post_tweet(user_id, tweet_text):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Tweets (UserID, Content)
                VALUES (%s, %s)
                """, (user_id, tweet_text))
            conn.commit()

def get_timeline_tweets(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT tweets.userid, tweets.content, tweets.timestamp
                FROM tweets
                WHERE tweets.userid IN (
                    SELECT follows.followedid FROM follows WHERE follows.followerid = %s
                )
                ORDER BY tweets.timestamp DESC
            """, (user_id,))
            tweets = cur.fetchall()
    return tweets

def search_tweets(search_string):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT * FROM Tweets
                WHERE Content LIKE %s
            """, ('%' + search_string + '%',))
            results = cur.fetchall()
            
def get_following_tweets(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT * FROM tweets
                where userid IN ( 
                    SELECT followedid FROM follows WHERE followerid = %s
                ) or userid = %s  
                ORDER BY timestamp DESC
            """, (user_id, user_id))
            return cur.fetchall()


            
def search_users(query):
    with get_connection() as con:  
        with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT * FROM Users
                WHERE username LIKE %s
            """, ('%' + query + '%',))
            return cur.fetchall()

def search_tweets(query):
    with get_connection() as con:  
        with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT * FROM Tweets
                WHERE content LIKE %s
            """, ('%' + query + '%',))
            return cur.fetchall()
        
def delete_tweet(tweet_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM Tweets
                WHERE TweetID = %s
            """, (tweet_id,))
            conn.commit()

def get_user_tweets(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT * FROM Tweets
                WHERE UserID = %s
                ORDER BY Timestamp DESC
            """, (user_id,))
            return cur.fetchall()

def like_tweet(user_id, tweet_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Likes (UserID, TweetID)
                VALUES (%s, %s)
                """, (user_id, tweet_id))
            conn.commit()

def count_likes(tweet_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM Likes
                WHERE TweetID = %s
            """, (tweet_id,))
            likes = cur.fetchone()[0]
    return likes

def follow_user(follower_id, followed_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO follows (followerid, followedid)
                VALUES (%s, %s)
                """, (follower_id, followed_id))
            conn.commit()

def post_reply(user_id, tweet_id, reply_text):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Replies (UserID, TweetID, Content)
                VALUES (%s, %s, %s)
                """, (user_id, tweet_id, reply_text))
            conn.commit()

def get_replies(tweet_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT Replies.*, Users.UserName FROM Replies
                JOIN Users ON Replies.UserID = Users.UserID
                WHERE TweetID = %s
                ORDER BY Timestamp DESC
            """, (tweet_id,))
            return cur.fetchall()


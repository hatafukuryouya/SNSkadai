from flask import Flask, render_template, request, redirect, url_for,session
from werkzeug.security import check_password_hash
import db, string, random

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = db.get_user(username)
    if user and check_password_hash(user['hashedpassword'], password): 
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template('top.html', error='ログインに失敗しました。')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url('/'))
    user_id = db.get_user_id(session['username'])
    tweets = db.get_following_tweets(user_id)
    if request.method == 'POST':
        tweet_text = request.form.get('tweet-text')
        if tweet_text:  # ツイートのテキストが空でないことを確認
            db.post_tweet(user_id, tweet_text)
            return redirect(url_for('dashboard'))
    return render_template('dashboard.html', username=session['username'], tweets=tweets)





@app.route('/')
def top():
    tweets = db.get_tweets()
    return render_template('top.html', tweets=tweets)

@app.route('/post_tweet', methods=['POST'])
def post_tweet():
    if 'username' not in session:
        return redirect(url_for('login'))
    tweet_text = request.form.get('tweet-text')
    user_id = db.get_user_id(session['username'])
    db.post_tweet(user_id, tweet_text)
    return redirect(url_for('top'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        db.create_user(username, email, password)
        return redirect(url_for('top'))
    else:
        return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('top'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_type = request.form.get('searchType')
        search_query = request.form.get('searchQuery')
        results = None  
        if search_type == 'users':
            results = db.search_users(search_query)
        elif search_type == 'tweets':
            results = db.search_tweets(search_query)
        return render_template('search_results.html', results=results)
    else:
        return render_template('search_results.html')
    
@app.route('/delete_tweet/<int:tweet_id>', methods=['POST'])
def delete_tweet(tweet_id):
    db.delete_tweet(tweet_id)
    return redirect(url_for('dashboard'))

def get_user_tweets(user_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT * FROM Tweets
                WHERE UserID = %s
                ORDER BY Timestamp DESC
            """, (user_id,))
            return cur.fetchall()

@app.route('/my_tweets', methods=['GET'])
def my_tweets():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = db.get_user_id(session['username'])
    tweets = db.get_user_tweets(user_id)
    return render_template('my_tweets.html', tweets=tweets)

@app.route('/like_tweet/<int:tweet_id>', methods=['POST'])
def like_tweet(tweet_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = db.get_user_id(session['username'])
    db.like_tweet(user_id, tweet_id)
    return redirect(url_for('dashboard'))

@app.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    follower_id = db.get_user_id(session['username'])
    db.follow_user(follower_id, user_id)
    return redirect(url_for('dashboard'))

@app.route('/reply/<int:tweet_id>', methods=['POST'])
def post_reply(tweet_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    reply_text = request.form.get('reply-text')
    user_id = db.get_user_id(session['username'])
    db.post_reply(user_id, tweet_id, reply_text)
    return redirect(url_for('dashboard'))

@app.route('/replies/<int:tweet_id>', methods=['GET'])
def get_replies(tweet_id):
    replies = db.get_replies(tweet_id)
    return render_template('replies.html', replies=replies)


if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session
import db, string, random

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

@app.route('/')
def top():
    tweets = db.get_tweets()
    return render_template('top.html', tweets=tweets)

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

@app.route('/tweet', methods=['POST'])
def tweet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tweet_text = request.form.get('tweet-text')
    db.post_tweet(session['user_id'], tweet_text)
    return redirect(url_for('top'))

if __name__ == '__main__':
    app.run(debug=True)

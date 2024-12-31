from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)  # Text message content
    attachment = db.Column(db.String(200), nullable=True)  # Path to attachment


# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username exists
        if User.query.filter_by(username=username).first():
            return "Username already exists. Choose another."

        # Create user
        hashed_password = generate_password_hash(password)
        print("normal",str(password))
        print("hash",str(hashed_password))
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('chat'))

        return "Invalid credentials. Try again."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    selected_user_id = request.args.get('selected_user_id', type=int)

    if request.method == 'POST' and selected_user_id:
        content = request.form.get('message')
        attachment = request.files.get('attachment')
        attachment_path = None

        # Handle attachment
        if attachment and attachment.filename != '':
            filename = secure_filename(attachment.filename)
            attachment_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            attachment.save(attachment_path)
            # Replace backslashes with forward slashes
            attachment_path = attachment_path.replace('\\', '/')

        # Save message
        new_message = Message(
            sender_id=user_id,
            receiver_id=selected_user_id,
            content=content,
            attachment=attachment_path
        )
        db.session.add(new_message)
        db.session.commit()

    # Fetch users and messages
    users = User.query.all()
    messages = []
    if selected_user_id:
        messages = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == selected_user_id)) |
            ((Message.sender_id == selected_user_id) & (Message.receiver_id == user_id))
        ).order_by(Message.id).all()

    return render_template('chat.html', users=users, messages=messages, selected_user_id=selected_user_id, current_user_id=user_id)

if __name__ == '__main__':
    with app.app_context():
     
        db.create_all()  # Recreates the tables based on the current models
    app.run(debug=True)


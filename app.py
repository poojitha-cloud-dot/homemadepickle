from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import uuid

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_12345'

# ================== TEMPORARY LOCAL DATA ==================

users = {
    'poojitha': generate_password_hash('Poojitha@1234')
}

orders = []

products = {
    'non_veg_pickles': [
        {'id': 1, 'name': 'Chicken Pickle', 'weights': {'250': 600, '500': 1200, '1000': 1800}},
        {'id': 2, 'name': 'Fish Pickle', 'weights': {'250': 200, '500': 400, '1000': 800}},
        {'id': 3, 'name': 'Gongura Mutton', 'weights': {'250': 400, '500': 800, '1000': 1600}},
        {'id': 4, 'name': 'Mutton Pickle', 'weights': {'250': 400, '500': 800, '1000': 1600}},
        {'id': 5, 'name': 'Gongura Prawns', 'weights': {'250': 600, '500': 1200, '1000': 1800}},
        {'id': 6, 'name': 'Chicken Pickle (Gongura)', 'weights': {'250': 350, '500': 700, '1000': 1050}}
    ],

    'veg_pickles': [
        {'id': 7, 'name': 'Traditional Mango Pickle', 'weights': {'250': 150, '500': 280, '1000': 500}},
        {'id': 8, 'name': 'Zesty Lemon Pickle', 'weights': {'250': 120, '500': 220, '1000': 400}},
        {'id': 9, 'name': 'Tomato Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 10, 'name': 'Kakarakaya Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 11, 'name': 'Chintakaya Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 12, 'name': 'Spicy Pandu Mirchi', 'weights': {'250': 130, '500': 240, '1000': 450}}
    ],

    'snacks': [
        {'id': 13, 'name': 'Banana Chips', 'weights': {'250': 300, '500': 600, '1000': 800}},
        {'id': 14, 'name': 'Crispy Aam-Papad', 'weights': {'250': 150, '500': 300, '1000': 600}},
        {'id': 15, 'name': 'Crispy Chekka Pakodi', 'weights': {'250': 50, '500': 100, '1000': 200}},
        {'id': 16, 'name': 'Boondhi Acchu', 'weights': {'250': 300, '500': 600, '1000': 900}},
        {'id': 17, 'name': 'Chekkalu', 'weights': {'250': 350, '500': 700, '1000': 1000}},
        {'id': 18, 'name': 'Ragi Laddu', 'weights': {'250': 350, '500': 700, '1000': 1000}},
        {'id': 19, 'name': 'Dry Fruit Laddu', 'weights': {'250': 500, '500': 1000, '1000': 1500}},
        {'id': 20, 'name': 'Kara Boondi', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 21, 'name': 'Gavvalu', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 22, 'name': 'Kaju Chikki', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 23, 'name': 'Peanut Chikki', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 24, 'name': 'Rava Laddu', 'weights': {'250': 250, '500': 500, '1000': 750}}
    ]
}

# ================== AUTH ROUTES ==================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username not in users:
            return render_template('login.html', error="User not found")

        if check_password_hash(users[username], password):
            session['logged_in'] = True
            session['username'] = username
            session.setdefault('cart', [])
            return redirect(url_for('home'))

        return render_template('login.html', error="Invalid password")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if username in users:
            return render_template('signup.html', error="Username already exists")

        users[username] = generate_password_hash(password)

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================== PRODUCT PAGES ==================

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('home.html')


@app.route('/non_veg_pickles')
def non_veg_pickles():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('non_veg_pickles.html', products=products['non_veg_pickles'])


@app.route('/veg_pickles')
def veg_pickles():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('veg_pickles.html', products=products['veg_pickles'])


@app.route('/snacks')
def snacks():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('snacks.html', products=products['snacks'])


# ================== CART ==================

@app.route('/cart')
def cart():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('cart.html')


# ================== CHECKOUT ==================

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':

        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        payment_method = request.form.get('payment')

        cart_data = request.form.get('cart_data', '[]')
        total_amount = request.form.get('total_amount', '0')

        try:
            cart_items = json.loads(cart_data)
        except:
            return render_template('checkout.html', error="Invalid cart data")

        order = {
            "order_id": str(uuid.uuid4()),
            "username": session['username'],
            "name": name,
            "address": address,
            "phone": phone,
            "items": cart_items,
            "total": total_amount,
            "payment_method": payment_method,
            "time": datetime.now().isoformat()
        }

        orders.append(order)

        return redirect(url_for('success'))

    return render_template('checkout.html')


# ================== SUCCESS ==================

@app.route('/success')
def success():
    return render_template('sucess.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
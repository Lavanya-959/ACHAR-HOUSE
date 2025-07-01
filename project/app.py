from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
from datetime import datetime
import json, uuid




app = Flask(__name__)
app.secret_key = 'your_strong_secret_key_here'  # ADD THIS - VERY IMPORTANT

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

users_table = dynamodb.Table('Users')
orders_table = dynamodb.Table('Orders')

@app.route('/')  # This handles the base URL
def index():
    return render_template('index.html')  # Make sure index.html exists

# FIXED PRODUCT IDs - ALL UNIQUE NOW
products = {
    'non_veg_pickles': [
        {'id': 1, 'name': 'Chicken Pickle', 'weights': {'250': 600, '500': 1200, '1000': 1800}},
        {'id': 2, 'name': 'Fish Pickle', 'weights': {'250': 200, '500': 400, '1000': 800}},
        {'id': 4, 'name': 'Mutton Pickle', 'weights': {'250': 400, '500': 800, '1000': 1600}},
        {'id': 6, 'name': 'Prawn Pickle', 'weights': {'250': 350, '500': 700, '1000': 1050}}
    ],
    'veg_pickles': [
        {'id': 7, 'name': 'Traditional Mango Pickle', 'weights': {'250': 150, '500': 280, '1000': 500}},
        {'id': 8, 'name': 'Zesty Lemon Pickle', 'weights': {'250': 120, '500': 220, '1000': 400}},
        {'id': 9, 'name': 'Tomato Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 10, 'name': 'Amla Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 11, 'name': 'Chintakaya Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 12, 'name': 'Spicy Pandu Mirchi', 'weights': {'250': 130, '500': 240, '1000': 450}}
    ],
    'snacks': [
        {'id': 13, 'name': 'Banana Chips', 'weights': {'250': 300, '500': 600, '1000': 800}},
        {'id': 14, 'name': 'aam papad', 'weights': {'250': 150, '500': 300, '1000': 600}},
        {'id': 15, 'name': 'Boondhi Acchu', 'weights': {'250': 300, '500': 600, '1000': 900}},
        {'id': 16, 'name': 'Crispy Chekka Pakodi', 'weights': {'250': 50, '500': 100, '1000': 200}},
        {'id': 19, 'name': 'Dry Fruit Laddu', 'weights': {'250': 500, '500': 1000, '1000': 1500}},
        {'id': 20, 'name': 'Chakralu', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 21, 'name': 'Murukulu', 'weights': {'250': 250, '500': 500, '1000': 750}} # Fixed weight key
    ]
}



def get_products():
    try:
        response = products.scan()
        return response.get('Items', [])
    except Exception as e:
        app.logger.error(f"Error fetching products: {str(e)}")
        return []
    
# Add order status tracking
def create_order(order_data):
    order_data.update({
        'status': 'pending',
        'order_date': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    })
    try:
        orders_table.put_item(Item=order_data)
        return True
    except Exception as e:
        app.logger.error(f"Order creation failed: {str(e)}")
        return False
        
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get featured products (3 from each category)
    featured_products = {
        'non_veg_pickles': products['non_veg_pickles'][:3],
        'veg_pickles': products['veg_pickles'][:3],
        'snacks': products['snacks'][:3]
    }
    
    return render_template('home.html', 
                         products=featured_products,
                         all_products=products)
    
    
@app.route('/non_veg_pickles')  # Make sure this exists exactly like this
def non_veg_pickles():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('non_veg_pickles.html', products=products['non_veg_pickles'])
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle cart updates if needed
        pass
        
    return render_template('cart.html')

@app.route('/veg_pickles')  # Make sure this exists exactly like this
def veg_pickles():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('veg_pickles.html', products=products['veg_pickles'])
@app.route('/snacks')  # Make sure this exists exactly like this
def snacks():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('snacks.html', products=products['snacks'])


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/about_us')
def about_us():
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    # Hardcoded demo credentials
    DEMO_CREDENTIALS = {
        'demo1': 'password1',
        'demo2': 'password2',
        'admin': 'admin123'
    }

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # First check demo credentials
        if username in DEMO_CREDENTIALS and DEMO_CREDENTIALS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            session['is_demo'] = True  # Mark as demo user
            return redirect(url_for('home'))
            
        # Then check database users
        try:
            response = users_table.get_item(Key={'username': username})
            if 'Item' not in response:
                return render_template('login.html', error='User not found')
                
            user = response['Item']
            if 'password' not in user:
                return render_template('login.html', error='Password not found in database')
                
            if check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['username'] = username
                session['is_demo'] = False  # Mark as real user
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Invalid username or password')
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")  # Log the error
            return render_template('login.html', error='Login failed. Please try again.')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        try:
            # Validate input
            if not username or not email or not password:
                return render_template('signup.html', error='All fields are required')
                
            response = users_table.get_item(Key={'username': username})
            if 'Item' in response:
                return render_template('signup.html', error='Username already exists')
                
            hashed_password = generate_password_hash(password)
            
            users_table.put_item(
                Item={
                    'username': username,
                    'email': email,
                    'password': hashed_password
                }
            )
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('signup.html', error='Registration failed: ' + str(e))
    return render_template('signup.html')

# Other routes remain mostly the same except for the fixes below

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if session.get('is_demo'):
        return render_template('checkout.html', error="Demo accounts cannot place real orders. Please sign up for a real account.")
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            address = request.form.get('address', '').strip()
            phone = request.form.get('phone', '').strip()
            payment_method = request.form.get('payment', '').strip()
    
            # Validate inputs
            if not all([name, address, phone, payment_method]):
                return render_template('checkout.html', error="All fields are required.")
                
            if not phone.isdigit() or len(phone) != 10:
                return render_template('checkout.html', error="Phone number must be exactly 10 digits.")
            
            # Get cart data
            cart_data = request.form.get('cart_data', '[]')
            total_amount = request.form.get('total_amount', '0')
            
            try:
                cart_items = json.loads(cart_data)
                total_amount = float(total_amount)
            except (json.JSONDecodeError, ValueError):
                return render_template('checkout.html', error="Invalid cart data format.")
               
            if not cart_items:
                return render_template('checkout.html', error="Your cart is empty.")
            
            # Generate order ID
            order_id = str(uuid.uuid4())
            
            # Store order
            orders_table.put_item(
                Item={
                    'order_id': order_id,
                    'username': session.get('username', 'Guest'),  # Fixed typo
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'items': cart_items,
                    'total_amount': total_amount,
                    'payment_method': payment_method,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Redirect with order ID
            return redirect(url_for('success', order_id=order_id))
        except Exception as e:
            return render_template('checkout.html', error="An error occurred: " + str(e))
            
    return render_template('checkout.html')

@app.route('/success')
def success():
    order_id = request.args.get('order_id', '')
    return render_template('success.html', order_id=order_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
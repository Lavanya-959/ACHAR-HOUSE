#-- Libraries --- 
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import boto3
from datetime import datetime
import json, uuid

from dotenv import load_dotenv
load_dotenv()  # This loads the environment variables from .env file

##############################################
# ------- Flask App Configuration ------- ####
##############################################

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sns_client = boto3.client('sns', region_name=AWS_REGION)

users_table = dynamodb.Table(os.environ.get('USERS_TABLE', 'Users'))
orders_table = dynamodb.Table(os.environ.get('ORDERS_TABLE', 'Orders'))

# SNS Configuration
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
ENABLE_SNS = os.environ.get('ENABLE_SNS', 'False').lower() == 'true'

EMAIL_ADDRESS = 'lavanyap.csd@gmail.com'
EMAIL_PASSWORD = 'admin@123'
# Add testing endpoints (remove in production)
@app.route('/test/sns')
def test_sns():
    if not app.debug:
        return "Not available in production", 403
    send_sns_notification("Test Notification", "This is a test message from the pickle store")
    return "Notification sent"

@app.route('/test/db')
def test_db():
    if not app.debug:
        return "Not available in production", 403
    try:
        users_table.scan(Limit=1)
        return "DB connection successful"
    except Exception as e:
        return f"DB connection failed: {str(e)}", 500

############################################################################
#----------------- Main Program starts ----------------------------------##
############################################################################

@app.route('/')  # This handles the base URL
def index():
    return render_template('index.html')  

# FIXED PRODUCT IDs - ALL UNIQUE 
# Make sure Your Id and Images name with same spelling
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
        {'id': 13, 'name': 'Banana Chips', 'weights': {'250': 180, '500': 360, '1000': 720}},
        {'id': 14, 'name': 'aam papad', 'weights': {'250': 150, '500': 300, '1000': 600}},
        {'id': 15, 'name': 'Boondhi Acchu', 'weights': {'250': 200, '500': 400, '1000': 800}},
        {'id': 16, 'name': 'Crispy Chekka Pakodi', 'weights': {'250': 50, '500': 100, '1000': 200}},
        {'id': 19, 'name': 'Dry Fruit Laddu', 'weights': {'250': 500, '500': 1000, '1000': 1500}},
        {'id': 20, 'name': 'Chakralu', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 21, 'name': 'Murukulu', 'weights': {'250': 250, '500': 500, '1000': 750}}
    ]
}

# Function to get products
def get_products():
    try:
        response = products.scan()
        return response.get('Items', [])
    except Exception as e:
        app.logger.error(f"Error fetching products: {str(e)}")
        return []

# Function to create an order
def create_order(order_data):
    try:
        orders_table.put_item(Item=order_data)
        
        # Send SNS notification
        message = f"New order received: {order_data['order_id']}\n"
        message += f"Customer: {order_data['customer_name']}\n"
        message += f"Total: ₹{order_data['total_amount']}"
        send_sns_notification("New Order Received", message)
        
        return True
    except Exception as e:
        app.logger.error(f"Order creation failed: {str(e)}")
        return False
  
# Home Page Route      
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get featured products (first 4 from each category)
    featured_non_veg = products['non_veg_pickles'][:4]
    featured_veg = products['veg_pickles'][:4]
    featured_snacks = products['snacks'][:4]
    
    return render_template('home.html', 
                         non_veg_pickles=products['non_veg_pickles'],
                         veg_pickles=products['veg_pickles'],
                         snacks=products['snacks'],
                         featured_non_veg=featured_non_veg,
                         featured_veg=featured_veg,
                         featured_snacks=featured_snacks)

## ------------- Product Routes --------##
# Make sure this exists exactly like this
@app.route('/non_veg_pickles')  
def non_veg_pickles():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('non_veg_pickles.html', products=products['non_veg_pickles'])
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



# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500



# About Us and Contact Us
@app.route('/about_us')
def about_us():
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

###############################################
#-------------------- Login -----------------#
###############################################
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




###############################################
#-------------------- Signup -----------------#
###############################################

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




#############################################
#-------------------- Cart -----------------#
#############################################
@app.route('/static/js/cart.js')
def cart_js():
    return app.send_static_file('js/cart.js')

@app.route('/static/js/checkout.js')
def checkout_js():
    return app.send_static_file('js/checkout.js')
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle cart updates if needed
        pass
        
    return render_template('cart.html')
# Cart page route
@app.route('/cart')
def view_cart():
    cart_items = session.get('cart', [])
    total = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)




# Checkout page route
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if session.get('is_demo'):
        return render_template('checkout.html', 
                            error="Demo accounts cannot place real orders. Please sign up for a real account.")
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            address = request.form.get('address', '').strip()
            phone = request.form.get('phone', '').strip()
            payment_method = request.form.get('payment', '').strip()
            
            # Validate inputs
            if not all([name, address, phone, payment_method]):
                return render_template('checkout.html', 
                                    error="All fields are required.",
                                    name=name,
                                    address=address,
                                    phone=phone)
            
            if not phone.isdigit() or len(phone) != 10:
                return render_template('checkout.html', 
                                    error="Phone number must be exactly 10 digits.",
                                    name=name,
                                    address=address,
                                    phone=phone)
            
            # Get cart data
            cart_data = session.get('cart', [])
            if not cart_data:
                return render_template('checkout.html', 
                                    error="Your cart is empty.",
                                    name=name,
                                    address=address,
                                    phone=phone)
            
            # Calculate total
            total_amount = sum(float(item['price']) * int(item['quantity']) for item in cart_data)
            
            # Create order
            order_id = str(uuid.uuid4())
            order_data = {
                'order_id': order_id,
                'user_id': session.get('username'),
                'customer_name': name,
                'shipping_address': address,
                'phone_number': phone,
                'items': cart_data,
                'total_amount': total_amount,
                'payment_method': payment_method,
                'status': 'pending',
                'order_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            # Save to database
            orders_table.put_item(Item=order_data)
            
            # Clear cart and redirect
            session.pop('cart', None)
            return redirect(url_for('order_success', order_id=order_id))
            
        except Exception as e:
            app.logger.error(f"Checkout error: {str(e)}")
            return render_template('checkout.html', 
                                error="An error occurred during checkout. Please try again.")
    
    # GET request - show checkout page
    cart_items = session.get('cart', [])
    total = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
    return render_template('checkout.html', cart=cart_items, total=total)    


# Order tracking
@app.route('/orders/<order_id>')
def order_tracking(order_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        response = orders_table.get_item(Key={'order_id': order_id})
        if 'Item' not in response:
            return render_template('404.html'), 404
            
        order = response['Item']
        
        # Verify the order belongs to the current user
        if order.get('user_id') != session.get('username'):
            return render_template('403.html'), 403
            
        return render_template('order_details.html', order=order)
    except Exception as e:
        app.logger.error(f"Order tracking error: {str(e)}")
        return render_template('500.html'), 500
    
def send_order_confirmation(email, order_id, order_details):
    msg = MIMEMultipart()
    msg['From'] = os.environ.get('FROM_EMAIL', 'noreply@yourpicklestore.com')
    msg['To'] = email
    msg['Subject'] = f'Your Pickle Order #{order_id}'
    
    # ... (rest of your HTML email code remains the same)
    
    try:
        with smtplib.SMTP(os.environ.get('SMTP_SERVER'), 
                        int(os.environ.get('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.environ.get('EMAIL_ADDRESS'), 
                       os.environ.get('EMAIL_PASSWORD'))
            server.send_message(msg)
    except Exception as e:
        app.logger.error(f"Failed to send email: {str(e)}")
        



###############################
# SNS Notification
###############################
def send_sns_notification(subject, message):
    try:
        if ENABLE_SNS and SNS_TOPIC_ARN:
            response = sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject=subject
            )
            return response
    except Exception as e:
        app.logger.error(f"SNS notification failed: {str(e)}")
    return None          

# Success page   
@app.route('/success')
def success():
    order_id = request.args.get('order_id', '')
    return render_template('success.html', order_id=order_id)



###############################
# Run app
###############################
if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=5000)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
        


###############################
# Date 02/07/2025
# Developed by 
# K VVS Manohar , Lavanya 
# ###############################

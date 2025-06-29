from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Home route
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

# # About route
# @app.route('/about')
# def about():
#     return render_template('about.html')

# # Contact route
# @app.route('/contact')
# def contact():
#     return render_template('contact.html')

# # Login route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         # Dummy login logic
#         username = request.form.get('username')
#         password = request.form.get('password')
#         if username and password:
#             return redirect(url_for('home'))
#         else:
#             return render_template('login.html', error="Invalid credentials")
#     return render_template('login.html')

# # Signup route
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         # Dummy signup logic
#         name = request.form.get('name')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         if name and email and password:
#             return redirect(url_for('success'))
#     return render_template('signup.html')

# Cart route
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Checkout route
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

# Snacks route
@app.route('/snacks')
def snacks():
    return render_template('snacks.html')

# Veg Pickles route
@app.route('/veg_pickles')
def veg_pickles():
    return render_template('veg_pickles.html')

# Non-Veg Pickles route
@app.route('/non_veg_pickles')
def non_veg_pickles():
    return render_template('non_veg_pickles.html')

# Success route
@app.route('/success')
def success():
    return render_template('success.html')

# Index route (optional)
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact.html')

@app.route('/about-us')
def about_us():
    return render_template('about.html')

# Start the app
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, g, session, flash, send_from_directory, jsonify
import sqlite3
import hashlib
from werkzeug.utils import secure_filename
import os
import time
import secrets
import random
import string
from flask import abort
from flask_mail import Mail, Message




app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'jorandelgado23@gmail.com'
app.config['MAIL_PASSWORD'] = 'vnlc ylxv hgkz hadv'

mail = Mail(app)

mail = Mail(app)

app.secret_key = 'your_secret_key'





# Get the base directory path of the current file
# base_directory = os.path.abspath(os.path.dirname(__file__))

# # Define the upload folder path relative to the base directory
# upload_folder = os.path.join(base_directory, 'uploads')

# # Set the upload folder in the Flask app configuration
# app.config['UPLOAD_FOLDER'] = upload_folder



app.config['UPLOAD_FOLDER'] = 'C:/Users/Administrator/Documents/website/COSMIC WEBSITE/uploads'


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_product_id_by_name(product_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT product_id FROM products WHERE name = ?', (product_name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None  # Handle the case when the product is not found

# Database connection for users
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('users.db')
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)  # Use 'db' instead of '_database'
    if db is not None:
        db.close()

# Create the 'users' table for user information
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        password TEXT,
        role TEXT,
        shop_name TEXT,
        username TEXT,
        birthday TEXT,
        location TEXT,
        phone_number TEXT,
        session_id TEXT,
        image_filename,
        reset_token TEXT,
        wallet_balance REAL
    )
''')
conn.commit()
cursor.close()
conn.close()

conn_admin = sqlite3.connect('users.db')
cursor_admin = conn_admin.cursor()
cursor_admin.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
''')

def get_user_data(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

admin_username = "admin"
admin_password = "password"  # You should hash this password for security
hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()

cursor_admin.execute('INSERT INTO admin (username, password) VALUES (?, ?)',
                   (admin_username, hashed_password))
conn_admin.commit()
cursor_admin.close()
conn_admin.close()


conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        price REAL,
        stock INTEGER,
        variations TEXT,
        category TEXT,
        image_filename TEXT,
        discount_rate REAL,
        discount_amount REAL,
        discounted_price REAL,
        session_id TEXT,
        shop_id TEXT,
        shop_name TEXT,
        shipping_fee REAL  -- Add a new column for shipping fee
    )
''')
conn.commit()
conn.close()


conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            email TEXT NOT NULL,
            rating INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
 
conn.commit()
conn.close()

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        product_id INTEGER PRIMARY KEY,
        user_email TEXT,
        shop_name TEXT,
        name TEXT,
        price REAL,
        description TEXT,
        quantity INTEGER,
        total REAL,
        variation TEXT,
        shipping_fee REAL
    )
''')
conn.commit()
conn.close()

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create the 'checkout' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS checkout_orders (
        id INTEGER PRIMARY KEY,
        transaction_id TEXT,
        firstname TEXT,
        lastname TEXT,
        shop_name TEXT,
        email TEXT,
        address TEXT,
        phone_number TEXT,
        payment_method TEXT,
        product_name TEXT,
        variation TEXT,
        price REAL,
        quantity INTEGER,
        subtotal REAL,
        overall_total REAL,
        status TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()


conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT,
        lastname TEXT,
        email TEXT,
        address TEXT,
        phone_number TEXT,
        payment_method TEXT,
        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT,
        shop_name TEXT,
        cancellation_status TEXT,
        cancellation_reason TEXT,
        cancel_status TEXT,
        seller_decision TEXT
    )
''')

conn.commit()
conn.close()


conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS seller_account (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        password TEXT,
        role TEXT,
        shop_name TEXT,
        location TEXT,
        phone_number TEXT,
        session_id TEXT,
        image_filename TEXT,  -- Assuming image_filename is a text field
        shop_id TEXT,
        wallet_balance REAL
    )
''')

conn.commit()
cursor.close()
conn.close()


conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create the "order_items" table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_name TEXT,
        variation TEXT,  -- Add this column for variations
        product_price INTEGER,
        quantity INTEGER,
        subtotal INTEGER,
        shipping_cost INTEGER,
        shop_name TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
''')



# Commit the changes and close the connection
conn.commit()
conn.close()



conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS wishlist (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT,
        image_filename TEXT,
        product_price TEXT,
        stock INTEGER,
        session_id TEXT,
        user_id TEXT,
        user_email TEXT
    )
''')

conn.commit()
conn.close()


conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create the Address table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY,
        fullName TEXT NOT NULL,
        phoneNumber TEXT NOT NULL,
        region TEXT NOT NULL,
        province TEXT NOT NULL,
        city TEXT NOT NULL,
        barangay TEXT NOT NULL,
        postalCode TEXT NOT NULL,
        streetName TEXT NOT NULL,
        building TEXT NOT NULL,
        houseNo TEXT NOT NULL
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()


conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT,
            request_amount REAL,
            request_message TEXT,
            status TEXT DEFAULT 'pending'
        )
  ''')

conn.commit()
conn.close()

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_wallet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email INTEGER,
        amount INTEGER,
        status TEXT DEFAULT 'pending',  -- pending/confirmed/denied
        transaction_type TEXT,  -- cash_in/cash_out
        FOREIGN KEY (user_email) REFERENCES users (email)
    )
''')

conn.commit()
cursor.close()
conn.close()


# Routes
def get_wishlist_count(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM wishlist WHERE user_email = ?', (email,))
    count = cursor.fetchone()[0]

    conn.close()
    return count

def get_cart_count(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM cart WHERE user_email = ?', (email,))
    count = cursor.fetchone()[0]

    conn.close()
    return count

# Define the index route
@app.route('/')
def index():
    
    session_id = session.get('session_id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Retrieve products from the database
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    cursor.execute('SELECT * FROM seller_account WHERE session_id =? ', (session_id,))
    user_exist = cursor.fetchone()
    
    

    # Close the connection after fetching products
    conn.close()
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    user_email = session.get('user_email')
    cursor.execute('SELECT image_filename FROM users WHERE email = ?', (user_email,))
    user_data = cursor.fetchone()

    # Close the connection after fetching data
    cursor.close()
    conn.close()

    email = session.get('email')
    logged_in = True if email else False

    products_list = []
    for product in products:
        product_dict = {
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'price': product[3],
            'stock': product[4],
            'variation': product[5],
            'category': product[6],
            'image_filename': product[7],
            'discount_rate': product[8],
            
        }
        products_list.append(product_dict)

    user_email = session.get('user_email')

   

    # Use the modified get_wishlist_count function to retrieve the wishlist count
    wishlist_count = get_wishlist_count(email)
    
     # Use the get_cart_count function to retrieve the cart count
    cart_count = get_cart_count(email)

    # Assuming you want to display the image filename of the first product.
    if products_list:
        image_filename = products_list[0]['image_filename']
    else:
    # Handle the case when there are no products
        image_filename = None  # or set a default value

    # Introducing a slight delay using time.sleep(1)
    time.sleep(1)

    # Render the template with the required variables
    return render_template('index.html',user_exist=user_exist, image_filename=image_filename, email=email, logged_in=logged_in, products=products_list, wishlist_count=wishlist_count, cart_count=cart_count)

    # Handle the case where products_list is empty.
    #return render_template('index.html', email=email, logged_in=logged_in, products=products_list, count=count)


        
    
    
    # return render_template('index.html', email=email, logged_in=logged_in, products=products)

from flask import render_template

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            
            session_id = secrets.token_hex(4) 
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'buyer')
            shop_name = request.form.get('shop_name')  # Add this line to get the shop name
            birthday = request.form.get('birthday')  # Add this line to get the birthday
            location = request.form.get('location')  # Add this line to get the location
            phone_number = request.form.get('phone_number')  # Add this line to get the phone number
            username = request.form.get('username')  # Add this line to get the username
            wallet_balance = "0"  # Add this line to get the username

            conn = get_db()
            cursor = conn.cursor()

            # Check if the email already exists
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('An account with this email already exists. Please log in or use a different email.', 'error')
                return render_template('register.html')

            # If email doesn't exist, proceed with registration
            cursor.execute(
    'INSERT INTO users (first_name, last_name, email, password, role, shop_name, birthday, location, phone_number, username, session_id, wallet_balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
    (first_name, last_name, email, password, role, shop_name, birthday, location, phone_number, username, session_id, wallet_balance)
)

            conn.commit()
            cursor.close()
            flash('Sign-up successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash('An error occurred during sign-up. Please try again.', 'error')
            return render_template('error.html', error=str(e))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Check the users table
            conn_users = get_db()
            cursor_users = conn_users.cursor()
            cursor_users.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cursor_users.fetchone()
            cursor_users.close()

            if user is not None:
                session['email'] = email
                session['role'] = user[5]  
                session['session_id'] = user[11]  
                
                

                # if session['role'] == 'seller':
                #     flash("Login successful! Welcome, Seller!", "success")
                #     return redirect(url_for('sellerpage'))  # Redirect to seller page
                # else:
                flash("Login successful! Welcome, Buyer!", "success")
                return redirect(url_for('index'))  # Redirect to index or buyer page

            # If not found in users table, check the seller_account table
            conn_seller = get_db()
            cursor_seller = conn_seller.cursor()
            cursor_seller.execute("SELECT * FROM seller_account WHERE email = ? AND password = ?", (email, password))
            seller = cursor_seller.fetchone()
            cursor_seller.close()

            if seller is not None:
                session['email'] = email
                session['role'] = 'seller'  # Assuming role is 'seller' for seller accounts

                flash("Login successful! Welcome, Seller!", "success")
                return redirect(url_for('sellerpage'))  # Redirect to seller page

            # If not found in both tables, show error message
            flash("Incorrect email or password. Please try again.", "error")
            return redirect(url_for("login"))

        except sqlite3.Error as e:
            return render_template('error.html', error=str(e))
    else:
        return render_template('login.html')


# Function to generate a secure token
def create_connection():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    return connection, cursor

def generate_reset_code():
    # Generate a random code, e.g., a combination of letters and digits
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return code

# Your forgot_password route
# Your forgot_password route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        connection, cursor = create_connection()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            reset_code = generate_reset_code()
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (reset_code, email))
            connection.commit()
            connection.close()

            # Send the reset code via email
            msg = Message("Temporary Password", sender='jorandelgado23@gmail.com', recipients=[email])
            msg.body = f"Your Temporary Password is: {reset_code}"
            mail.send(msg)
            flash("Temporary Password sent to your email. Please check your inbox.")
            return redirect(url_for('login'))
        else:
            flash("Email not found. Please check your email address.")
            return render_template('forgot_password')

    return render_template('forgot_password.html')


categories = ["sports equipment", "sportswear", "dietary product", "fitness equipment", "protective equipment"]

@app.route('/shop', methods=['GET'])
def shop():
    email = session.get('email')
    logged_in = True if email else False
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if a category is specified in the query parameters
    selected_category = request.args.get('category')

    if selected_category:
        # If a category is specified, filter products by category
        cursor.execute('SELECT * FROM products WHERE category = ?', (selected_category,))
    else:
        # If no category is specified, get all products
        cursor.execute('SELECT * FROM products')

    products = cursor.fetchall()
    conn.close()

    email = session.get('email')
    logged_in = True if email else False

    products_list = []
    for product in products:
        product_dict = {
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'price': product[3],
            'stock': product[4],
            'variation': product[5],
            'category': product[6],
            'image_filename': product[7]
        }
        products_list.append(product_dict)

    if products_list:
        # Assuming you want to display the image filename of the first product.
        image_filename = products_list[0]['image_filename']
        return render_template('shop.html', image_filename=image_filename, email=email, logged_in=logged_in, products=products_list, categories=categories, selected_category=selected_category)

    # Handle the case where products_list is empty.
    return render_template('shop.html', email=email, logged_in=logged_in, products=products_list, categories=categories, selected_category=selected_category)






@app.route('/product/<product_id>', methods=['GET', 'POST'])
def product(product_id):
    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            
            session_id = session.get('session_id')
            
            
            
            

            # Fetch product details
            cursor.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
            product = cursor.fetchone()
            
            if product:
                shop_id = product[12]
            cursor.execute('SELECT * FROM products WHERE shop_id = ?', (shop_id,))
            seller = cursor.fetchone()
            
            
            
            

            if not product:
                return render_template('product_not_found.html')

            # Split the variations and convert to a list
            if product[5]:
                variations = product[5].split(',')
            else:
                variations = []

            # Calculate discount related values
            discount_rate = product[8]  # Assuming discount_rate is in the 9th position (0-indexed)
            discount_amount = round(product[9], 2)  # Round to 2 decimal places
            discounted_price = round(product[10], 2)  # Round to 2 decimal places

            product_dict = {
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'price': product[3],
                'stock': product[4],
                'variations': variations,
                'category': product[6],
                'image_filename': product[7],
                'discount_rate': discount_rate,
                'discount_amount': discount_amount,
                'discounted_price': discounted_price,
                'discount_percentage': round((1 - (discounted_price / product[3])) * 100, 2) if product[3] != 0 else 0,
                'shop_name': product[13],
                'shop_id': product[12],
                'shipping_fees': product[14]  # Change 'shipping_fee' to 'shipping_fees'
            }

           # Fetch reviews for the product
            cursor.execute('SELECT * FROM product_reviews WHERE product_id = ?', (product_id,))
            reviews = cursor.fetchall()

            #     # Add the reviews to the product_dict
            product_dict['reviews'] = reviews

            email = session.get('email')
            logged_in = True if email else False

            if request.method == 'POST':
                # Handle review submission
                author = request.form['author']
                email = request.form['email']
                rating = request.form['rating']
                title = request.form['title']
                body = request.form['body']

                # Insert the review into the database
                cursor.execute(
                    'INSERT INTO product_reviews (product_id, author, email, rating, title, body) VALUES (?, ?, ?, ?, ?, ?)',
                    (product_id, author, email, rating, title, body)
                )
                conn.commit()

                flash('Review submitted successfully!', 'success')
                return redirect(url_for('product', product_id=product_id))

            time.sleep(1)
            return render_template('product.html', email=email, logged_in=logged_in, product=product_dict, reviews=reviews, seller=seller, shipping_fees=product_dict['shipping_fees'])


    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('An error occurred while processing your request.', 'error')
        return render_template('error.html')


@app.route('/submit_review/<int:product_id>', methods=['POST'])
def submit_review(product_id):
    if request.method == 'POST':
        author = request.form['author']
        email = request.form['email']
        rating = request.form['rating']
        title = request.form['title']
        body = request.form['body']

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO product_reviews (product_id, author, email, rating, title, body) VALUES (?, ?, ?, ?, ?, ?)',
                (product_id, author, email, rating, title, body)
            )
            conn.commit()

        flash('Review submitted successfully!', 'success')
        return redirect(url_for('product', product_id=product_id))


@app.route('/product_by_name/<string:product_name>', methods=['GET'])
def product_by_name(product_name):
    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE name = ?', (product_name,))
            product = cursor.fetchone()

        if product:
            # Split the variations and convert to a list
            variations = product[5].split(',') if product[5] else []

            product_dict = {
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'price': product[3],
                'stock': product[4],
                'variations': variations,
                'category': product[6],
                'image_filename': product[7],
                'discount_rate': product[8],
                'discount_amount': round(product[9], 2) if product[9] is not None else None,
                'discounted_price': round(product[10], 2) if product[10] is not None else None,
                'discount_percentage': round((1 - (product[10] / product[3])) * 100, 2) if product[3] != 0 and product[10] is not None else 0
            }

            email = session.get('email')
            logged_in = True if email else False
            time.sleep(1)
            return render_template('product.html', email=email, logged_in=logged_in, product=product_dict)
        else:
            return render_template('product_not_found.html')

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('An error occurred while processing your request.', 'error')
        return render_template('error.html')




@app.route('/LOGOUT', methods=['POST', 'GET'])
def LOGOUT():
    email = session.pop('email', None)
    role = session.pop('role', None)
    if email:
        flash(f"Successfully logged out. Goodbye, {email}!", 'success')
    else:
        flash("You are not logged in.", 'info')
    return redirect(url_for('index'))




@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Fetch admin credentials from the admin database
        conn_admin = sqlite3.connect('users.db')
        cursor_admin = conn_admin.cursor()
        cursor_admin.execute('SELECT * FROM admin WHERE username = ?', (username,))
        admin = cursor_admin.fetchone()
        conn_admin.close()
        if admin and admin[2] == hashlib.sha256(password.encode()).hexdigest():
            # Authentication successful, redirect to admin panel
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            error_message = "Invalid username or password. Please try again."
    else:
        error_message = None
    return render_template('adminlogin.html', error_message=error_message)



def get_user_count_by_role(role):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', (role,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def get_seller_count_by_role(role):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM seller_account WHERE role = ?', (role,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count

def get_product_count_by_product_id(product_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM products WHERE product_id = ?', (product_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count



@app.route('/admin/panel')
def admin_panel():
    if session.get('admin_logged_in'):
        # Fetch user count based on role
        user_count = get_user_count_by_role('buyer')  # Replace 'user' with the role for regular users

        # Fetch seller count based on role
        seller_count = get_seller_count_by_role('seller')  # Replace 'seller' with the role for sellers
        
        
        product_count = get_product_count_by_product_id('product_id')


        return render_template('admin_panel.html', user_count=user_count, seller_count=seller_count, product_count=product_count)
    else:
        flash('You need to be logged in as an admin to access the admin panel.', 'info')
        return redirect(url_for('admin_login'))

    
    
    
@app.route('/ADD_USER', methods=['GET', 'POST'])
def ADD_USER():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'buyer')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (first_name, last_name, email, password, role) VALUES (?, ?, ?, ?, ?)',
                       (first_name, last_name, email, password, role))
        conn.commit()
        cursor.close()
        flash('User added successfully!', 'success')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    
    return render_template('user_management.html', users=users)


@app.route('/view_users', methods=['GET'])
def view_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    return render_template('view_users.html', users=users)


@app.route('/view_sellers', methods=['GET'])
def view_sellers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, first_name, last_name, email, role, shop_name, shop_id FROM seller_account')
    sellers = cursor.fetchall()
    cursor.close()
    return render_template('view_sellers.html', sellers=sellers)




def get_seller_data(seller_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM seller_account WHERE id = ?', (seller_id,))
    seller = cursor.fetchone()
    cursor.close()
    return seller
# Assuming you have a route for editing a seller
@app.route('/edit_seller/<int:seller_id>', methods=['GET', 'POST'])
def edit_seller(seller_id):
    # Implement the logic to fetch and update the seller information
    if request.method == 'POST':
        # Update seller information in the database
        flash('Seller information updated successfully.', 'success')
        return redirect(url_for('view_sellers'))

    # Fetch seller information and render the edit form
    seller = get_seller_data(seller_id)  # Implement the function to fetch seller data
    return render_template('edit_seller.html', seller=seller)

# Assuming you have a route for deleting a seller
@app.route('/delete_seller/<int:seller_id>', methods=['POST'])
def delete_seller(seller_id):
    # Implement the logic to delete the seller from the database
    flash('Seller deleted successfully.', 'success')
    return redirect(url_for('view_sellers'))


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        new_role = request.form.get('role')
        new_id = request.form.get('id')
        new_first_name = request.form.get('first_name')
        new_last_name = request.form.get('last_name')
        new_email = request.form.get('email')
        new_password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET role = ?, id = ?, first_name = ?, last_name = ?, email = ?, password = ? WHERE id = ?', (new_role, new_id, new_first_name, new_last_name, new_email, new_password, user_id))
        conn.commit()
        cursor.close()
        flash('User information updated successfully!', 'success')
        return redirect(url_for('user_management'))
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return render_template('edit_user.html', user=user)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    cursor.close()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('user_management'))


@app.route('/user_management', methods=['GET'])
def user_management():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM seller_account')
    sellers = cursor.fetchall()
    cursor.close()
    
    return render_template('user_management.html', users=users, sellers=sellers)



@app.route('/show_users')
def show_users():
    # Retrieve user data from your database
    users = get_user_data()  # Replace with your actual data retrieval function

    return render_template('show_users.html', users=users)



shipping_fees = {
    'NCR': 85,
    'Bulacan': 95,
    'Cavite': 40,
    'Laguna': 60,
    'Rizal': 80,
    'Cebu': 100,
    'Palawan': 465,
    'Davao del Sur': 500,
    'Davao del Norte': 500,
    'Zamboanga del Sur': 500,
    'Misamis Oriental': 0,
    'South Cotabato': 0,
    'Pampanga': 120,
    'Ilocos Norte': 150,
    'Ilocos Sur': 150,
    'Cagayan': 200,
    'Isabela': 200,
    'Quirino': 200,
    'Aurora': 200,
    'Batanes': 250,
    'Benguet': 250,
    'Ifugao': 250,
    'Kalinga': 250,
    'Apayao': 250,
    'Nueva Vizcaya': 250,
    'Batangas': 80,
    'Quezon': 80,
    'Mindoro Occidental': 100,
    'Mindoro Oriental': 100,
    'Marinduque': 100,
    'Romblon': 100,
}

@app.route('/add_product', methods=['POST'])
def add_product():
    session_id = session.get('session_id')

    if request.method == 'POST':
        name = request.form.get('name')
        shop_id = secrets.token_hex(4)
        shop_name = request.form.get('shop_name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = request.form.get('stock')
        variations = ",".join(request.form.getlist('variations[]'))
        category = request.form.get('category')
        image = request.files['image']
        discount_rate = float(request.form.get('discount', 0))
        location = request.form.get('location')

        # Check if a file was uploaded and it is of an allowed type
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM seller_account WHERE session_id = ?', (session_id,))
            shop_details = cursor.fetchone()

            if shop_details:
                shop_id = shop_details[11]
                shop_name = shop_details[6]

            cursor.execute('SELECT * FROM products WHERE name=? AND description=? AND price=?',
                           (name, description, price))
            existing_product = cursor.fetchone()

            if not existing_product:
                # Save the image to your server's designated folder
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Calculate the discounted price
                discount_amount = (price * discount_rate) / 100
                discounted_price = price - discount_amount

                # Get the selected location from the form
                location = request.form.get('location')

                # Check if the selected location is in the shipping fees dictionary
                if location in shipping_fees:
                    # Get the shipping fee for the selected location
                    shipping_fee = shipping_fees[location]
                else:
                    # If the location is not in the dictionary, set a default shipping fee or handle it as needed
                    shipping_fee = 0

                # Calculate the total price including the shipping fee
                total_price = discounted_price + shipping_fee

                # Store the product details in the database
                cursor.execute(
                    'INSERT INTO products (name, description, price, stock, variations, category, image_filename, discount_rate, discount_amount, discounted_price, session_id, shop_id, shop_name, shipping_fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (name, description, price, stock, variations, category, filename, discount_rate,
                     discount_amount, discounted_price, session_id, shop_id, shop_name, shipping_fee))

                conn.commit()

            conn.close()

    return redirect(url_for('index'))









@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if request.method == 'POST':
        user_email = session.get('email')

        # Check if the user is logged in
        if not user_email:
            flash('Please log in to add products to your cart.', 'error')
            return redirect(url_for('login'))  # Redirect to the login page

        product_id = request.form.get('product_id')
        selected_variation = request.form.get('selected_variation')
        quantity = int(request.form.get('quantity', 1))

        # Fetch the product details from the database based on the product_id
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Fetch the product details including the discounted price, current stock, and shipping fee
        cursor.execute('''
            SELECT price, discounted_price, stock, shipping_fee, shop_name, name, description
            FROM products
            WHERE product_id = ?
        ''', (product_id,))
        product_details = cursor.fetchone()

        if product_details:
            # Check if there is a discounted price
            price = product_details[1] if product_details[1] is not None else product_details[0]

            # Check if there is sufficient stock
            current_stock = product_details[2]
            if current_stock < quantity:
                flash('Insufficient stock. Please select a lower quantity.', 'error')
                conn.close()
                return redirect(request.referrer)

            # Calculate the total based on the selected quantity and price
            total = price * quantity
            formatted_price = round(price, 2)
            formatted_total = round(total, 2)

            # Add the shipping fee to the total
            shipping_fee = product_details[3] if product_details[3] is not None else 0
            formatted_total_with_shipping = formatted_total + shipping_fee

            # Update the stock in the products table
            updated_stock = current_stock - quantity
            cursor.execute('UPDATE products SET stock = ? WHERE product_id = ?', (updated_stock, product_id))

            # Add the product to the cart table with the shipping fee
            cursor.execute('''
                INSERT INTO cart (user_email, shop_name, name, description, price, quantity, total, variation, shipping_fee)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_email, product_details[4], product_details[5], product_details[6], formatted_price, quantity, formatted_total_with_shipping, selected_variation, shipping_fee))

            conn.commit()
            conn.close()

            # Redirect to the cart page or perform other actions as needed
            flash('Product added to cart successfully!', 'success')
            return redirect(url_for('cart'))

    # Handle other cases or return an error page if needed
    return render_template('error.html')


# ... (previous code)

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    email = session.get('email')
    logged_in = True if email else False
    
    session_id = session.get('session_id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM seller_account WHERE session_id =? ', (session_id,))
    user_exist = cursor.fetchone()
    
    # Check if selected items are in the session
    selected_items = session.get('selected_items', [])
    
    if request.method == 'POST':
        if 'clear' in request.form:
            # Clear the user's cart in the database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cart WHERE user_email = ?', (email,))
            conn.commit()
            conn.close()
            
        elif 'update' in request.form:
            updated_cart = []  # Create a new list to store updated cart items
            for item in session.get('cart', []):
                name, description, price, _, _ = item
                product_id = get_product_id_by_name(name)
                new_quantity_str = request.form.get(f'quantity_{product_id}')
                try:
                    new_quantity = int(new_quantity_str)
                    if new_quantity < 1:
                        new_quantity = 1  # Ensure quantity is at least 1
                except (ValueError, TypeError):
                    new_quantity = 1  # Use 1 as the default if parsing fails

                # Calculate total and create a new tuple with the updated quantity and other elements
                total = price * new_quantity
                updated_item = (email, name, description, price, new_quantity, total)  # Include user_email in the tuple
                updated_cart.append(updated_item)

            # Update the user's cart in the session
            session['cart'] = updated_cart

            # Update the user's cart in the database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            for updated_item in updated_cart:
                # Update the existing cart item in the database
                cursor.execute(
                    '''
                    UPDATE cart
                    SET quantity = ?, total = ?
                    WHERE user_email = ? AND name = ?
                    ''',
                    (updated_item[4], updated_item[5], email, updated_item[1])
                )

            conn.commit()
            conn.close()

            # Check if the "Proceed to Checkout" button was clicked
            if 'checkout' in request.form:
                # Remove the cart items from the database
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()

                for updated_item in updated_cart:
                    # Delete the item from the cart in the database
                    cursor.execute(
                        '''
                        DELETE FROM cart
                        WHERE user_email = ? AND name = ?
                        ''',
                        (email, updated_item[1])
                    )

                conn.commit()
                conn.close()

                # Clear the cart in the session and redirect to the checkout route
                session.pop('cart', None)
                return redirect(url_for('checkout'))
            
            
            # Update the session with the selected items
        selected_items = request.form.getlist('selected_items')
        session['selected_items'] = selected_items
            

     # Fetch the user's cart items from the "cart" table
    # Fetch the user's cart items from the "cart" table
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
            'SELECT name, description, price, quantity, total, variation, shop_name, shipping_fee FROM cart WHERE user_email = ?',
            (email,)
        )

    cart = cursor.fetchall()
    conn.close()  # Close the connection

        # Calculate the subtotal for the user's cart
    subtotal = 0.0  # Initialize the subtotal as a float
    shipping_fees = set()  # Use a set to store unique shipping fees
    total = 0.0  # Initialize the total as a float

    for item in cart:
        try:
            subtotal += float(item[4])  # Attempt to convert the value to a float and add it to the subtotal
            shipping_fees.add(float(item[7]))  # Add the shipping fee to the set
        except (ValueError, TypeError):
            pass  # Ignore non-numeric values

    # Sum up unique shipping fees
    total_shipping_fee = sum(shipping_fees)

    # Calculate the total by adding the subtotal and the total shipping fee
    total = subtotal + total_shipping_fee

    return render_template('cart.html', cart=cart, email=email, logged_in=logged_in, subtotal=subtotal, shipping=total_shipping_fee, total=total, selected_items=selected_items, user_exist=user_exist)





@app.route('/delete_item', methods=['POST'])
def delete_item():
    email = session.get('email')
    print(f"Email: {email}")

    if not email:
        # Redirect to login or handle the case when the user is not logged in
        return redirect(url_for('login'))

    item_name = request.form.get('delete_item')
    print(f"Item Name: {item_name}")

    if item_name:
        # Remove the item from the session
        updated_cart = [item for item in session.get('cart', []) if item[1] != item_name]
        print(f"Updated Cart in Session: {updated_cart}")
        session['cart'] = updated_cart

        # Remove the item from the cart in the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM cart WHERE user_email = ? AND name = ?', (email, item_name))
        conn.commit()
        conn.close()

    # Update the session with the selected items
    selected_items = request.form.getlist('selected_items')
    session['selected_items'] = selected_items

    print("Item deleted successfully.")

    # Redirect back to the cart page after deletion
    return redirect(url_for('cart'))



@app.route('/update-cart', methods=['POST'])
def update_cart():
    try:
        data = request.json
        product_name = data['productName']
        quantity = int(data['quantity'])

        # Fetch cart items from the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, description, price, quantity, total FROM cart WHERE user_email = ?', (session.get('email'),))
        cart = cursor.fetchall()

        # Update the cart data
        updated_cart = []

        for item in cart:
            if item[0] == product_name:
                item_list = list(item)
                item_list[3] = quantity  # Update quantity
                item_list[4] = item_list[2] * quantity  # Update total
                updated_cart.append(tuple(item_list))
            else:
                updated_cart.append(item)

        # Update the cart in the database
        for updated_item in updated_cart:
            cursor.execute(
                '''
                UPDATE cart
                SET quantity = ?, total = ?
                WHERE user_email = ? AND name = ?
                ''',
                (updated_item[3], updated_item[4], session.get('email'), updated_item[0])
            )

        conn.commit()
        conn.close()

        # Update the cart in the session
        session['cart'] = updated_cart

        # Calculate and return the new subtotal
        subtotal = calculate_subtotal(updated_cart)

        return jsonify({'subtotal': subtotal})
    except Exception as e:
        print(f"Error in update_cart: {e}")
        return jsonify({'error': str(e)}), 400
    
def calculate_subtotal(cart):
    return sum(item[4] for item in cart)

def calculate_overall_total(cart_items):
    total = 0

    for item in cart_items:
        if len(item) > 6 and isinstance(item[6], (int, float)):
            total += item[6]

    return total



def get_user_info(email):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT first_name, last_name, email, phone_number FROM users WHERE email = ?', (email,))
        user_info = cursor.fetchone()
        return user_info
    except sqlite3.Error as e:
        flash('An error occurred while fetching user information.', 'error')
        return None
    finally:
        conn.close()
        
def total_shipping_cost(cart_items):
    shipping_cost = sum(item[10] for item in cart_items)  # Assuming shipping_fee is at index 10
    return f'₱{shipping_cost}'

def total_shipping_cost(cart_items):
    shipping_cost = sum(float(item[10]) for item in cart_items)  # Assuming shipping_fee is at index 10
    return shipping_cost


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    
    session_id = session.get('session_id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM seller_account WHERE session_id =? ', (session_id,))
    user_exist = cursor.fetchone()
    
    email = session.get('email')
    logged_in = True if email else False
    if request.method == 'POST':
        # Handle the form submission and process the order
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        address = request.form.get('Address')
        phone_number = request.form.get('Phone Number')
        payment_method = request.form.get('payment_method')

        try:
            # Retrieve cart items from the database, including shop_name and shipping_fee
            with sqlite3.connect('users.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, variation, price, quantity, shop_name, shipping_fee, total
                    FROM cart
                    WHERE user_email = ?
                ''', (session.get('email'),))
                cart_items = cursor.fetchall()

            # Calculate the total price
            overall_total = calculate_overall_total(cart_items)  # Assuming the total is at index 5 in the cart item tuple

            # Insert order details into the database
            with sqlite3.connect('users.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO orders (firstname, lastname, email, address, phone_number, payment_method, status, shop_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (firstname, lastname, email, address, phone_number, payment_method, 'Pending', cart_items[0][4]))
                order_id = cursor.lastrowid  # Retrieve the order ID

                # Insert order items into the database with variation
                for item in cart_items:
                    cursor.execute('''
                        INSERT INTO order_items (order_id, shop_name, product_name, variation, product_price, quantity, subtotal, shipping_cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (order_id, item[4], item[0], item[1], item[2], item[3], item[5], item[6]))

            # Clear the cart after successful checkout
            session.pop('cart', None)

            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_confirmation', order_id=order_id))
        except sqlite3.Error as e:
            flash('An error occurred during checkout. Please try again.', 'error')
            return render_template('error.html', error=str(e))

    # Fetch user information for pre-filling the form
    user_info = get_user_info(session.get('email'))

    # Fetch cart items from the database for rendering the checkout form
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cart WHERE user_email = ?', (session.get('email'),))

        cart_items_db = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        flash('An error occurred while fetching cart items from the database.', 'error')
        return render_template('error.html', error=str(e))

    # Calculate the overall total for rendering in the template
    overall_total = calculate_overall_total(cart_items_db)

    # Render the checkout form with the overall total and cart items
    return render_template('checkout.html', cart_items=cart_items_db, overall_total=overall_total, user_info=user_info, total_shipping_cost=total_shipping_cost, email=email, logged_in=logged_in, user_exist=user_exist)





@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Fetch order details
        cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        order_details = cursor.fetchone()

        # Fetch order items associated with the order
        cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
        order_items = cursor.fetchall()

        return render_template('order_confirmation.html', order_details=order_details, order_items=order_items)
    except sqlite3.Error as e:
        flash('An error occurred while fetching order details from the database.', 'error')
        return render_template('error.html', error=str(e))
    finally:
        conn.close()



def get_user_shop_id(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Assuming you have a 'users' table with columns 'email' and 'shop_id'
    cursor.execute('SELECT shop_id FROM seller_account WHERE email = ?', (email,))
    
    # Fetch the shop_id
    result = cursor.fetchone()
    
    # Close the connection
    conn.close()

    # Return the shop_id if it exists, otherwise return None
    return result[0] if result else None

def get_product_count(shop_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Assuming you have a 'products' table with a 'shop_id' column
    cursor.execute('SELECT COUNT(*) FROM products WHERE shop_id = ?', (shop_id,))

    # Fetch the product count
    result = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    # Return the product count
    return result

@app.route('/sellerpage', methods=['GET'])
def sellerpage():
    # Check if the user is logged in
    email = session.get('email')
    if not email:
        # Redirect to login page or handle as appropriate
        return redirect('/login')

    # Check if the user has the 'seller' role
    user_role = get_user_role(email)  # Implement a function to retrieve the user's role
    if user_role != 'seller':
        # Redirect to unauthorized page or handle as appropriate
        return render_template('unauthorized.html')

    # Get the user's shop_id
    shop_id = get_user_shop_id(email)

    # If the user is a seller, fetch product count using shop_id
    if shop_id is not None:
        product_count = get_product_count(shop_id)
    else:
        product_count = 0  # or any default value

    # If the user is a seller, render the seller page with product count
    logged_in = True
    return render_template('sellerpage.html', email=email, logged_in=logged_in, product_count=product_count)

class User:
    def __init__(self, email, role):
        self.email = email
        self.role = role

# Function to get the user's role based on email
def get_user_role(email):
    # Replace this with your actual logic to retrieve the user's role
    # For example, querying a database or using some authentication system
    # Here, we're using a dummy function that returns 'seller' for demonstration purposes
    user = User(email, 'seller')
    return user.role
    return render_template('sellerpage.html')
    


@app.route('/seller_profile', methods=['GET'])
def seller_profile():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    email_name = session.get('email')
    logged_in = True if email_name else False

    cursor.execute('SELECT * FROM seller_account WHERE email = ?',(email_name,))
    seller_data = cursor.fetchone()

    if seller_data:
        firstname = seller_data[1]
        lastname = seller_data[2]
        email = seller_data[3]
        password = seller_data[4]
        location = seller_data[7]
        phone_number = seller_data[8]
        image_filename = seller_data[10]

    conn.close()

    return render_template('seller_profile.html', firstname=firstname, lastname=lastname, email_name=email_name, phone_number=phone_number, location=location, password=password, logged_in=logged_in, email=email, image_filename=image_filename)


@app.route('/update_prof2', methods=['POST'])
def update_prof2():
    if request.method == 'POST':
        new_firstname = request.form['new_firstname']
        new_lastname = request.form['new_lastname']
        new_location = request.form['new_location']
        new_email = request.form['new_email']
        new_phone_number = request.form['new_phone_number']
        new_password = request.form['new_password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Replace placeholders with your actual table and column names
        cursor.execute('''
            UPDATE seller_account 
            SET first_name=?, last_name=?, email=?, phone_number=?, password=?, location=? 
            WHERE email=?
        ''', (new_firstname, new_lastname, new_email, new_phone_number, new_password, new_location, session.get('email')))

        conn.commit()
        conn.close()

        return redirect(url_for('seller_profile'))


@app.route('/update_seller_picture', methods=['POST'])
def update_seller_picture():
    if request.method == 'POST':
        new_picture = request.files.get('new_seller_picture')
        email = session.get('email')

        if new_picture:
            # Save the new picture and update the database with the new picture filename
            image_filename = secure_filename(new_picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            new_picture.save(picture_path)

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Replace placeholders with your actual table and column names
            cursor.execute('UPDATE seller_account SET image_filename=? WHERE email=?', (image_filename, email))
            conn.commit()
            conn.close()

    return redirect(url_for('seller_profile'))


@app.route('/aboutus', methods=['GET'])
def aboutus():
    # Add your code to retrieve and display a product
    return render_template('aboutus.html')

@app.route('/history', methods=['GET'])
def history():
    # Add your code to handle the '/history' endpoint
    return render_template('history.html')

@app.route('/profile', methods=['GET'])
def profile():
    # Add your code to retrieve and display a product
    return render_template('profile.html')


@app.route('/prof', methods=['GET'])
def prof():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    email_name = session.get('email')
    logged_in = True if email_name else False

    cursor.execute('SELECT * FROM users WHERE email = ?',(email_name,))
    user_data = cursor.fetchone()

    if user_data:
        username = user_data[7]
        firstname = user_data[1]
        lastname = user_data[2]
        email = user_data[3]
        phone_number = user_data[10]
        birthday = user_data[8]
        location = user_data[9]
        id = user_data[0]
        image_filename = user_data[12]
        password = user_data[4]

    conn.close()

    return render_template('profile.html', username=username, lastname=lastname, firstname=firstname,
                            phone_number=phone_number, birthday=birthday, location=location, id=id,
                           image_filename=image_filename, email_name=email_name, logged_in=logged_in, email=email, password=password)




    
    # Route to handle the form submission
@app.route('/update_prof', methods=['POST'])
def update_prof():
    if request.method == 'POST':
        njewid = request.form['id']
        new_firstname = request.form['new_firstname']
        new_lastname = request.form['new_lastname']
        new_location = request.form['new_location']
        new_email = request.form['new_email']
        new_phone_number = request.form['new_phone_number']
        new_birthday = request.form['new_birthday']
        new_password = request.form['new_password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Update non-password fields
        cursor.execute('UPDATE users SET first_name=?, last_name=?, email=?, phone_number=?, birthday=?, location=? WHERE id=?',
                       (new_firstname, new_lastname, new_email, new_phone_number, new_birthday, new_location, njewid))

        # Update password field if a new password is provided
        if new_password:
            cursor.execute('UPDATE users SET password=? WHERE id=?', (new_password, njewid))

        conn.commit()
        conn.close()

        return redirect(url_for('prof'))

    
             # return 'Profile updated successfully!'
            # print(f"Error updating user profile: {e}")
            # return 'Error updating profile. Please try again.'
            
@app.route('/update_picture', methods=['POST'])
def update_picture():
    if request.method == 'POST':
        new_picture = request.files['new_profile_picture']
        email = session.get('email')

        if new_picture:
            # Save the new picture and update the database with the new picture filename
            image_filename = secure_filename(new_picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            new_picture.save(picture_path)

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Replace placeholders with your actual table and column names
            cursor.execute('UPDATE users SET image_filename=? WHERE email=?', (image_filename, email))
            conn.commit()
            conn.close()

    return redirect(url_for('prof'))
            
            

            
def get_wishlist_count(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM wishlist WHERE user_email = ?', (email,))
    count = cursor.fetchone()[0]

    conn.close()
    return count

# Define the route for the wishlist page
@app.route('/WISHLIST.html', methods=['GET', 'POST'])
def WISHLIST():
    # Get the user's email from the session
    email = session.get('email')

    # Check if the user is logged in
    logged_in = True if email else False

    # Check if the request method is POST (i.e., form submission)
    if request.method == 'POST':
        # Existing code for adding items to the wishlist
        product_name = request.form.get('product_name')
        image_filename = request.form.get('image_filename')
        product_price = request.form.get('product_price')
        stock = request.form.get('stock')

        # Insert data into the wishlist table associated with the user
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO wishlist (user_email, product_name, image_filename, product_price, stock)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, product_name, image_filename, product_price, stock))
        conn.commit()
        conn.close()

        # Redirect to the wishlist page or another page as needed
        return redirect('/WISHLIST.html')

    # Fetch wishlist data for the logged-in user from the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM wishlist WHERE user_email = ?', (email,))
    wishlist_data = cursor.fetchall()

    # Fetch additional user data (e.g., image filename)
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user_data = cursor.fetchone()
    if user_data:
        image_filename = user_data[12]

    # Close the database connection
    conn.close()

    # Get the number of items in the wishlist
    wishlist_count = get_wishlist_count(email)

    # Render the wishlist page with the fetched data and wishlist count
    return render_template('WISHLIST.html', wishlist=wishlist_data, email=email, logged_in=logged_in, image_filename=image_filename, wishlist_count=wishlist_count)

    
    
@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    if request.method == 'POST':
        # Check if the user is logged in
        if 'email' not in session:
            # Redirect to the login page
            return redirect(url_for('login'))

        product_id = request.form.get('product_id')

        # Retrieve product details from the main database based on product_id
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if the 'products' table has a 'product_id' column
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        if 'product_id' not in column_names:
            conn.close()
            return "Error: 'product_id' column not found in the 'products' table."

        cursor.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
        product = cursor.fetchone()

        if product:
            # Insert the product into the wishlist table associated with the user
            cursor.execute('''
                INSERT INTO wishlist (user_email, product_name, image_filename, product_price, stock)
                VALUES (?, ?, ?, ?, ?)
            ''', (session.get('email'), product[1], product[7], product[3], product[4]))
            conn.commit()
            conn.close()

            # Redirect to the original product page or wishlist page as needed
            return redirect('/product/' + str(product_id))
        else:
            conn.close()
            return "Error: Product not found."


@app.route('/remove_from_wishlist/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    # Remove the item with the given product_id from the wishlist table
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wishlist WHERE user_email = ? AND product_id = ?', (session.get('email'), product_id))
    conn.commit()
    conn.close()

    # Redirect back to the wishlist page
    return redirect('/WISHLIST.html')


@app.route('/clear_wishlist', methods=['POST'])
def clear_wishlist():
    # Clear all items from the wishlist table for the logged-in user
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM wishlist WHERE user_email = ?', (session.get('email'),))
    conn.commit()
    conn.close()

    # Redirect back to the wishlist page
    return redirect('/WISHLIST.html')
    
    
@app.route('/add_product_form1')
def add_product_form1():
    email = session.get('email')
    session_id = session.get('session_id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM seller_account WHERE session_id = ?', (session_id,))
    shop_details = cursor.fetchone()
    
    logged_in = True if email else False
    
    return render_template('add_product.html', email=email, logged_in=logged_in, shop_details=shop_details)



@app.route('/add_product_form11', methods=['GET', 'POST'])
def add_product_form11():
    # email = session.get('email')
    session_id = session.get('session_id')
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM seller_account WHERE session_id = ?', (session_id,))
    shop_details = cursor.fetchone()
    
    if shop_details:
        shop_name = shop_details[6]
        
    conn.commit()
    # conn.close()
    
    return render_template('add_product.html', shop_details=shop_details)

@app.route('/addpr')
def addpr():
    email = session.get('email')
    logged_in = True if email else False
    session_id = session.get('session_id')
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM seller_account WHERE session_id = ?', (session_id,))
    shop_details = cursor.fetchone()
    
    
    
    return render_template('add_product.html',shop_details=shop_details, email=email, logged_in=logged_in)


@app.route('/my_products')
def my_products():
    
    session_id = session.get('session_id')
    
    email = session.get('email')
    logged_in = True if email else False

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        # Fetch all products from the database
        cursor.execute('SELECT * FROM products WHERE session_id = ? ', (session_id,))
        products = cursor.fetchall()
    except sqlite3.Error as e:
        flash('An error occurred while fetching products from the database.', 'error')
        return render_template('error.html', error=str(e))
    finally:
        conn.close()

    return render_template('my_products.html', products=products, email=email, logged_in=logged_in)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get updated information from the form
        new_name = request.form.get('new_name')
        new_description = request.form.get('new_description')
        new_price = float(request.form.get('new_price'))  # Convert to float for calculations
        new_stock = int(request.form.get('new_stock'))  # Convert to int for calculations
        new_variation = request.form.get('new_variation')
        new_category = request.form.get('new_category')
        new_discount_rate = float(request.form.get('new_discount_rate'))

        try:
            # Calculate new discount_amount and discounted_price
            discount_amount = new_price * (new_discount_rate / 100)
            discounted_price = new_price - discount_amount

            # Update the product information in the database
            cursor.execute('''
                UPDATE products 
                SET name=?, description=?, price=?, stock=?, variations=?, category=?, 
                discount_rate=?, discount_amount=?, discounted_price=?
                WHERE product_id=?
            ''', (new_name, new_description, new_price, new_stock, new_variation, new_category,
                  new_discount_rate, discount_amount, discounted_price, product_id))

            conn.commit()

            flash('Product updated successfully!', 'success')
            return redirect(url_for('my_products'))
        except sqlite3.Error as e:
            flash('An error occurred while updating the product.', 'error')
            return render_template('error.html', error=str(e))
        finally:
            conn.close()

    # Fetch the current product details for pre-filling the form
    cursor.execute('SELECT * FROM products WHERE product_id=?', (product_id,))
    product = cursor.fetchone()
    conn.close()

    return render_template('edit_product.html', product=product)



# Add route for deleting a product
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        # Delete the product from the database
        cursor.execute('DELETE FROM products WHERE product_id=?', (product_id,))
        conn.commit()

        flash('Product deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash('An error occurred while deleting the product.', 'error')
        return render_template('error.html', error=str(e))
    finally:
        conn.close()

    return redirect(url_for('my_products'))


@app.route('/uploads/<image_filename>')
def uploaded_file(image_filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], image_filename)

def generate_category_sidebar(categories):
    sidebar_html = render_template('sidebar.html', categories=categories)
    return sidebar_html

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Handle search form submission
        search_query = request.form.get('search_query')
        category = request.form.get('category')

        # Build the SQL query based on the search query and category
        sql_query = "SELECT * FROM products WHERE name LIKE ?"
        params = ['%' + search_query + '%']

        if category:
            sql_query += " AND category = ?"
            params.append(category)

        # Perform the search in the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(sql_query, tuple(params))
        search_results = cursor.fetchall()
        conn.close()

        # Format the search results as a list of dictionaries
        search_list = []
        for result in search_results:
            product_dict = {
                'id': result[0],
                'name': result[1],
                'description': result[2],
                'price': result[3],
                'image_filename': result[7],
                'category': result[6]
            }
            search_list.append(product_dict)

        # Example categories (replace with actual data from your database)
        categories = ["sports equipment", "sportswear", "dietary product", "fitness equipment", "protective equipment"]

        # Generate the HTML for the category sidebar
        category_filter_html = generate_category_sidebar(categories)

        return render_template('shop.html', search_query=search_query, results=search_list, category_filter_html=category_filter_html)

    # Render the search form
    return render_template('search.html', categories=categories)



@app.route('/filter_by_category/<string:category>')
def filter_by_category(category):
    # Perform the filtering logic based on the selected category
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    filtered_results = cursor.fetchall()
    conn.close()

    # Format the filtered results as a list of dictionaries
    filtered_list = []
    for result in filtered_results:
        product_dict = {
            'id': result[0],
            'name': result[1],
            'description': result[2],
            'price': result[3],
            'image_filename': result[7]
        }
        filtered_list.append(product_dict)

    # Example categories (replace with actual data from your database)
    categories = ["sports equipment", "sportswear", "dietary product", "fitness equipment", "protective equipment"]
    
    # Generate the HTML for the category sidebar
    category_filter_html = generate_category_sidebar(categories)

    return render_template('shop.html', results=filtered_list, category_filter_html=category_filter_html)


    
@app.route('/order', methods=['GET'])
def order_detail():
    user_email = session.get('email')

    if not user_email:
        flash('Please log in to view order details.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Fetch orders and order_items from the database for the specific user
    filter_status = request.args.get('status', 'all')
    query = '''
    SELECT orders.order_id, firstname, lastname, email, address, phone_number, payment_method, order_date, status, cancel_status,
        product_name, variation, product_price, quantity, subtotal
    FROM orders
    JOIN order_items ON orders.order_id = order_items.order_id
    WHERE orders.email = ? AND (orders.status = ? OR ? = 'all')
    ORDER BY orders.order_id, order_items.item_id
    '''
    params = (user_email, filter_status, filter_status)  # Fix the duplicate status placeholder
    cursor.execute(query, params)

    # Fetch all results
    rows = cursor.fetchall()

    # Organize the results into a dictionary for easy processing in the template
    orders = {}
    for row in rows:
        order_id = row[0]
        if order_id not in orders:
            orders[order_id] = {
                'order_id': row[0],
                'firstname': row[1],
                'lastname': row[2],
                'email': row[3],
                'address': row[4],
                'phone_number': row[5],
                'payment_method': row[6],
                'order_date': row[7],
                'status': row[8],
                'order_items': [],
            }
        orders[order_id]['order_items'].append({
            'product_name': row[9],
            'variation': row[10],
            'product_price': row[11],
            'quantity': row[12],
            'subtotal': row[13],
        })

    conn.close()

    return render_template('order_detail.html', orders=orders.values(), filter_status=filter_status)



@app.route('/order/<int:order_id>/cancel', methods=['GET', 'POST'])
def cancel_order(order_id):
    user_email = session.get('email')

    if not user_email:
        flash('Please log in to cancel orders.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT status, cancel_status
        FROM orders
        WHERE order_id = ? AND email = ?
    ''', (order_id, user_email))

    order_status, cancel_status = cursor.fetchone()

    if not order_status:
        flash('Order not found.', 'error')
        conn.close()
        return redirect(url_for('order_detail'))

    if request.method == 'POST':
        if order_status == 'Pending' and cancel_status != 'Canceled':
            cancellation_reason = request.form.get('cancellation_reason')

            # Update the cancellation_reason and cancel_status
            cursor.execute('''
                UPDATE orders
                SET cancellation_reason = ?, cancel_status = 'Pending'
                WHERE order_id = ? AND email = ?
            ''', (cancellation_reason, order_id, user_email))

            conn.commit()
            flash(f'Cancellation request for Order #{order_id} has been submitted.', 'success')

        conn.close()
        return redirect(url_for('order_detail'))

    conn.close()

    return render_template('cancel_order.html', order_id=order_id, order_status=order_status)





@app.route('/update_status', methods=['GET', 'POST'])
def update_status():
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')

    # Update the order status in the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?', (new_status, order_id))
    conn.commit()
    conn.close()

    # Redirect back to the latest orders pag

    # Redirect back to the latest orders page
    return redirect('user_transaction')  # Replace with the actual URL for your latest orders page



@app.route('/user_transaction', methods=['GET', 'POST'])
def user_transaction():
    user_email = session.get('email')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    email = session.get('email')
    logged_in = True if email else False

    # Fetch the shop_name associated with the logged-in seller
    cursor.execute('SELECT shop_name FROM seller_account WHERE email = ?', (user_email,))
    result = cursor.fetchone()

    if result:
        shop_name = result[0]

        # Fetch orders and order_items from the database for the current seller
        cursor.execute('''
            SELECT orders.order_id, firstname, lastname, email, address, phone_number, payment_method, order_date, status,
                   product_name, variation, product_price, quantity, subtotal
            FROM orders
            JOIN order_items ON orders.order_id = order_items.order_id
            WHERE orders.shop_name = ?
            ORDER BY orders.order_id, order_items.item_id
        ''', (shop_name,))

        # Fetch all results
        rows = cursor.fetchall()

        # Organize the results into a dictionary for easy processing in the template
        orders = {}
        for row in rows:
            order_id = row[0]
            if order_id not in orders:
                orders[order_id] = {
                    'order_id': row[0],
                    'firstname': row[1],
                    'lastname': row[2],
                    'email': row[3],
                    'address': row[4],
                    'phone_number': row[5],
                    'payment_method': row[6],
                    'order_date': row[7],
                    'status': row[8],
                    'order_items': [],
                }
            orders[order_id]['order_items'].append({
                'product_name': row[9],
                'variation': row[10],
                'product_price': row[11],
                'quantity': row[12],
                'subtotal': row[13],
            })

        conn.close()

        return render_template('user_transaction.html', orders=orders.values(), logged_in=logged_in, email=email)
    else:
        # Handle the case where the shop_name is not found for the logged-in seller
        flash('Shop name not found for the logged-in seller.', 'error')
        return redirect(url_for('login'))




@app.route('/order_tracking/<order_id>', methods=['GET', 'POST'])
def order_tracking(order_id):
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Fetch orders and order_items from the database
    cursor.execute(' SELECT * FROM orders WHERE order_id = ?', (order_id,))
    order = cursor.fetchone()
    
    # Organize the results into a dictionary for easy processing in the template
    
    
    
    expected_date = "december 09, 2023"  # Replace this with the actual expected date from your database
    

    
    # cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?', (new_status, order_id))
    conn.commit()
    conn.close()
    
    

    return render_template('order_tracking.html', order_id=order_id, expected_date=expected_date, order=order)


@app.route('/own_address', methods=['GET'])
def own_address():
    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM addresses')
            addresses = cursor.fetchall()
        return render_template('own_address.html', addresses=addresses)
    except sqlite3.Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update_address/<int:id>', methods=['GET', 'POST'])
def update_address(id):
    try:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM addresses WHERE id = ?', (id,))
            address = cursor.fetchone()

            if address is None:
                abort(404)

            if request.method == 'POST':
                new_values = (
                    request.form['fullName'],
                    request.form['phoneNumber'],
                    request.form['region'],
                    request.form['province'],
                    request.form['city'],
                    request.form['barangay'],
                    request.form['postalCode'],
                    request.form['streetName'],
                    request.form['building'],
                    request.form['houseNo'],
                    id
                )

                cursor.execute('''
                    UPDATE addresses
                    SET fullName=?, phoneNumber=?, region=?, province=?, city=?,
                        barangay=?, postalCode=?, streetName=?, building=?, houseNo=?
                    WHERE id=?
                ''', new_values)

                conn.commit()

                return jsonify({'success': True, 'message': 'Address updated successfully'})

    except sqlite3.Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('update_address.html', address=address)

@app.route('/add_address', methods=['GET', 'POST'])
def add_address():
    try:
        if request.method == 'POST':
            new_values = (
                request.form['fullName'],
                request.form['phoneNumber'],
                request.form['region'],
                request.form['province'],
                request.form['city'],
                request.form['barangay'],
                request.form['postalCode'],
                request.form['streetName'],
                request.form['building'],
                request.form['houseNo']
            )

            with sqlite3.connect('users.db') as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO addressesnt
                    (fullName, phoneNumber, region, province, city, barangay, postalCode, streetName, building, houseNo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', new_values)

                conn.commit()

            return jsonify({'success': True, 'message': 'Address added successfully'})

    except sqlite3.Error as e:
        return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('add_address.html')


@app.route('/seller_registration', methods=['GET', 'POST'])
def seller_registration():
    
    session_id = session.get('session_id')
    
    if request.method == 'POST':
        # Get form data
        # shop_id = secrets.token_hex(4) 
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        shop_name = request.form.get('shop_name')
        location = request.form.get('location')
        phone_number = request.form.get('phone_number')
        

        # Check if the user already exists in the users table (buyer account)
        conn_users = get_db()
        cursor_users = conn_users.cursor()
        cursor_users.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor_users.fetchone()
        cursor_users.close()

        # Check if the user already has a seller account
        conn_seller = get_db()
        cursor_seller = conn_seller.cursor()
        cursor_seller.execute("SELECT * FROM seller_account WHERE email = ?", (email,))
        existing_seller = cursor_seller.fetchone()
        cursor_seller.close()

        if existing_user:
            if existing_seller:
                # If the user already has a seller account, update the session role
                session['role'] = 'seller'

                flash("You already have a seller account! Welcome back!", "success")
                return redirect(url_for('sellerpage'))

            # Save seller-specific information to the seller_account table
            # session_id = secrets.token_hex(5)
            shop_id = secrets.token_hex(5)

            conn_seller = get_db()
            cursor_seller = conn_seller.cursor()
            cursor_seller.execute('''
                INSERT INTO seller_account (first_name, last_name, email, password, role, shop_name, location, phone_number, session_id, shop_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, password, 'seller', shop_name, location, phone_number, session_id, shop_id))
            conn_seller.commit()
            cursor_seller.close()

            flash("Your seller account has been created successfully!", "success")
            return redirect(url_for('sellerpage'))

    # Get buyer information for pre-filling the form
    conn_users = get_db()
    cursor_users = conn_users.cursor()
    cursor_users.execute("SELECT * FROM users WHERE email = ?", (session.get('email'),))
    buyer_info = cursor_users.fetchone()
    cursor_users.close()

    # Render the seller registration form with default values from the buyer's information
    return render_template('seller_registration.html', buyer_info=buyer_info)




def get_orders_with_reasons():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT order_id, firstname, lastname, cancellation_reason
        FROM orders
        WHERE status = 'Pending' AND cancellation_reason IS NOT NULL
    ''')

    rows = cursor.fetchall()

    orders_with_reasons = {}
    for row in rows:
        order_id = row[0]
        if order_id not in orders_with_reasons:
            orders_with_reasons[order_id] = {
                'order_id': order_id,
                'firstname': row[1],
                'lastname': row[2],
                'cancellation_reason': row[3],
            }

    conn.close()

    return orders_with_reasons

@app.route('/seller_cancellation', methods=['GET', 'POST'])
def seller_cancellation():
    if request.method == 'POST':
        # Handle the form submission if needed
        pass

    # Retrieve orders with cancellation reasons for the seller's shop from the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Assuming 'seller_shop_name' is the session variable containing the current seller's shop_name
    seller_shop_name = session.get('seller_shop_name')

    cursor.execute('''
        SELECT order_id, firstname, lastname, cancellation_reason
        FROM orders
        WHERE status = 'Pending' AND cancellation_reason IS NOT NULL AND shop_name = ?
    ''', (seller_shop_name,))

    orders_with_reasons = cursor.fetchall()

    conn.close()

    orders_with_reasons = get_orders_with_reasons()

    return render_template('seller_cancellation.html', orders_with_reasons=orders_with_reasons)




@app.route('/seller/accept_order/<int:order_id>', methods=['POST'])
def seller_accept_order(order_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        # Check if the order has a pending cancellation request
        cursor.execute('''
            SELECT status, cancel_status
            FROM orders
            WHERE order_id = ? AND status = 'Pending'
        ''', (order_id,))

        order_status, cancel_status = cursor.fetchone()

        if order_status == 'Pending' and cancel_status == 'Pending':
            # Update the order status as accepted and set seller_decision
            cursor.execute('''
                UPDATE orders
                SET status = 'Canceled', seller_decision = 'Accepted'
                WHERE order_id = ? AND status = 'Pending' AND cancel_status = 'Pending'
            ''', (order_id,))

            conn.commit()
            flash(f'Order #{order_id} has been accepted.', 'success')
        else:
            flash(f'Order #{order_id} cannot be accepted. Check the order status.', 'danger')
    except sqlite3.Error as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()

    # Redirect back to the seller_cancellation page
    return redirect(url_for('seller_cancellation'))


@app.route('/seller/deny_order/<int:order_id>', methods=['POST'])
def seller_deny_order(order_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        # Update the order status as denied and set seller_decision
        cursor.execute('''
            UPDATE orders
            SET status = 'Denied', seller_decision = 'Denied'
            WHERE order_id = ? AND status = 'Pending'
        ''', (order_id,))

        conn.commit()
        flash(f'Order #{order_id} has been denied.', 'success')
    except sqlite3.Error as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()

    # Redirect back to the seller_cancellation page
    return redirect(url_for('seller_cancellation'))




def get_db_connection():
    return sqlite3.connect('users.db')

@app.route('/view_shop/<shop_id>', methods=['GET', 'POST'])
def view_shop(shop_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch seller information
    cursor.execute('SELECT * FROM seller_account WHERE shop_id = ?', (shop_id,))
    seller = cursor.fetchone()

    # Check if seller information is found
    if seller:
        # Assuming 'shop_id' is a unique identifier for the shop
        shop_name = seller[6]  # Accessing the first tuple in the list
        contact = seller[8]
        banner = seller[10]
        first = seller[1]
        last = seller[2]
        location = seller[7]
        image_filename = seller[10]  # Assuming 'image_filename' is at index 10 in the tuple

        # Assuming you want to display the image filename of the first product.
        cursor.execute('SELECT * FROM products WHERE shop_id = ?', (shop_id,))
        products = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('view_shop.html', seller=seller, products=products, shop_name=shop_name, contact=contact, banner=banner, first=first, last=last, location=location, image_filename=image_filename)

    # Handle case where seller information is not found
    else:
        cursor.close()
        conn.close()
        flash('Seller not found', 'error')
        return redirect(url_for('some_error_page'))


            


@app.route('/users_wallet', methods=['GET', 'POST'])
def users_wallet():
    
    email = session.get('email')
    logged_in = True if email else False
    
    if request.method == 'POST':
        # Handle cash-in requests for users
        user_email = request.form.get('user_email')  # Change 'user_id' to 'user_email'
        amount = float(request.form.get('amount'))  # Assuming the amount is a float
        session_id = session.get('email')
        # Perform wallet operations, e.g., record the transaction for admin approval
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # cursor.execute('SELECT * FROM users WHERE email = ?', (session_id,))
        # user_data = cursor.fetall()
        
        # if user_data:
        #     email = user_data[3]

        # Example: Insert a transaction record into admin_wallet table with 'pending' status
        cursor.execute('INSERT INTO admin_wallet (user_email, amount, status, transaction_type) VALUES (?, ?, ?, ?)',
                       (user_email, amount, 'pending', 'cash_in'))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('users_wallet') )

    # Fetch pending transactions for user's view
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Example: Fetch all pending transactions for the user
    cursor.execute('SELECT * FROM admin_wallet WHERE user_email = ? AND status = ?', ('user_email', 'pending'))
    pending_transactions = cursor.fetchall()

    # Example: Fetch user's wallet balance
    cursor.execute('SELECT wallet_balance FROM users WHERE email = ?', ('user_email',))
    user_data = cursor.fetchone()

    if user_data:
        user_wallet_balance = user_data[0]
    else:
        # Handle the case when no user is found with the provided email
        user_wallet_balance = None  # Or set a default value or handle the situation as needed
    
    conn.commit()
    cursor.close()
    conn.close()

    return render_template('users_wallet.html', pending_transactions=pending_transactions, user_wallet_balance=user_wallet_balance, email=email, logged_in=logged_in)

@app.route('/seller_wallet', methods=['GET', 'POST'])
def seller_wallet():
    email = session.get('email')
    logged_in = True if email else False
    
    if request.method == 'POST':
        # Handle cash-in and cash-out requests for sellers
        seller_email = request.form.get('seller_email')  # Change 'seller_id' to 'seller_email'
        amount = float(request.form.get('amount'))  # Assuming the amount is a float
        # transaction_type = request.form.get('transaction_type')  # 'cash_in' or 'cash_out'

        # Perform wallet operations, e.g., record the transaction for admin approval
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO admin_wallet (user_email, amount, status, transaction_type) VALUES (?, ?, ?, ?)',
                       (seller_email, amount, 'pending', 'cash_out'))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('seller_wallet'))

    # Fetch pending transactions for seller's view
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admin_wallet WHERE user_email = ? AND status = ?', ('seller_email', 'pending'))
    pending_transactions = cursor.fetchall()

    cursor.execute('SELECT wallet_balance FROM seller_account WHERE email = ?', ('seller_email',))
    seller_data = cursor.fetchone()

    if seller_data:
        seller_wallet_balance = seller_data[0]
    else:
        seller_wallet_balance = None  # Or set a default value or handle the situation as needed

    conn.commit()
    cursor.close()
    conn.close()

    return render_template('seller_wallet.html', pending_transactions=pending_transactions, seller_wallet_balance=seller_wallet_balance, email=email, logged_in=logged_in)



@app.route('/admin_wallet1', methods=['GET', 'POST'])
def admin_wallet1():
    if request.method == 'POST':
        # Handle admin actions - confirm or deny wallet transactions
        transaction_id = request.form.get('transaction_id')
        action = request.form.get('action')  # 'confirm' or 'deny'

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        if action == 'confirm':
            # Example: Update the status of the transaction to 'confirmed'
            cursor.execute('UPDATE admin_wallet SET status = ? WHERE id = ?', ('confirmed', transaction_id))

            # Fetch user email and amount for the confirmed transaction
            # cursor.execute('SELECT user_email, amount FROM admin_wallet WHERE id = ? AND status = ?', (transaction_id, 'confirmed'))
            # transaction_data = cursor.fetchone()
            
            

            cursor.execute('SELECT * admin_wallet WHERE id = ? AND status = ?', (transaction_id, 'confirmed'))
            ewallet_data = cursor.fetchone()
                
            if ewallet_data:
                amount = ewallet_data[2]
                email_name = ewallet_data[1]

                # Update the user's wallet balance
            cursor.execute('UPDATE users SET wallet_balance = wallet_balance + ? WHERE email = ?', (amount, email_name))

        elif action == 'deny':
            # Example: Update the status of the transaction to 'denied'
            cursor.execute('UPDATE admin_wallet SET status = ? WHERE id = ?', ('denied', transaction_id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('admin_wallet'))

    # Fetch pending transactions for admin approval
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Example: Fetch all pending transactions
    cursor.execute('SELECT * FROM admin_wallet WHERE status = ?', ('pending',))
    pending_transactions = cursor.fetchall()
    
    
    

    conn.commit()
    cursor.close()
    conn.close()

    return render_template('admin_wallet.html', pending_transactions=pending_transactions)



@app.route('/admin_wallet', methods=['GET', 'POST'])
def admin_wallet():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM admin_wallet ORDER by id DESC')
    pending_transactions = cursor.fetchall()
    
    
    conn.commit()
    conn.close()

    return render_template('admin_wallet.html', pending_transactions=pending_transactions)




@app.route('/update_cashin_request2', methods=['POST'])
def update_cashin_request2():
    if request.method == 'POST':
        cashout_id = request.form['cashout_id']
        status = request.form['status']
        amount = request.form['amount']
        email = request.form['email'] 
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Update cashout status including shop_id
        cursor.execute("UPDATE admin_wallet SET status=? WHERE id=?", (status, cashout_id))
        
        if status == 'confirmed':

            # Update balance in ewallet table when status is 'Deny request'
            cursor.execute("UPDATE user SET wallet_balance = wallet_balance + ? WHERE email=?", (amount, email))
            
        conn.commit()
        conn.close()
        return "Status updated successfully"
    
@app.route('/update_cashin_request', methods=['POST'])
def update_cashin_request():
    try:
        if request.method == 'POST':
            cashout_id = request.form['cashout_id']
            status = request.form['status']
            amount = request.form['amount']
            email = request.form['email']

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Use placeholders to prevent SQL injection
            cursor.execute("UPDATE admin_wallet SET status=? WHERE id=?", (status, cashout_id))

            if status == 'confirmed':
                # Update balance in ewallet table when status is 'Deny request'
                cursor.execute("UPDATE users SET wallet_balance = wallet_balance + ? WHERE email=?", (amount, email))

            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Status updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})







@app.route('/seller_dashboard', methods=['GET', 'POST'])
def seller_dashboard():
    return render_template('seller_dashboard.html')




if __name__ == '__main__':
    app.run(debug=True)

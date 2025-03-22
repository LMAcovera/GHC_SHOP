from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import UserRole
import os
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'glamorosa_db'
}

# Database connection function
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != UserRole.ADMIN.value:
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Update the UPLOAD_FOLDER to use absolute path
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'products')
VALID_IDS_FOLDER = os.path.join(UPLOAD_FOLDER, 'valid_ids')
PAYMENT_PROOF_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'payments', 'proof')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VALID_IDS_FOLDER, exist_ok=True)
os.makedirs(PAYMENT_PROOF_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

APPOINTMENT_UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'appointments')
os.makedirs(APPOINTMENT_UPLOADS, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Modified query to use RAND() for random ordering
    cursor.execute('''
        SELECT p.*, c.name as category_name, 
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as primary_image
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        ORDER BY RAND()
    ''')
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                         products=products, 
                         user_name=session.get('full_name'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute('SELECT email FROM users WHERE email = %s', (email,))
            if cursor.fetchone():
                flash('Email already registered', 'error')
                return redirect(url_for('signup'))
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (full_name, email, phone_number, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            ''', (full_name, email, phone, password_hash, UserRole.BUYER.value))
            
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except mysql.connector.Error as err:
            flash(f'An error occurred: {err}', 'error')
            return redirect(url_for('signup'))
        finally:
            cursor.close()
            conn.close()
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get user by email
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                # Store user info in session
                session['user_id'] = user['user_id']
                session['full_name'] = user['full_name']
                session['email'] = user['email']
                session['role'] = user['role']
                
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'error')
                return redirect(url_for('login'))
                
        except mysql.connector.Error as err:
            flash(f'An error occurred: {err}', 'error')
            return redirect(url_for('login'))
        finally:
            cursor.close()
            conn.close()
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user_name=session.get('full_name'))

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get today's appointments
    cursor.execute('''
        SELECT a.*, u.full_name, c.name as category_name,
               TIME_FORMAT(a.appointment_time, '%h:%i %p') as formatted_time
        FROM appointments a
        JOIN users u ON a.user_id = u.user_id
        JOIN categories c ON a.category_id = c.category_id
        WHERE DATE(a.appointment_date) = CURDATE()
        ORDER BY a.appointment_time
    ''')
    todays_appointments = cursor.fetchall()
    
    # Get upcoming appointments (next 7 days)
    cursor.execute('''
        SELECT a.*, u.full_name, c.name as category_name,
               DATE_FORMAT(a.appointment_date, '%b %d, %Y') as formatted_date,
               TIME_FORMAT(a.appointment_time, '%h:%i %p') as formatted_time
        FROM appointments a
        JOIN users u ON a.user_id = u.user_id
        JOIN categories c ON a.category_id = c.category_id
        WHERE a.appointment_date > CURDATE() 
        AND a.appointment_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        ORDER BY a.appointment_date, a.appointment_time
    ''')
    upcoming_appointments = cursor.fetchall()
    
    # Get active rentals
    cursor.execute('''
        SELECT r.*, p.name, u.full_name as customer_name
        FROM rentals r
        JOIN products p ON r.product_id = p.product_id
        JOIN users u ON r.user_id = u.user_id
        WHERE r.status IN ('processing', 'shipped', 'delivered')
        AND r.end_date >= CURDATE()
        ORDER BY r.end_date
    ''')
    active_rentals = cursor.fetchall()
    
    # Get overdue rentals
    cursor.execute('''
        SELECT r.*, p.name, u.full_name as customer_name,
               DATEDIFF(CURDATE(), r.end_date) as days_overdue
        FROM rentals r
        JOIN products p ON r.product_id = p.product_id
        JOIN users u ON r.user_id = u.user_id
        WHERE r.status IN ('shipped', 'delivered')
        AND r.end_date < CURDATE()
        ORDER BY r.end_date
    ''')
    overdue_rentals = cursor.fetchall()
    
    # Get categories
    cursor.execute('SELECT * FROM categories')
    categories = cursor.fetchall()
    
    # Get products with their primary images and sizes
    cursor.execute('''
        SELECT p.*, c.name as category_name, 
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as primary_image,
               GROUP_CONCAT(ps.size) as sizes
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN product_sizes ps ON p.product_id = ps.product_id
        GROUP BY p.product_id
        ORDER BY p.created_at DESC
    ''')
    products = cursor.fetchall()
    
    # Get orders with product and user details
    cursor.execute('''
        SELECT o.*, 
               p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image,
               u.full_name as customer_name,
               ua.complete_address,
               ua.contact_number
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN users u ON o.user_id = u.user_id
        JOIN user_addresses ua ON o.address_id = ua.address_id
        ORDER BY o.created_at DESC
    ''')
    orders = cursor.fetchall()
    
    # Get rental requests with product and user details
    cursor.execute('''
        SELECT r.*, 
               p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image,
               u.full_name as customer_name
        FROM rental_requests r
        JOIN products p ON r.product_id = p.product_id
        JOIN users u ON r.user_id = u.user_id
        ORDER BY r.created_at DESC
    ''')
    rental_requests = cursor.fetchall()
    
    # Get rentals with product details
    cursor.execute('''
        SELECT r.*, 
               p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
        FROM rentals r
        JOIN products p ON r.product_id = p.product_id
        ORDER BY r.created_at DESC
    ''')
    rentals = cursor.fetchall()
    
    # Get appointment requests with user and category details
    cursor.execute('''
        SELECT ar.*, u.full_name, u.phone_number as contact_number, c.name as category_name 
        FROM appointment_requests ar
        JOIN users u ON ar.user_id = u.user_id
        JOIN categories c ON ar.category_id = c.category_id
        ORDER BY ar.created_at DESC
    ''')
    appointment_requests = cursor.fetchall()
    
    # Get appointments
    cursor.execute('''
        SELECT a.*, u.full_name, u.phone_number as contact_number, 
               c.name as category_name 
        FROM appointments a
        JOIN users u ON a.user_id = u.user_id
        JOIN categories c ON a.category_id = c.category_id
        ORDER BY a.appointment_date, a.appointment_time
    ''')
    appointments = cursor.fetchall()
    
    # Get reservation requests with product and user details
    cursor.execute('''
        SELECT r.*, 
               p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image,
               u.full_name as customer_name
        FROM reservation_requests r
        JOIN products p ON r.product_id = p.product_id
        JOIN users u ON r.user_id = u.user_id
        ORDER BY r.created_at DESC
    ''')
    reservation_requests = cursor.fetchall()
    
    # Get reservations with product details
    cursor.execute('''
        SELECT r.*, p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
        FROM reservations r
        JOIN products p ON r.product_id = p.product_id
        ORDER BY r.created_at DESC
    ''')
    reservations = cursor.fetchall()
    
    # Format dates and times for appointment requests
    for request in appointment_requests:
        if request['preferred_date']:
            request['formatted_date'] = request['preferred_date'].strftime('%b %d, %Y')
        if request['preferred_time']:
            total_minutes = int(request['preferred_time'].total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            request['formatted_time'] = f"{hours:02d}:{minutes:02d}"
            
    # Format dates and times for appointments
    for appointment in appointments:
        if appointment['appointment_date']:
            appointment['formatted_date'] = appointment['appointment_date'].strftime('%b %d, %Y')
        if appointment['appointment_time']:
            total_minutes = int(appointment['appointment_time'].total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            appointment['formatted_time'] = f"{hours:02d}:{minutes:02d}"
    
    cursor.close()
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         categories=categories, 
                         products=products,
                         orders=orders,
                         rental_requests=rental_requests,
                         rentals=rentals,
                         reservation_requests=reservation_requests,
                         appointment_requests=appointment_requests,
                         appointments=appointments,
                         todays_appointments=todays_appointments,
                         upcoming_appointments=upcoming_appointments,
                         active_rentals=active_rentals,
                         overdue_rentals=overdue_rentals,
                         reservations=reservations)

@app.route('/admin/add-product', methods=['POST'])
@login_required
@admin_required
def add_product():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Insert product details (removed size from the query)
        cursor.execute('''
            INSERT INTO products (name, category_id, description, regular_price, 
                                rental_fee_per_day, color, material)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            request.form['name'],
            request.form['category_id'],
            request.form['description'],
            request.form['regular_price'],
            request.form['rental_fee_per_day'],
            request.form['color'],
            request.form['material']
        ))
        
        product_id = cursor.lastrowid
        
        # Handle sizes
        sizes = request.form.getlist('sizes[]')
        for size in sizes:
            if size.strip():  # Only insert non-empty sizes
                cursor.execute('''
                    INSERT INTO product_sizes (product_id, size)
                    VALUES (%s, %s)
                ''', (product_id, size.strip()))
        
        # Handle image uploads
        images = request.files.getlist('images')
        for i, image in enumerate(images):
            if image and allowed_file(image.filename):
                filename = secure_filename(f"{product_id}_{image.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Ensure the directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Save the file
                image.save(filepath)
                
                # Store the relative path in database
                relative_path = os.path.join('uploads', 'products', filename).replace('\\', '/')
                
                cursor.execute('''
                    INSERT INTO product_images (product_id, image_path, is_primary)
                    VALUES (%s, %s, %s)
                ''', (product_id, relative_path, i == 0))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/delete-product/<int:product_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete product (images will be deleted via ON DELETE CASCADE)
        cursor.execute('DELETE FROM products WHERE product_id = %s', (product_id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/product/<int:product_id>')
def view_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get product details with category
    cursor.execute('''
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = %s
    ''', (product_id,))
    product = cursor.fetchone()
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('index'))
    
    # Get all product images
    cursor.execute('SELECT * FROM product_images WHERE product_id = %s', (product_id,))
    images = cursor.fetchall()
    
    # Get product sizes
    cursor.execute('SELECT * FROM product_sizes WHERE product_id = %s', (product_id,))
    sizes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('product_details.html', 
                         product=product, 
                         images=images, 
                         sizes=sizes,
                         user_name=session.get('full_name'))

@app.route('/checkout')
@login_required
def checkout():
    product_id = request.args.get('product_id')
    size = request.args.get('size')
    
    # Get product details
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT p.*, c.name as category_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as primary_image
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = %s
    ''', (product_id,))
    product = cursor.fetchone()
    
    # Get user's saved addresses
    cursor.execute('SELECT * FROM user_addresses WHERE user_id = %s', (session['user_id'],))
    addresses = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('checkout.html', 
                         product=product, 
                         size=size,
                         addresses=addresses)

@app.route('/place-order', methods=['POST'])
@login_required
def place_order():
    try:
        # Get form data
        product_id = request.form.get('product_id')
        size = request.form.get('size')
        payment_method = request.form.get('paymentMethod')
        total_amount = request.form.get('total_amount')
        
        # Handle address
        if 'savedAddress' in request.form:
            address_id = request.form.get('savedAddress')
        else:
            # Create new address
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_addresses (user_id, full_name, contact_number, complete_address)
                VALUES (%s, %s, %s, %s)
            ''', (
                session['user_id'],
                request.form.get('fullName'),
                request.form.get('contactNumber'),
                request.form.get('address')
            ))
            
            address_id = cursor.lastrowid
            
            # Save address if checkbox is checked
            if request.form.get('saveAddress'):
                cursor.execute('UPDATE user_addresses SET is_default = 0 WHERE user_id = %s', 
                             (session['user_id'],))
                cursor.execute('UPDATE user_addresses SET is_default = 1 WHERE address_id = %s', 
                             (address_id,))
            
            conn.commit()
            cursor.close()
            conn.close()

        # Handle GCash payment details
        gcash_reference = None
        payment_proof_path = None
        
        if payment_method == 'GCASH':
            gcash_reference = request.form.get('gcash_reference')
            payment_proof = request.files.get('payment_proof')
            
            if payment_proof and allowed_file(payment_proof.filename):
                filename = secure_filename(f"order_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{payment_proof.filename.rsplit('.', 1)[1].lower()}")
                payment_proof_path = os.path.join('uploads/payments/proof', filename)
                payment_proof.save(os.path.join('static', payment_proof_path))

        # Create order
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (
                user_id, product_id, address_id, size, total_amount, 
                payment_method, delivery_method, gcash_reference, payment_proof
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            session['user_id'],
            product_id,
            address_id,
            size,
            total_amount,
            payment_method,
            'delivery' if payment_method == 'GCASH' else 'pickup',
            gcash_reference,
            payment_proof_path
        ))
        
        order_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'success': True, 'orderId': order_id})
        
    except Exception as e:
        print(f"Error in place_order: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/order-details/<int:order_id>')
@login_required
@admin_required
def get_order_details(order_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT o.*, 
               p.name as product_name, 
               u.full_name as customer_name,
               ua.complete_address, 
               ua.contact_number,
               o.payment_method,
               o.gcash_reference,
               o.payment_proof,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        JOIN users u ON o.user_id = u.user_id
        JOIN user_addresses ua ON o.address_id = ua.address_id
        WHERE o.order_id = %s
    ''', (order_id,))
    
    order = cursor.fetchone()
    
    if order:
        # Format dates
        order['created_at'] = order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Ensure payment_proof path is properly formatted
        if order['payment_proof']:
            order['payment_proof'] = order['payment_proof'].replace('\\', '/')
    
    cursor.close()
    conn.close()
    
    return jsonify(order)

@app.route('/admin/update-order-status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    try:
        status = request.json.get('status')
        if status not in ['pending', 'processing', 'completed', 'cancelled']:
            return jsonify({'success': False, 'message': 'Invalid status'})
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE orders SET order_status = %s WHERE order_id = %s',
                      (status, order_id))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/delete-order/<int:order_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_order(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM orders WHERE order_id = %s', (order_id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/rental-request/<int:product_id>')
@login_required
def rental_request(product_id):
    size = request.args.get('size')
    if not size:
        flash('Please select a size first', 'error')
        return redirect(url_for('view_product', product_id=product_id))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get product details
    cursor.execute('''
        SELECT p.*, c.name as category_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as primary_image
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = %s
    ''', (product_id,))
    product = cursor.fetchone()
    
    # Get product sizes
    cursor.execute('SELECT * FROM product_sizes WHERE product_id = %s', (product_id,))
    sizes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('rental_request.html', 
                         product=product, 
                         sizes=sizes, 
                         selected_size=size)

@app.route('/submit-rental-request', methods=['GET', 'POST'])
@login_required
def submit_rental_request():
    try:
        if request.method != 'POST':
            return jsonify({'success': False, 'message': 'Invalid request method'})

        # Validate required fields
        required_fields = ['product_id', 'size', 'startDate', 'endDate', 
                         'fullName', 'contactNumber', 'address', 'paymentMethod']
        
        for field in required_fields:
            if field not in request.form:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'})

        # Validate file upload
        if 'validId' not in request.files:
            return jsonify({'success': False, 'message': 'Valid ID file is required'})

        valid_id = request.files['validId']
        if valid_id.filename == '':
            return jsonify({'success': False, 'message': 'No valid ID file selected'})

        if not allowed_file(valid_id.filename):
            return jsonify({'success': False, 'message': 'Invalid file type for valid ID'})

        # Handle valid ID upload
        filename = secure_filename(f"valid_id_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{valid_id.filename}")
        filepath = os.path.join(VALID_IDS_FOLDER, filename)
        valid_id.save(filepath)
        valid_id_path = os.path.join('uploads', 'products', 'valid_ids', filename).replace('\\', '/')
        
        # Handle GCash payment details if applicable
        gcash_reference = None
        payment_proof_path = None
        if request.form['paymentMethod'] == 'GCASH':
            gcash_reference = request.form.get('gcash_reference')
            if 'payment_proof' in request.files:
                payment_proof = request.files['payment_proof']
                if payment_proof and allowed_file(payment_proof.filename):
                    filename = secure_filename(f"rental_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{payment_proof.filename.rsplit('.', 1)[1].lower()}")
                    payment_proof_path = os.path.join('uploads/payments/proof', filename)
                    payment_proof.save(os.path.join('static', payment_proof_path))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create rental request
        cursor.execute('''
            INSERT INTO rental_requests (
                user_id, product_id, size, start_date, end_date,
                full_name, contact_number, address,
                payment_method, valid_id_path, rental_days,
                total_amount, gcash_reference, payment_proof,
                status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        ''', (
            session['user_id'],
            request.form['product_id'],
            request.form['size'],
            request.form['startDate'],
            request.form['endDate'],
            request.form['fullName'],
            request.form['contactNumber'],
            request.form['address'],
            request.form['paymentMethod'],
            valid_id_path,
            request.form['rental_days'],
            request.form['total_amount'],
            gcash_reference,
            payment_proof_path
        ))
        
        request_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'success': True, 'requestId': request_id})
        
    except Exception as e:
        print(f"Error in submit_rental_request: {str(e)}")  # Add logging
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/admin/request-details/rental/<int:request_id>')
@login_required
@admin_required
def get_rental_request_details(request_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT r.*, 
                   p.name as product_name,
                   p.rental_fee_per_day,
                   (SELECT image_path FROM product_images 
                    WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image,
                   r.gcash_reference,
                   r.payment_proof
            FROM rental_requests r
            JOIN products p ON r.product_id = p.product_id
            WHERE r.request_id = %s
        ''', (request_id,))
        
        request = cursor.fetchone()
        
        if request:
            # Calculate total rental fee
            request['total_rental_fee'] = float(request['rental_fee_per_day']) * request['rental_days']
            # Format dates for display
            request['start_date'] = request['start_date'].strftime('%Y-%m-%d')
            request['end_date'] = request['end_date'].strftime('%Y-%m-%d')
            request['created_at'] = request['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Ensure valid_id_path is properly formatted
            if request['valid_id_path']:
                request['valid_id_path'] = request['valid_id_path'].replace('\\', '/')
            
            # Ensure payment_proof is properly formatted
            if request['payment_proof']:
                request['payment_proof'] = request['payment_proof'].replace('\\', '/')
            
            return jsonify(request)
        else:
            return jsonify({'error': 'Request not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/update-request-status/appointment/<int:appointment_id>', methods=['POST'])
@admin_required
def update_appointment_request_status(appointment_id):
    try:
        data = request.json
        new_status = data.get('status')
        note = data.get('note', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if new_status == 'approved':
            # Get the original request details
            cursor.execute('''
                SELECT * FROM appointment_requests 
                WHERE appointment_id = %s
            ''', (appointment_id,))
            request_data = cursor.fetchone()
            
            if not request_data:
                return jsonify({'success': False, 'message': 'Appointment request not found'}), 404
            
            # Insert into appointments table
            cursor.execute('''
                INSERT INTO appointments (
                    user_id, category_id, description, appointment_date, 
                    appointment_time, inspiration_image, budget_range, 
                    special_requirements, status, original_request_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'processing', %s)
            ''', (
                request_data['user_id'],
                request_data['category_id'],
                request_data['description'],
                request_data['preferred_date'],
                request_data['preferred_time'],
                request_data['inspiration_image'],
                request_data['budget_range'],
                request_data['special_requirements'],
                request_data['appointment_id']
            ))
            
            # Delete the original request
            cursor.execute('DELETE FROM appointment_requests WHERE appointment_id = %s', (appointment_id,))
            
        elif new_status == 'rejected':
            # For rejected requests, just delete them
            cursor.execute('DELETE FROM appointment_requests WHERE appointment_id = %s', (appointment_id,))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/delete-request/rental/<int:request_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_rental_request(request_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, get the valid ID path to delete the file
        cursor.execute('SELECT valid_id_path FROM rental_requests WHERE request_id = %s', (request_id,))
        request = cursor.fetchone()
        
        if request and request['valid_id_path']:
            # Delete the valid ID file
            file_path = os.path.join(app.static_folder, request['valid_id_path'])
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete the request from database
        cursor.execute('DELETE FROM rental_requests WHERE request_id = %s', (request_id,))
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/rental-details/<int:rental_id>')
@login_required
@admin_required
def get_rental_details(rental_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT r.*, 
                   p.name as product_name,
                   (SELECT image_path FROM product_images 
                    WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image,
                   u.full_name as customer_name
            FROM rentals r
            JOIN products p ON r.product_id = p.product_id
            JOIN users u ON r.user_id = u.user_id
            WHERE r.rental_id = %s
        ''', (rental_id,))
        
        rental = cursor.fetchone()
        
        if rental:
            # Format dates for display
            rental['start_date'] = rental['start_date'].strftime('%Y-%m-%d')
            rental['end_date'] = rental['end_date'].strftime('%Y-%m-%d')
            rental['created_at'] = rental['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if rental['return_date']:
                rental['return_date'] = rental['return_date'].strftime('%Y-%m-%d')
            
            # Ensure paths are properly formatted
            if rental['valid_id_path']:
                rental['valid_id_path'] = rental['valid_id_path'].replace('\\', '/')
            if rental['payment_proof']:
                rental['payment_proof'] = rental['payment_proof'].replace('\\', '/')
                
            return jsonify(rental)
        else:
            return jsonify({'error': 'Rental not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/update-rental-status/<int:rental_id>', methods=['POST'])
@login_required
@admin_required
def update_rental_status(rental_id):
    try:
        new_status = request.json.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE rentals SET status = %s WHERE rental_id = %s',
                      (new_status, rental_id))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/delete-rental/<int:rental_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_rental(rental_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM rentals WHERE rental_id = %s', (rental_id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/orders')
@login_required
def orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get orders
    cursor.execute('''
        SELECT o.*, p.name as product_name, 
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.user_id = %s
        ORDER BY o.created_at DESC
    ''', (session['user_id'],))
    orders = cursor.fetchall()
    
    # Get rental requests
    cursor.execute('''
        SELECT r.*, p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
        FROM rental_requests r
        JOIN products p ON r.product_id = p.product_id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    ''', (session['user_id'],))
    rental_requests = cursor.fetchall()
    
    # Get reservation requests
    cursor.execute('''
        SELECT r.*, p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
        FROM reservation_requests r
        JOIN products p ON r.product_id = p.product_id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    ''', (session['user_id'],))
    reservation_requests = cursor.fetchall()
    
    # Get rentals
    cursor.execute('''
        SELECT r.*, p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
        FROM rentals r
        JOIN products p ON r.product_id = p.product_id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    ''', (session['user_id'],))
    rentals = cursor.fetchall()
    
    # Get reservations
    cursor.execute('''
        SELECT r.*, p.name as product_name,
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
        FROM reservations r
        JOIN products p ON r.product_id = p.product_id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    ''', (session['user_id'],))
    reservations = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('orders.html',
                         orders=orders,
                         rental_requests=rental_requests,
                         reservation_requests=reservation_requests,
                         rentals=rentals,
                         reservations=reservations)

@app.route('/admin/confirm-return/<int:rental_id>', methods=['POST'])
@login_required
@admin_required
def confirm_rental_return(rental_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get rental details including the product's rental fee
        cursor.execute('''
            SELECT r.*, p.rental_fee_per_day
            FROM rentals r
            JOIN products p ON r.product_id = p.product_id
            WHERE r.rental_id = %s
        ''', (rental_id,))
        
        rental = cursor.fetchone()
        if not rental:
            return jsonify({'success': False, 'message': 'Rental not found'})
        
        # Calculate if return is late
        end_date = rental['end_date']
        current_date = datetime.now().date()
        
        if current_date > end_date:
            # Calculate days late
            days_late = (current_date - end_date).days
            
            # Calculate late fee (1.5x regular rate per day late)
            late_fee_per_day = float(rental['rental_fee_per_day']) * 1.5
            total_late_fee = late_fee_per_day * days_late
            
            # Update rental with late fee
            new_total = float(rental['total_amount']) + total_late_fee
            
            cursor.execute('''
                UPDATE rentals 
                SET status = 'completed',
                    return_date = %s,
                    days_late = %s,
                    late_fee = %s,
                    final_amount = %s
                WHERE rental_id = %s
            ''', (current_date, days_late, total_late_fee, new_total, rental_id))
            
            message = f'Rental returned {days_late} days late. Late fee: ₱{total_late_fee:.2f}'
        else:
            # On-time return
            cursor.execute('''
                UPDATE rentals 
                SET status = 'completed',
                    return_date = %s,
                    final_amount = total_amount
                WHERE rental_id = %s
            ''', (current_date, rental_id))
            
            message = 'Rental returned on time'
        
        conn.commit()
        return jsonify({
            'success': True, 
            'message': message,
            'isLate': current_date > end_date
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/revenue-data')
@login_required
@admin_required
def get_revenue_data():
    period = request.args.get('period', 'weekly')
    year = int(request.args.get('year', datetime.now().year))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get summary data including counts
        cursor.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN order_status = 'completed' THEN total_amount ELSE 0 END), 0) as orders_revenue,
                COUNT(CASE WHEN order_status = 'completed' THEN 1 END) as total_orders,
                (
                    SELECT COALESCE(SUM(CASE WHEN status = 'completed' THEN final_amount ELSE 0 END), 0)
                    FROM rentals
                ) as rentals_revenue,
                (
                    SELECT COUNT(*) FROM rentals WHERE status = 'completed'
                ) as total_rentals,
                (
                    SELECT COUNT(*) FROM rentals 
                    WHERE status IN ('processing', 'shipped', 'delivered')
                ) as active_rentals,
                (
                    SELECT COUNT(*) FROM rentals 
                    WHERE status = 'delivered' AND end_date < CURRENT_DATE
                ) as late_returns,
                (
                    SELECT COALESCE(SUM(late_fee), 0)
                    FROM rentals 
                    WHERE status = 'completed' AND late_fee > 0
                ) as late_fees
            FROM orders
        ''')
        
        summary = cursor.fetchone()
        total_revenue = float(summary['orders_revenue']) + float(summary['rentals_revenue'])
        
        # Initialize data arrays
        labels = []
        orders_data = []
        rentals_data = []
        
        # Get chart data based on period
        if period == 'weekly':
            # Generate all weeks of the year
            labels = [f'Week {i}' for i in range(1, 54)]
            
            # Get orders data
            cursor.execute('''
                SELECT 
                    WEEK(created_at) as period,
                    COALESCE(SUM(CASE WHEN order_status = 'completed' THEN total_amount ELSE 0 END), 0) as amount
                FROM orders 
                WHERE YEAR(created_at) = %s
                GROUP BY WEEK(created_at)
            ''', (year,))
            orders_by_week = {row['period']: float(row['amount']) for row in cursor.fetchall()}
            
            # Get rentals data
            cursor.execute('''
                SELECT 
                    WEEK(created_at) as period,
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN final_amount ELSE 0 END), 0) as amount
                FROM rentals 
                WHERE YEAR(created_at) = %s
                GROUP BY WEEK(created_at)
            ''', (year,))
            rentals_by_week = {row['period']: float(row['amount']) for row in cursor.fetchall()}
            
            # Fill in the data arrays
            for week in range(1, 54):
                orders_data.append(orders_by_week.get(week, 0))
                rentals_data.append(rentals_by_week.get(week, 0))
                
        elif period == 'monthly':
            months = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']
            labels = months
            
            # Get orders data
            cursor.execute('''
                SELECT 
                    MONTH(created_at) as period,
                    COALESCE(SUM(CASE WHEN order_status = 'completed' THEN total_amount ELSE 0 END), 0) as amount
                FROM orders 
                WHERE YEAR(created_at) = %s
                GROUP BY MONTH(created_at)
            ''', (year,))
            orders_by_month = {row['period']: float(row['amount']) for row in cursor.fetchall()}
            
            # Get rentals data
            cursor.execute('''
                SELECT 
                    MONTH(created_at) as period,
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN final_amount ELSE 0 END), 0) as amount
                FROM rentals 
                WHERE YEAR(created_at) = %s
                GROUP BY MONTH(created_at)
            ''', (year,))
            rentals_by_month = {row['period']: float(row['amount']) for row in cursor.fetchall()}
            
            # Fill in the data arrays
            for month in range(1, 13):
                orders_data.append(orders_by_month.get(month, 0))
                rentals_data.append(rentals_by_month.get(month, 0))
                
        elif period == 'yearly':
            # Get 5 years of data
            start_year = year - 4
            labels = [str(y) for y in range(start_year, year + 1)]
            
            # Get orders data
            cursor.execute('''
                SELECT 
                    YEAR(created_at) as period,
                    COALESCE(SUM(CASE WHEN order_status = 'completed' THEN total_amount ELSE 0 END), 0) as amount
                FROM orders 
                WHERE YEAR(created_at) BETWEEN %s AND %s
                GROUP BY YEAR(created_at)
            ''', (start_year, year))
            orders_by_year = {row['period']: float(row['amount']) for row in cursor.fetchall()}
            
            # Get rentals data
            cursor.execute('''
                SELECT 
                    YEAR(created_at) as period,
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN final_amount ELSE 0 END), 0) as amount
                FROM rentals 
                WHERE YEAR(created_at) BETWEEN %s AND %s
                GROUP BY YEAR(created_at)
            ''', (start_year, year))
            rentals_by_year = {row['period']: float(row['amount']) for row in cursor.fetchall()}
            
            # Fill in the data arrays
            for y in range(start_year, year + 1):
                orders_data.append(orders_by_year.get(y, 0))
                rentals_data.append(rentals_by_year.get(y, 0))
        
        return jsonify({
            'summary': {
                'total': total_revenue,
                'orders': float(summary['orders_revenue']),
                'rentals': float(summary['rentals_revenue']),
                'late_fees': float(summary['late_fees']),
                'total_orders': int(summary['total_orders']),
                'total_rentals': int(summary['total_rentals']),
                'active_rentals': int(summary['active_rentals']),
                'late_returns': int(summary['late_returns'])
            },
            'chart': {
                'labels': labels,
                'orders': orders_data,
                'rentals': rentals_data
            }
        })
        
    except Exception as e:
        print(f"Error in get_revenue_data: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/contact')
def contact():
    return render_template('contact.html', user_name=session.get('full_name'))

@app.route('/categories')
def categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all categories with 3 random products each
    cursor.execute('''
        SELECT c.*, 
               (SELECT COUNT(*) FROM products WHERE category_id = c.category_id) as product_count
        FROM categories c
    ''')
    categories = cursor.fetchall()
    
    # For each category, get 3 random products
    for category in categories:
        cursor.execute('''
            SELECT p.*, 
                   (SELECT image_path FROM product_images 
                    WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as primary_image
            FROM products p
            WHERE p.category_id = %s
            ORDER BY RAND()
            LIMIT 3
        ''', (category['category_id'],))
        category['products'] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('categories.html', 
                         categories=categories,
                         user_name=session.get('full_name'))

@app.route('/category/<int:category_id>')
def view_category(category_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get category details
    cursor.execute('SELECT * FROM categories WHERE category_id = %s', (category_id,))
    category = cursor.fetchone()
    
    if not category:
        flash('Category not found', 'error')
        return redirect(url_for('categories'))
    
    # Get all products in this category with their primary images
    cursor.execute('''
        SELECT p.*, 
               (SELECT image_path FROM product_images 
                WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as primary_image
        FROM products p
        WHERE p.category_id = %s
        ORDER BY p.created_at DESC
    ''', (category_id,))
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('category_view.html', 
                         category=category,
                         products=products,
                         user_name=session.get('full_name'))

@app.route('/toggle-wishlist/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if product is already in wishlist
        cursor.execute('''
            SELECT * FROM wishlists 
            WHERE user_id = %s AND product_id = %s
        ''', (session['user_id'], product_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # Remove from wishlist
            cursor.execute('''
                DELETE FROM wishlists 
                WHERE user_id = %s AND product_id = %s
            ''', (session['user_id'], product_id))
            status = 'removed'
        else:
            # Add to wishlist
            cursor.execute('''
                INSERT INTO wishlists (user_id, product_id)
                VALUES (%s, %s)
            ''', (session['user_id'], product_id))
            status = 'added'
            
        conn.commit()
        return jsonify({'success': True, 'status': status})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/wishlist')
@login_required
def view_wishlist():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get wishlist items with product details
        cursor.execute('''
            SELECT p.*, c.name as category_name,
                   (SELECT image_path FROM product_images 
                    WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as primary_image
            FROM wishlists w
            JOIN products p ON w.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            WHERE w.user_id = %s
            ORDER BY w.created_at DESC
        ''', (session['user_id'],))
        
        wishlist_items = cursor.fetchall()
        
        return render_template('wishlist.html', 
                             wishlist_items=wishlist_items,
                             user_name=session.get('full_name'))
                             
    except Exception as e:
        flash('Error loading wishlist', 'error')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

@app.route('/check-wishlist/<int:product_id>')
@login_required
def check_wishlist(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM wishlists 
            WHERE user_id = %s AND product_id = %s
        ''', (session['user_id'], product_id))
        
        in_wishlist = cursor.fetchone() is not None
        
        return jsonify({'success': True, 'inWishlist': in_wishlist})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/update-product/<int:product_id>', methods=['POST'])
@admin_required
def update_product(product_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Update product prices
        cursor.execute('''
            UPDATE products 
            SET regular_price = %s, 
                rental_fee_per_day = %s 
            WHERE product_id = %s
        ''', (data['regular_price'], data['rental_fee_per_day'], product_id))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/book-us')
def book_us():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get categories for the dropdown
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('book_us.html', 
                         categories=categories,
                         user_name=session.get('full_name'))

@app.route('/book-appointment', methods=['POST'])
@login_required
def book_appointment():
    try:
        # Get form data
        user_id = session['user_id']
        category_id = request.form['category_id']
        description = request.form['description']
        preferred_date = request.form['preferred_date']
        preferred_time = request.form['preferred_time']
        budget_range = request.form['budget_range']
        special_requirements = request.form.get('special_requirements', '')
        
        # Handle inspiration image upload
        inspiration_image = request.files['inspiration_image']
        inspiration_path = None
        if inspiration_image:
            filename = secure_filename(f"inspiration_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{inspiration_image.filename}")
            filepath = os.path.join(APPOINTMENT_UPLOADS, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            inspiration_image.save(filepath)
            inspiration_path = os.path.join('uploads', 'appointments', filename).replace('\\', '/')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            INSERT INTO appointment_requests 
            (user_id, category_id, description, preferred_date, preferred_time, 
             inspiration_image, budget_range, special_requirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, category_id, description, preferred_date, preferred_time, 
              inspiration_path, budget_range, special_requirements))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment request submitted successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
        
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

@app.route('/admin/request-details/appointment/<int:request_id>', methods=['GET'])
@admin_required
def get_appointment_request_details(request_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT ar.*, u.full_name, u.phone_number as contact_number, 
                   c.name as category_name 
            FROM appointment_requests ar
            JOIN users u ON ar.user_id = u.user_id
            JOIN categories c ON ar.category_id = c.category_id
            WHERE ar.appointment_id = %s
        ''', (request_id,))
        
        appointment = cursor.fetchone()
        
        if not appointment:
            return jsonify({'error': 'Appointment request not found'}), 404
        
        # Convert datetime/date objects to strings
        if appointment['preferred_date']:
            appointment['preferred_date'] = appointment['preferred_date'].strftime('%Y-%m-%d')
        if appointment['preferred_time']:
            # Convert timedelta to string in HH:MM format
            total_minutes = int(appointment['preferred_time'].total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            appointment['preferred_time'] = f"{hours:02d}:{minutes:02d}"
        if appointment['created_at']:
            appointment['created_at'] = appointment['created_at'].strftime('%Y-%m-%d %I:%M %p')
        
        cursor.close()
        conn.close()
        
        return jsonify(appointment)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/admin/appointments')
@admin_required
def get_appointments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT a.*, u.full_name, u.phone_number as contact_number, 
                   c.name as category_name 
            FROM appointments a
            JOIN users u ON a.user_id = u.user_id
            JOIN categories c ON a.category_id = c.category_id
            ORDER BY a.appointment_date, a.appointment_time
        ''')
        
        appointments = cursor.fetchall()
        
        # Format dates and times for display
        for appointment in appointments:
            if appointment['appointment_date']:
                appointment['appointment_date'] = appointment['appointment_date'].strftime('%Y-%m-%d')
            if appointment['appointment_time']:
                total_minutes = int(appointment['appointment_time'].total_seconds() / 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                appointment['formatted_time'] = f"{hours:02d}:{minutes:02d}"
        
        return jsonify(appointments)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/appointment-details/<int:appointment_id>')
@admin_required
def get_appointment_details(appointment_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Modified query to use full_name from users table
        cursor.execute('''
            SELECT a.*, u.full_name, u.phone_number as contact_number, 
                   c.name as category_name,
                   DATE_FORMAT(a.appointment_date, '%Y-%m-%d') as appointment_date,
                   TIME_FORMAT(a.appointment_time, '%H:%i') as appointment_time
            FROM appointments a
            JOIN users u ON a.user_id = u.user_id
            JOIN categories c ON a.category_id = c.category_id
            WHERE a.appointment_id = %s
        ''', (appointment_id,))
        
        appointment = cursor.fetchone()
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
            
        # Format the response data using full_name from users table
        response = {
            'full_name': appointment['full_name'],  # Use full_name instead of customer_name
            'contact_number': appointment['contact_number'],
            'category_name': appointment['category_name'],
            'description': appointment['description'],
            'appointment_date': appointment['appointment_date'],
            'appointment_time': appointment['appointment_time'],
            'budget_range': float(appointment['budget_range']),
            'special_requirements': appointment['special_requirements'],
            'status': appointment['status'],
            'inspiration_image': appointment['inspiration_image']
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in get_appointment_details: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/update-appointment-status/<int:appointment_id>', methods=['POST'])
@admin_required
def update_appointment_status(appointment_id):
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            UPDATE appointments 
            SET status = %s,
                updated_at = CURRENT_TIMESTAMP 
            WHERE appointment_id = %s
        ''', (new_status, appointment_id))
        
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/delete-appointment/<int:appointment_id>', methods=['DELETE'])
@admin_required
def delete_appointment(appointment_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First, check if appointment exists
        cursor.execute('SELECT * FROM appointments WHERE appointment_id = %s', (appointment_id,))
        appointment = cursor.fetchone()
        
        if not appointment:
            return jsonify({'success': False, 'message': 'Appointment not found'}), 404
        
        # Delete the appointment
        cursor.execute('DELETE FROM appointments WHERE appointment_id = %s', (appointment_id,))
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/create-appointment', methods=['POST'])
@admin_required
def create_appointment():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get the original request details
        cursor.execute('''
            SELECT * FROM appointment_requests 
            WHERE appointment_id = %s
        ''', (data['request_id'],))
        
        request_data = cursor.fetchone()
        
        if not request_data:
            return jsonify({'success': False, 'message': 'Original request not found'}), 404
        
        # Insert new appointment - removed duplicate appointment_time
        cursor.execute('''
            INSERT INTO appointments (
                user_id, category_id, description, appointment_date, 
                appointment_time, inspiration_image, budget_range, 
                special_requirements, status, original_request_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'processing', %s)
        ''', (
            request_data['user_id'],
            request_data['category_id'],
            request_data['description'],
            request_data['preferred_date'],
            request_data['preferred_time'],
            request_data['inspiration_image'],
            request_data['budget_range'],
            request_data['special_requirements'],
            request_data['appointment_id']
        ))
        
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/appointments')
@login_required
def appointments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get pending appointment requests
        cursor.execute('''
            SELECT ar.*, c.name as category_name 
            FROM appointment_requests ar
            JOIN categories c ON ar.category_id = c.category_id
            WHERE ar.user_id = %s AND ar.status IN ('pending', 'rejected')
            ORDER BY ar.created_at DESC
        ''', (session['user_id'],))
        pending_appointments = cursor.fetchall()
        
        # Get active/approved appointments
        cursor.execute('''
            SELECT a.*, c.name as category_name 
            FROM appointments a
            JOIN categories c ON a.category_id = c.category_id
            WHERE a.user_id = %s
            ORDER BY a.appointment_date DESC
        ''', (session['user_id'],))
        active_appointments = cursor.fetchall()
        
        # Format dates and times
        for appointment in pending_appointments:
            if appointment['preferred_date']:
                appointment['preferred_date'] = appointment['preferred_date'].strftime('%B %d, %Y')
            if appointment['preferred_time']:
                # Convert timedelta to formatted time
                total_minutes = int(appointment['preferred_time'].total_seconds() / 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                appointment['preferred_time'] = f"{hours:02d}:{minutes:02d}"

        for appointment in active_appointments:
            if appointment['appointment_date']:
                appointment['appointment_date'] = appointment['appointment_date'].strftime('%B %d, %Y')
            if appointment['appointment_time']:
                # Convert timedelta to formatted time
                total_minutes = int(appointment['appointment_time'].total_seconds() / 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                appointment['appointment_time'] = f"{hours:02d}:{minutes:02d}"
        
        return render_template('appointments.html',
                             pending_appointments=pending_appointments,
                             active_appointments=active_appointments,
                             pending_count=len(pending_appointments),
                             active_count=len(active_appointments))
                             
    except Exception as e:
        print(f"Error in appointments route: {str(e)}")
        flash('An error occurred while loading appointments', 'error')
        return redirect(url_for('index'))
        
    finally:
        cursor.close()
        conn.close()

@app.route('/submit-reservation', methods=['POST'])
@login_required
def submit_reservation():
    try:
        # Get form data
        product_id = request.form.get('product_id')
        size = request.form.get('size')
        full_name = request.form.get('full_name')
        contact_number = request.form.get('contact_number')
        address = request.form.get('complete_address')
        total_amount = request.form.get('total_amount')
        payment_method = request.form.get('payment_method')
        gcash_reference = request.form.get('gcash_reference')

        # Handle file uploads
        valid_id = request.files.get('valid_id')
        payment_proof = request.files.get('payment_proof')

        # Save valid ID
        valid_id_filename = secure_filename(f"valid_id_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{valid_id.filename}")
        valid_id_path = os.path.join('uploads/products/valid_ids', valid_id_filename)
        valid_id.save(os.path.join(app.static_folder, valid_id_path))

        # Save payment proof
        payment_proof_filename = secure_filename(f"payment_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{payment_proof.filename}")
        payment_proof_path = os.path.join('uploads/payments/proof', payment_proof_filename)
        payment_proof.save(os.path.join(app.static_folder, payment_proof_path))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert into reservation_requests instead of rental_requests
        cursor.execute('''
            INSERT INTO reservation_requests (
                user_id, product_id, size, full_name, contact_number, 
                address, total_amount, payment_method, gcash_reference,
                valid_id_path, payment_proof, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        ''', (
            session['user_id'], product_id, size, full_name, contact_number,
            address, total_amount, payment_method, gcash_reference,
            valid_id_path, payment_proof_path
        ))

        conn.commit()
        return jsonify({'success': True, 'message': 'Reservation request submitted successfully!'})

    except Exception as e:
        print(f"Error in submit_reservation: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while submitting your reservation'})

    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

@app.route('/admin/request-details/reservation/<int:request_id>')
@login_required
@admin_required
def get_reservation_request_details(request_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT r.*, 
                   p.name as product_name,
                   p.rental_fee_per_day,
                   (SELECT image_path FROM product_images 
                    WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image,
                   r.gcash_reference,
                   r.payment_proof,
                   u.full_name as customer_name
            FROM reservation_requests r
            JOIN products p ON r.product_id = p.product_id
            JOIN users u ON r.user_id = u.user_id
            WHERE r.request_id = %s
        ''', (request_id,))
        
        request = cursor.fetchone()
        
        if request:
            # Format dates for display
            request['created_at'] = request['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Ensure paths are properly formatted
            if request['valid_id_path']:
                request['valid_id_path'] = request['valid_id_path'].replace('\\', '/')
            if request['payment_proof']:
                request['payment_proof'] = request['payment_proof'].replace('\\', '/')
            
            return jsonify(request)
        else:
            return jsonify({'error': 'Request not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/update-request-status/reservation/<int:request_id>', methods=['POST'])
@login_required
@admin_required
def update_reservation_request_status(request_id):
    try:
        data = request.json
        new_status = data.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # If approving the request, transfer it to reservations table
        if new_status == 'approved':
            # Get the request details
            cursor.execute('''
                SELECT * FROM reservation_requests 
                WHERE request_id = %s
            ''', (request_id,))
            request_data = cursor.fetchone()
            
            if not request_data:
                return jsonify({'success': False, 'message': 'Request not found'}), 404
            
            # Insert into reservations table
            cursor.execute('''
                INSERT INTO reservations (
                    user_id, product_id, size, full_name, contact_number,
                    address, total_amount, payment_method, gcash_reference,
                    valid_id_path, payment_proof, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'processing')
            ''', (
                request_data['user_id'],
                request_data['product_id'],
                request_data['size'],
                request_data['full_name'],
                request_data['contact_number'],
                request_data['address'],
                request_data['total_amount'],
                request_data['payment_method'],
                request_data['gcash_reference'],
                request_data['valid_id_path'],
                request_data['payment_proof']
            ))
            
            # Delete from reservation_requests table
            cursor.execute('DELETE FROM reservation_requests WHERE request_id = %s', (request_id,))
            
        else:
            # Just update the status for non-approved cases
            cursor.execute('''
                UPDATE reservation_requests 
                SET status = %s 
                WHERE request_id = %s
            ''', (new_status, request_id))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/delete-request/reservation/<int:request_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_reservation_request(request_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, get the file paths to delete the files
        cursor.execute('SELECT valid_id_path, payment_proof FROM reservation_requests WHERE request_id = %s', (request_id,))
        request = cursor.fetchone()
        
        if request:
            # Delete the files if they exist
            for file_path in [request['valid_id_path'], request['payment_proof']]:
                if file_path:
                    full_path = os.path.join(app.static_folder, file_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)
        
        # Delete the request from database
        cursor.execute('DELETE FROM reservation_requests WHERE request_id = %s', (request_id,))
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/reservation-details/<int:reservation_id>')
@login_required
@admin_required
def get_reservation_details(reservation_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT r.*, p.name as product_name,
                   (SELECT image_path FROM product_images 
                    WHERE product_id = p.product_id AND is_primary = 1 LIMIT 1) as product_image
            FROM reservations r
            JOIN products p ON r.product_id = p.product_id
            WHERE r.reservation_id = %s
        ''', (reservation_id,))
        
        reservation = cursor.fetchone()
        
        return jsonify(reservation)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/update-reservation-status/<int:reservation_id>', methods=['POST'])
@login_required
@admin_required
def update_reservation_status(reservation_id):
    try:
        data = request.json
        new_status = data.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reservations 
            SET status = %s 
            WHERE reservation_id = %s
        ''', (new_status, reservation_id))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/delete-reservation/<int:reservation_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_reservation(reservation_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, get the file paths to delete the files
        cursor.execute('SELECT valid_id_path, payment_proof FROM reservations WHERE reservation_id = %s', (reservation_id,))
        reservation = cursor.fetchone()
        
        if reservation:
            # Delete the files if they exist
            for file_path in [reservation['valid_id_path'], reservation['payment_proof']]:
                if file_path:
                    full_path = os.path.join(app.static_folder, file_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)
        
        # Delete the reservation from database
        cursor.execute('DELETE FROM reservations WHERE reservation_id = %s', (reservation_id,))
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
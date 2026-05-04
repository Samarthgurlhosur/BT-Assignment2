"""
Land Registration System - Main Flask Application
Full-stack web application with Blockchain and AI features
"""

import os
import secrets
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

from models import db, User, Land, LandDocument, LandImage, Offer, Message, Transaction, Recommendation
from blockchain import Blockchain
from ai_features import check_document_fraud, get_land_recommendations

# Flask App Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///land_registry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'documents'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)

# Initialize Extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socket_io = SocketIO(app, cors_allowed_origins="*")

# Initialize Blockchain
blockchain = Blockchain()

# Global variables
active_negotiations = {}  # Track active negotiations by land_id


# ===== Authentication Setup =====
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def role_required(roles):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                return jsonify({'error': 'Access denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===== Database Setup =====
@app.before_request
def create_tables():
    """Create database tables"""
    db.create_all()


# ===== Authentication Routes =====
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Validate inputs
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            role=data.get('role', 'buyer')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        user = User.query.filter_by(username=data.get('username')).first()
        
        if user and user.check_password(data.get('password')):
            login_user(user)
            if request.is_json:
                return jsonify({'message': 'Login successful', 'user_id': user.id, 'role': user.role}), 200
            return redirect(url_for('dashboard'))
        
        if request.is_json:
            return jsonify({'error': 'Invalid username or password'}), 401
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))


# ===== Dashboard Routes =====
@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard (different for owner and buyer)"""
    if current_user.role == 'owner':
        return render_template('owner_dashboard.html', user=current_user)
    else:
        return render_template('buyer_dashboard.html', user=current_user)


# ===== Land Registration Routes (Owner Panel) =====
@app.route('/api/lands', methods=['GET'])
def get_lands():
    """Get all lands or user's lands"""
    if request.args.get('my_lands') and current_user.is_authenticated and current_user.role == 'owner':
        lands = Land.query.filter_by(owner_id=current_user.id).all()
    else:
        lands = Land.query.filter_by(is_available=True).all()
    
    return jsonify([land.to_dict() for land in lands])


@app.route('/api/lands', methods=['POST'])
@login_required
@role_required(['owner'])
def create_land():
    """Create new land listing"""
    data = request.get_json()
    
    # Validate inputs
    required_fields = ['title', 'location', 'size_sqft', 'price']
    if not all(data.get(field) for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    land = Land(
        owner_id=current_user.id,
        title=data['title'],
        description=data.get('description', ''),
        location=data['location'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        size_sqft=float(data['size_sqft']),
        price=float(data['price']),
        verification_status='pending'
    )
    
    db.session.add(land)
    db.session.commit()
    
    return jsonify(land.to_dict()), 201


@app.route('/api/lands/<land_id>', methods=['GET'])
def get_land(land_id):
    """Get land details"""
    land = Land.query.get(land_id)
    
    if not land:
        return jsonify({'error': 'Land not found'}), 404
    
    return jsonify(land.to_dict())


@app.route('/api/lands/<land_id>', methods=['PUT'])
@login_required
@role_required(['owner'])
def update_land(land_id):
    """Update land details"""
    land = Land.query.get(land_id)
    
    if not land or land.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'title' in data:
        land.title = data['title']
    if 'description' in data:
        land.description = data['description']
    if 'price' in data:
        land.price = float(data['price'])
    if 'size_sqft' in data:
        land.size_sqft = float(data['size_sqft'])
    if 'is_available' in data:
        land.is_available = data['is_available']
    
    db.session.commit()
    return jsonify(land.to_dict())


@app.route('/api/lands/<land_id>', methods=['DELETE'])
@login_required
@role_required(['owner'])
def delete_land(land_id):
    """Delete land listing"""
    land = Land.query.get(land_id)
    
    if not land or land.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(land)
    db.session.commit()
    
    return jsonify({'message': 'Land deleted successfully'})


# ===== Document Upload Routes =====
@app.route('/api/lands/<land_id>/documents', methods=['POST'])
@login_required
@role_required(['owner'])
def upload_document(land_id):
    """Upload ownership proof document"""
    land = Land.query.get(land_id)
    
    if not land or land.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    doc_type = request.form.get('document_type', 'titleDeeds')
    
    if not file or file.filename == '':
        return jsonify({'error': 'Invalid file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    filename = f"{land_id}_{datetime.utcnow().timestamp()}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', filename)
    file.save(file_path)
    
    # Check for fraud/duplicate
    fraud_result = check_document_fraud(file_path)
    
    # Get existing document hashes
    existing_hashes = [
        doc.filename for doc in LandDocument.query.filter_by(document_type=doc_type).all()
    ]
    
    # Create document record
    document = LandDocument(
        land_id=land_id,
        document_type=doc_type,
        filename=file.filename,
        file_path=file_path,
        is_verified=False,
        is_fraud_detected=not fraud_result['is_authentic'],
        fraud_confidence=fraud_result['fraud_confidence']
    )
    
    db.session.add(document)
    db.session.commit()
    
    return jsonify({
        'message': 'Document uploaded',
        'document': document.to_dict(),
        'fraud_check': fraud_result
    }), 201


@app.route('/api/lands/<land_id>/images', methods=['POST'])
@login_required
@role_required(['owner'])
def upload_image(land_id):
    """Upload land image"""
    land = Land.query.get(land_id)
    
    if not land or land.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if not file or file.filename == '':
        return jsonify({'error': 'Invalid file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Save image
    filename = secure_filename(file.filename)
    filename = f"{land_id}_{datetime.utcnow().timestamp()}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', filename)
    file.save(file_path)
    
    is_primary = request.form.get('is_primary', False) == 'true'
    
    # If setting as primary, unset other images
    if is_primary:
        for img in LandImage.query.filter_by(land_id=land_id).all():
            img.is_primary = False
    
    image = LandImage(
        land_id=land_id,
        filename=file.filename,
        file_path=file_path,
        is_primary=is_primary
    )
    
    db.session.add(image)
    db.session.commit()
    
    return jsonify({
        'message': 'Image uploaded',
        'image': image.to_dict()
    }), 201


# ===== Search and Filter Routes =====
@app.route('/api/lands/search')
def search_lands():
    """Search and filter lands"""
    query = Land.query.filter_by(is_available=True)
    
    # Filter by location
    location = request.args.get('location')
    if location:
        query = query.filter(Land.location.ilike(f'%{location}%'))
    
    # Filter by price range
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_price:
        query = query.filter(Land.price >= min_price)
    if max_price:
        query = query.filter(Land.price <= max_price)
    
    # Filter by size range
    min_size = request.args.get('min_size', type=float)
    max_size = request.args.get('max_size', type=float)
    if min_size:
        query = query.filter(Land.size_sqft >= min_size)
    if max_size:
        query = query.filter(Land.size_sqft <= max_size)
    
    # Filter by verification status
    verified = request.args.get('verified', type=bool)
    if verified:
        query = query.filter(Land.verification_status == 'verified')
    
    lands = query.all()
    return jsonify([land.to_dict() for land in lands])


# ===== Offer/Negotiation Routes =====
@app.route('/api/offers', methods=['POST'])
@login_required
@role_required(['buyer'])
def create_offer():
    """Create an offer on a land"""
    data = request.get_json()
    
    land_id = data.get('land_id')
    offered_price = data.get('offered_price')
    message = data.get('message', '')
    
    land = Land.query.get(land_id)
    if not land:
        return jsonify({'error': 'Land not found'}), 404
    
    offer = Offer(
        land_id=land_id,
        buyer_id=current_user.id,
        seller_id=land.owner_id,
        offered_price=float(offered_price),
        message=message,
        status='pending'
    )
    
    db.session.add(offer)
    db.session.commit()
    
    # Notify seller via socket
    socket_io.emit('new_offer', {
        'offer': offer.to_dict(),
        'land': land.to_dict(include_owner=False),
        'buyer': current_user.to_dict()
    }, room=land.owner_id)
    
    return jsonify(offer.to_dict()), 201


@app.route('/api/offers/<offer_id>', methods=['PUT'])
@login_required
def update_offer(offer_id):
    """Accept or reject an offer"""
    offer = Offer.query.get(offer_id)
    
    if not offer or offer.seller_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    status = data.get('status')  # 'accepted' or 'rejected'
    
    if status not in ['accepted', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    
    offer.status = status
    offer.updated_at = datetime.utcnow()
    
    if status == 'accepted':
        # Create transaction
        transaction = Transaction(
            land_id=offer.land_id,
            buyer_id=offer.buyer_id,
            seller_id=offer.seller_id,
            final_amount=offer.offered_price
        )
        
        # Record in blockchain
        tx_data = {
            'land_id': offer.land_id,
            'buyer_id': offer.buyer_id,
            'seller_id': offer.seller_id,
            'amount': offer.offered_price
        }
        blockchain.add_transaction(tx_data)
        blockchain.mine_pending_transactions('SYSTEM')
        
        # Get the block index and hash
        latest_block = blockchain.get_latest_block()
        transaction.blockchain_hash = latest_block.hash
        transaction.blockchain_index = latest_block.index
        
        # Mark land as sold
        land = Land.query.get(offer.land_id)
        land.is_available = False
        
        db.session.add(transaction)
    
    db.session.commit()
    
    # Notify buyer
    socket_io.emit('offer_response', {
        'offer': offer.to_dict(),
        'status': status
    }, room=offer.buyer_id)
    
    return jsonify(offer.to_dict())


@app.route('/api/offers')
@login_required
def get_offers():
    """Get offers for current user"""
    if current_user.role == 'owner':
        offers = Offer.query.filter_by(seller_id=current_user.id).all()
    else:
        offers = Offer.query.filter_by(buyer_id=current_user.id).all()
    
    return jsonify([offer.to_dict() for offer in offers])


# ===== Recommendation Routes =====
@app.route('/api/recommendations')
@login_required
@role_required(['buyer'])
def get_recommendations():
    """Get AI-based recommendations for buyer"""
    # Get buyer's previous offers
    buyer_offers = Offer.query.filter_by(buyer_id=current_user.id).all()
    buyer_offers_dict = [offer.to_dict() for offer in buyer_offers]
    
    # Get available lands
    available_lands = [land.to_dict() for land in Land.query.filter_by(is_available=True).all()]
    
    # Get recommendations
    recommendations = get_land_recommendations(
        current_user.id,
        buyer_offers_dict,
        available_lands,
        top_k=5
    )
    
    return jsonify(recommendations)


# ===== Blockchain Routes =====
@app.route('/api/blockchain')
def get_blockchain():
    """Get entire blockchain"""
    return jsonify(blockchain.get_blockchain())


@app.route('/api/blockchain/statistics')
def get_blockchain_stats():
    """Get blockchain statistics"""
    return jsonify(blockchain.get_statistics())


@app.route('/api/transactions/<land_id>')
def get_land_transactions(land_id):
    """Get transaction history for a land"""
    transactions = blockchain.get_transaction_history(land_id)
    return jsonify(transactions)


@app.route('/api/verify-transaction', methods=['POST'])
def verify_transaction():
    """Verify transaction in blockchain"""
    data = request.get_json()
    
    result = blockchain.verify_transaction(
        data.get('land_id'),
        data.get('buyer_id'),
        data.get('seller_id')
    )
    
    return jsonify(result)


# ===== Real-time Messaging (WebSocket) =====
@socket_io.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        join_room(current_user.id)
        emit('connected', {'user_id': current_user.id, 'username': current_user.username})


@socket_io.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        leave_room(current_user.id)


@socket_io.on('join_negotiation')
def handle_join_negotiation(data):
    """Join negotiation room"""
    land_id = data.get('land_id')
    room_name = f"negotiation_{land_id}"
    join_room(room_name)
    emit('negotiation_joined', {
        'land_id': land_id,
        'user_id': current_user.id,
        'username': current_user.username
    }, room=room_name)


@socket_io.on('send_message')
def handle_send_message(data):
    """Send message during negotiation"""
    land_id = data.get('land_id')
    receiver_id = data.get('receiver_id')
    message_text = data.get('message')
    
    # Save message to database
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        land_id=land_id,
        message_text=message_text
    )
    db.session.add(message)
    db.session.commit()
    
    # Broadcast to room
    room_name = f"negotiation_{land_id}"
    emit('new_message', {
        'id': message.id,
        'sender_id': current_user.id,
        'sender_name': current_user.username,
        'message': message_text,
        'timestamp': message.created_at.isoformat()
    }, room=room_name)


@socket_io.on('send_offer')
def handle_send_offer(data):
    """Send price offer during negotiation"""
    land_id = data.get('land_id')
    offered_price = data.get('offered_price')
    
    room_name = f"negotiation_{land_id}"
    emit('price_offer', {
        'sender_id': current_user.id,
        'sender_name': current_user.username,
        'offered_price': offered_price,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room_name)


# ===== Transaction History Routes =====
@app.route('/api/my-transactions')
@login_required
def get_my_transactions():
    """Get user's transaction history"""
    if current_user.role == 'owner':
        transactions = Transaction.query.filter_by(seller_id=current_user.id).all()
    else:
        transactions = Transaction.query.filter_by(buyer_id=current_user.id).all()
    
    return jsonify([tx.to_dict() for tx in transactions])


# ===== User Profile Routes =====
@app.route('/api/user/profile')
@login_required
def get_profile():
    """Get current user profile"""
    return jsonify(current_user.to_dict())


@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    data = request.get_json()
    
    if 'full_name' in data:
        current_user.full_name = data['full_name']
    if 'phone' in data:
        current_user.phone = data['phone']
    if 'address' in data:
        current_user.address = data['address']
    
    db.session.commit()
    return jsonify(current_user.to_dict())


# ===== Admin Panel Routes (Basic) =====
@app.route('/api/admin/users')
def get_all_users():
    """Get all users (admin only)"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.route('/api/admin/transactions')
def get_all_transactions():
    """Get all transactions (admin only)"""
    transactions = Transaction.query.all()
    return jsonify([tx.to_dict() for tx in transactions])


# ===== Error Handlers =====
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ===== CLI Commands for Testing =====
@app.cli.command()
def init_db():
    """Initialize database"""
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def seed_data():
    """Seed sample data"""
    # Create test users
    owner = User(
        username='john_owner',
        email='owner@test.com',
        full_name='John Owner',
        phone='1234567890',
        address='123 Main St',
        role='owner'
    )
    owner.set_password('password123')
    
    buyer = User(
        username='jane_buyer',
        email='buyer@test.com',
        full_name='Jane Buyer',
        phone='0987654321',
        address='456 Oak Ave',
        role='buyer'
    )
    buyer.set_password('password123')
    
    db.session.add(owner)
    db.session.add(buyer)
    db.session.commit()
    
    # Create sample lands
    lands_data = [
        {
            'title': 'Beautiful Residential Plot',
            'location': 'Downtown Area',
            'size_sqft': 5000,
            'price': 500000,
            'description': 'Prime residential land with excellent location'
        },
        {
            'title': 'Commercial Space',
            'location': 'Business District',
            'size_sqft': 10000,
            'price': 1500000,
            'description': 'Premium commercial land ready for development'
        },
        {
            'title': 'Agricultural Land',
            'location': 'Rural Area',
            'size_sqft': 50000,
            'price': 200000,
            'description': 'Fertile agricultural land with good irrigation'
        }
    ]
    
    for land_data in lands_data:
        land = Land(
            owner_id=owner.id,
            title=land_data['title'],
            description=land_data['description'],
            location=land_data['location'],
            size_sqft=land_data['size_sqft'],
            price=land_data['price'],
            verification_status='verified'
        )
        db.session.add(land)
    
    db.session.commit()
    print("Sample data seeded successfully!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # For development
    port = int(os.environ.get('PORT', 5000))
    socket_io.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

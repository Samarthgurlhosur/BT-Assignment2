# Land Registration System with AI and Blockchain

A full-stack web application for land registration and transaction management using Python (Flask), Blockchain, and AI features.

## Features

### 1. **User Authentication & Roles**
- Two user roles: Land Owners and Buyers
- Secure login/signup system with password hashing
- Role-based access control

### 2. **Land Registration (Owner Panel)**
- Add land details (location, size, price, images, documents)
- Upload ownership proof documents (PDF/Images)
- View listed properties
- Unique ID for each land entry
- Verification status tracking

### 3. **Buyer Panel**
- Browse available lands with filtering
- Search by location, price range, size
- View full land details with documents and images
- Make offers on land
- Track offer status

### 4. **Real-Time Negotiation System**
- WebSocket-based real-time chat using Socket.IO
- Live price offering during negotiations
- Message notifications
- Active negotiation tracking

### 5. **Blockchain Integration**
- Custom Python blockchain implementation
- Immutable transaction records
- Proof of Work mechanism
- Transaction history per land
- Blockchain statistics and verification

### 6. **AI Features**
- Document fraud detection using image analysis
- Duplicate document detection via hashing
- Land recommendations based on buyer preferences
- Collaborative and content-based filtering

### 7. **Tech Stack**
- **Backend**: Python 3.8+, Flask 2.3+
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Real-time Communication**: Flask-SocketIO
- **Blockchain**: Custom Python implementation
- **AI/ML**: scikit-learn, OpenCV, NumPy

## Project Structure

```
BT/
├── app.py                  # Main Flask application
├── blockchain.py           # Blockchain implementation
├── models.py              # Database models
├── ai_features.py         # AI and ML features
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── owner_dashboard.html
│   └── buyer_dashboard.html
│
├── static/               # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
└── uploads/             # User uploads (created on first run)
    ├── documents/
    └── images/
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Step 1: Clone/Download the Project
```bash
cd /path/to/BT
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>>
```

Or use CLI command:
```bash
flask --app app init_db
```

### Step 5: Seed Sample Data (Optional)
```bash
flask --app app seed_data
```

This creates:
- 2 test users (owner and buyer)
- 3 sample land listings

**Demo Credentials:**
- Owner: `john_owner` / `password123`
- Buyer: `jane_buyer` / `password123`

### Step 6: Run the Application
```bash
python app.py
```

The application will start at: **http://localhost:5000**

## Usage Guide

### For Land Owners

1. **Register** with email and create account as "Land Owner"
2. **Login** to access Owner Dashboard
3. **Add Land**:
   - Fill in land details (title, location, size, price)
   - Add description
   - Click "Add Land"

4. **Upload Documents**:
   - Go to "My Lands" tab
   - Click "Upload Docs" on a land
   - Upload ownership proof (PDF/Images)
   - System checks for fraud/duplicates

5. **Manage Offers**:
   - Go to "Offers Received" tab
   - Accept or reject buyer offers
   - Automatically creates transaction when accepted

### For Buyers

1. **Register** with email and create account as "Buyer"
2. **Login** to access Buyer Dashboard
3. **Browse Lands**:
   - Use search filters (location, price, size)
   - View land details and documents
   - Check verification status

4. **Make Offers**:
   - Click "Make Offer" on a land
   - Enter your offered price
   - Wait for seller's response

5. **AI Recommendations**:
   - Go to "AI Recommendations" tab
   - Get personalized suggestions based on your offer history
   - Each recommendation includes matching score

6. **Real-Time Negotiation**:
   - Click "Chat" on an offer
   - Send messages and price offers
   - Communicate directly with seller

7. **View Purchases**:
   - Go to "My Purchases" tab
   - See all completed transactions
   - View blockchain verification details

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Lands
- `GET /api/lands` - Get all available lands
- `GET /api/lands?my_lands=true` - Get user's lands (owner only)
- `POST /api/lands` - Create new land (owner only)
- `GET /api/lands/<id>` - Get land details
- `PUT /api/lands/<id>` - Update land (owner only)
- `DELETE /api/lands/<id>` - Delete land (owner only)
- `GET /api/lands/search` - Search lands with filters

### Documents & Images
- `POST /api/lands/<id>/documents` - Upload document
- `POST /api/lands/<id>/images` - Upload image

### Offers
- `GET /api/offers` - Get user's offers
- `POST /api/offers` - Create new offer (buyer only)
- `PUT /api/offers/<id>` - Accept/reject offer (seller only)

### Recommendations
- `GET /api/recommendations` - Get AI recommendations (buyer only)

### Blockchain
- `GET /api/blockchain` - Get entire blockchain
- `GET /api/blockchain/statistics` - Get blockchain stats
- `GET /api/transactions/<land_id>` - Get land transactions
- `POST /api/verify-transaction` - Verify transaction

### User
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile

## Blockchain Details

### Block Structure
```python
{
    'index': int,
    'transaction': {
        'land_id': str,
        'buyer_id': str,
        'seller_id': str,
        'amount': float,
        'timestamp': str
    },
    'timestamp': str,
    'previous_hash': str,
    'hash': str,
    'nonce': int
}
```

### Genesis Block
Automatically created on blockchain initialization with system transaction.

### Mining
Blocks use Proof of Work (default difficulty: 2 leading zeros).

### Verification
Chain integrity verified by:
- Checking all block hashes
- Verifying previous hash pointers
- Ensuring no tampering

## AI Features

### Document Fraud Detection
- Extracts image features using SIFT, edge detection, histogram analysis
- Calculates document hash for duplicate detection
- Checks for unusual brightness, blur, aspect ratio
- Returns fraud confidence score (0.0 - 1.0)

### Land Recommendations
- Profile extraction from buyer's offer history
- Feature extraction from land listings
- Scoring based on:
  - Price matching with budget
  - Property availability
  - Verification status
  - Buyer's success history
- Returns top K recommendations with reasons

## Testing

### Manual Testing

1. **Register two accounts** (one owner, one buyer)
2. **Owner adds a land** with details
3. **Owner uploads documents** (check fraud detection)
4. **Buyer searches for lands** (test filters)
5. **Buyer makes an offer**
6. **Owner accepts offer** (triggers blockchain transaction)
7. **View transaction** in blockchain ledger

### API Testing with cURL

```bash
# Register user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"pass","role":"buyer"}'

# Get all lands
curl http://localhost:5000/api/lands

# Get blockchain
curl http://localhost:5000/api/blockchain

# Get blockchain stats
curl http://localhost:5000/api/blockchain/statistics
```

## Sample Data

### Users Created by seed_data
```
Owner:
- Username: john_owner
- Email: owner@test.com
- Password: password123

Buyer:
- Username: jane_buyer
- Email: buyer@test.com
- Password: password123
```

### Lands Created
1. Beautiful Residential Plot - $500,000 (5000 sq ft)
2. Commercial Space - $1,500,000 (10,000 sq ft)
3. Agricultural Land - $200,000 (50,000 sq ft)

## Troubleshooting

### Issue: "Address already in use"
**Solution**: Change port in app.py:
```python
socket_io.run(app, debug=True, host='0.0.0.0', port=5001)
```

### Issue: "ModuleNotFoundError"
**Solution**: Make sure virtual environment is activated and requirements are installed:
```bash
pip install -r requirements.txt
```

### Issue: Database errors
**Solution**: Delete `instance/land_registry.db` and reinitialize:
```bash
flask --app app init_db
flask --app app seed_data
```

### Issue: Upload folder doesn't exist
**Solution**: Create manually or run app once (it auto-creates):
```bash
mkdir -p uploads/documents uploads/images
```

## Security Considerations

⚠️ **This is a demonstration system. For production:**

1. **Use environment variables** for sensitive data:
   ```python
   import os
   SECRET_KEY = os.getenv('SECRET_KEY')
   ```

2. **Enable HTTPS** in production
3. **Add CSRF protection** to all forms
4. **Implement rate limiting** for API endpoints
5. **Use stronger password policies**
6. **Validate and sanitize all inputs**
7. **Implement proper authentication tokens** (JWT)
8. **Use production database** (PostgreSQL, etc.)
9. **Add logging and monitoring**
10. **Regular security audits**

## Performance Optimization Tips

1. **Database Indexing**: Already optimized with indexes on frequently queried fields
2. **Caching**: Consider implementing Redis for frequently accessed data
3. **Pagination**: Implement pagination for large land listings
4. **Image Optimization**: Resize images before upload
5. **Blockchain**: Consider moving old transactions to archive

## Future Enhancements

- [ ] Multi-signature transactions
- [ ] Smart contracts on blockchain
- [ ] Payment gateway integration
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Mobile app
- [ ] Advanced mapping features
- [ ] Document OCR
- [ ] Government database integration
- [ ] Insurance partnerships
- [ ] Escrow services
- [ ] Legal document generation

## Contributing

To contribute to this project:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is open source and available under MIT License.

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Contact: support@landregistry.com

## Author

Built as a demonstration of:
- Full-stack Python web development
- Blockchain implementation
- AI/ML integration
- Real-time communication
- Secure authentication

---

**Last Updated**: 2024
**Version**: 1.0.0
**Python Version**: 3.8+

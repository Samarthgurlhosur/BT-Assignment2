# Land Registration System - API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
Most endpoints require user to be logged in. Session-based authentication is used.

---

## Authentication Endpoints

### Register User
```
POST /register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "full_name": "John Doe",
  "phone": "1234567890",
  "address": "123 Main St",
  "role": "buyer"  // or "owner"
}

Response: 201 Created
{
  "message": "Registration successful",
  "user_id": "uuid"
}
```

### Login
```
POST /login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepass123"
}

Response: 200 OK
{
  "message": "Login successful",
  "user_id": "uuid",
  "role": "buyer"
}
```

### Logout
```
GET /logout

Response: 302 Redirect to /login
```

---

## Land Endpoints

### Get All Available Lands
```
GET /api/lands

Response: 200 OK
[
  {
    "id": "uuid",
    "title": "Beautiful Residential Plot",
    "description": "Prime location",
    "location": "Downtown",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "size_sqft": 5000,
    "price": 500000,
    "is_available": true,
    "verification_status": "verified",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "images": [],
    "documents": []
  }
]
```

### Get User's Lands (Owner Only)
```
GET /api/lands?my_lands=true

Authorization: Must be logged in as owner

Response: 200 OK
[
  {
    "id": "uuid",
    "title": "My Land",
    ...
  }
]
```

### Get Land Details
```
GET /api/lands/{land_id}

Response: 200 OK
{
  "id": "uuid",
  "title": "Beautiful Residential Plot",
  "location": "Downtown",
  "size_sqft": 5000,
  "price": 500000,
  "is_available": true,
  "verification_status": "verified",
  "owner": {
    "id": "uuid",
    "username": "john_owner",
    "full_name": "John Owner",
    ...
  },
  "images": [],
  "documents": []
}
```

### Create New Land (Owner Only)
```
POST /api/lands
Content-Type: application/json
Authorization: Must be logged in as owner

{
  "title": "New Property",
  "description": "Beautiful land",
  "location": "Downtown",
  "size_sqft": 5000,
  "price": 500000,
  "latitude": 40.7128,
  "longitude": -74.0060
}

Response: 201 Created
{
  "id": "new-uuid",
  "title": "New Property",
  "location": "Downtown",
  ...
}
```

### Update Land (Owner Only)
```
PUT /api/lands/{land_id}
Content-Type: application/json
Authorization: Must be owner of land

{
  "title": "Updated Title",
  "price": 550000,
  "is_available": false
}

Response: 200 OK
{
  "id": "uuid",
  "title": "Updated Title",
  ...
}
```

### Delete Land (Owner Only)
```
DELETE /api/lands/{land_id}
Authorization: Must be owner of land

Response: 200 OK
{
  "message": "Land deleted successfully"
}
```

### Search Lands
```
GET /api/lands/search?location=Downtown&min_price=100000&max_price=1000000&min_size=1000&max_size=10000&verified=true

Query Parameters:
- location (string): Search in location
- min_price (number): Minimum price
- max_price (number): Maximum price
- min_size (number): Minimum size in sq ft
- max_size (number): Maximum size in sq ft
- verified (boolean): Only verified properties

Response: 200 OK
[
  { land object },
  ...
]
```

---

## Document & Image Endpoints

### Upload Document (Owner Only)
```
POST /api/lands/{land_id}/documents
Content-Type: multipart/form-data
Authorization: Must be owner of land

Form Data:
- file: (PDF/Image file)
- document_type: "titleDeeds" or "surveyReport" or "taxDocument"

Response: 201 Created
{
  "message": "Document uploaded",
  "document": {
    "id": "uuid",
    "filename": "document.pdf",
    "document_type": "titleDeeds",
    "uploaded_at": "2024-01-15T10:30:00",
    "is_verified": false,
    "is_fraud_detected": false,
    "fraud_confidence": 0.15
  },
  "fraud_check": {
    "is_authentic": true,
    "fraud_confidence": 0.15,
    "reasons": ["Slightly low brightness detected"],
    "duplicate_detected": false
  }
}
```

### Upload Image (Owner Only)
```
POST /api/lands/{land_id}/images
Content-Type: multipart/form-data
Authorization: Must be owner of land

Form Data:
- file: (Image file)
- is_primary: true/false

Response: 201 Created
{
  "message": "Image uploaded",
  "image": {
    "id": "uuid",
    "filename": "land.jpg",
    "is_primary": true,
    "uploaded_at": "2024-01-15T10:30:00"
  }
}
```

---

## Offer Endpoints

### Create Offer (Buyer Only)
```
POST /api/offers
Content-Type: application/json
Authorization: Must be logged in as buyer

{
  "land_id": "uuid",
  "offered_price": 450000,
  "message": "Interested in your property"
}

Response: 201 Created
{
  "id": "uuid",
  "land_id": "uuid",
  "buyer_id": "uuid",
  "seller_id": "uuid",
  "offered_price": 450000,
  "status": "pending",
  "message": "Interested in your property",
  "created_at": "2024-01-15T10:30:00"
}
```

### Get Offers
```
GET /api/offers
Authorization: Must be logged in

Response: 200 OK
[
  {
    "id": "uuid",
    "land_id": "uuid",
    "buyer_id": "uuid",
    "seller_id": "uuid",
    "offered_price": 450000,
    "status": "pending",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### Accept/Reject Offer (Seller Only)
```
PUT /api/offers/{offer_id}
Content-Type: application/json
Authorization: Must be seller of offer

{
  "status": "accepted"  // or "rejected"
}

Response: 200 OK
{
  "id": "uuid",
  "status": "accepted",
  "updated_at": "2024-01-15T10:31:00"
}
```

---

## Blockchain Endpoints

### Get Entire Blockchain
```
GET /api/blockchain

Response: 200 OK
[
  {
    "index": 0,
    "transaction": { ... },
    "timestamp": "2024-01-15T10:30:00",
    "previous_hash": "0",
    "hash": "abc123...",
    "nonce": 100
  },
  ...
]
```

### Get Blockchain Statistics
```
GET /api/blockchain/statistics

Response: 200 OK
{
  "total_blocks": 10,
  "total_transactions": 5,
  "total_amount_transacted": 2500000,
  "chain_valid": true,
  "pending_transactions": 0
}
```

### Get Transaction History for Land
```
GET /api/transactions/{land_id}

Response: 200 OK
[
  {
    "block_index": 5,
    "block_hash": "abc123...",
    "land_id": "uuid",
    "buyer_id": "uuid",
    "seller_id": "uuid",
    "amount": 500000,
    "timestamp": "2024-01-15T10:30:00",
    "status": "COMPLETED"
  }
]
```

### Verify Transaction
```
POST /api/verify-transaction
Content-Type: application/json

{
  "land_id": "uuid",
  "buyer_id": "uuid",
  "seller_id": "uuid"
}

Response: 200 OK
{
  "verified": true,
  "transaction": { transaction details },
  "message": "Transaction found in blockchain"
}
```

---

## Recommendation Endpoints

### Get AI Recommendations (Buyer Only)
```
GET /api/recommendations
Authorization: Must be logged in as buyer

Response: 200 OK
[
  {
    "land_id": "uuid",
    "title": "Beautiful Plot",
    "price": 500000,
    "size_sqft": 5000,
    "location": "Downtown",
    "score": 0.85,
    "reason": "Recommended because it's within your budget, verified property, currently available"
  },
  ...
]
```

---

## Transaction Endpoints

### Get User Transactions
```
GET /api/my-transactions
Authorization: Must be logged in

Response: 200 OK
[
  {
    "id": "uuid",
    "land_id": "uuid",
    "buyer_id": "uuid",
    "seller_id": "uuid",
    "final_amount": 500000,
    "blockchain_hash": "abc123...",
    "blockchain_index": 5,
    "status": "completed",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

## User Profile Endpoints

### Get User Profile
```
GET /api/user/profile
Authorization: Must be logged in

Response: 200 OK
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "1234567890",
  "address": "123 Main St",
  "role": "buyer",
  "created_at": "2024-01-15T10:30:00"
}
```

### Update User Profile
```
PUT /api/user/profile
Content-Type: application/json
Authorization: Must be logged in

{
  "full_name": "John Doe Updated",
  "phone": "9876543210",
  "address": "456 Oak Ave"
}

Response: 200 OK
{
  "id": "uuid",
  "full_name": "John Doe Updated",
  ...
}
```

---

## Admin Endpoints

### Get All Users
```
GET /api/admin/users

Response: 200 OK
[
  { user objects },
  ...
]
```

### Get All Transactions
```
GET /api/admin/transactions

Response: 200 OK
[
  { transaction objects },
  ...
]
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid username or password"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## WebSocket Events

### Connect
```javascript
socket.on('connect', () => {
  console.log('Connected to server');
});
```

### Join Negotiation
```javascript
socket.emit('join_negotiation', { land_id: 'uuid' });
```

### Send Message
```javascript
socket.emit('send_message', {
  land_id: 'uuid',
  receiver_id: 'uuid',
  message: 'Hi, interested in this!'
});

socket.on('new_message', (data) => {
  console.log(data.message);
});
```

### Send Price Offer
```javascript
socket.emit('send_offer', {
  land_id: 'uuid',
  offered_price: 450000
});

socket.on('price_offer', (data) => {
  console.log('New price offer:', data.offered_price);
});
```

---

## Rate Limiting
Currently no rate limiting. Recommended for production.

## Pagination
Currently returns all results. Implement pagination for large datasets.

## Caching
Currently no caching. Recommended for frequently accessed data (lands, recommendations).

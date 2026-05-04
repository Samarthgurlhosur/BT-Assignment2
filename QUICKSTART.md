# Quick Start Guide

## Get Running in 2 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
python app.py
```

### 3. Open Browser
```
http://localhost:5000
```

## Demo Login Credentials

**Owner Account:**
- Username: `john_owner`
- Password: `password123`

**Buyer Account:**
- Username: `jane_buyer`
- Password: `password123`

> **Note**: Run `flask --app app seed_data` first to create demo accounts and sample lands.

## Quick Actions

### Owner Workflow
1. Login as `john_owner`
2. Go to "Add New Land" tab
3. Fill in land details
4. Upload ownership documents
5. View "Offers Received" when buyers make offers
6. Accept offers to complete transaction

### Buyer Workflow
1. Login as `jane_buyer`
2. Browse lands in "Browse Lands" tab
3. Use filters to search
4. Click "Make Offer" on a land
5. View AI recommendations
6. Track offers in "My Offers" tab

## Key Features to Try

### Real-Time Features
- Open two browser windows (owner and buyer)
- Make offer as buyer → See notification on owner
- Accept offer → See blockchain transaction created

### AI Features
- Upload documents as owner → Check fraud detection
- View buyer recommendations → AI suggests suitable lands

### Blockchain
- View blockchain ledger under "Blockchain" tab
- See all transactions recorded immutably
- Verify transaction integrity

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port 5000 in use | Change port in `app.py` line ~420 |
| Database error | Delete `land_registry.db`, run `init_db` again |
| Uploads not working | Create `uploads/documents` and `uploads/images` folders |

## File Organization

```
BT/
├── app.py              ← Main app
├── blockchain.py       ← Blockchain logic
├── models.py          ← Database models
├── ai_features.py     ← AI/ML features
├── templates/         ← HTML files
├── static/           ← CSS, JS files
└── uploads/          ← User uploads (created on first run)
```

## API Examples

### Get All Available Lands
```bash
curl http://localhost:5000/api/lands
```

### Get Blockchain Stats
```bash
curl http://localhost:5000/api/blockchain/statistics
```

### Search Lands
```bash
curl "http://localhost:5000/api/lands/search?location=Downtown&min_price=100000&max_price=1000000"
```

## Database

- **Type**: SQLite
- **Location**: `land_registry.db` (created on first run)
- **Tables**: Users, Lands, Offers, Messages, Transactions, etc.

## Next Steps

1. ✅ Run `python app.py`
2. 🔓 Login with demo credentials
3. 🏠 Explore features
4. 📚 Read [README.md](README.md) for full documentation
5. 🚀 Deploy to production

---

**Having issues?** Check [README.md](README.md) Troubleshooting section

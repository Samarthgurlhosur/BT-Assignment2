# Testing Guide for Land Registration System

## Test Scenarios

This guide provides step-by-step testing scenarios for all features of the application.

---

## Scenario 1: User Registration and Login

### Step 1: Register as Owner
1. Go to http://localhost:5000/register
2. Fill in:
   - Username: `test_owner_1`
   - Email: `owner1@test.com`
   - Full Name: `Test Owner`
   - Phone: `1234567890`
   - Address: `123 Owner St`
   - Role: Select "Land Owner"
   - Password: `TestPass123!`
3. Click "Register"
4. Should be redirected to login

### Step 2: Register as Buyer
1. Go to http://localhost:5000/register
2. Fill in:
   - Username: `test_buyer_1`
   - Email: `buyer1@test.com`
   - Full Name: `Test Buyer`
   - Phone: `0987654321`
   - Address: `456 Buyer Ave`
   - Role: Select "Buyer"
   - Password: `TestPass123!`
3. Click "Register"

### Step 3: Login as Owner
1. Go to http://localhost:5000/login
2. Username: `test_owner_1`
3. Password: `TestPass123!`
4. Click "Login"
5. Should see "Owner Dashboard"

### Expected Results ✓
- Users can register with unique usernames
- Users can login with correct credentials
- Different dashboards appear for different roles

---

## Scenario 2: Land Registration (Owner)

### Step 1: Add First Land
1. Login as owner
2. Go to "Add New Land" tab
3. Fill in:
   - Title: `Prime Downtown Plot`
   - Location: `Downtown Area`
   - Size: `5000` sq ft
   - Price: `500000`
   - Description: `Beautiful residential plot in prime location`
4. Click "Add Land"

### Step 2: Add Second Land
1. Same as step 1, but with:
   - Title: `Commercial Space`
   - Location: `Business District`
   - Size: `10000` sq ft
   - Price: `1500000`
   - Description: `Premium commercial land ready for development`

### Step 3: View Lands
1. Go to "My Lands" tab
2. Should see both lands listed
3. Click "Details" on a land to see full information

### Step 4: Update Land
1. In "My Lands" tab, click "Details"
2. Update price to `550000`
3. Click "Update"
4. Price should be updated

### Expected Results ✓
- Lands can be created with all details
- Lands appear in owner's listing
- Lands can be updated
- Each land gets unique ID

---

## Scenario 3: Document Upload (Owner)

### Step 1: Prepare Test Document
1. Create a simple text file named `title_deed.txt`
2. Add some content to it

### Step 2: Upload Document
1. Login as owner
2. Go to "My Lands" tab
3. Click "Upload Docs" on a land
4. Select the file
5. Choose document type: "Title Deeds"
6. Click "Upload"

### Step 3: Check Fraud Detection Results
1. After upload, should see fraud detection results
2. For text file: Fraud confidence should be low (legitimate)
3. Document should appear in land details

### Step 4: Try Uploading Invalid File
1. Try uploading a .txt file if not supported
2. Should get error: "File type not allowed"

### Expected Results ✓
- Documents upload successfully
- Fraud detection runs on upload
- Only allowed file types accepted
- Documents appear in land listing

---

## Scenario 4: Buyer Browsing (Buyer)

### Step 1: Browse Available Lands
1. Login as buyer
2. Go to "Browse Lands" tab
3. Should see all owner's lands
4. Each land shows title, location, price, size

### Step 2: Test Search Filters
1. Location filter: Search for "Downtown"
   - Should show only Downtown lands
2. Price filter: Min: `400000`, Max: `600000`
   - Should filter lands by price
3. Size filter: Min: `3000`, Max: `7000`
   - Should filter lands by size
4. Verified only: Check the checkbox
   - Should show only verified lands

### Step 3: View Land Details
1. Click "View Details" on a land
2. Modal should open with full details
3. Should show owner information
4. Should show documents and images

### Expected Results ✓
- All available lands display
- Filters work correctly
- Search results are accurate
- Land details modal opens properly

---

## Scenario 5: Making Offers (Buyer)

### Step 1: Make First Offer
1. Login as buyer
2. Go to "Browse Lands" tab
3. Click "Make Offer" on "Prime Downtown Plot"
4. Enter offer price: `450000`
5. Click "Submit"

### Step 2: Make Second Offer
1. Click "Make Offer" on "Commercial Space"
2. Enter offer price: `1400000`
3. Click "Submit"

### Step 3: View My Offers
1. Go to "My Offers" tab
2. Should see both offers
3. Status should be "pending"
4. Should show offered price and original price

### Expected Results ✓
- Offers can be created with custom prices
- Offers appear in buyer's list
- Offer status is "pending"
- Multiple offers can be made

---

## Scenario 6: Handling Offers (Owner)

### Step 1: Accept Offer
1. Login as owner
2. Go to "Offers Received" tab
3. Should see offers from buyers
4. Click "Accept" on first offer (450000)
5. Should see notification: "Offer accepted"

### Step 2: View Blockchain Transaction
1. Go to "Blockchain" tab
2. Should see new block with transaction
3. Check block details:
   - Land ID present
   - Buyer ID present
   - Seller ID present
   - Amount: 450000

### Step 3: Reject Offer
1. Go to "Offers Received" tab
2. Click "Reject" on second offer (1400000)
3. Status should change to "rejected"

### Expected Results ✓
- Offers can be accepted/rejected
- Blockchain records transactions
- Transaction appears in blockchain
- Offer status updates correctly

---

## Scenario 7: Recommendations (Buyer)

### Step 1: View AI Recommendations
1. Login as buyer who made offers
2. Go to "AI Recommendations" tab
3. Should see recommended lands
4. Each recommendation shows:
   - Title
   - Price
   - Size
   - Location
   - Recommendation score (0-100%)
   - AI reason

### Step 2: Check Recommendation Logic
1. Recommendations should be based on:
   - Buyer's budget (from previous offers)
   - Similar lands
   - Verified status

### Expected Results ✓
- Recommendations appear for buyer
- Scores are meaningful (0-100%)
- Recommendations have reasons
- Algorithm considers buyer history

---

## Scenario 8: Real-Time Notifications

### Step 1: Open Two Browser Windows/Tabs
1. Window 1: Logged in as owner
2. Window 2: Logged in as buyer

### Step 2: Test Offer Notification
1. In Window 2 (buyer): Make offer on a land
2. In Window 1 (owner): Should see notification
   - "New offer: $450000"

### Step 3: Test Offer Response Notification
1. In Window 1 (owner): Accept the offer
2. In Window 2 (buyer): Should see notification
   - "Offer accepted"

### Expected Results ✓
- Notifications are real-time
- Both sides see updates
- Notifications contain relevant info

---

## Scenario 9: Blockchain Verification

### Step 1: View Blockchain
1. Login as owner
2. Go to "Blockchain" tab
3. Should see blockchain statistics:
   - Total blocks
   - Total transactions
   - Total amount transacted
   - Chain validity ✓

### Step 2: View Blockchain Ledger
1. Scroll down to "Blockchain Ledger"
2. Should see list of blocks
3. Each block shows:
   - Block number
   - Hash (partial)
   - Previous hash

### Step 3: Verify Transaction
1. After accepting offer, transaction should be in blockchain
2. Transaction hash should be recorded
3. Should be immutable (can't modify)

### Expected Results ✓
- Blockchain displays correctly
- Statistics are accurate
- Transactions are immutable
- Chain integrity verified

---

## Scenario 10: Transaction History

### Step 1: Owner View Transactions
1. Login as owner
2. Go to "Transactions" tab
3. Should see transaction details:
   - Land ID
   - Buyer ID
   - Amount
   - Blockchain index
   - Date

### Step 2: Buyer View Purchases
1. Login as buyer
2. Go to "My Purchases" tab
3. Should see purchases:
   - Land details
   - Price paid
   - Blockchain confirmation
   - Date

### Expected Results ✓
- Transactions display correctly
- Blockchain references are present
- Transaction history is complete

---

## Test Data Checklist

### Owner Profile
- [ ] Username: `test_owner_1`
- [ ] Email: `owner1@test.com`
- [ ] Role: Owner
- [ ] At least 2 lands added
- [ ] Documents uploaded

### Buyer Profile
- [ ] Username: `test_buyer_1`
- [ ] Email: `buyer1@test.com`
- [ ] Role: Buyer
- [ ] Made at least 2 offers
- [ ] Accepted/rejected offers

### Lands
- [ ] Land 1: "Prime Downtown Plot" - $500,000
- [ ] Land 2: "Commercial Space" - $1,500,000
- [ ] All lands verified

### Offers
- [ ] Offer 1: $450,000 (Accepted -> Transaction)
- [ ] Offer 2: $1,400,000 (Rejected)

### Blockchain
- [ ] At least 1 transaction recorded
- [ ] Chain is valid
- [ ] Statistics updated

---

## API Testing with cURL

### Test User Registration
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"api_test_user",
    "email":"apitest@test.com",
    "password":"ApiTest123!",
    "full_name":"API Test User",
    "role":"buyer"
  }'
```

### Test Get Lands
```bash
curl http://localhost:5000/api/lands
```

### Test Search Lands
```bash
curl "http://localhost:5000/api/lands/search?location=Downtown&max_price=600000"
```

### Test Get Blockchain
```bash
curl http://localhost:5000/api/blockchain
```

### Test Blockchain Stats
```bash
curl http://localhost:5000/api/blockchain/statistics
```

### Test Create Offer
```bash
curl -X POST http://localhost:5000/api/offers \
  -H "Content-Type: application/json" \
  -d '{
    "land_id":"uuid-here",
    "offered_price":450000,
    "message":"Interested!"
  }'
```

---

## Performance Test

### Test Data Insertion
1. Seed 100+ lands
2. Add 500+ offers
3. Check response times

### Check Stats
```bash
curl http://localhost:5000/api/blockchain/statistics
```

Should return in < 100ms

---

## Error Handling Tests

### Test Invalid Input
1. Try registering with duplicate username
   - Expected: Error message
2. Try non-existent land
   - Expected: 404 Not Found
3. Try accessing other user's lands
   - Expected: 403 Forbidden

---

## Security Tests

### Test Password Security
1. Try weak password
   - Should accept (no validation)
   - Add validation in production
2. Try common passwords
   - Should add blacklist in production

### Test Session Security
1. Login and close browser
2. Open new browser tab
3. Should require re-login

---

## Checklist for Release

- [ ] All 10 scenarios pass
- [ ] API responses correct
- [ ] Blockchain working
- [ ] Real-time notifications working
- [ ] AI recommendations working
- [ ] No errors in console
- [ ] Database integrity maintained
- [ ] Performance acceptable
- [ ] Security tests pass

---

## Known Issues & Workarounds

| Issue | Workaround |
|-------|-----------|
| Port 5000 in use | Change to 5001 in app.py |
| Database locked | Delete .db and reinitialize |
| Uploads not working | Create uploads/ folder |
| Socket.IO not connecting | Check browser console |

---

**Last Updated**: 2024
**Test Version**: 1.0.0

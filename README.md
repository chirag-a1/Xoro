# xoro
A full-stack trading platform featuring a Flask backend and a React frontend. It provides user authentication, portfolio management, trading operations, AI-powered recommendations, and live market data. The backend handles all API endpoints, database models, and business logic, while the frontend offers a modern UI for trading, analytics, and watchlists. The app is designed for paper trading and analytics, with robust error handling and clear documentation.


## 🚀 **How to Run**

### 1. **Start Backend Server**
```bash
cd backend
python app.py
```
**Backend runs on:** `http://localhost:5000`

### 2. **Start Frontend Server**
```bash
cd fend
python -m http.server 3000
```
**Frontend runs on:** `http://localhost:3000`

### 3. **Access Application**
Open your browser and go to: `http://localhost:3000/xoro_premium_trading_app.html`

## 📡 **API Endpoints**

### **Authentication**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT token)
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - Logout user

### **Portfolio Management**
- `GET /api/portfolio/` - Get full portfolio
- `GET /api/portfolio/balance` - Get cash balance
- `GET /api/portfolio/holdings` - Get stock holdings
- `GET /api/portfolio/stats` - Get portfolio statistics
- `POST /api/portfolio/reset` - Reset portfolio (testing)

### **Trading Operations**
- `POST /api/trading/buy` - Buy stocks
- `POST /api/trading/sell` - Sell stocks
- `GET /api/trading/orders` - Get trading history
- `GET /api/trading/orders/<id>` - Get specific trade
- `GET /api/trading/market-data/<symbol>` - Get market data

### **AI Recommendations**
- `POST /api/ai/recommendations` - Get AI trading recommendations
- `GET /api/ai/market-analysis` - Get market analysis
- `GET /api/ai/portfolio-analysis` - Get portfolio analysis

### **Health Check**
- `GET /api/health` - Server health check

## 🔧 **Technical Features**

### **CORS Configuration**
- ✅ Allows `http://localhost:3000`
- ✅ Allows `http://127.0.0.1:3000`
- ✅ Allows `file://` protocol
- ✅ Supports preflight OPTIONS requests
- ✅ Allows all necessary headers and methods

### **Database**
- ✅ SQLite database with proper relationships
- ✅ User, Portfolio, Stock, Trade models
- ✅ Auto-creates tables on startup
- ✅ Proper constraints and validations

### **Authentication**
- ✅ JWT tokens with 12-hour expiration
- ✅ Bcrypt password hashing
- ✅ Proper error handling for invalid tokens
- ✅ Token refresh functionality

### **Error Handling**
- ✅ Consistent JSON error responses
- ✅ Proper HTTP status codes
- ✅ Database constraint handling
- ✅ Input validation

## 🧪 **Testing the Application**

### **1. Test Registration**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

### **2. Test Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### **3. Test Portfolio**
```bash
curl -X GET http://localhost:5000/api/portfolio/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **4. Test Trading**
```bash
curl -X POST http://localhost:5000/api/trading/buy \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"symbol":"AAPL","quantity":1,"price":150.00}'
```

## 🎉 **Success Indicators**

When everything is working correctly, you should see:

1. **Backend Console:** Shows all registered routes
2. **Frontend:** No network errors on login/signup
3. **Authentication:** JWT tokens working properly
4. **Trading:** Buy/sell operations working
5. **Portfolio:** Data loading correctly
6. **CORS:** No preflight failures

## 🔍 **Troubleshooting**

### **If you still see network errors:**

1. **Check both servers are running:**
   - Backend: `http://localhost:5000/api/health`
   - Frontend: `http://localhost:3000`

2. **Verify CORS is working:**
   - Check browser developer tools → Network tab
   - Look for OPTIONS requests succeeding

3. **Check JWT tokens:**
   - Verify token is being sent in Authorization header
   - Check token expiration

## 🎯 **Final Result**

✅ **Complete Flask backend** with all required features  
✅ **Working authentication** with JWT  
✅ **CORS properly configured**  
✅ **All API endpoints functional**  
✅ **Database models working**  
✅ **Error handling implemented**  
✅ **Frontend can communicate** without network errors  

**Your trading application is now fully functional!** 🚀


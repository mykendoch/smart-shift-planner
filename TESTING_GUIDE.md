# 🧪 TESTING INSTRUCTIONS - Smart Shift Planner

**Date:** February 13, 2026  
**You are here:** Frontend running at http://localhost:3000

---

## ✅ QUICK START CHECKLIST

- [x] Frontend build: **SUCCESSFUL** - npm run dev running
- [x] Design system: **IMPLEMENTED** - CSS files created for all pages
- [x] Login page: **REDESIGNED** - Professional, no Google login
- [x] Logging: **ADDED** - Check console (F12) for debug messages
- [x] Forgot password: **CREATED** - Separate page ready
- [ ] Backend: **NEEDS TO START** - Run `uvicorn src.main:app --reload --port 8000`
- [ ] Database: **SEEDED** - Admin and driver credentials ready

---

## 🚀 TESTING FLOW

### Step 1: Verify Frontend is Running ✅
- Frontend is currently running at http://localhost:3000
- You should see the login page with:
  - White card centered on gray background
  - "Welcome Back" heading
  - Email input field
  - Password input field with show/hide toggle
  - Orange "Login" button
  - Admin mode toggle at bottom

### Step 2: Start the Backend
```bash
cd c:\Users\myken\GIHUB PROJECT\STUDENT\smart-shift-planner\backend

# Option 1: Using uvicorn directly
uvicorn src.main:app --reload --port 8000

# Option 2: Using Python module
python -m uvicorn src.main:app --reload --port 8000

# Should see:
# Uvicorn running on http://127.0.0.1:8000
# Application startup complete
```

### Step 3: Test Admin Login ✅
```
1. Go to http://localhost:3000 (already redirects to /login)
2. Enter Email: mykendoche@gmail.com
3. Enter Password: admin123
4. Click "Login" button
5. Verify:
   - Loading state (button shows "Logging in...")
   - Console shows [INFO] messages (F12)
   - Redirects to http://localhost:3000/dashboard
```

### Step 4: Test Logging System ✅
```
1. Open DevTools: F12 or Ctrl+Shift+I
2. Go to Console tab
3. Try to login with wrong password
4. Look for messages with [INFO], [DEBUG], [ERROR] prefix
5. Should see:
   - [INFO] Login attempt started
   - [ERROR] Login failed (with error message)
6. Try correct password
7. Should see:
   - [INFO] Login attempt started
   - [INFO] Login successful
   - [INFO] Redirecting to dashboard
```

### Step 5: Test Forgot Password ✅
```
1. From login page, click "Forgot Password?" button
2. Should navigate to http://localhost:3000/forgot-password
3. Enter any email address
4. Click "Send Reset Link"
5. Should see:
   - Button changes to "Sending..."
   - Success message displays
   - Auto-countdown to redirect
   - Redirects to /login after 3 seconds
```

### Step 6: Test Admin/Driver Toggle ✅
```
1. From login page, scroll down
2. Click "Login as Admin" (or "Login as Driver" if already in admin mode)
3. Mode should switch in UI
4. Email and password fields clear
5. Try login with:
   - Admin: mykendoche@gmail.com / admin123
   - Driver: driver@example.com / driver123
```

### Step 7: Test Design System ✅
**Color Verification:**
- [ ] Orange button (#ff5722) - hover becomes darker (#d84a25)
- [ ] Dark gray text (#333) for headings
- [ ] Medium gray text (#666) for descriptions
- [ ] Light gray borders (#e0e0e0)
- [ ] Light gray background (#f5f5f5)
- [ ] White cards (#fff)

**Responsive Design:**
- [ ] Resize browser to 480px width - layout adjusts
- [ ] Resize to 768px width - still readable
- [ ] Resize to 1200px width - proper spacing
- [ ] Mobile view: 1 column, compact padding
- [ ] Desktop view: centered card, good spacing

**Interactive Elements:**
- [ ] Hover password input - border becomes orange
- [ ] Hover button - becomes darker orange
- [ ] Focus on input - shows orange border + box shadow
- [ ] Disabled inputs - grayed out, not clickable
- [ ] Checkbox - checked state is orange

---

## 📊 Dashboard Pages Testing

### After Successful Login
You should see the dashboard with navigation to:
1. **Accuracy** - Model performance metrics
2. **Analytics** - Shift data analytics
3. **Eligibility** - Worker eligibility status
4. **Survey Admin** - Aggregated survey feedback
5. **Surveys** - Individual survey responses
6. **Volatility** - Income volatility analysis
7. **Workers** - Worker management interface

**Verify:**
- [ ] All pages load without errors
- [ ] Design is consistent across pages
- [ ] Orange accent color (#ff5722) visible
- [ ] Professional spacing and typography
- [ ] Responsive on mobile resize

---

## 🐛 DEBUGGING WITH LOGS

### View Logs
1. Press F12 (or Ctrl+Shift+I on Windows)
2. Click "Console" tab
3. Perform action (login, forgot password, navigate)
4. Look for prefixed messages:
   - `[INFO]` - Normal operations
   - `[DEBUG]` - Detailed information
   - `[ERROR]` - Errors and warnings

### Example Log Output
```
[INFO] Login attempt started {email: "mykendoche@gmail.com"}
[DEBUG] Calling authentication service {endpoint: "/auth/login"}
[INFO] Login successful {email: "mykendoche@gmail.com"}
[DEBUG] Token stored in localStorage {hasToken: true}
[INFO] Redirecting to dashboard {path: "/dashboard"}
```

### Clear Logs
```
console.clear()  // Clears all logs
```

---

## ❌ TROUBLESHOOTING

### Issue: "Cannot reach localhost:8000"
**Solution:**
```bash
# Start backend
cd backend
python -m uvicorn src.main:app --reload --port 8000

# Should show:
# Uvicorn running on http://127.0.0.1:8000
# Application startup complete
```

### Issue: "Database connection refused"
**Solution:**
1. Ensure PostgreSQL is running
2. Check .env file has correct DATABASE_URL
3. Verify database credentials: `postgres:Ndoch`
4. Seed database:
```bash
cd backend
python scripts/seed_admin.py
```

### Issue: "Login page not loading"
**Solution:**
```bash
# Rebuild frontend
cd frontend
npm install  # Install dependencies
npm run build  # Build for production
npm run dev  # Run development server
```

### Issue: "No console logs showing"
**Solution:**
1. Open DevTools (F12)
2. Go to Console tab
3. Check for filters - remove any active filters
4. Reload page (F5)
5. Try login again

### Issue: "Page redirects loop"
**Solution:**
1. Open DevTools Application tab
2. Go to Storage → Local Storage
3. Delete "token" key
4. Reload page
5. Try login again

---

## 📈 SUCCESS CRITERIA

Your testing is successful when:

### Frontend ✅
- [ ] Pages load without JavaScript errors
- [ ] No TypeScript compilation errors
- [ ] All 13 routes accessible
- [ ] Build size reasonable (<200KB per page)

### Design System ✅
- [ ] Colors consistent across all pages
- [ ] Typography readable and proper size
- [ ] Spacing balanced and consistent
- [ ] Responsive layout works on all sizes
- [ ] Hover/focus states visible

### Authentication ✅
- [ ] Admin can login with correct credentials
- [ ] Driver can login with correct credentials
- [ ] Wrong password shows error message
- [ ] Successful login redirects to /dashboard
- [ ] Logout clears token and redirects to /login

### Logging ✅
- [ ] Console shows [INFO] messages for successful login
- [ ] Console shows [DEBUG] messages for API calls
- [ ] Console shows [ERROR] messages for failures
- [ ] Timestamps and context included
- [ ] No JavaScript errors in console

### Forgot Password ✅
- [ ] Page loads properly
- [ ] Email input accepts input
- [ ] Submit button sends request
- [ ] Success message displays
- [ ] Auto-redirects after 3 seconds

---

## 📱 RESPONSIVE TESTING

### Mobile (320px - 480px)
```
Expected:
- Single column layout
- Full-width cards with margin
- Readable font size (16px minimum)
- Touchable button size (44px minimum)
```

### Tablet (481px - 768px)
```
Expected:
- Readable text
- Good button spacing
- Cards with proper padding
- Images/graphics scaled properly
```

### Desktop (769px+)
```
Expected:
- Centered content
- Max-width for readability (450px for login)
- Proper whitespace
- Professional spacing
```

---

## 🔍 VERIFICATION CHECKLIST

### Before Testing
- [ ] Frontend running: `npm run dev` or npm run build + preview
- [ ] Backend running: `uvicorn src.main:app --reload`
- [ ] Database: PostgreSQL running, .env configured
- [ ] Browser: Open http://localhost:3000, not file://
- [ ] DevTools: F12 can be opened

### During Testing
- [ ] All clicks respond immediately
- [ ] No console red error messages
- [ ] Buttons show loading state
- [ ] Error messages appear for invalid input
- [ ] Success messages appear for valid actions
- [ ] Redirects happen within 1-2 seconds
- [ ] Logs appear in console with proper format

### After Testing
- [ ] Can logout and login again
- [ ] Multiple logins work correctly
- [ ] Dashboard loads after login
- [ ] All pages are accessible
- [ ] Design is consistent
- [ ] No performance issues

---

## 📞 SUPPORT

If you encounter issues:

1. **Check the logs:** F12 → Console (look for [ERROR])
2. **Check the docs:** See VERIFICATION_COMPLETE.md
3. **Check the code:** frontend/src/app/login/page.tsx
4. **Check the setup:** backend/.env for DATABASE_URL
5. **Rebuild frontend:** `npm run build` and test again

---

## 🎯 TEST RESULTS

### Test Date: February 13, 2026
- Frontend Build: ✅ PASSED
- TypeScript Check: ✅ PASSED
- Design System: ✅ IMPLEMENTED
- Login Page: ✅ REDESIGNED
- Logging: ✅ ADDED  
- Forgot Password: ✅ CREATED
- CSS Files: ✅ ALL CREATED (5 files)
- API Integration: ✅ READY

**Overall Status: ✅ PRODUCTION READY FOR TESTING**

---

Remember:
- Keep DevTools open (F12) while testing
- Check console logs for authentication flow visibility
- Test on different screen sizes
- Try both admin and driver accounts
- Verify all dashboard pages load

**Happy Testing! 🎉**

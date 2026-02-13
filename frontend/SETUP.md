# Frontend Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env.local
```

Edit `.env.local` to point to your backend API:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Start Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Demo Login Credentials

After the backend is running and database is seeded with demo data:

**Driver Account**:
- Email: `driver@example.com`
- Password: `password123`

**Admin Account**:
- Email: `admin@example.com`
- Password: `password123`

## What You Can Do

### As a Driver
1. **Login** with driver credentials
2. **View Dashboard** with quick links
3. **Check Income Insights** - See how guarantee reduces volatility
4. **Submit Feedback** - Rate your experience on 6 dimensions
5. **Review Eligibility** - Check if you qualify for income guarantee

### As an Admin
1. **Login** with admin credentials
2. **Monitor Analytics** - View system-wide metrics
3. **Check Model Performance** - Track prediction accuracy
4. **Review Survey Reports** - Analyze aggregated driver feedback
5. **Manage Workers** - Check worker status and eligibility

## File Structure Overview

```
frontend/
├── src/
│   ├── app/              # Pages and layouts
│   │   ├── login/        # Authentication
│   │   ├── register/
│   │   └── dashboard/    # Main application
│   ├── lib/
│   │   ├── store.ts      # User authentication state
│   │   ├── api.ts        # Backend API calls
│   │   └── hooks.ts      # Custom React hooks
│   ├── globals.css       # Styling with Tailwind
│   └── layout.tsx        # Root layout
├── public/               # Static assets
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
└── tailwind.config.js    # Tailwind config
```

## Development Workflow

### Add a New Feature Page

1. Create page file in `src/app/dashboard/{feature}/page.tsx`
2. Add navigation link in `src/app/dashboard/layout.tsx`
3. Use existing hooks from `lib/hooks.ts` for API calls
4. Style with Tailwind classes

### Make API Calls

1. Add method to `lib/api.ts`
2. Create hook in `lib/hooks.ts`
3. Use hook in component:

```typescript
const { data, loading, error } = useVolatility(worker_id, 30);
```

### Styling

- Use Tailwind classes: `className="text-blue-600 font-bold"`
- Component classes: `.card`, `.btn-primary`, `.input-field`
- Colors: Blue (#3B82F6), Green (#10B981), Red (#EF4444)

## Running in Production

### Build
```bash
npm run build
npm start
```

### Deploy to Vercel
```bash
vercel deployment
```

Set `NEXT_PUBLIC_API_BASE_URL` environment variable on Vercel dashboard.

## Troubleshooting

### "Cannot GET /dashboard"
- Backend API not running
- `NEXT_PUBLIC_API_BASE_URL` incorrect
- Solution: Start backend and verify URL

### "401 Unauthorized"
- Token expired
- Invalid credentials
- Solution: Clear localStorage and re-login

### Page Blank/Crashing
- Check browser console for errors
- Check Network tab for failed API calls
- Verify backend is reachable

## Next Steps

1. **Run backend**: Start FastAPI server on port 8000
2. **Seed data**: Run database migrations and seed demo accounts
3. **Start frontend**: `npm run dev`
4. **Login**: Use demo credentials
5. **Explore**: Click through pages and interact with features

## Notes

- All passwords are hashed with BCrypt on backend
- JWT tokens stored in browser localStorage
- Logout clears token from localStorage
- Admin features require ADMIN role
- Driver can only see own data (filtered on backend)

## Support

Check the main [README.md](./README.md) for detailed documentation.

# Smart Shift Planner - Frontend

A Next.js dashboard frontend for the Smart Shift Planner system, providing role-based interfaces for drivers and administrators.

## Features

### Driver Dashboard
- **Income Insights**: Visualize earnings volatility reduction with income guarantee
- **Survey Feedback**: Submit Likert-scale surveys on income stress, schedule satisfaction, app usefulness, and more
- **Eligibility Status**: Check current guarantee eligibility and track required metrics
- **Authentication**: Secure login and registration with JWT tokens

### Admin Dashboard
- **System Analytics**: Monitor key system metrics and worker performance
- **Model Performance**: Track prediction accuracy (MAPE, MAE, RMSE, R²) against specification targets
- **Survey Reports**: View aggregated driver feedback and extract anonymized data for research
- **Worker Management**: Monitor worker status, eligibility, and manage accounts

## Tech Stack

- **Framework**: Next.js 14+ (TypeScript)
- **State Management**: Zustand
- **HTTP Client**: Axios with JWT interceptors
- **Charting**: Recharts
- **Styling**: Tailwind CSS
- **API Integration**: RESTful backend (FastAPI)

## Setup

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update `.env.local` with your backend API URL:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### Running the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The app will automatically reload on code changes.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                          # Next.js app directory
│   ├── layout.tsx               # Root layout with auth check
│   ├── globals.css              # Global Tailwind styles
│   ├── login/page.tsx           # Login page
│   ├── register/page.tsx        # Registration page
│   └── dashboard/
│       ├── layout.tsx           # Dashboard layout with navigation
│       ├── page.tsx             # Main dashboard with role-based content
│       ├── volatility/page.tsx  # Driver: Income insights (FR14)
│       ├── surveys/page.tsx     # Driver: Survey submission (FR16)
│       ├── eligibility/page.tsx # Driver: Eligibility status (FR9)
│       ├── analytics/page.tsx   # Admin: System analytics
│       ├── accuracy/page.tsx    # Admin: Model performance (NFR3)
│       ├── survey-admin/page.tsx # Admin: Survey reports
│       └── workers/page.tsx     # Admin: Worker management
├── lib/
│   ├── store.ts                 # Zustand auth store
│   ├── api.ts                   # Axios API client & service functions
│   └── hooks.ts                 # React hooks for data fetching

```

## Authentication Flow

1. User navigates to `/login` or `/register`
2. Backend validates credentials and returns JWT token
3. Token stored in localStorage
4. Axios interceptor automatically adds token to all requests
5. If token expires (401), user is redirected to login
6. Dashboard pages check authentication and redirect if needed

## API Integration

All API calls go through `lib/api.ts` service:

```typescript
// Example: Submit survey
import { apiService } from '@/lib/api';

const response = await apiService.submitSurvey({
  income_stress_level: 4,
  schedule_satisfaction: 3,
  // ... other fields
  feedback: "User comment"
});
```

### Available Endpoints

**Authentication**:
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user profile

**Volatility (Driver/Admin)**:
- `GET /analytics/worker/{worker_id}/volatility` - Get volatility metrics
- `GET /analytics/volatility/summary` - System-wide summary (admin only)

**Accuracy (Admin)**:
- `GET /models/accuracy` - Get accuracy metrics
- `GET /models/accuracy/summary` - Overall accuracy summary

**Surveys (Driver/Admin)**:
- `POST /surveys/submit` - Submit survey response
- `GET /surveys/my-surveys` - Get own survey history
- `GET /surveys/aggregate-report` - Aggregated results (admin only)
- `GET /surveys/export-anonymized` - Export hashed data (admin only)

**Eligibility (Driver/Admin)**:
- `GET /eligibility/worker/{worker_id}` - Check eligibility status
- `POST /eligibility/worker/{worker_id}/recalculate` - Recalculate metrics (admin only)
- `POST /eligibility/worker/{worker_id}/suspend` - Suspend access (admin only)
- `POST /eligibility/worker/{worker_id}/reactivate` - Reactivate account (admin only)

## Role-Based Access Control

### DRIVER
- View own income insights and volatility metrics
- Submit and view survey responses
- Check own eligibility status
- Profile management

### ADMIN
- View system-wide analytics
- Monitor model performance against specification targets
- View aggregated survey reports
- Manage worker eligibility
- Export anonymized survey data for research
- Configure system parameters

## Features Implemented

### FR14: Income Volatility Analysis
- Displays earnings comparison with and without guarantee
- Statistical metrics: mean, std dev, CV, percentiles, IQR
- Visual charts showing volatility reduction percentage
- Answers RQ2: Income variance reduction quantification

### NFR3: Model Accuracy Monitoring
- Tracks MAPE, MAE, RMSE, R² metrics
- Compliance check against specification (MAPE ≤ 20%)
- Accuracy levels: Excellent/Good/Acceptable/Poor
- Accuracy breakdown by location and hour of day

### FR16: Survey Data Collection
- 6-point Likert scale questions plus open feedback
- Submission tracking with timestamps
- Admin aggregation and analysis
- Anonymization with SHA-256 hashing for research export
- Answers RQ3: System impact on productivity/satisfaction

### FR9: Eligibility Enforcement
- Status checking with detailed metric breakdown
- Active hours, acceptance rate, cancellation rate validation
- Average rating requirements
- Admin suspension/reactivation capabilities

## Styling

Tailwind CSS is configured with custom color palette:
- Primary: `#3B82F6` (blue)
- Secondary: `#10B981` (green) 
- Danger: `#EF4444` (red)
- Warning: `#F59E0B` (amber)

Custom component classes in `globals.css`:
- `.card` - Rounded white card with shadow
- `.btn-primary` - Primary button
- `.btn-secondary` / `.btn-danger` - Other button variants
- `.input-field` - Styled form input
- `.error-message` / `.success-message` - Status messages

## Development Tips

### Adding a New Page

1. Create file in `src/app/dashboard/{feature}/page.tsx`
2. Add authentication check if role-specific
3. Import and use hooks from `lib/hooks.ts`
4. Add navigation link in `dashboard/layout.tsx`

### Adding API Integration

1. Add service method to `lib/api.ts`
2. Create custom hook in `lib/hooks.ts` using `useEffect` for data fetching
3. Use hook in component with loading/error states

### Debugging

Set `NEXT_PUBLIC_DEBUG=true` in `.env.local` to enable console logging.

Use browser DevTools:
- Network tab: Monitor API calls and tokens
- Application tab: Inspect localStorage tokens
- Console: Check for client-side errors

## Performance

- Server-side rendering for initial page load
- Client-side navigation between dashboard pages
- Images optimized with Next.js Image component
- Code splitting automatic per route

## Error Handling

All API calls include error boundaries:
```typescript
try {
  const response = await apiService.getWorkerVolatility(workerId);
  setData(response.data);
} catch (err: any) {
  setError(err.response?.data?.detail || 'Failed to fetch data');
}
```

## Testing

Currently no automatic tests. To add:

1. Install Jest and React Testing Library
2. Create `__tests__` folders alongside components
3. Test component rendering and user interactions
4. Mock Zustand store and API calls

Example:
```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set `NEXT_PUBLIC_API_BASE_URL` in environment variables
4. Deploy automatically on push

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Environment Configuration

- Development: `http://localhost:3000`
- Production: Set `NEXT_PUBLIC_API_BASE_URL` to deployed backend URL

## Troubleshooting

### Build Fails
- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run lint`

### API Calls Failing
- Verify backend is running on correct port
- Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
- Clear localStorage: Open DevTools → Application → Clear All
- Check CORS configuration on backend

### Authentication Issues
- Token stored in localStorage might be expired
- Check browser console for 401 Unauthorized
- Manually delete token from localStorage and re-login
- Verify backend `SECRET_KEY` matches frontend expectations

## Contributing

1. Follow TypeScript strict mode
2. Use Tailwind classes instead of inline styles
3. Add error handling for all API calls
4. Test role-based access before committing

## License

Proprietary - Smart Shift Planner Project

## Support

For issues or questions:
- Check API backend documentation
- Review component error messages in console
- Verify authentication state in localStorage

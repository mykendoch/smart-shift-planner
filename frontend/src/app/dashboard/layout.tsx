'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';

interface LayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: LayoutProps) {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-blue-600">Smart Shift Planner</h1>
            {user && (
              <p className="ml-4 text-gray-600">
                {user.role === 'admin' ? '👨‍💼 Admin' : '👤 Driver'} Dashboard
              </p>
            )}
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <>
                <span className="text-gray-700">{user.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="btn-secondary text-sm"
                >
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex space-x-6">
            <NavLink href="/dashboard" label="Home" />
            {user?.role === 'driver' && (
              <>
                <NavLink href="/dashboard/volatility" label="Income Insights" />
                <NavLink href="/dashboard/surveys" label="Feedback" />
                <NavLink href="/dashboard/eligibility" label="Eligibility" />
              </>
            )}
            {user?.role === 'admin' && (
              <>
                <NavLink href="/dashboard/analytics" label="Analytics" />
                <NavLink href="/dashboard/accuracy" label="Model Performance" />
                <NavLink href="/dashboard/survey-admin" label="Survey Reports" />
                <NavLink href="/dashboard/workers" label="Workers" />
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="text-gray-600 hover:text-blue-600 font-medium transition"
    >
      {label}
    </Link>
  );
}

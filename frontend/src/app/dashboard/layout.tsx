'use client';

import { useRouter } from 'next/navigation';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from '@/lib/store';
import { showToast } from '@/lib/notify';
import { colors, spacing } from '@/lib/theme';

interface LayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: LayoutProps) {
  const router = useRouter();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    showToast.success('Signed out successfully');
    setTimeout(() => {
      router.push('/login');
    }, 500);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: colors.neutral[50] }}>
      <Toaster position="top-right" />
      <main style={{ width: '100%' }}>
        {children}
      </main>
    </div>
  );
}


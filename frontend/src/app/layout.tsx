'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { token, loadUserFromToken } = useAuthStore();

  useEffect(() => {
    // Load user from token on mount
    if (!useAuthStore.getState().user && token) {
      loadUserFromToken();
    }
  }, []);

  // Redirect to login if not authenticated (except on login/register pages)
  useEffect(() => {
    const isPublicPage = pathname === '/login' || pathname === '/register';
    const isAuthenticated = !!useAuthStore.getState().token;

    if (!isAuthenticated && !isPublicPage) {
      router.push('/login');
    }
  }, [pathname, router]);

  return (
    <html lang="en">
      <head>
        <title>Smart Shift Planner</title>
        <meta name="description" content="Smart Shift Planner Dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="bg-gray-50">
        {children}
      </body>
    </html>
  );
}

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Toaster } from 'react-hot-toast';
import { Eye, EyeOff, AlertCircle, LogIn } from 'lucide-react';
import { useAuthStore } from '@/lib/store';
import { showToast } from '@/lib/notify';
import './login.css';

// Logger utility for debugging
const logger = {
  debug: (msg: string, data?: any) => console.log(`[DEBUG] ${msg}`, data || ''),
  info: (msg: string, data?: any) => console.log(`[INFO] ${msg}`, data || ''),
  error: (msg: string, data?: any) => console.error(`[ERROR] ${msg}`, data || ''),
};

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState('');
  const [isAdminMode, setIsAdminMode] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    logger.info('Login attempt started', { email, isAdminMode });

    if (!email || !password) {
      const msg = 'Email and password are required';
      setLocalError(msg);
      showToast.error(msg);
      logger.error(msg);
      return;
    }

    try {
      logger.debug('Calling authentication service', { endpoint: '/auth/login' });
      
      const response = await login(email, password);
      logger.info('Login successful', { email });
      
      showToast.success('Welcome back!');
      
      // Determine redirect based on role or mode
      const token = localStorage.getItem('token');
      logger.debug('Token stored in localStorage', { hasToken: !!token });
      
      const redirectPath = '/dashboard';
      logger.info('Redirecting to dashboard', { path: redirectPath });
      
      setTimeout(() => {
        router.push(redirectPath);
      }, 800);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Invalid email or password';
      setLocalError(errorMsg);
      showToast.error(errorMsg);
      logger.error('Login failed', { email, error: errorMsg, status: error.response?.status });
    }
  };

  const handleForgotPassword = (e: React.MouseEvent) => {
    e.preventDefault();
    logger.info('Navigating to password reset');
    router.push('/forgot-password');
  };

  return (
    <>
      <Toaster />
      <div className="auth-container">
        <div className="auth-card">
          {/* Header */}
          <div className="auth-header">
            <h1>Welcome Back</h1>
            <p>Login to {isAdminMode ? 'Admin' : 'Smart Shift Planner'}</p>
          </div>

          {/* Error Alert */}
          {(error || localError) && (
            <div className="alert alert-error">
              <AlertCircle size={16} className="alert-icon" />
              <span>{error || localError}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
                autoFocus
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="password-input-wrapper">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Form Options */}
            <div className="form-options">
              <label className="remember-me">
                <input type="checkbox" disabled={isLoading} />
                Remember me
              </label>
              <button 
                type="button" 
                className="forgot-password"
                onClick={handleForgotPassword}
                disabled={isLoading}
              >
                Forgot Password?
              </button>
            </div>

            {/* Submit Button */}
            <button type="submit" className="btn-submit" disabled={isLoading}>
              <LogIn size={16} style={{ marginRight: '8px' }} />
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          {/* Divider */}
          <div className="divider">
            <span>or</span>
          </div>

          {/* Admin/User Toggle */}
          <div className="auth-toggle">
            {!isAdminMode ? (
              <p className="auth-toggle-text">
                Are you staff?{' '}
                <button 
                  type="button" 
                  className="toggle-link"
                  onClick={() => {
                    setIsAdminMode(true);
                    setEmail('');
                    setPassword('');
                    setLocalError('');
                    logger.info('Switched to admin mode');
                  }}
                >
                  Login as Admin
                </button>
              </p>
            ) : (
              <p className="auth-toggle-text">
                Driver account?{' '}
                <button 
                  type="button" 
                  className="toggle-link"
                  onClick={() => {
                    setIsAdminMode(false);
                    setEmail('');
                    setPassword('');
                    setLocalError('');
                    logger.info('Switched to driver mode');
                  }}
                >
                  Login as Driver
                </button>
              </p>
            )}
          </div>

          {/* Footer */}
          <div className="auth-footer">
            Don't have an account?{' '}
            <Link href="/register" className="link-primary">
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}

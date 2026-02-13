'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Toaster } from 'react-hot-toast';
import { ArrowLeft, Mail } from 'lucide-react';
import { showToast } from '@/lib/notify';
import '../login/login.css'; // Reuse login styles

// Logger utility
const logger = {
  debug: (msg: string, data?: any) => console.log(`[DEBUG] ${msg}`, data || ''),
  info: (msg: string, data?: any) => console.log(`[INFO] ${msg}`, data || ''),
  error: (msg: string, data?: any) => console.error(`[ERROR] ${msg}`, data || ''),
};

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    logger.info('Password reset requested', { email });

    if (!email) {
      const msg = 'Email is required';
      setError(msg);
      showToast.error(msg);
      logger.error(msg);
      return;
    }

    try {
      setIsLoading(true);
      logger.debug('Sending password reset email to', { email });
      
      // TODO: Implement actual password reset API call
      // const response = await axios.post(`${API_BASE_URL}/auth/forgot-password`, { email });
      
      // For now, simulate the request
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setIsSubmitted(true);
      showToast.success('Password reset link sent to your email!');
      logger.info('Password reset email sent successfully', { email });
      
      // Redirect after 3 seconds
      setTimeout(() => {
        router.push('/login');
      }, 3000);
    } catch (error: any) {
      const errorMsg = error?.response?.data?.detail || 'Failed to send reset email';
      setError(errorMsg);
      showToast.error(errorMsg);
      logger.error('Password reset failed', { email, error: errorMsg });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Toaster />
      <div className="auth-container">
        <div className="auth-card">
          {/* Header */}
          <div className="auth-header">
            <h1>Reset Password</h1>
            <p>Enter your email to receive a password reset link</p>
          </div>

          {!isSubmitted ? (
            <>
              {error && (
                <div className="alert alert-error">
                  <span>{error}</span>
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="email">Email Address</label>
                  <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                    <Mail size={16} style={{ position: 'absolute', left: '15px', color: '#999' }} />
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      required
                      autoFocus
                      disabled={isLoading}
                      style={{ paddingLeft: '40px' }}
                    />
                  </div>
                </div>

                {/* Submit Button */}
                <button type="submit" className="btn-submit" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Mail size={16} style={{ animation: 'spin 1s linear infinite' }} />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail size={16} />
                      Send Reset Link
                    </>
                  )}
                </button>
              </form>

              {/* Back to Login */}
              <div className="auth-footer">
                <Link href="/login" className="link-primary" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <ArrowLeft size={14} />
                  Back to Login
                </Link>
              </div>
            </>
          ) : (
            <>
              {/* Success Message */}
              <div className="alert alert-success" style={{ background: '#d4edda', border: '1px solid #c3e6cb', color: '#155724' }}>
                ✓ Email sent successfully!
              </div>

              <div style={{ textAlign: 'center', padding: '24px 0' }}>
                <Mail size={48} style={{ color: '#ff5722', opacity: 0.7, marginBottom: '16px' }} />
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#333', marginBottom: '8px' }}>
                  Check Your Email
                </h3>
                <p style={{ color: '#666', fontSize: '14px', marginBottom: '16px' }}>
                  We've sent a password reset link to <strong>{email}</strong>
                </p>
                <p style={{ color: '#999', fontSize: '13px', marginBottom: '24px' }}>
                  Click the link in the email to reset your password. If you don't see it, check your spam folder.
                </p>
                <p style={{ color: '#999', fontSize: '12px' }}>
                  Redirecting to login in a few seconds...
                </p>
              </div>

              {/* Manual Back Link */}
              <div className="auth-footer">
                <Link href="/login" className="link-primary">
                  Back to Login
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

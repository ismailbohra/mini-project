import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import authService from '../services/authService';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await authService.forgotPassword(email);
      setSubmitted(true);
      toast.success(response.message || 'Password reset link sent to your email!');
    } catch (err) {
      const apiMessage = err.response?.data?.error?.message || err.response?.data?.detail || err.response?.data?.message;
      const message = apiMessage || err.message || 'Failed to send reset link';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="card shadow-lg" style={{ maxWidth: '450px', width: '100%' }}>
        <div className="card-body p-5">
          <h2 className="text-center mb-4">
            <i className="bi bi-key me-2"></i>
            Forgot Password
          </h2>

          {!submitted ? (
            <>
              <p className="text-muted text-center mb-4">
                Enter your email address and we'll send you a link to reset your password.
              </p>

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="email" className="form-label">
                    Email Address
                  </label>
                  <input
                    type="email"
                    className="form-control"
                    id="email"
                    name="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100 mb-3"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Sending...
                    </>
                  ) : (
                    'Send Reset Link'
                  )}
                </button>
              </form>
            </>
          ) : (
            <div className="alert alert-success">
              <i className="bi bi-check-circle me-2"></i>
              If an account with that email exists, you will receive a password reset link shortly.
            </div>
          )}

          <div className="text-center">
            <p className="mb-0">
              Remember your password?{' '}
              <Link to="/login" className="text-decoration-none">
                Back to Login
              </Link>
            </p>
          </div>
        </div>
      </div>
      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
};

export default ForgotPassword;

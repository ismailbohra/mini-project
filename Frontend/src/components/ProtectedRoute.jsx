import React, { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { setUser } from '../store/slices/authSlice';
import authService from '../services/authService';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();

  useEffect(() => {
    // Fetch user if authenticated but user data not loaded
    if (isAuthenticated && !user) {
      authService.getCurrentUser()
        .then((userData) => {
          dispatch(setUser(userData));
        })
        .catch(() => {
          // Token invalid, will redirect to login via interceptor
        });
    }
  }, [isAuthenticated, user, dispatch]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check role if required
  if (requiredRole && user) {
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    if (!roles.includes(user.role)) {
      return <Navigate to="/" replace />;
    }
  }

  return children ? children : <Outlet />;
};

export default ProtectedRoute;

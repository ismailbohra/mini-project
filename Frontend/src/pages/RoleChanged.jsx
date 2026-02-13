import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { logout } from '../store/slices/authSlice';
import { clearNotifications } from '../store/slices/notificationSlice';

const RoleChanged = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch();

    useEffect(() => {
        // Clear all user data and tokens
        dispatch(logout());
        dispatch(clearNotifications());
        localStorage.clear();
        sessionStorage.clear();
    }, [dispatch]);

    const handleLogin = () => {
        navigate('/login');
    };

    return (
        <div className="container-fluid vh-100 d-flex align-items-center justify-content-center bg-light">
            <div className="card shadow-lg" style={{ maxWidth: '550px', width: '100%' }}>
                <div className="card-body p-5 text-center">
                    <div className="mb-4">
                        <i className="bi bi-arrow-repeat text-warning" style={{ fontSize: '4rem' }}></i>
                    </div>

                    <h2 className="mb-3">Your Role Has Changed</h2>

                    <p className="text-muted mb-4">
                        Your account role has been modified by an administrator. This means your access permissions have changed.
                    </p>

                    <div className="alert alert-warning d-flex align-items-start" role="alert">
                        <i className="bi bi-exclamation-triangle-fill me-2 mt-1"></i>
                        <div className="text-start">
                            <strong>Important:</strong> You need to log in again to continue using the application with your updated role and permissions.
                        </div>
                    </div>

                    <div className="mb-4">
                        <small className="text-muted">
                            <i className="bi bi-info-circle me-1"></i>
                            Your session has been cleared for security reasons.
                        </small>
                    </div>

                    <button
                        className="btn btn-warning w-100 btn-lg"
                        onClick={handleLogin}
                    >
                        <i className="bi bi-box-arrow-in-right me-2"></i>
                        Login Again
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RoleChanged;

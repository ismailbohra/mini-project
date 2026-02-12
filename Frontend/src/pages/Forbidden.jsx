import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { logout } from '../store/slices/authSlice';
const Forbidden = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch();
    useEffect(() => {
       dispatch(logout());
    }, [])

    const handleLogin = () => {
        navigate('/login');
    };

    return (
        <div className="container-fluid vh-100 d-flex align-items-center justify-content-center bg-light">
            <div className="card shadow-lg" style={{ maxWidth: '500px', width: '100%' }}>
                <div className="card-body p-5 text-center">
                    <div className="mb-4">
                        <i className="bi bi-shield-exclamation text-danger" style={{ fontSize: '4rem' }}></i>
                    </div>

                    <h2 className="mb-3">Access Forbidden</h2>

                    <p className="text-muted mb-4">
                        You don't have permission to access this resource. Your account role may have been changed by an administrator.
                    </p>

                    <div className="alert alert-info" role="alert">
                        <i className="bi bi-info-circle me-2"></i>
                        Please log in again to refresh your permissions.
                    </div>

                    <button
                        className="btn btn-primary w-100"
                        onClick={handleLogin}
                    >
                        <i className="bi bi-box-arrow-in-right me-2"></i>
                        Go to Login
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Forbidden;

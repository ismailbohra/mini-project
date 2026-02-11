import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// Layout
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import PostDetail from './pages/PostDetail';
import CreatePost from './pages/CreatePost';
import MyPosts from './pages/MyPosts';
import Profile from './pages/Profile';
import Users from './pages/Users';
import Review from './pages/Review';
import Notifications from './pages/Notifications';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Home />} />
              <Route path="/home" element={<Home />} />
              <Route path="/post/:postId" element={<PostDetail />} />
              <Route path="/create-post" element={<CreatePost />} />
              <Route path="/my-posts" element={<MyPosts />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/profile" element={<Profile />} />
              
              {/* Admin Only */}
              <Route 
                path="/users" 
                element={
                  <ProtectedRoute requiredRole="Admin">
                    <Users />
                  </ProtectedRoute>
                } 
              />
              
              {/* Moderator & Admin */}
              <Route 
                path="/review" 
                element={
                  <ProtectedRoute requiredRole={['Moderator', 'Admin']}>
                    <Review />
                  </ProtectedRoute>
                } 
              />
            </Route>
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </Provider>
  );
}

export default App;

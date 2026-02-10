import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <Header toggleSidebar={toggleSidebar} />
      <div className="d-flex flex-grow-1">
        <Sidebar isOpen={sidebarOpen} />
        <main className={`flex-grow-1 p-3 ${sidebarOpen ? '' : 'ms-0'}`} style={{ marginLeft: sidebarOpen ? '250px' : '0', transition: 'margin-left 0.3s' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;

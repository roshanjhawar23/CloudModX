import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import Navbar from '../components/Navbar';
import apiService from '../services/api';

export default function MainLayout({ children }) {
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const data = await apiService.getHealth();
        setSystemStatus(data);
      } catch (err) {
        setSystemStatus({ status: 'offline', details: err.message });
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans">
      <Navbar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header systemStatus={systemStatus} />
        <main className="p-8 flex-1 max-w-7xl w-full mx-auto">
          {typeof children === 'function' ? children({ systemStatus }) : children}
        </main>
      </div>
    </div>
  );
}

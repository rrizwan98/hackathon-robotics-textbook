import React, { useEffect } from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import ChatWidget from '../components/ChatWidget';

// Default Root component from Docusaurus with ChatKit integration
function Root({ children }: { children: React.ReactNode }) {
  // Load ChatKit script dynamically
  useEffect(() => {
    // Check if script is already loaded
    if (document.querySelector('script[src*="chatkit.js"]')) {
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://cdn.platform.openai.com/deployments/chatkit/chatkit.js';
    script.async = true;
    document.head.appendChild(script);

    return () => {
      // Cleanup on unmount (optional)
    };
  }, []);

  return (
    <AuthProvider>
      {children}
      <ChatWidget />
    </AuthProvider>
  );
}

export default Root;

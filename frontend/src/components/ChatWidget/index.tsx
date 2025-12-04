'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import type { ChatKitOptions } from '@openai/chatkit-react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './styles.module.css';

/**
 * Mapping of URL paths to exact section names (as defined in backend VALID_TEXTBOOK_SECTIONS)
 */
const URL_TO_SECTION_NAME: Record<string, string> = {
  'intro': 'Introduction to Physical AI & Humanoid Robotics',
  'ros2': 'Robot Operating System 2 (ROS2)',
};

/**
 * Get the current textbook section name from the page
 */
function getTextbookSectionName(): string {
  if (typeof document === 'undefined') return 'Front Page';
  
  const pathname = window.location.pathname;
  
  if (!pathname.startsWith('/docs/')) {
    return 'Front Page';
  }
  
  const match = pathname.match(/\/docs\/([^/]+)/);
  if (match) {
    const urlSlug = match[1].replace(/-ur$/, '');
    if (URL_TO_SECTION_NAME[urlSlug]) {
      return URL_TO_SECTION_NAME[urlSlug];
    }
  }
  
  const h1 = document.querySelector('article h1');
  if (h1?.textContent) {
    return h1.textContent.trim();
  }
  
  const title = document.title;
  if (title) {
    const parts = title.split('|');
    return parts[0].trim();
  }
  
  return 'Front Page';
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [textbookName, setTextbookName] = useState<string>('');
  const { isAuthenticated, user, token, logout } = useAuth();

  // Update textbook name when widget opens or URL changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const updateTextbookName = () => {
        const name = getTextbookSectionName();
        console.log('[ChatWidget] Extracted textbook name:', name);
        setTextbookName(name);
      };
      
      updateTextbookName();
      window.addEventListener('popstate', updateTextbookName);
      
      return () => {
        window.removeEventListener('popstate', updateTextbookName);
      };
    }
  }, []);

  useEffect(() => {
    if (isOpen && typeof window !== 'undefined') {
      setTextbookName(getTextbookSectionName());
    }
  }, [isOpen]);

  // Build API URL with textbook_name and user_email for thread filtering
  const apiUrl = useMemo(() => {
    const baseUrl = 'http://localhost:8000/chatkit';
    const params = new URLSearchParams();
    
    params.set('textbook_name', textbookName?.trim() || 'Front Page');
    
    // Pass user email for thread filtering (each user sees their own threads)
    if (isAuthenticated && user?.email) {
      params.set('user_email', user.email);
    }
    
    return `${baseUrl}?${params.toString()}`;
  }, [textbookName, isAuthenticated, user?.email]);

  // ChatKit Configuration
  const chatKitOptions: ChatKitOptions = useMemo(() => ({
    api: {
      url: apiUrl,
      domainKey: 'textbook-assistant',
    },
    theme: {
      colorScheme: 'light',
      radius: 'round',
      density: 'normal',
      color: {
        accent: {
          primary: '#181818',
          level: 1
        },
        surface: {
          background: '#ededed',
          foreground: '#cfcfcf'
        }
      },
      typography: {
        baseSize: 16,
        fontFamily: '"OpenAI Sans", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif',
        fontFamilyMono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace',
        fontSources: [
          {
            family: 'OpenAI Sans',
            src: 'https://cdn.openai.com/common/fonts/openai-sans/v2/OpenAISans-Regular.woff2',
            weight: 400,
            style: 'normal',
            display: 'swap'
          }
        ]
      }
    },
    composer: {
      placeholder: 'Talk with book',
      attachments: {
        enabled: false
      },
    },
    startScreen: {
      greeting: '',
      prompts: [],
    },
  }), [apiUrl]);

  const chatKit = useChatKit(chatKitOptions);

  const goToLogin = () => {
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={styles.chatButton}
          aria-label="Open AI Assistant"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
          <span className={styles.chatButtonLabel}>AI</span>
        </button>
      )}

      {/* Chat Widget Container */}
      {isOpen && (
        <div className={styles.widgetContainer}>
          {/* Main Chat Area */}
          <div className={styles.chatArea}>
            {/* Header */}
            <div className={styles.chatHeader}>
              {!isAuthenticated && (
                <button onClick={goToLogin} className={styles.loginPromptBtn}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  Login to save chats
                </button>
              )}

              {isAuthenticated && user && (
                <div className={styles.userSection}>
                  <span className={styles.userBadge}>
                    {user.name || user.email}
                  </span>
                  <button 
                    onClick={() => { logout(); setIsOpen(false); }}
                    className={styles.logoutBtn}
                    title="Logout"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </button>
                </div>
              )}

              <button
                onClick={() => setIsOpen(false)}
                className={styles.closeBtn}
                aria-label="Close chat"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* ChatKit Component - with native thread list enabled */}
            <div className={styles.chatKitWrapper}>
              <ChatKit
                control={chatKit.control}
                style={{ 
                  height: '100%', 
                  width: '100%', 
                  border: 'none', 
                  borderRadius: '0',
                  display: 'block',
                }}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import type { ChatKitOptions } from '@openai/chatkit-react';
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
 * This extracts the section name from the URL path first (most reliable),
 * then falls back to H1 heading
 * Returns "Front Page" if on homepage, or section name if on docs page
 */
function getTextbookSectionName(): string {
  if (typeof document === 'undefined') return 'Front Page';
  
  const pathname = window.location.pathname;
  
  // Check if we're on a docs page (not homepage)
  if (!pathname.startsWith('/docs/')) {
    return 'Front Page'; // Homepage or other non-docs pages
  }
  
  // Method 1: Get from URL path mapping (most reliable - matches backend exactly)
  const match = pathname.match(/\/docs\/([^/]+)/);
  if (match) {
    const urlSlug = match[1].replace(/-ur$/, ''); // Remove -ur suffix if present
    if (URL_TO_SECTION_NAME[urlSlug]) {
      return URL_TO_SECTION_NAME[urlSlug];
    }
  }
  
  // Method 2: Get from the article H1 heading (fallback)
  const h1 = document.querySelector('article h1');
  if (h1?.textContent) {
    return h1.textContent.trim();
  }
  
  // Method 3: Get from the page title (before the | separator)
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

  // Update textbook name when widget opens or URL changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const updateTextbookName = () => {
        const name = getTextbookSectionName();
        console.log('[ChatWidget] Extracted textbook name:', name);
        setTextbookName(name);
      };
      
      // Get initial name
      updateTextbookName();
      
      // Listen for URL changes (for SPA navigation)
      window.addEventListener('popstate', updateTextbookName);
      
      return () => {
        window.removeEventListener('popstate', updateTextbookName);
      };
    }
  }, []);

  // Also update when widget opens
  useEffect(() => {
    if (isOpen && typeof window !== 'undefined') {
      setTextbookName(getTextbookSectionName());
    }
  }, [isOpen]);

  // Build API URL with textbook_name as query parameter
  // Always pass textbook_name (either "Front Page" or section name)
  const apiUrl = useMemo(() => {
    const baseUrl = 'http://localhost:8000/chatkit';
    if (textbookName && textbookName.trim()) {
      return `${baseUrl}?textbook_name=${encodeURIComponent(textbookName)}`;
    }
    // Fallback to "Front Page" if somehow textbookName is empty
    return `${baseUrl}?textbook_name=${encodeURIComponent('Front Page')}`;
  }, [textbookName]);

  // ChatKit Configuration - textbook_name passed via URL query parameter
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

      {/* Pure OpenAI ChatKit Widget Container */}
      {isOpen && (
        <div 
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            zIndex: 9999,
            width: '400px',
            height: '600px',
            borderRadius: '16px',
            overflow: 'hidden',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            background: '#fff',
          }}
        >
          {/* Close Button */}
          <button
            onClick={() => setIsOpen(false)}
            style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              zIndex: 10001,
              backgroundColor: 'rgba(55, 65, 81, 0.9)',
              color: 'white',
              borderRadius: '50%',
              padding: '8px',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            aria-label="Close chat"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>

          {/* Pure OpenAI ChatKit Component - Using explicit pixel dimensions */}
          <ChatKit
            control={chatKit.control}
            style={{ 
              height: '600px', 
              width: '400px', 
              border: 'none', 
              borderRadius: '16px',
              display: 'block',
            }}
          />
        </div>
      )}
    </>
  );
}

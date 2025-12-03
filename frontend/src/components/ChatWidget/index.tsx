'use client';

import React, { useState, useEffect } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import type { ChatKitOptions } from '@openai/chatkit-react';
import styles from './styles.module.css';

/**
 * Get the current textbook section name from the page
 */
function getTextbookSectionName(): string {
  if (typeof document === 'undefined') return 'General';
  
  // Try to get the page title from various sources
  const h1 = document.querySelector('article h1');
  if (h1?.textContent) {
    return h1.textContent.trim();
  }
  
  const title = document.title;
  if (title) {
    const parts = title.split('|');
    return parts[0].trim();
  }
  
  const pathname = window.location.pathname;
  const match = pathname.match(/\/docs\/([^/]+)/);
  if (match) {
    return match[1].replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }
  
  return 'General';
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [textbookName, setTextbookName] = useState<string>('');

  // Update textbook name when widget opens
  useEffect(() => {
    if (isOpen && typeof window !== 'undefined') {
      setTextbookName(getTextbookSectionName());
    }
  }, [isOpen]);

  // ChatKit Configuration - using correct property names
  const chatKitOptions: ChatKitOptions = {
    api: {
      url: 'http://localhost:8000/chatkit',
      domainKey: 'textbook-assistant',
    },
    theme: {
      colorScheme: 'light',
      radius: 'round',
      density: 'normal',
      color: {
        grayscale: { hue: 123, tint: 0, shade: -2 },
        accent: { primary: '#2e8555', level: 1 }, // Docusaurus primary color
        surface: { background: '#f8f9fa', foreground: '#ffffff' }
      },
      typography: {
        baseSize: 16,
        fontFamily: '"OpenAI Sans", system-ui, sans-serif',
        fontFamilyMono: 'ui-monospace, monospace',
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
      placeholder: `Ask about ${textbookName || 'this textbook'}...`,
      attachments: { enabled: false },
    },
    startScreen: {
      greeting: `Hi! I'm your Textbook AI Assistant for ${textbookName || 'Physical AI & Humanoid Robotics'}`,
      prompts: [
        { label: 'Explain concepts', prompt: 'Explain the main concepts of this section' },
        { label: 'Summary', prompt: 'Give me a summary of this topic' },
        { label: 'Key takeaways', prompt: 'What are the key takeaways?' },
      ],
    },
  };

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

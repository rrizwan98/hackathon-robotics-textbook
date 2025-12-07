'use client';

import React, { useState, useEffect, useRef } from 'react';
import Layout from '@theme/Layout';
import { useAuth } from '../contexts/AuthContext';
import styles from './login.module.css';

export default function LoginPage(): React.ReactNode {
  const { login, register, isAuthenticated, user } = useAuth();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Use refs for uncontrolled inputs (works better with browser automation)
  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const nameRef = useRef<HTMLInputElement>(null);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && typeof window !== 'undefined') {
      window.location.href = '/';
    }
  }, [isAuthenticated]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    // Get values from DOM directly
    const email = emailRef.current?.value || '';
    const password = passwordRef.current?.value || '';
    const name = nameRef.current?.value || '';

    try {
      if (isLoginMode) {
        const result = await login(email, password);
        if (!result.success) {
          setError(result.message);
        }
        // Redirect happens via useEffect when isAuthenticated changes
      } else {
        const result = await register(email, password, name);
        if (result.success) {
          setSuccess(result.message);
          // Switch to login mode after successful registration
          setTimeout(() => {
            setIsLoginMode(true);
            setSuccess('');
          }, 2000);
        } else {
          setError(result.message);
        }
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setError('');
    setSuccess('');
    // Clear form inputs when switching modes
    if (emailRef.current) emailRef.current.value = '';
    if (passwordRef.current) passwordRef.current.value = '';
    if (nameRef.current) nameRef.current.value = '';
  };

  return (
    <Layout
      title={isLoginMode ? 'Login' : 'Register'}
      description="Login to access your chat sessions"
    >
      <main className={styles.container}>
        <div className={styles.formWrapper}>
          {/* Logo/Brand */}
          <div className={styles.brand}>
            <div className={styles.logoIcon}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48"
                height="48"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <h1 className={styles.title}>Robotics Textbook</h1>
            <p className={styles.subtitle}>AI-Powered Learning Assistant</p>
          </div>

          {/* Form Card */}
          <div className={styles.formCard}>
            <h2 className={styles.formTitle}>
              {isLoginMode ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className={styles.formSubtitle}>
              {isLoginMode
                ? 'Login to access your chat history'
                : 'Sign up to save your conversations'}
            </p>

            <form onSubmit={handleSubmit} className={styles.form}>
              {!isLoginMode && (
                <div className={styles.inputGroup}>
                  <label htmlFor="name" className={styles.label}>
                    Name
                  </label>
                  <input
                    id="name"
                    type="text"
                    ref={nameRef}
                    className={styles.input}
                    placeholder="Enter your name"
                    required={!isLoginMode}
                  />
                </div>
              )}

              <div className={styles.inputGroup}>
                <label htmlFor="email" className={styles.label}>
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  ref={emailRef}
                  className={styles.input}
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div className={styles.inputGroup}>
                <label htmlFor="password" className={styles.label}>
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  ref={passwordRef}
                  className={styles.input}
                  placeholder={isLoginMode ? 'Enter your password' : 'Create a password (min 8 chars)'}
                  required
                  minLength={8}
                />
              </div>

              {error && (
                <div className={styles.errorMessage}>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {error}
                </div>
              )}

              {success && (
                <div className={styles.successMessage}>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  {success}
                </div>
              )}

              <button
                type="submit"
                className={styles.submitButton}
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className={styles.spinner}></span>
                ) : isLoginMode ? (
                  'Sign In'
                ) : (
                  'Create Account'
                )}
              </button>
            </form>

            <div className={styles.divider}>
              <span>or</span>
            </div>

            <button onClick={toggleMode} className={styles.switchButton}>
              {isLoginMode
                ? "Don't have an account? Sign Up"
                : 'Already have an account? Sign In'}
            </button>
          </div>

          {/* Features */}
          <div className={styles.features}>
            <div className={styles.feature}>
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
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
              <span>Save chat history</span>
            </div>
            <div className={styles.feature}>
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
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              <span>Sync across devices</span>
            </div>
            <div className={styles.feature}>
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
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
              <span>Secure & private</span>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}

/**
 * Authentication Context for Project Minerva
 * 
 * Provides authentication state and methods throughout the application.
 * Supports email/password and Google OAuth authentication.
 * Implements role-based access control with 'investor' and 'founder' roles.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
  User,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged
} from 'firebase/auth';
import { auth, googleProvider } from '../config/firebase';
import axios from 'axios';

export type UserRole = 'investor' | 'founder';

interface AuthUser extends User {
  role?: UserRole;
}

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signUp: (email: string, password: string, role: UserRole, displayName?: string) => Promise<void>;
  signOut: () => Promise<void>;
  isInvestor: boolean;
  isFounder: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch user role from backend
  const fetchUserRole = async (firebaseUser: User): Promise<UserRole | undefined> => {
    try {
      const idToken = await firebaseUser.getIdToken();
      const response = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/firebase-auth/me`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      return response.data.role;
    } catch (err) {
      console.error('Failed to fetch user role:', err);
      return undefined;
    }
  };

  // Set up auth state listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // Fetch role from backend
        const role = await fetchUserRole(firebaseUser);
        const authUser: AuthUser = {
          ...firebaseUser,
          role
        };
        setUser(authUser);
      } else {
        setUser(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  // Sign in with email and password
  const signIn = async (email: string, password: string) => {
    try {
      setError(null);
      setLoading(true);
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const role = await fetchUserRole(userCredential.user);
      const authUser: AuthUser = {
        ...userCredential.user,
        role
      };
      setUser(authUser);
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Sign in with Google
  const signInWithGoogle = async () => {
    try {
      setError(null);
      setLoading(true);
      const userCredential = await signInWithPopup(auth, googleProvider);
      
      // Check if user has a role, if not, they need to complete registration
      const role = await fetchUserRole(userCredential.user);
      
      if (!role) {
        // New Google user - needs role assignment
        // Sign out and throw a specific error that can be caught for redirect
        await firebaseSignOut(auth);
        const error = new Error('UNREGISTERED_USER');
        error.name = 'UnregisteredUserError';
        throw error;
      }
      
      const authUser: AuthUser = {
        ...userCredential.user,
        role
      };
      setUser(authUser);
    } catch (err: any) {
      setError(err.message);
      // Sign out if role not set (for other errors)
      if (err.name !== 'UnregisteredUserError') {
        await firebaseSignOut(auth);
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Sign up with email and password
  const signUp = async (email: string, password: string, role: UserRole, displayName?: string) => {
    try {
      setError(null);
      setLoading(true);
      
      // Register user via backend API
      const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/api/firebase-auth/register`, {
        email,
        password,
        role,
        display_name: displayName
      });

      if (response.data.success) {
        // Sign in the newly created user
        await signIn(email, password);
      } else {
        throw new Error('Failed to create user');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Sign out
  const signOut = async () => {
    try {
      setError(null);
      await firebaseSignOut(auth);
      setUser(null);
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    error,
    signIn,
    signInWithGoogle,
    signUp,
    signOut,
    isInvestor: user?.role === 'investor',
    isFounder: user?.role === 'founder'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

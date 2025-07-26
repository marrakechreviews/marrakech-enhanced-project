import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../lib/api';
import { getToken, setToken, removeToken, getUser, setUser } from '../lib/auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUserState] = useState(getUser());
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(!!getToken());

  useEffect(() => {
    const initAuth = async () => {
      const token = getToken();
      if (token) {
        try {
          const response = await authAPI.getProfile();
          if (response.success) {
            setUserState(response.data.user);
            setUser(response.data.user);
            setIsAuthenticated(true);
          } else {
            removeToken();
            setIsAuthenticated(false);
          }
        } catch (error) {
          console.error('Auth initialization error:', error);
          removeToken();
          setIsAuthenticated(false);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      if (response.success) {
        const { user: userData, token } = response.data;
        setToken(token);
        setUser(userData);
        setUserState(userData);
        setIsAuthenticated(true);
        return { success: true };
      }
      return { success: false, message: response.message };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      if (response.success) {
        const { user: newUser, token } = response.data;
        setToken(token);
        setUser(newUser);
        setUserState(newUser);
        setIsAuthenticated(true);
        return { success: true };
      }
      return { success: false, message: response.message };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const logout = () => {
    removeToken();
    setUserState(null);
    setIsAuthenticated(false);
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await authAPI.updateProfile(profileData);
      if (response.success) {
        const updatedUser = response.data.user;
        setUser(updatedUser);
        setUserState(updatedUser);
        return { success: true };
      }
      return { success: false, message: response.message };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const hasRole = (requiredRoles) => {
    if (!user) return false;
    
    if (Array.isArray(requiredRoles)) {
      return requiredRoles.includes(user.role);
    }
    
    return user.role === requiredRoles;
  };

  const isAdmin = () => hasRole('admin');
  const isModerator = () => hasRole(['admin', 'moderator']);

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateProfile,
    hasRole,
    isAdmin,
    isModerator,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};


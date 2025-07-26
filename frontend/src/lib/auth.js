// Authentication utilities
export const getToken = () => {
  return localStorage.getItem('token');
};

export const setToken = (token) => {
  localStorage.setItem('token', token);
};

export const removeToken = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user));
};

export const isAuthenticated = () => {
  return !!getToken();
};

export const hasRole = (requiredRoles) => {
  const user = getUser();
  if (!user) return false;
  
  if (Array.isArray(requiredRoles)) {
    return requiredRoles.includes(user.role);
  }
  
  return user.role === requiredRoles;
};

export const isAdmin = () => {
  return hasRole('admin');
};

export const isModerator = () => {
  return hasRole(['admin', 'moderator']);
};

export const logout = () => {
  removeToken();
  window.location.href = '/';
};


import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Home, Shield } from 'lucide-react';

const UnauthorizedPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="mb-8">
          <div className="mx-auto w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <Shield className="h-12 w-12 text-red-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Access Denied
          </h1>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            You don't have permission to access this page. 
            Please contact an administrator if you believe this is an error.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild>
            <Link to="/">
              <Home className="mr-2 h-4 w-4" />
              Go Home
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/login">
              Sign In
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default UnauthorizedPage;


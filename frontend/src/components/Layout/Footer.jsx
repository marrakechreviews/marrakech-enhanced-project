import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { 
  Facebook, 
  Twitter, 
  Instagram, 
  Mail, 
  MapPin, 
  Phone,
  Heart
} from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    explore: [
      { name: 'Popular Reviews', href: '/reviews?featured=true' },
      { name: 'Latest Articles', href: '/articles' },
      { name: 'Top Restaurants', href: '/reviews?placeType=Restaurant' },
      { name: 'Best Hotels', href: '/reviews?placeType=Hotel/Riad' },
      { name: 'Hidden Gems', href: '/reviews?placeType=Hidden Gem' },
    ],
    categories: [
      { name: 'Restaurants', href: '/reviews?placeType=Restaurant' },
      { name: 'Hotels & Riads', href: '/reviews?placeType=Hotel/Riad' },
      { name: 'Attractions', href: '/reviews?placeType=Attraction' },
      { name: 'Shopping', href: '/reviews?placeType=Shopping' },
      { name: 'Activities', href: '/reviews?placeType=Activity/Tour' },
    ],
    company: [
      { name: 'About Us', href: '/about' },
      { name: 'Contact', href: '/contact' },
      { name: 'Privacy Policy', href: '/privacy' },
      { name: 'Terms of Service', href: '/terms' },
      { name: 'FAQ', href: '/faq' },
    ],
  };

  return (
    <footer className="bg-muted/30 border-t">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <Link to="/" className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">MR</span>
              </div>
              <span className="font-bold text-lg text-primary">Marrakech Reviews</span>
            </Link>
            <p className="text-sm text-muted-foreground">
              Your trusted guide to discovering the best experiences in Morocco's enchanting Red City. 
              From authentic riads to hidden souks, we help you explore Marrakech like a local.
            </p>
            <div className="flex space-x-4">
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0" asChild>
                <a href="https://www.facebook.com/share/1Hz616hPW7/?mibextid=wwXIfr" target="_blank" rel="noopener noreferrer">
                  <Facebook className="h-4 w-4" />
                </a>
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0" asChild>
                <a href="#" target="_blank" rel="noopener noreferrer">
                  <Twitter className="h-4 w-4" />
                </a>
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0" asChild>
                <a href="https://www.instagram.com/marrakechreviews?igsh=MjcyenFwcThrN21u&utm_source=qr" target="_blank" rel="noopener noreferrer">
                  <Instagram className="h-4 w-4" />
                </a>
              </Button>
            </div>

          </div>

          {/* Explore Links */}
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground">Explore</h3>
            <ul className="space-y-2">
              {footerLinks.explore.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Categories Links */}
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground">Categories</h3>
            <ul className="space-y-2">
              {footerLinks.categories.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-sm text-muted-foreground hover:text-primary transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Newsletter & Contact */}
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground">Stay Updated</h3>
            <p className="text-sm text-muted-foreground">
              Get the latest reviews and travel tips delivered to your inbox.
            </p>
            <div className="flex space-x-2">
              <Input
                type="email"
                placeholder="Enter your email"
                className="flex-1"
              />
              <Button size="sm">
                <Mail className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="space-y-2 pt-4">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>Marrakech, Morocco</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Mail className="h-4 w-4" />
                <span>Contact@marrakech.reviews</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Phone className="h-4 w-4" />
                <span>+212 708 040 530</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-4">
              <p className="text-sm text-muted-foreground">
                © {currentYear} Marrakech Reviews. All rights reserved.
              </p>
              <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                <span>Made with</span>
                <Heart className="h-4 w-4 text-red-500 fill-current" />
                <span>for travelers</span>
              </div>
            </div>
            
            <div className="flex space-x-6">
              {footerLinks.company.slice(2).map((link) => (
                <Link
                  key={link.name}
                  to={link.href}
                  className="text-sm text-muted-foreground hover:text-primary transition-colors"
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;


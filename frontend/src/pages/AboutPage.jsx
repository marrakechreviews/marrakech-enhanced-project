import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  MapPin, 
  Users, 
  Star, 
  Award, 
  Heart, 
  Globe,
  Camera,
  Coffee,
  Utensils,
  Building,
  Compass,
  Clock
} from 'lucide-react';

const AboutPage = () => {
  const stats = [
    { icon: MapPin, label: 'Locations Covered', value: '500+' },
    { icon: Users, label: 'Happy Travelers', value: '10,000+' },
    { icon: Star, label: 'Average Rating', value: '4.8/5' },
    { icon: Award, label: 'Years Experience', value: '8+' }
  ];

  const features = [
    {
      icon: Heart,
      title: 'Authentic Experiences',
      description: 'We showcase the real Marrakech, from hidden gems to local favorites that tourists rarely discover.'
    },
    {
      icon: Globe,
      title: 'Local Expertise',
      description: 'Our team of local experts and long-time residents share insider knowledge and genuine recommendations.'
    },
    {
      icon: Camera,
      title: 'Visual Stories',
      description: 'Every review comes with stunning photography that captures the essence and atmosphere of each location.'
    },
    {
      icon: Clock,
      title: 'Always Updated',
      description: 'We continuously update our reviews and recommendations to ensure accuracy and relevance.'
    }
  ];

  const team = [
    {
      name: 'Youssef Benali',
      role: 'Founder & Local Guide',
      image: '/api/placeholder/150/150',
      description: 'Born and raised in Marrakech, Youssef has been sharing the magic of his city with travelers for over a decade.'
    },
    {
      name: 'Aicha Mansouri',
      role: 'Food & Culture Expert',
      image: '/api/placeholder/150/150',
      description: 'A culinary enthusiast who knows every hidden restaurant and traditional recipe in the medina.'
    },
    {
      name: 'Omar Ziani',
      role: 'Adventure Specialist',
      image: '/api/placeholder/150/150',
      description: 'Your go-to expert for outdoor adventures, from Atlas Mountains treks to desert excursions.'
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-orange-500 to-red-600 text-white py-20">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">About Marrakech Reviews</h1>
            <p className="text-xl mb-8 opacity-90">
              Your trusted companion for discovering the authentic soul of Marrakech. 
              We're passionate locals sharing genuine experiences and hidden treasures.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Badge variant="secondary" className="text-lg px-4 py-2">
                <Coffee className="mr-2 h-4 w-4" />
                Local Cafés
              </Badge>
              <Badge variant="secondary" className="text-lg px-4 py-2">
                <Utensils className="mr-2 h-4 w-4" />
                Traditional Cuisine
              </Badge>
              <Badge variant="secondary" className="text-lg px-4 py-2">
                <Building className="mr-2 h-4 w-4" />
                Historic Riads
              </Badge>
              <Badge variant="secondary" className="text-lg px-4 py-2">
                <Compass className="mr-2 h-4 w-4" />
                Hidden Gems
              </Badge>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-orange-100 text-orange-600 rounded-full mb-4">
                  <stat.icon className="h-8 w-8" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Our Story Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-6">Our Story</h2>
              <p className="text-xl text-gray-600">
                Born from a love for Marrakech and a desire to share its authentic beauty with the world
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h3 className="text-2xl font-bold mb-4">Why We Started</h3>
                <p className="text-gray-600 mb-6">
                  After years of seeing tourists miss the real magic of Marrakech – the tiny family-run restaurants, 
                  the artisan workshops tucked away in narrow alleys, the peaceful gardens known only to locals – 
                  we decided to create a platform that bridges this gap.
                </p>
                <p className="text-gray-600 mb-6">
                  Marrakech Reviews was born from countless conversations with travelers who wished they had known 
                  about the authentic experiences that make this city truly special. We're not just another review site; 
                  we're your local friends sharing the places we genuinely love.
                </p>
                <Button className="bg-orange-600 hover:bg-orange-700">
                  Start Exploring
                </Button>
              </div>
              <div className="relative">
                <img 
                  src="/api/placeholder/500/400" 
                  alt="Marrakech medina" 
                  className="rounded-lg shadow-lg"
                />
                <div className="absolute -bottom-6 -right-6 bg-white p-4 rounded-lg shadow-lg">
                  <div className="flex items-center space-x-2">
                    <Star className="h-5 w-5 text-yellow-400 fill-current" />
                    <span className="font-semibold">4.8/5</span>
                    <span className="text-gray-500">from 10k+ reviews</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-6">What Makes Us Different</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We're not just reviewers – we're storytellers, culture enthusiasts, and your local connection to Marrakech
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-orange-100 text-orange-600 rounded-full mx-auto mb-4">
                    <feature.icon className="h-8 w-8" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-6">Meet Our Team</h2>
            <p className="text-xl text-gray-600">
              The passionate locals behind every authentic recommendation
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {team.map((member, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-32 h-32 mx-auto mb-4 rounded-full overflow-hidden bg-gray-200">
                    <img 
                      src={member.image} 
                      alt={member.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <CardTitle className="text-xl">{member.name}</CardTitle>
                  <CardDescription className="text-orange-600 font-medium">
                    {member.role}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{member.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-16 bg-orange-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">Our Mission</h2>
            <p className="text-xl text-gray-700 mb-8">
              To connect travelers with the authentic heart of Marrakech, supporting local businesses 
              and creating meaningful cultural exchanges that benefit both visitors and our community.
            </p>
            <div className="grid md:grid-cols-3 gap-8 mt-12">
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-600 text-white rounded-full flex items-center justify-center mx-auto mb-4">
                  <Heart className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-bold mb-2">Authentic</h3>
                <p className="text-gray-600">Every recommendation comes from genuine local experience</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-600 text-white rounded-full flex items-center justify-center mx-auto mb-4">
                  <Users className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-bold mb-2">Community</h3>
                <p className="text-gray-600">Supporting local businesses and cultural preservation</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-orange-600 text-white rounded-full flex items-center justify-center mx-auto mb-4">
                  <Globe className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-bold mb-2">Connection</h3>
                <p className="text-gray-600">Building bridges between cultures through travel</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-orange-600 to-red-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Discover Authentic Marrakech?</h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of travelers who've discovered the real magic of our city
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="text-orange-600">
              Browse Reviews
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-orange-600">
              Share Your Experience
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;


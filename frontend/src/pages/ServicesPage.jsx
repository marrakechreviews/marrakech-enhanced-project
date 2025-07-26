import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  MapPin, 
  Camera, 
  Users, 
  Star, 
  Clock, 
  Shield,
  Compass,
  Coffee,
  Utensils,
  Building,
  Car,
  Mountain,
  Palette,
  BookOpen,
  Heart,
  CheckCircle,
  ArrowRight
} from 'lucide-react';

const ServicesPage = () => {
  const services = [
    {
      icon: MapPin,
      title: 'Personalized City Tours',
      description: 'Custom-designed tours based on your interests, from historic medina walks to modern Marrakech exploration.',
      features: ['Private local guide', 'Flexible itinerary', 'Hidden gems included', 'Photo opportunities'],
      price: 'From $50/person',
      duration: '3-8 hours',
      popular: true
    },
    {
      icon: Utensils,
      title: 'Culinary Experiences',
      description: 'Authentic food tours and cooking classes with local families and renowned chefs.',
      features: ['Traditional cooking class', 'Market visit', 'Family recipes', 'Certificate included'],
      price: 'From $75/person',
      duration: '4-6 hours',
      popular: false
    },
    {
      icon: Building,
      title: 'Riad & Hotel Booking',
      description: 'Curated selection of authentic riads and boutique hotels with verified reviews.',
      features: ['Verified properties', 'Best price guarantee', '24/7 support', 'Local recommendations'],
      price: 'No booking fees',
      duration: 'Instant booking',
      popular: false
    },
    {
      icon: Mountain,
      title: 'Atlas Mountains Adventures',
      description: 'Day trips and multi-day treks to the stunning Atlas Mountains and Berber villages.',
      features: ['Professional guides', 'All equipment provided', 'Traditional lunch', 'Cultural immersion'],
      price: 'From $120/person',
      duration: '1-3 days',
      popular: true
    },
    {
      icon: Car,
      title: 'Desert Excursions',
      description: 'Unforgettable desert experiences from day trips to luxury camping under the stars.',
      features: ['Camel trekking', 'Desert camping', 'Traditional dinner', 'Sunrise/sunset views'],
      price: 'From $200/person',
      duration: '1-3 days',
      popular: true
    },
    {
      icon: Palette,
      title: 'Artisan Workshops',
      description: 'Learn traditional crafts from master artisans in pottery, weaving, and metalwork.',
      features: ['Master artisan instruction', 'Take home your creation', 'Workshop visit', 'Cultural insights'],
      price: 'From $60/person',
      duration: '2-4 hours',
      popular: false
    }
  ];

  const additionalServices = [
    {
      icon: Camera,
      title: 'Photography Services',
      description: 'Professional photography sessions to capture your Marrakech memories.'
    },
    {
      icon: BookOpen,
      title: 'Cultural Consultations',
      description: 'Pre-trip planning and cultural guidance for a respectful visit.'
    },
    {
      icon: Shield,
      title: 'Travel Insurance',
      description: 'Comprehensive travel insurance options for peace of mind.'
    },
    {
      icon: Heart,
      title: 'Special Occasions',
      description: 'Romantic dinners, proposals, and celebration planning.'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      location: 'New York, USA',
      rating: 5,
      text: 'The personalized city tour was incredible! Our guide Youssef showed us places we never would have found on our own.',
      service: 'City Tour'
    },
    {
      name: 'Marco Rossi',
      location: 'Milan, Italy',
      rating: 5,
      text: 'The cooking class was the highlight of our trip. Learning from a local family was such an authentic experience.',
      service: 'Culinary Experience'
    },
    {
      name: 'Emma Thompson',
      location: 'London, UK',
      rating: 5,
      text: 'The Atlas Mountains trek was breathtaking. Professional guides and stunning scenery made it unforgettable.',
      service: 'Atlas Mountains'
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-orange-500 to-red-600 text-white py-20">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">Our Services</h1>
            <p className="text-xl mb-8 opacity-90">
              Authentic experiences crafted by locals who know Marrakech inside and out. 
              From guided tours to desert adventures, we make your journey unforgettable.
            </p>
            <Button size="lg" variant="secondary" className="text-orange-600">
              Book Your Experience
            </Button>
          </div>
        </div>
      </section>

      {/* Main Services Grid */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-6">Featured Experiences</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Carefully curated experiences that showcase the authentic beauty and culture of Marrakech
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-8">
            {services.map((service, index) => (
              <Card key={index} className={`relative hover:shadow-xl transition-all duration-300 ${service.popular ? 'ring-2 ring-orange-500' : ''}`}>
                {service.popular && (
                  <Badge className="absolute -top-3 left-6 bg-orange-500 hover:bg-orange-600">
                    Most Popular
                  </Badge>
                )}
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="p-3 bg-orange-100 text-orange-600 rounded-lg">
                        <service.icon className="h-6 w-6" />
                      </div>
                      <div>
                        <CardTitle className="text-xl">{service.title}</CardTitle>
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {service.duration}
                          </span>
                          <span className="font-semibold text-orange-600">{service.price}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <CardDescription className="text-base mt-4">
                    {service.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">What's Included:</h4>
                      <ul className="space-y-1">
                        {service.features.map((feature, idx) => (
                          <li key={idx} className="flex items-center text-sm text-gray-600">
                            <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="flex space-x-3 pt-4">
                      <Button className="flex-1 bg-orange-600 hover:bg-orange-700">
                        Book Now
                      </Button>
                      <Button variant="outline" className="flex-1">
                        Learn More
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Additional Services */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-6">Additional Services</h2>
            <p className="text-xl text-gray-600">
              Complete your Marrakech experience with our complementary services
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {additionalServices.map((service, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-orange-100 text-orange-600 rounded-full mx-auto mb-4">
                    <service.icon className="h-8 w-8" />
                  </div>
                  <CardTitle className="text-lg">{service.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 text-sm">{service.description}</p>
                  <Button variant="link" className="mt-3 p-0 text-orange-600">
                    Learn More <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-6">What Our Guests Say</h2>
            <p className="text-xl text-gray-600">
              Real experiences from travelers who've explored Marrakech with us
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <CardTitle className="text-lg">{testimonial.name}</CardTitle>
                      <CardDescription>{testimonial.location}</CardDescription>
                    </div>
                    <div className="flex">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="h-4 w-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                  </div>
                  <Badge variant="secondary" className="w-fit">
                    {testimonial.service}
                  </Badge>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 italic">"{testimonial.text}"</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="py-16 bg-orange-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-6">Why Choose Our Services</h2>
              <p className="text-xl text-gray-600">
                We're not just tour operators – we're your local friends in Marrakech
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center flex-shrink-0">
                    <Users className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Local Expertise</h3>
                    <p className="text-gray-600">Born and raised in Marrakech, our guides know every hidden corner and authentic experience.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center flex-shrink-0">
                    <Shield className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Safety First</h3>
                    <p className="text-gray-600">All our experiences are carefully planned with safety as our top priority.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center flex-shrink-0">
                    <Heart className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Authentic Connections</h3>
                    <p className="text-gray-600">We create meaningful connections between travelers and local communities.</p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center flex-shrink-0">
                    <Star className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Highly Rated</h3>
                    <p className="text-gray-600">Consistently rated 4.8/5 stars by thousands of satisfied travelers.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center flex-shrink-0">
                    <Clock className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Flexible Scheduling</h3>
                    <p className="text-gray-600">We adapt to your schedule and preferences for a personalized experience.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-orange-600 text-white rounded-full flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Best Price Guarantee</h3>
                    <p className="text-gray-600">We offer competitive prices with no hidden fees and best value guarantee.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-orange-600 to-red-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready for Your Marrakech Adventure?</h2>
          <p className="text-xl mb-8 opacity-90">
            Book your authentic Marrakech experience today and create memories that will last a lifetime
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="text-orange-600">
              Book Now
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-orange-600">
              Contact Us
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ServicesPage;


import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import { 
  Search, 
  Filter, 
  Grid3X3, 
  List,
  MapPin,
  Calendar,
  Camera,
  Heart,
  Share2,
  Download,
  Eye,
  ChevronLeft,
  ChevronRight,
  X
} from 'lucide-react';

const GalleryPage = () => {
  const [viewMode, setViewMode] = useState('grid');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Sample gallery data - in real app, this would come from API
  const galleryImages = [
    {
      id: 1,
      src: '/api/placeholder/400/300',
      title: 'Jemaa el-Fnaa at Sunset',
      category: 'attractions',
      location: 'Medina',
      photographer: 'Youssef Benali',
      date: '2024-01-15',
      description: 'The famous square comes alive as the sun sets, with storytellers, musicians, and food vendors creating a magical atmosphere.',
      tags: ['sunset', 'square', 'culture', 'evening'],
      likes: 245
    },
    {
      id: 2,
      src: '/api/placeholder/400/300',
      title: 'Traditional Tagine Preparation',
      category: 'food',
      location: 'Local Restaurant',
      photographer: 'Aicha Mansouri',
      date: '2024-01-20',
      description: 'Master chef preparing authentic Moroccan tagine with traditional spices and techniques passed down through generations.',
      tags: ['tagine', 'cooking', 'traditional', 'spices'],
      likes: 189
    },
    {
      id: 3,
      src: '/api/placeholder/400/300',
      title: 'Riad Courtyard Garden',
      category: 'architecture',
      location: 'Historic Medina',
      photographer: 'Omar Ziani',
      date: '2024-01-25',
      description: 'Beautiful traditional riad courtyard with intricate tilework, fountain, and lush garden creating a peaceful oasis.',
      tags: ['riad', 'courtyard', 'architecture', 'peaceful'],
      likes: 312
    },
    {
      id: 4,
      src: '/api/placeholder/400/300',
      title: 'Atlas Mountains Vista',
      category: 'nature',
      location: 'Atlas Mountains',
      photographer: 'Omar Ziani',
      date: '2024-02-01',
      description: 'Breathtaking panoramic view of the snow-capped Atlas Mountains from a traditional Berber village.',
      tags: ['mountains', 'landscape', 'berber', 'panorama'],
      likes: 428
    },
    {
      id: 5,
      src: '/api/placeholder/400/300',
      title: 'Souk Artisan at Work',
      category: 'culture',
      location: 'Souk des Artisans',
      photographer: 'Youssef Benali',
      date: '2024-02-05',
      description: 'Skilled artisan crafting traditional leather goods using techniques unchanged for centuries.',
      tags: ['artisan', 'leather', 'crafts', 'traditional'],
      likes: 156
    },
    {
      id: 6,
      src: '/api/placeholder/400/300',
      title: 'Majorelle Garden Blues',
      category: 'attractions',
      location: 'Majorelle Garden',
      photographer: 'Aicha Mansouri',
      date: '2024-02-10',
      description: 'The iconic cobalt blue walls and exotic plants of the famous Majorelle Garden create a stunning contrast.',
      tags: ['majorelle', 'garden', 'blue', 'exotic'],
      likes: 367
    },
    {
      id: 7,
      src: '/api/placeholder/400/300',
      title: 'Desert Sunset Camel Trek',
      category: 'nature',
      location: 'Sahara Desert',
      photographer: 'Omar Ziani',
      date: '2024-02-15',
      description: 'Silhouettes of camels and riders against the golden dunes as the sun sets over the Sahara Desert.',
      tags: ['desert', 'camels', 'sunset', 'sahara'],
      likes: 523
    },
    {
      id: 8,
      src: '/api/placeholder/400/300',
      title: 'Mint Tea Ceremony',
      category: 'culture',
      location: 'Traditional Café',
      photographer: 'Aicha Mansouri',
      date: '2024-02-20',
      description: 'The art of Moroccan mint tea preparation, poured from height to create the perfect foam.',
      tags: ['tea', 'ceremony', 'traditional', 'hospitality'],
      likes: 234
    }
  ];

  const categories = [
    { value: 'all', label: 'All Photos' },
    { value: 'attractions', label: 'Attractions' },
    { value: 'food', label: 'Food & Cuisine' },
    { value: 'culture', label: 'Culture' },
    { value: 'architecture', label: 'Architecture' },
    { value: 'nature', label: 'Nature' }
  ];

  const filteredImages = galleryImages.filter(image => {
    const matchesCategory = selectedCategory === 'all' || image.category === selectedCategory;
    const matchesSearch = image.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         image.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const openImageModal = (image, index) => {
    setSelectedImage(image);
    setCurrentImageIndex(index);
  };

  const navigateImage = (direction) => {
    const newIndex = direction === 'next' 
      ? (currentImageIndex + 1) % filteredImages.length
      : (currentImageIndex - 1 + filteredImages.length) % filteredImages.length;
    
    setCurrentImageIndex(newIndex);
    setSelectedImage(filteredImages[newIndex]);
  };

  const ImageCard = ({ image, index }) => (
    <Card className="group cursor-pointer overflow-hidden hover:shadow-xl transition-all duration-300">
      <div className="relative">
        <img 
          src={image.src} 
          alt={image.title}
          className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
          onClick={() => openImageModal(image, index)}
        />
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300" />
        <div className="absolute top-4 left-4">
          <Badge variant="secondary" className="bg-white/90 text-gray-800">
            {categories.find(cat => cat.value === image.category)?.label}
          </Badge>
        </div>
        <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="flex space-x-2">
            <Button size="sm" variant="secondary" className="bg-white/90 hover:bg-white">
              <Heart className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="secondary" className="bg-white/90 hover:bg-white">
              <Share2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div className="absolute bottom-4 left-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="bg-white/90 backdrop-blur-sm rounded-lg p-3">
            <h3 className="font-semibold text-gray-900 mb-1">{image.title}</h3>
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span className="flex items-center">
                <MapPin className="h-3 w-3 mr-1" />
                {image.location}
              </span>
              <span className="flex items-center">
                <Heart className="h-3 w-3 mr-1" />
                {image.likes}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );

  const ImageListItem = ({ image, index }) => (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => openImageModal(image, index)}>
      <CardContent className="p-4">
        <div className="flex space-x-4">
          <img 
            src={image.src} 
            alt={image.title}
            className="w-24 h-24 object-cover rounded-lg flex-shrink-0"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-semibold text-lg truncate">{image.title}</h3>
              <Badge variant="secondary">
                {categories.find(cat => cat.value === image.category)?.label}
              </Badge>
            </div>
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">{image.description}</p>
            <div className="flex items-center justify-between text-sm text-gray-500">
              <div className="flex items-center space-x-4">
                <span className="flex items-center">
                  <MapPin className="h-3 w-3 mr-1" />
                  {image.location}
                </span>
                <span className="flex items-center">
                  <Camera className="h-3 w-3 mr-1" />
                  {image.photographer}
                </span>
                <span className="flex items-center">
                  <Calendar className="h-3 w-3 mr-1" />
                  {new Date(image.date).toLocaleDateString()}
                </span>
              </div>
              <span className="flex items-center">
                <Heart className="h-3 w-3 mr-1" />
                {image.likes}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-orange-500 to-red-600 text-white py-20">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">Photo Gallery</h1>
            <p className="text-xl mb-8 opacity-90">
              Discover the beauty of Marrakech through the lens of our local photographers. 
              From bustling souks to serene gardens, every image tells a story.
            </p>
            <div className="flex items-center justify-center space-x-4 text-lg">
              <span className="flex items-center">
                <Camera className="mr-2 h-5 w-5" />
                {galleryImages.length} Photos
              </span>
              <span className="flex items-center">
                <Eye className="mr-2 h-5 w-5" />
                50k+ Views
              </span>
              <span className="flex items-center">
                <Heart className="mr-2 h-5 w-5" />
                2.5k Likes
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Filters and Controls */}
      <section className="py-8 bg-gray-50 border-b">
        <div className="container mx-auto px-4">
          <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
            <div className="flex flex-wrap gap-4 items-center">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(category => (
                    <SelectItem key={category.value} value={category.value}>
                      {category.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search photos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {filteredImages.length} photos
              </span>
              <div className="flex border rounded-lg">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid3X3 className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Gallery Grid/List */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          {filteredImages.length === 0 ? (
            <div className="text-center py-12">
              <Camera className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No photos found</h3>
              <p className="text-gray-600">Try adjusting your search or filter criteria</p>
            </div>
          ) : (
            <div className={viewMode === 'grid' 
              ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6" 
              : "space-y-4"
            }>
              {filteredImages.map((image, index) => (
                viewMode === 'grid' 
                  ? <ImageCard key={image.id} image={image} index={index} />
                  : <ImageListItem key={image.id} image={image} index={index} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Image Modal */}
      <Dialog open={!!selectedImage} onOpenChange={() => setSelectedImage(null)}>
        <DialogContent className="max-w-6xl max-h-[90vh] p-0 overflow-hidden">
          {selectedImage && (
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                className="absolute top-4 right-4 z-10 bg-black/50 text-white hover:bg-black/70"
                onClick={() => setSelectedImage(null)}
              >
                <X className="h-4 w-4" />
              </Button>
              
              <div className="flex">
                <div className="flex-1 relative">
                  <img 
                    src={selectedImage.src} 
                    alt={selectedImage.title}
                    className="w-full h-[70vh] object-cover"
                  />
                  
                  {/* Navigation Arrows */}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black/50 text-white hover:bg-black/70"
                    onClick={() => navigateImage('prev')}
                  >
                    <ChevronLeft className="h-6 w-6" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black/50 text-white hover:bg-black/70"
                    onClick={() => navigateImage('next')}
                  >
                    <ChevronRight className="h-6 w-6" />
                  </Button>
                </div>
                
                <div className="w-80 p-6 bg-white">
                  <div className="space-y-4">
                    <div>
                      <h2 className="text-2xl font-bold mb-2">{selectedImage.title}</h2>
                      <Badge variant="secondary">
                        {categories.find(cat => cat.value === selectedImage.category)?.label}
                      </Badge>
                    </div>
                    
                    <p className="text-gray-600">{selectedImage.description}</p>
                    
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{selectedImage.location}</span>
                      </div>
                      <div className="flex items-center">
                        <Camera className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{selectedImage.photographer}</span>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{new Date(selectedImage.date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center">
                        <Heart className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{selectedImage.likes} likes</span>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-2">
                      {selectedImage.tags.map(tag => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          #{tag}
                        </Badge>
                      ))}
                    </div>
                    
                    <div className="flex space-x-2 pt-4">
                      <Button className="flex-1" size="sm">
                        <Heart className="h-4 w-4 mr-2" />
                        Like
                      </Button>
                      <Button variant="outline" size="sm">
                        <Share2 className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default GalleryPage;


import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import config from '../config/config';
import state from '../store';
import { slideAnimation, fadeAnimation } from '../config/motion';

const endpoints = import.meta.env.PROD ? config.production.endpoints : config.development.endpoints;

const ProfessionalRecommendations = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [imageErrors, setImageErrors] = useState({});
  const [userProfile, setUserProfile] = useState({
    user_id: 1,
    name: '',
    email: '',
    age: 25,
    gender: 'female',
    measurements: {
      height: '',
      weight: '',
      chest: '',
      waist: '',
      hips: ''
    }
  });
  const [styleQuiz, setStyleQuiz] = useState({
    preferred_colors: [],
    preferred_styles: [],
    budget_range: { min: 1000, max: 10000 },
    occasions: [],
    body_type: '',
    skin_tone: ''
  });

  const steps = [
    { id: 0, title: 'Welcome', description: "Let's find your perfect style" },
    { id: 1, title: 'Basic Info', description: 'Tell us about yourself' },
    { id: 2, title: 'Style Quiz', description: 'Discover your fashion personality' },
    { id: 3, title: 'Your Recommendations', description: 'Personalized outfits for you' }
  ];

  const handleImageError = (outfitId, itemId, itemType) => {
    setImageErrors(prev => ({
      ...prev,
      [`${outfitId}-${itemId}`]: true
    }));
  };

  const getFallbackImage = (itemType) => {
    const fallbackColors = {
      'top': 'https://via.placeholder.com/200x200/4A90E2/FFFFFF?text=Top',
      'bottom': 'https://via.placeholder.com/200x200/2E8B57/FFFFFF?text=Bottom',
      'shoes': 'https://via.placeholder.com/200x200/8B4513/FFFFFF?text=Shoes',
      'accessory': 'https://via.placeholder.com/200x200/FFD700/000000?text=Accessory'
    };
    return fallbackColors[itemType] || 'https://via.placeholder.com/200x200/f0f0f0/666?text=Item';
  };

  const handleNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const getRecommendations = async () => {
    console.log('=== GET RECOMMENDATIONS STARTED ===');
    setLoading(true);
    try {
      const requestData = {
        user_id: userProfile.user_id || 1,
        age: userProfile.age || 25,
        gender: userProfile.gender || 'male',
        color_pref: styleQuiz.preferred_colors?.[0] || 'blue',
        style_pref: styleQuiz.preferred_styles?.[0] || 'casual',
        budget: styleQuiz.budget_range?.max || 25000,
        measurements: userProfile.measurements || {},
        body_type: styleQuiz.body_type || 'average',
        skin_tone: styleQuiz.skin_tone || 'medium'
      };

      console.log('Request data:', requestData);
      console.log('API endpoint:', endpoints.recommendations);

      // Try API call with fallback
      let data;
      try {
        const res = await fetch(endpoints.recommendations, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData),
        });
        
        console.log('Response status:', res.status);
        console.log('Response ok:', res.ok);
        
        if (res.ok) {
          data = await res.json();
          console.log('Response data:', data);
        } else {
          throw new Error(`API Error: ${res.status}`);
        }
      } catch (apiError) {
        console.warn('API call failed, using fallback data:', apiError);
        // Use fallback recommendations
        data = {
          recommendations: getFallbackRecommendations(requestData.gender, requestData.style_pref)
        };
      }
      
      setRecommendations(data.recommendations || []);
      setCurrentStep(3);
      console.log('Recommendations set successfully!');
    } catch (e) {
      console.error('Error in getRecommendations:', e);
      // Use fallback even on error
      setRecommendations(getFallbackRecommendations(userProfile.gender, 'casual'));
      setCurrentStep(3);
    } finally {
      setLoading(false);
      console.log('=== GET RECOMMENDATIONS ENDED ===');
    }
  };

  // Fallback recommendations function
  const getFallbackRecommendations = (gender, style) => {
    const baseOutfits = [
      {
        outfit_id: 1,
        name: `${style === 'casual' ? 'Casual' : 'Stylish'} ${gender === 'male' ? 'Streetwear' : 'Summer'} Look`,
        description: `Perfect ${style} outfit for ${gender === 'male' ? 'men' : 'women'}`,
        total_price: gender === 'male' ? 8497 : 6797,
        style: style,
        color_scheme: gender === 'male' ? 'blue' : 'yellow',
        target_gender: gender,
        items: [
          {
            id: 1,
            name: gender === 'male' ? 'Blue Streetwear Hoodie' : 'Yellow Summer Dress',
            brand: gender === 'male' ? 'Urban Style' : 'Sunny Style',
            price: gender === 'male' ? 2999 : 2299,
            image_url: `https://picsum.photos/seed/${gender}outfit1/400/400.jpg`,
            type: gender === 'male' ? 'top' : 'dress'
          },
          {
            id: 2,
            name: gender === 'male' ? 'Black Denim Jeans' : 'Beige Flats',
            brand: gender === 'male' ? 'Denim Co' : 'Comfort Zone',
            price: gender === 'male' ? 2499 : 1999,
            image_url: `https://picsum.photos/seed/${gender}outfit2/400/400.jpg`,
            type: gender === 'male' ? 'bottom' : 'shoes'
          },
          {
            id: 3,
            name: gender === 'male' ? 'White Sneakers' : 'Brown Sunglasses',
            brand: gender === 'male' ? 'Street Kicks' : 'Sun Style',
            price: gender === 'male' ? 3999 : 2499,
            image_url: `https://picsum.photos/seed/${gender}outfit3/400/400.jpg`,
            type: gender === 'male' ? 'shoes' : 'accessories'
          }
        ]
      },
      {
        outfit_id: 2,
        name: `${style === 'formal' ? 'Business' : 'Sporty'} ${gender === 'male' ? 'Professional' : 'Athletic'} Look`,
        description: `Complete ${style} outfit for ${gender === 'male' ? 'office' : 'workouts'}`,
        total_price: gender === 'male' ? 12497 : 6997,
        style: style,
        color_scheme: gender === 'male' ? 'navy' : 'black',
        target_gender: gender,
        items: [
          {
            id: 4,
            name: gender === 'male' ? 'White Formal Shirt' : 'Black Athletic Top',
            brand: gender === 'male' ? 'Office Wear' : 'Fit Gear',
            price: gender === 'male' ? 1899 : 1999,
            image_url: `https://picsum.photos/seed/${gender}outfit4/400/400.jpg`,
            type: gender === 'male' ? 'top' : 'top'
          },
          {
            id: 5,
            name: gender === 'male' ? 'Navy Blue Trousers' : 'Black Sports Shorts',
            brand: gender === 'male' ? 'Formal Wear Co' : 'Athletic Pro',
            price: gender === 'male' ? 3499 : 1299,
            image_url: `https://picsum.photos/seed/${gender}outfit5/400/400.jpg`,
            type: gender === 'male' ? 'bottom' : 'bottom'
          },
          {
            id: 6,
            name: gender === 'male' ? 'Brown Formal Shoes' : 'Red Running Shoes',
            brand: gender === 'male' ? 'Executive Style' : 'Athletic Pro',
            price: gender === 'male' ? 3999 : 5499,
            image_url: `https://picsum.photos/seed/${gender}outfit6/400/400.jpg`,
            type: gender === 'male' ? 'shoes' : 'shoes'
          }
        ]
      }
    ];
    
    return baseOutfits;
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <WelcomeStep onNext={handleNextStep} />;
      case 1:
        return <BasicInfoStep 
          userProfile={userProfile} 
          setUserProfile={setUserProfile}
          onNext={handleNextStep}
          onPrev={handlePrevStep}
        />;
      case 2:
        return <StyleQuizStep 
          userProfile={userProfile}
          styleQuiz={styleQuiz}
          setStyleQuiz={setStyleQuiz}
          onNext={getRecommendations}
          onPrev={handlePrevStep}
          loading={loading}
        />;
      case 3:
        return <RecommendationsStep 
          recommendations={recommendations}
          userProfile={userProfile}
          styleQuiz={styleQuiz}
          onRestart={() => setCurrentStep(0)}
        />;
      default:
        return null;
    }
  };

  return (
    <motion.div className="absolute top-0 left-0 z-10 w-full h-full bg-gradient-to-br from-purple-50 to-pink-50" {...slideAnimation('up')}>
      <div className="max-w-6xl mx-auto h-full p-6 flex flex-col">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                  index <= currentStep ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-600'
                }`}>
                  {index < currentStep ? '✓' : index + 1}
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-1 mx-2 ${
                    index < currentStep ? 'bg-purple-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800">{steps[currentStep].title}</h2>
            <p className="text-gray-600">{steps[currentStep].description}</p>
          </div>
        </div>

        {/* Step Content */}
        <div className="flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.3 }}
              className="h-full"
            >
              {renderStep()}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center mt-6">
          <button
            onClick={() => {
              // Reset to home page
              state.intro = true;
              state.view = "home";
            }}
            className="px-6 py-2 rounded-lg font-medium bg-gray-100 text-gray-700 hover:bg-gray-50 border border-gray-300"
          >
            ← Back to Home
          </button>
          <button
            onClick={handleNextStep}
            disabled={currentStep === steps.length - 1}
            className={`px-6 py-2 rounded-lg font-medium flex items-center gap-2 ${
              currentStep === steps.length - 1
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-purple-600 text-white hover:bg-purple-700'
            }`}
          >
            Next
            <span className="text-xl">→</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
};

// Welcome Step Component
const WelcomeStep = ({ onNext }) => (
  <div className="flex flex-col items-center justify-center h-full text-center">
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ duration: 0.5 }}
      className="mb-8"
    >
      <div className="w-32 h-32 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center mb-6 shadow-xl">
        <span className="text-5xl">👗</span>
      </div>
      <h1 className="text-5xl font-bold text-gray-800 mb-4">AiBotique</h1>
      <p className="text-xl text-gray-600 mb-4 max-w-2xl">
        Your Personal AI Fashion Stylist
      </p>
      <p className="text-lg text-gray-500 mb-8 max-w-xl">
        Discover your perfect style with AI-powered outfit recommendations tailored just for you
      </p>
    </motion.div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 max-w-4xl">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
      >
        <div className="w-12 h-12 text-purple-600 mb-4 flex items-center justify-center mx-auto">
          <span className="text-3xl">🎨</span>
        </div>
        <h3 className="font-semibold mb-2 text-lg">Style Quiz</h3>
        <p className="text-sm text-gray-600">Discover your unique fashion personality</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
      >
        <div className="w-12 h-12 text-green-600 mb-4 flex items-center justify-center mx-auto">
          <span className="text-3xl">🤖</span>
        </div>
        <h3 className="font-semibold mb-2 text-lg">AI Recommendations</h3>
        <p className="text-sm text-gray-600">Smart outfit suggestions based on your preferences</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
      >
        <div className="w-12 h-12 text-blue-600 mb-4 flex items-center justify-center mx-auto">
          <span className="text-3xl">💎</span>
        </div>
        <h3 className="font-semibold mb-2 text-lg">Complete Outfits</h3>
        <p className="text-sm text-gray-600">Full styling with matching accessories</p>
      </motion.div>
    </div>

    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.6 }}
      className="flex flex-col items-center gap-4"
    >
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <span>✓ Works for Men & Women</span>
        <span>•</span>
        <span>✓ Indian Pricing</span>
        <span>•</span>
        <span>✓ Instant Results</span>
      </div>
      
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onNext}
        className="px-10 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-bold text-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl flex items-center gap-3"
      >
        Get Started Now
        <span className="text-xl">→</span>
      </motion.button>
      
      <p className="text-xs text-gray-400 mt-2">
        Takes less than 2 minutes • No credit card required
      </p>
    </motion.div>
  </div>
);

// Basic Info Step Component
const BasicInfoStep = ({ userProfile, setUserProfile, onNext, onPrev }) => {
  const validateForm = () => {
    console.log('Validating form with userProfile:', userProfile);
    
    // Check required fields
    if (!userProfile.name.trim()) {
      alert('Please enter your name');
      return false;
    }
    
    if (!userProfile.email.trim()) {
      alert('Please enter your email');
      return false;
    }
    
    if (!userProfile.age || userProfile.age < 16 || userProfile.age > 100) {
      alert('Please enter a valid age (16-100)');
      return false;
    }
    
    if (!userProfile.gender) {
      alert('Please select your gender');
      return false;
    }
    
    console.log('Form validation passed!');
    return true;
  };

  const handleNextClick = () => {
    console.log('Next button clicked');
    if (validateForm()) {
      console.log('Form is valid, proceeding to next step');
      onNext();
    } else {
      console.log('Form validation failed');
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-2xl font-bold mb-6">Tell us about yourself</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
            <input
              type="text"
              value={userProfile.name}
              onChange={(e) => {
                console.log('Name changed to:', e.target.value);
                setUserProfile({...userProfile, name: e.target.value});
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Your name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={userProfile.email}
              onChange={(e) => {
                console.log('Email changed to:', e.target.value);
                setUserProfile({...userProfile, email: e.target.value});
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Age</label>
            <input
              type="number"
              value={userProfile.age}
              onChange={(e) => {
                console.log('Age changed to:', e.target.value);
                setUserProfile({...userProfile, age: parseInt(e.target.value)});
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              min="16"
              max="100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
            <select
              value={userProfile.gender}
              onChange={(e) => {
                console.log('Gender changed to:', e.target.value);
                setUserProfile({...userProfile, gender: e.target.value});
              }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Height (cm)</label>
            <input
              type="number"
              value={userProfile.measurements.height}
              onChange={(e) => setUserProfile({
                ...userProfile, 
                measurements: {...userProfile.measurements, height: e.target.value}
              })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="165"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
            <input
              type="number"
              value={userProfile.measurements.weight}
              onChange={(e) => setUserProfile({
                ...userProfile, 
                measurements: {...userProfile.measurements, weight: e.target.value}
              })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="60"
            />
          </div>
        </div>

        <div className="flex justify-between mt-8">
          <button
            onClick={onPrev}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Previous
          </button>
          <button
            onClick={handleNextClick}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

// Style Quiz Step Component
const StyleQuizStep = ({ userProfile, styleQuiz, setStyleQuiz, onNext, onPrev, loading }) => {
  const colors = ['Black', 'White', 'Blue', 'red', 'Green', 'Yellow', 'Pink', 'Purple', 'Gray', 'Brown'];
  const styles = ['Casual', 'Formal', 'Sporty', 'Elegant', 'Streetwear', 'Vintage', 'Modern', 'Bohemian'];
  const occasions = ['Work', 'Party', 'Date', 'Casual', 'Gym', 'Travel', 'Beach', 'Business Meeting'];
  const bodyTypes = ['Slim', 'Athletic', 'Average', 'Curvy', 'Petite', 'Tall'];
  const skinTones = ['Fair', 'Light', 'Medium', 'Olive', 'Tan', 'Dark'];

  const toggleSelection = (category, value) => {
    try {
      console.log('Toggling selection:', category, value);
      setStyleQuiz(prev => {
        const newQuiz = {
          ...prev,
          [category]: prev[category].includes(value)
            ? prev[category].filter(item => item !== value)
            : [...prev[category], value]
        };
        console.log('New styleQuiz:', newQuiz);
        return newQuiz;
      });
    } catch (error) {
      console.error('Error in toggleSelection:', error);
    }
  };

  const handleGetRecommendations = () => {
    console.log('=== HANDLE GET RECOMMENDATIONS CALLED ===');
    console.log('Current styleQuiz:', styleQuiz);
    console.log('Current userProfile:', userProfile);
    
    // Skip validation for now - just proceed
    console.log('Proceeding to get recommendations...');
    onNext();
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-2xl font-bold mb-6">Style Quiz</h3>
        
        <div className="space-y-8">
          {/* Preferred Colors */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Favorite Colors</label>
            <div className="flex flex-wrap gap-2">
              {colors.map(color => (
                <button
                  key={color}
                  onClick={() => toggleSelection('preferred_colors', color)}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    styleQuiz.preferred_colors.includes(color)
                      ? 'border-purple-600 bg-purple-50 text-purple-600'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {color}
                </button>
              ))}
            </div>
          </div>

          {/* Preferred Styles */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Preferred Styles</label>
            <div className="flex flex-wrap gap-2">
              {styles.map(style => (
                <button
                  key={style}
                  onClick={() => toggleSelection('preferred_styles', style)}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    styleQuiz.preferred_styles.includes(style)
                      ? 'border-purple-600 bg-purple-50 text-purple-600'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

          {/* Budget Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Budget Range: ₹{styleQuiz.budget_range.min.toLocaleString()} - ₹{styleQuiz.budget_range.max.toLocaleString()}
            </label>
            <div className="space-y-2">
              <input
                type="range"
                min="500"
                max="50000"
                step="500"
                value={styleQuiz.budget_range.max}
                onChange={(e) => setStyleQuiz(prev => ({
                  ...prev,
                  budget_range: { ...prev.budget_range, max: parseInt(e.target.value) }
                }))}
                className="w-full"
              />
            </div>
          </div>

          {/* Occasions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Common Occasions</label>
            <div className="flex flex-wrap gap-2">
              {occasions.map(occasion => (
                <button
                  key={occasion}
                  onClick={() => toggleSelection('occasions', occasion)}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    styleQuiz.occasions.includes(occasion)
                      ? 'border-purple-600 bg-purple-50 text-purple-600'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {occasion}
                </button>
              ))}
            </div>
          </div>

          {/* Body Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Body Type</label>
            <div className="flex flex-wrap gap-2">
              {bodyTypes.map(type => (
                <button
                  key={type}
                  onClick={() => setStyleQuiz(prev => ({ ...prev, body_type: type }))}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    styleQuiz.body_type === type
                      ? 'border-purple-600 bg-purple-50 text-purple-600'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Skin Tone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Skin Tone</label>
            <div className="flex flex-wrap gap-2">
              {skinTones.map(tone => (
                <button
                  key={tone}
                  onClick={() => setStyleQuiz(prev => ({ ...prev, skin_tone: tone }))}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    styleQuiz.skin_tone === tone
                      ? 'border-purple-600 bg-purple-50 text-purple-600'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {tone}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-between mt-8">
          <button
            onClick={onPrev}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Previous
          </button>
          <button
            onClick={handleGetRecommendations}
            disabled={loading}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Getting Recommendations...' : 'Get My Recommendations'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Recommendations Step Component
const RecommendationsStep = ({ recommendations, userProfile, styleQuiz, onRestart }) => (
  <div className="max-w-6xl mx-auto">
    <div className="mb-6 text-center">
      <h3 className="text-3xl font-bold text-gray-800 mb-2">Your Personalized Outfits</h3>
      <p className="text-gray-600">
        Based on your style quiz and preferences, we've curated these outfits just for you
      </p>
    </div>

    {recommendations.length > 0 ? (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {recommendations.map((outfit) => (
          <motion.div
            key={outfit.outfit_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="text-xl font-bold text-gray-800">{outfit.name}</h4>
                  <p className="text-gray-600 text-sm">{outfit.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">
                    ₹{outfit.total_price?.toLocaleString('en-IN') || '0'}
                  </div>
                  <div className="text-xs text-gray-500">Total outfit price</div>
                </div>
              </div>

              <div className="flex gap-2 mb-4">
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
                  {outfit.style}
                </span>
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                  {outfit.color_scheme}
                </span>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                  {outfit.target_gender}
                </span>
              </div>

              <div className="mb-4">
                <h5 className="font-semibold mb-2">Complete Outfit Items:</h5>
                <div className="grid grid-cols-3 gap-3">
                  {outfit.items?.map((item, idx) => (
                    <div key={idx} className="text-center">
                      <div className="relative mb-2">
                        <img
                          src={item.image_url || `https://picsum.photos/seed/${item.id}/200/200.jpg`}
                          alt={item.name}
                          className="w-full h-20 object-cover rounded-lg"
                          onError={(e) => {
                            e.target.src = `https://picsum.photos/seed/fallback${item.id}/200/200.jpg`;
                          }}
                        />
                      </div>
                      <div className="text-xs font-medium truncate">{item.name}</div>
                      <div className="text-xs text-gray-500">{item.brand}</div>
                      <div className="text-xs font-bold text-green-600">
                        ₹{item.price?.toLocaleString('en-IN') || '0'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => window.open(`https://www.amazon.in/s?k=${encodeURIComponent(outfit.name)}`, '_blank')}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  View on Amazon
                </button>
                <button
                  onClick={() => alert(`Added "${outfit.name}" to cart!`)}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                >
                  Add to Cart
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    ) : (
      <div className="text-center py-12">
        <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-4xl">🛍️</span>
        </div>
        <h4 className="text-xl font-semibold text-gray-800 mb-2">No recommendations yet</h4>
        <p className="text-gray-600 mb-6">Complete the style quiz to get your personalized recommendations</p>
        <button
          onClick={() => {
            // Reset to home page
            state.intro = true;
            state.view = "home";
          }}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          ← Back to Home
        </button>
      </div>
    )}

    <div className="mt-8 text-center">
      <button
        onClick={() => {
          // Reset to home page
          state.intro = true;
          state.view = "home";
        }}
        className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all"
      >
        ← Back to Home
      </button>
    </div>
  </div>
);

export default ProfessionalRecommendations;

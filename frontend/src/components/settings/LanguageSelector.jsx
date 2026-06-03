import React, { useState, useEffect } from 'react';
import axiosInstance from '../api/axiosInstance';

/**
 * LanguageSelector Component
 * Allows users to switch between 8+ African languages
 * Supports: English, Swahili, Hausa, Yoruba, French, Amharic, Zulu, Spanish, Portuguese
 * Persists selection to localStorage and localStorage
 */
const LanguageSelector = () => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [saving, setSaving] = useState(false);

  const LANGUAGES = {
    en: { 
      name: 'English', 
      flag: '',
      regions: ['All regions']
    },
    sw: { 
      name: 'Swahili (Kiswahili)', 
      flag: '',
      regions: ['Kenya', 'Tanzania', 'Uganda']
    },
    ha: { 
      name: 'Hausa', 
      flag: '',
      regions: ['Nigeria', 'Niger']
    },
    yo: { 
      name: 'Yoruba', 
      flag: '',
      regions: ['Nigeria']
    },
    fr: { 
      name: 'Franais', 
      flag: '',
      regions: ['Cte d\'Ivoire', 'Cameroon', 'Senegal', 'DRC']
    },
    am: { 
      name: 'Amharic ()', 
      flag: '',
      regions: ['Ethiopia']
    },
    zu: { 
      name: 'Zulu', 
      flag: '',
      regions: ['South Africa']
    },
    es: { 
      name: 'Espaol', 
      flag: '',
      regions: ['Global']
    },
    pt: { 
      name: 'Portugus', 
      flag: '',
      regions: ['Angola', 'Mozambique', 'Guinea-Bissau']
    },
  };

  // Initialize language from localStorage or user settings
  useEffect(() => {
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'en';
    setCurrentLanguage(savedLanguage);
    applyLanguage(savedLanguage);
  }, []);

  const applyLanguage = (langCode) => {
    // Set Accept-Language header for all future API requests
    axiosInstance.defaults.headers.common['Accept-Language'] = langCode;
    localStorage.setItem('preferredLanguage', langCode);
    
    // Set HTML lang attribute
    document.documentElement.lang = langCode;
    
    // Emit custom event for other components to listen
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: langCode } }));
  };

  const handleLanguageChange = async (newLanguage) => {
    try {
      setSaving(true);
      
      // Update user profile language preference (if API available)
      if (localStorage.getItem('userLanguageUpdateEndpoint')) {
        await axiosInstance.patch('/users/me/', {
          language: newLanguage
        });
      }
      
      setCurrentLanguage(newLanguage);
      applyLanguage(newLanguage);
      
    } catch (error) {
      console.warn('Could not save language preference to server:', error);
      // Still apply language locally even if server save fails
      setCurrentLanguage(newLanguage);
      applyLanguage(newLanguage);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w-full">
      {/* Desktop Version - Dropdown */}
      <div className="hidden md:block">
        <div className="relative inline-block w-full md:w-64">
          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{LANGUAGES[currentLanguage]?.flag}</span>
              <div>
                <label className="block text-xs font-semibold text-gray-600 uppercase">Language</label>
                <span className="text-sm font-semibold text-gray-900">
                  {LANGUAGES[currentLanguage]?.name}
                </span>
              </div>
            </div>
            <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
          
          {/* Dropdown Menu */}
          <div className="absolute top-full left-0 mt-2 w-full bg-white border border-gray-200 rounded-lg shadow-xl z-50">
            {Object.entries(LANGUAGES).map(([code, lang]) => (
              <button
                key={code}
                onClick={() => handleLanguageChange(code)}
                disabled={saving}
                className={`w-full text-left px-4 py-3 border-b border-gray-100 last:border-b-0 flex items-center justify-between hover:bg-blue-50 transition ${
                  currentLanguage === code ? 'bg-blue-100 text-blue-900 font-semibold' : 'text-gray-700'
                } disabled:opacity-50`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{lang.flag}</span>
                  <div>
                    <div className="font-semibold">{lang.name}</div>
                    <div className="text-xs text-gray-500">{lang.regions.join(', ')}</div>
                  </div>
                </div>
                {currentLanguage === code && (
                  <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Mobile Version - Grid */}
      <div className="block md:hidden">
        <label className="block text-sm font-semibold text-gray-700 mb-3">Select Language</label>
        <div className="grid grid-cols-3 gap-2">
          {Object.entries(LANGUAGES).map(([code, lang]) => (
            <button
              key={code}
              onClick={() => handleLanguageChange(code)}
              disabled={saving}
              className={`p-2 rounded-lg border-2 transition text-center ${
                currentLanguage === code 
                  ? 'bg-blue-100 border-blue-600 text-blue-900' 
                  : 'bg-gray-50 border-gray-200 text-gray-700 hover:border-blue-300'
              } disabled:opacity-50`}
            >
              <div className="text-2xl mb-1">{lang.flag}</div>
              <div className="text-xs font-semibold line-clamp-2">{lang.name}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LanguageSelector;

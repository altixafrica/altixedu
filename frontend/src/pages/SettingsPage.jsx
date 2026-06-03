import React, { useState } from 'react';
import NotificationPreferencesSettings from './NotificationPreferencesSettings';
import LanguageSelector from './LanguageSelector';

/**
 * SettingsPage Component
 * Main settings hub for users to manage:
 * - Notification preferences (email, in-app, notification types)
 * - Language selection (8+ African languages)
 * - Theme preferences (future)
 * - Account settings (future)
 */
const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('notifications');

  const tabs = [
    { id: 'notifications', label: ' Notifications', icon: '' },
    { id: 'language', label: ' Language', icon: '' },
    { id: 'theme', label: ' Theme', icon: '', disabled: true },
    { id: 'account', label: ' Account', icon: '', disabled: true },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-8 shadow-lg">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold mb-2"> Settings</h1>
          <p className="text-blue-100">Customize your Altix Edu experience</p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs Navigation */}
        <div className="bg-white rounded-lg shadow-md mb-8 p-1">
          <div className="flex flex-wrap md:flex-nowrap gap-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => !tab.disabled && setActiveTab(tab.id)}
                disabled={tab.disabled}
                className={`flex-1 md:flex-none md:flex-1 px-4 py-3 font-semibold rounded-lg transition ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-gray-700 hover:bg-gray-100'
                } ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <span className="mr-2">{tab.icon}</span>
                <span className="hidden md:inline">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-lg shadow-lg">
          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div>
              <NotificationPreferencesSettings />
            </div>
          )}

          {/* Language Tab */}
          {activeTab === 'language' && (
            <div className="p-8">
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2"> Language Settings</h1>
                <p className="text-gray-600">Choose your preferred language. The interface will update immediately.</p>
              </div>
              
              {/* Supported Languages Info */}
              <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-3"> We Support 9 Languages</h3>
                <p className="text-blue-800 text-sm">
                  All translations are available in African languages to serve schools across the continent. 
                  Your language preference is saved automatically and will be used across all Altix Edu features.
                </p>
              </div>

              <LanguageSelector />

              {/* Language Information Table */}
              <div className="mt-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4"> Languages by Region</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Language</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Regions</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4"> English</td>
                        <td className="py-3 px-4">All regions</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4"> Swahili</td>
                        <td className="py-3 px-4">Kenya, Tanzania, Uganda</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4"> Hausa</td>
                        <td className="py-3 px-4">Nigeria, Niger</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4"> Yoruba</td>
                        <td className="py-3 px-4">Nigeria</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4"> Franais</td>
                        <td className="py-3 px-4">Cte d'Ivoire, Cameroon, Senegal, DRC</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4"> Amharic</td>
                        <td className="py-3 px-4">Ethiopia</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4"> Zulu</td>
                        <td className="py-3 px-4">South Africa</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                      <tr className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4"> Espaol</td>
                        <td className="py-3 px-4">Global</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                      <tr className="hover:bg-gray-50">
                        <td className="py-3 px-4"> Portugus</td>
                        <td className="py-3 px-4">Angola, Mozambique, Guinea-Bissau</td>
                        <td className="py-3 px-4"><span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Complete</span></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Theme Tab - Coming Soon */}
          {activeTab === 'theme' && (
            <div className="p-8 text-center">
              <div className="text-6xl mb-4"></div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Theme Settings</h2>
              <p className="text-gray-600">Coming soon! Customize light mode, dark mode, and color themes.</p>
            </div>
          )}

          {/* Account Tab - Coming Soon */}
          {activeTab === 'account' && (
            <div className="p-8 text-center">
              <div className="text-6xl mb-4"></div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Account Settings</h2>
              <p className="text-gray-600">Coming soon! Manage your profile, password, and security settings.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-600 text-sm">
          <p>Need help? <a href="/support" className="text-blue-600 hover:underline">Contact Support</a></p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;

import React, { createContext, useState, useCallback, useEffect } from 'react';
import { ChevronRight, Check, X } from 'lucide-react';

export const OnboardingContext = createContext();

export const OnboardingProvider = ({ children }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [userRole, setUserRole] = useState(null);

  const startOnboarding = useCallback((role) => {
    setUserRole(role);
    setCurrentStep(0);
    setIsOpen(true);
  }, []);

  const nextStep = useCallback(() => {
    setCurrentStep((prev) => prev + 1);
  }, []);

  const closeOnboarding = useCallback(() => {
    setIsOpen(false);
  }, []);

  return (
    <OnboardingContext.Provider
      value={{
        currentStep,
        isOpen,
        userRole,
        startOnboarding,
        nextStep,
        closeOnboarding,
      }}
    >
      {children}
      <OnboardingTour />
    </OnboardingContext.Provider>
  );
};

export const useOnboarding = () => {
  const context = React.useContext(OnboardingContext);
  if (!context) {
    throw new Error('useOnboarding must be used within OnboardingProvider');
  }
  return context;
};

const ROLE_TOURS = {
  admin: [
    {
      target: '#main-content',
      title: 'Welcome to AltixEdu Admin Dashboard!',
      description: 'Manage your school, teachers, students, and more from this central hub.',
      highlightClass: 'bg-blue-50',
    },
    {
      target: '#main-content',
      title: 'Navigation Menu',
      description: 'Access all features from the sidebar: Overview, Messages, Export, Users, and Settings.',
      position: 'right',
    },
    {
      target: '#main-content',
      title: 'Messages',
      description: 'Communicate with teachers, staff, and parents directly from the Messages tab.',
      position: 'right',
    },
    {
      target: '#main-content',
      title: 'Export Data',
      description: 'Export student records, attendance, fees, and more in CSV format.',
      position: 'right',
    },
    {
      target: '#main-content',
      title: 'Dashboard Complete!',
      description: 'You\'re all set. Explore all features and feel free to reach out if you need help!',
      position: 'center',
      isLast: true,
    },
  ],
  teacher: [
    {
      target: '#main-content',
      title: 'Welcome, Teacher!',
      description: 'Manage your classes, students, and grades from your personal dashboard.',
      highlightClass: 'bg-green-50',
    },
    {
      target: '#main-content',
      title: 'Your Workspace',
      description: 'View your assigned classes, students, and classroom activities.',
      position: 'right',
    },
    {
      target: '#main-content',
      title: 'Send Messages',
      description: 'Communicate with admin and parents using the Messages feature.',
      position: 'right',
    },
    {
      target: '#main-content',
      title: 'Export Records',
      description: 'Export attendance and grade records for your classes.',
      position: 'right',
    },
  ],
  student: [
    {
      target: '#main-content',
      title: 'Welcome to Your Student Portal!',
      description: 'Track your grades, attendance, and academic progress.',
      highlightClass: 'bg-purple-50',
    },
    {
      target: '#main-content',
      title: 'Your Grades',
      description: 'View your performance across all subjects in one place.',
      position: 'right',
    },
    {
      target: '#main-content',
      title: 'Connect with Your Teacher',
      description: 'Use Messages to ask questions and stay in touch with teachers.',
      position: 'right',
    },
  ],
  parent: [
    {
      target: '#main-content',
      title: 'Welcome to Family Portal!',
      description: 'Monitor your child\'s academic progress and stay connected.',
      highlightClass: 'bg-orange-50',
    },
    {
      target: '#main-content',
      title: 'Child\'s Progress',
      description: 'View grades, attendance, and performance analytics.',
      position: 'right',
    },
    {
      target: '#main-content',
      title: 'Communication Hub',
      description: 'Message teachers and admin with questions or concerns.',
      position: 'right',
    },
  ],
  bursar: [
    {
      target: '#main-content',
      title: 'Finance Dashboard',
      description: 'Manage fees, payments, and financial reports.',
      highlightClass: 'bg-emerald-50',
    },
    {
      target: '#main-content',
      title: 'Payment Tracking',
      description: 'Monitor student payments and outstanding fees.',
      position: 'right',
    },
    {
      target: '#main-content',
      title: 'Export Financial Data',
      description: 'Generate and export fee and payment reports.',
      position: 'right',
    },
  ],
};

const OnboardingTour = () => {
  const { currentStep, isOpen, userRole, nextStep, closeOnboarding } =
    useOnboarding();

  if (!isOpen || !userRole) return null;

  const steps = ROLE_TOURS[userRole] || [];
  if (steps.length === 0) return null;

  const step = steps[currentStep];
  if (!step) return null;

  const isLastStep = currentStep === steps.length - 1;
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/40 z-40"
        onClick={closeOnboarding}
      />

      {/* Tour Card */}
      <div
        className={`fixed z-50 bg-white rounded-lg shadow-2xl max-w-md p-6 ${
          step.position === 'center'
            ? 'left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2'
            : 'right-6 bottom-6'
        }`}
      >
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-gray-600">
              Step {currentStep + 1} of {steps.length}
            </span>
            <button
              onClick={closeOnboarding}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              {step.title}
            </h3>
            <p className="text-sm text-gray-600">{step.description}</p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            {currentStep > 0 && (
              <button
                onClick={() => {
                  // Go back
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium text-sm transition-colors"
              >
                Back
              </button>
            )}
            <button
              onClick={() => {
                if (isLastStep) {
                  closeOnboarding();
                  // Mark as seen
                  localStorage.setItem(
                    `onboarding_seen_${userRole}`,
                    'true'
                  );
                } else {
                  nextStep();
                }
              }}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-2"
            >
              {isLastStep ? (
                <>
                  <Check className="w-4 h-4" />
                  Done
                </>
              ) : (
                <>
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Tip */}
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-xs text-blue-700">
             You can always access help from the support menu in your dashboard.
          </p>
        </div>
      </div>
    </>
  );
};

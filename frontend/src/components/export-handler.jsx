import React, { useState } from 'react';
import { Download, Loader, Check, AlertCircle } from 'lucide-react';
import {
  exportStudentsData,
  exportStaffData,
  exportAttendanceData,
  exportFeesData,
  downloadFile,
} from '../lib/django';
import { useError } from './error-display';
import { formatErrorForDisplay } from '../lib/error-handler';

const EXPORT_OPTIONS = {
  students: {
    label: 'Students',
    fn: exportStudentsData,
    filename: 'students',
  },
  staff: {
    label: 'Staff/Teachers',
    fn: exportStaffData,
    filename: 'staff',
  },
  attendance: {
    label: 'Attendance Records',
    fn: exportAttendanceData,
    filename: 'attendance',
  },
  fees: {
    label: 'Fees/Finance',
    fn: exportFeesData,
    filename: 'fees',
  },
};

export const ExportButton = ({ type = 'students', label = null, icon = true, className = '' }) => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { addError } = useError();
  const option = EXPORT_OPTIONS[type];

  if (!option) {
    console.warn(`Unknown export type: ${type}`);
    return null;
  }

  const handleExport = async () => {
    setLoading(true);
    setSuccess(false);
    try {
      const blob = await option.fn('csv');
      const timestamp = new Date().toISOString().split('T')[0];
      downloadFile(blob, `${option.filename}-${timestamp}.csv`);
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      const formatted = formatErrorForDisplay(error);
      addError(formatted.message || 'Failed to export data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={loading}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
        success
          ? 'bg-green-100 text-green-700'
          : 'bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white'
      } ${className}`}
    >
      {loading ? (
        <Loader className="w-4 h-4 animate-spin" />
      ) : success ? (
        <Check className="w-4 h-4" />
      ) : icon ? (
        <Download className="w-4 h-4" />
      ) : null}
      {success ? 'Exported!' : label || option.label}
    </button>
  );
};

export const ExportPanel = ({ isOpen, onClose }) => {
  const [selectedFormat, setSelectedFormat] = useState('csv');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Download className="w-6 h-6 text-blue-600" />
            Export Data
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            
          </button>
        </div>

        <div className="space-y-4">
          {/* Format selector */}
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Format:</p>
            <div className="flex gap-2">
              {['csv', 'excel', 'pdf'].map((format) => (
                <button
                  key={format}
                  onClick={() => setSelectedFormat(format)}
                  className={`px-3 py-2 rounded-lg font-medium text-sm transition-colors ${
                    selectedFormat === format
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {format.toUpperCase()}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Note: Currently exporting as CSV format
            </p>
          </div>

          {/* Export options */}
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">Select data to export:</p>
            <div className="space-y-2">
              {Object.entries(EXPORT_OPTIONS).map(([key, option]) => (
                <ExportButton
                  key={key}
                  type={key}
                  className="w-full justify-start"
                />
              ))}
            </div>
          </div>

          <div className="pt-4 border-t">
            <p className="text-xs text-gray-500">
               Tip: Exported files will be saved to your Downloads folder with the current date.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

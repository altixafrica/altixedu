import React, { useState, useEffect } from 'react';
import axiosInstance from '../../api/axios';
import StudentPaymentModal from './StudentPaymentModal';

const StudentFeesPage = () => {
  const [studentFees, setStudentFees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFee, setSelectedFee] = useState(null);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [receipts, setReceipts] = useState([]);

  useEffect(() => {
    fetchStudentFees();
    fetchPaymentReceipts();
  }, []);

  const fetchStudentFees = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/student-fees/');
      setStudentFees(response.data.results || response.data);
    } catch (err) {
      setError('Failed to load fees');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPaymentReceipts = async () => {
    try {
      const response = await axiosInstance.get('/payments/receipts/');
      setReceipts(response.data.receipts || []);
    } catch (err) {
      console.error('Failed to load receipts:', err);
    }
  };

  const handlePaymentClick = (fee) => {
    setSelectedFee(fee);
    setPaymentModalOpen(true);
  };

  const handlePaymentSuccess = () => {
    fetchStudentFees();
    fetchPaymentReceipts();
    setPaymentModalOpen(false);
  };

  const getStatusBadge = (fee) => {
    if (fee.balance_due <= 0) {
      return (
        <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
           Paid
        </span>
      );
    } else if (fee.balance_due === fee.fee.amount) {
      return (
        <span className="inline-block px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
           Not Paid
        </span>
      );
    } else {
      return (
        <span className="inline-block px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-semibold">
           Partial
        </span>
      );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="inline-block animate-spin mb-4">
            <svg
              className="w-12 h-12 text-blue-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <p className="text-gray-600">Loading your fees...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900"> My School Fees</h1>
          <p className="mt-2 text-gray-600">View and pay your outstanding school fees</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Fees Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-2">Total Fees</p>
            <p className="text-3xl font-bold text-gray-900">
              {studentFees.reduce((sum, fee) => sum + (fee.fee.amount || 0), 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-2">Paid Amount</p>
            <p className="text-3xl font-bold text-green-600">
              {studentFees.reduce((sum, fee) => sum + (fee.amount_paid || 0), 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-2">Outstanding Balance</p>
            <p className="text-3xl font-bold text-red-600">
              {studentFees.reduce((sum, fee) => sum + Math.max(0, fee.balance_due), 0).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Fees Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Fee Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Paid
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Balance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {studentFees.map(fee => (
                  <tr key={fee.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                      {fee.fee.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {fee.currency_symbol}{fee.fee.amount}
                    </td>
                    <td className="px-6 py-4 text-sm text-green-600 font-semibold">
                      {fee.currency_symbol}{fee.amount_paid}
                    </td>
                    <td className="px-6 py-4 text-sm text-red-600 font-semibold">
                      {fee.currency_symbol}{Math.max(0, fee.balance_due)}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {getStatusBadge(fee)}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {fee.balance_due > 0 ? (
                        <button
                          onClick={() => handlePaymentClick(fee)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-xs font-semibold"
                        >
                           Pay
                        </button>
                      ) : (
                        <span className="text-gray-500"></span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {studentFees.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">No fees assigned yet</p>
            </div>
          )}
        </div>

        {/* Payment History */}
        {receipts.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900"> Payment History</h2>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                      Method
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                      Reference
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {receipts.map(receipt => (
                    <tr key={receipt.id}>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {new Date(receipt.payment_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-green-600">
                        {receipt.currency_code} {receipt.amount}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {receipt.payment_method}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 font-mono">
                        {receipt.reference}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Payment Modal */}
      {selectedFee && (
        <StudentPaymentModal
          studentFeeId={selectedFee.id}
          isOpen={paymentModalOpen}
          onClose={() => setPaymentModalOpen(false)}
          onPaymentSuccess={handlePaymentSuccess}
        />
      )}
    </div>
  );
};

export default StudentFeesPage;

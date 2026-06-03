import React, { useState, useEffect } from 'react';
import axiosInstance from '../../api/axios';

const StudentPaymentModal = ({ studentFeeId, isOpen, onClose, onPaymentSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [step, setStep] = useState('confirm'); // confirm, processing, success
  const [feeDetails, setFeeDetails] = useState(null);
  const [paymentLink, setPaymentLink] = useState(null);
  const [reference, setReference] = useState(null);

  useEffect(() => {
    if (isOpen && studentFeeId) {
      fetchFeeDetails();
    }
  }, [isOpen, studentFeeId]);

  const fetchFeeDetails = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(`/student-fees/${studentFeeId}/`);
      setFeeDetails(response.data);
    } catch (err) {
      setError('Failed to load fee details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const initiatePayment = async () => {
    try {
      setLoading(true);
      setError(null);

      // Create payment link
      const response = await axiosInstance.post('/payments/initiate-payment/', {
        student_fee_id: studentFeeId
      });

      if (response.data.success) {
        setPaymentLink(response.data.payment_link);
        setReference(response.data.reference);
        
        // Open Flutterwave payment modal
        // Note: In production, you'd integrate the actual Flutterwave modal
        window.open(response.data.payment_link, '_blank', 'width=800,height=600');
        
        // Start polling for payment status
        setStep('processing');
        pollPaymentStatus(response.data.reference);
      } else {
        setError(response.data.error || 'Failed to initiate payment');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to initiate payment');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const pollPaymentStatus = async (ref, attempts = 0) => {
    if (attempts > 30) {
      // Stop polling after 30 attempts (5 minutes)
      setError('Payment verification timeout. Please check your payment status.');
      return;
    }

    try {
      // Wait 10 seconds before checking
      await new Promise(resolve => setTimeout(resolve, 10000));

      const response = await axiosInstance.get(
        `/payments/payment-status/?reference=${ref}`
      );

      if (response.data.status === 'successful') {
        // Payment successful, verify and record
        verifyPayment(ref);
      } else if (response.data.status === 'pending') {
        // Keep polling
        pollPaymentStatus(ref, attempts + 1);
      } else {
        setError(`Payment ${response.data.status}. Please try again.`);
        setStep('confirm');
      }
    } catch (err) {
      // Continue polling even if check fails
      pollPaymentStatus(ref, attempts + 1);
    }
  };

  const verifyPayment = async (ref) => {
    try {
      setLoading(true);

      const response = await axiosInstance.post('/payments/verify-payment/', {
        reference: ref,
        student_fee_id: studentFeeId
      });

      if (response.data.success) {
        setStep('success');
        // Notify parent component
        if (onPaymentSuccess) {
          onPaymentSuccess(response.data.receipt);
        }
        
        // Close modal after 3 seconds
        setTimeout(() => {
          handleClose();
        }, 3000);
      } else {
        setError(response.data.error || 'Payment verification failed');
        setStep('confirm');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Payment verification failed');
      setStep('confirm');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setStep('confirm');
    setError(null);
    setPaymentLink(null);
    setReference(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">
            {step === 'success' ? ' Payment Successful' : ' Make Payment'}
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-6">
          {/* Confirm Step */}
          {step === 'confirm' && (
            <>
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              {feeDetails && (
                <div className="space-y-4 mb-6">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-600 text-sm mb-1">Fee Type</p>
                    <p className="text-gray-900 font-semibold">{feeDetails.fee.name}</p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-600 text-sm mb-1">Amount Due</p>
                    <p className="text-3xl font-bold text-blue-600">
                      {feeDetails.currency_symbol}{feeDetails.balance_due}
                    </p>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-blue-800 text-sm">
                      <strong>Payment Methods Available:</strong>
                      <br /> Card (Visa, Mastercard, AMEX)
                      <br /> Mobile Money (M-Pesa, Airtel, MTN)
                      <br /> Bank Transfer
                      <br /> USSD
                    </p>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                <button
                  onClick={initiatePayment}
                  disabled={loading}
                  className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-semibold"
                >
                  {loading ? 'Processing...' : ' Pay Now via Flutterwave'}
                </button>

                <button
                  onClick={handleClose}
                  className="w-full px-4 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
              </div>
            </>
          )}

          {/* Processing Step */}
          {step === 'processing' && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin">
                <svg
                  className="w-12 h-12 text-blue-600"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              </div>
              <p className="mt-4 text-gray-600">Verifying payment...</p>
              <p className="text-sm text-gray-500 mt-2">
                Please complete the payment in the popup window
              </p>
            </div>
          )}

          {/* Success Step */}
          {step === 'success' && (
            <div className="text-center py-8">
              <div className="text-6xl mb-4"></div>
              <p className="text-lg font-semibold text-gray-900 mb-2">
                Payment Successful!
              </p>
              <p className="text-gray-600 mb-4">
                Your fee payment has been recorded
              </p>
              <p className="text-sm text-gray-500">
                Closing in a few seconds...
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentPaymentModal;

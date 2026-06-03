import React, { useState, useEffect } from 'react';
import axiosInstance from '../../api/axios';

const TeacherExamScoreEntry = () => {
  const [formData, setFormData] = useState({
    exam_id: '',
    classroom_id: '',
    subject_id: '',
  });
  
  const [exams, setExams] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [scores, setScores] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Load exams on component mount
  useEffect(() => {
    fetchExams();
  }, []);

  const fetchExams = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/exams/');
      setExams(response.data.results || response.data);
    } catch (err) {
      setError('Failed to load exams');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchClassrooms = async () => {
    try {
      const response = await axiosInstance.get('/classrooms/');
      setClassrooms(response.data.results || response.data);
    } catch (err) {
      setError('Failed to load classrooms');
    }
  };

  const fetchSubjects = async () => {
    try {
      const response = await axiosInstance.get('/subjects/');
      setSubjects(response.data.results || response.data);
    } catch (err) {
      setError('Failed to load subjects');
    }
  };

  const fetchStudents = async (classroomId) => {
    try {
      const response = await axiosInstance.get(`/students/?classroom=${classroomId}`);
      const studentList = response.data.results || response.data;
      setStudents(studentList);
      
      // Initialize scores object
      const newScores = {};
      studentList.forEach(student => {
        newScores[student.id] = '';
      });
      setScores(newScores);
    } catch (err) {
      setError('Failed to load students');
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    if (name === 'classroom_id' && value) {
      fetchStudents(value);
    }
  };

  const handleScoreChange = (studentId, value) => {
    setScores(prev => ({
      ...prev,
      [studentId]: value === '' ? '' : Math.min(100, Math.max(0, parseFloat(value) || 0))
    }));
  };

  const validateForm = () => {
    if (!formData.exam_id || !formData.classroom_id || !formData.subject_id) {
      setError('Please select exam, classroom, and subject');
      return false;
    }

    // Check if at least one score is entered
    const hasScores = Object.values(scores).some(score => score !== '');
    if (!hasScores) {
      setError('Please enter at least one score');
      return false;
    }

    // Validate all entered scores
    for (const [studentId, score] of Object.entries(scores)) {
      if (score !== '' && (isNaN(score) || score < 0 || score > 100)) {
        setError(`Invalid score for student ${studentId}. Score must be between 0-100`);
        return false;
      }
    }

    return true;
  };

  const submitScores = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      // Format scores for submission
      const scoresArray = Object.entries(scores)
        .filter(([_, score]) => score !== '')
        .map(([studentId, score]) => ({
          student_id: parseInt(studentId),
          score: parseFloat(score)
        }));

      const response = await axiosInstance.post('/exam-results/bulk-enter-scores/', {
        exam_id: parseInt(formData.exam_id),
        classroom_id: parseInt(formData.classroom_id),
        subject_id: parseInt(formData.subject_id),
        scores: scoresArray
      });

      if (response.data.success) {
        setSuccess(` ${response.data.message}`);
        
        // Reset form
        setTimeout(() => {
          setFormData({ exam_id: '', classroom_id: '', subject_id: '' });
          setScores({});
          setStudents([]);
          setSuccess(null);
        }, 2000);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit scores');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const getStudentName = (student) => {
    return `${student.user.first_name} ${student.user.last_name}`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900"> Enter Exam Scores</h1>
          <p className="mt-2 text-gray-600">Enter student scores for a specific exam, subject, and classroom</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800">{success}</p>
          </div>
        )}

        {/* Selection Form */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Select Details</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {/* Exam Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Exam <span className="text-red-500">*</span>
              </label>
              <select
                name="exam_id"
                value={formData.exam_id}
                onChange={handleFormChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select an exam</option>
                {exams.map(exam => (
                  <option key={exam.id} value={exam.id}>
                    {exam.name} ({exam.class_name})
                  </option>
                ))}
              </select>
            </div>

            {/* Classroom Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Classroom <span className="text-red-500">*</span>
              </label>
              <select
                name="classroom_id"
                value={formData.classroom_id}
                onChange={handleFormChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a classroom</option>
                {classrooms.map(classroom => (
                  <option key={classroom.id} value={classroom.id}>
                    {classroom.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Subject Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject <span className="text-red-500">*</span>
              </label>
              <select
                name="subject_id"
                value={formData.subject_id}
                onChange={handleFormChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a subject</option>
                {subjects.map(subject => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Scores Entry Table */}
        {students.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold">
                Enter Scores ({students.length} students)
              </h2>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                      Student Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                      Admission No.
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                      Score (0-100)
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {students.map(student => (
                    <tr key={student.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {getStudentName(student)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {student.admission_number}
                      </td>
                      <td className="px-6 py-4">
                        <input
                          type="number"
                          min="0"
                          max="100"
                          value={scores[student.id] ?? ''}
                          onChange={(e) => handleScoreChange(student.id, e.target.value)}
                          placeholder="Enter score"
                          className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Submit Button */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3">
              <button
                onClick={submitScores}
                disabled={submitting || !formData.exam_id || !formData.classroom_id || !formData.subject_id}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
              >
                {submitting ? 'Saving...' : ' Save Scores'}
              </button>
              <button
                onClick={() => {
                  setScores({});
                  setError(null);
                }}
                className="px-6 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
              >
                 Clear
              </button>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!students.length && formData.classroom_id && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 text-lg">
              Select all fields above to see students
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherExamScoreEntry;

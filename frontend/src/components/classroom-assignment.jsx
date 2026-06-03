import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Users } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { LoadingButton } from './quick-wins-animations';
import apiClient from '../lib/api-client';

export const ClassroomAssignment = () => {
  const [classrooms, setClassrooms] = useState([]);
  const [students, setStudents] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [selectedClassroom, setSelectedClassroom] = useState(null);
  const [formData, setFormData] = useState({
    student_id: '',
    classroom_id: '',
    academic_year: new Date().getFullYear() + '-' + (new Date().getFullYear() + 1),
    roll_number: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [classroomsRes, studentsRes, assignmentsRes] = await Promise.all([
        apiClient.get('/api/classrooms/'),
        apiClient.get('/api/students/'),
        apiClient.get('/api/classroom-assignments/'),
      ]);

      setClassrooms(classroomsRes.data.results || classroomsRes.data);
      setStudents(studentsRes.data.results || studentsRes.data);
      setAssignments(assignmentsRes.data.results || assignmentsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handleAssignStudent = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.post('/api/classroom-assignments/', {
        student: parseInt(formData.student_id),
        classroom: parseInt(formData.classroom_id),
        academic_year: formData.academic_year,
        roll_number: parseInt(formData.roll_number),
      });

      setFormData({
        student_id: '',
        classroom_id: '',
        academic_year: new Date().getFullYear() + '-' + (new Date().getFullYear() + 1),
        roll_number: '',
      });
      setShowForm(false);

      fetchData();
      alert('Student assigned to classroom successfully!');
    } catch (error) {
      console.error('Error assigning student:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAssignment = async (assignmentId) => {
    if (!window.confirm('Remove this student from the classroom?')) return;

    try {
      await apiClient.delete(`/api/classroom-assignments/${assignmentId}/`);
      fetchData();
    } catch (error) {
      console.error('Error removing assignment:', error);
      alert('Error removing assignment');
    }
  };

  const getClassroomRoster = (classroomId) => {
    return assignments.filter(a => a.classroom === classroomId && a.is_active);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-display font-bold text-slate-900">Classroom Assignment</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Assign Student
        </button>
      </div>

      {/* Assignment Form */}
      {showForm && (
        <Card className="border-2 border-blue-200">
          <CardContent className="pt-6">
            <form onSubmit={handleAssignStudent} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Student</label>
                  <select
                    required
                    value={formData.student_id}
                    onChange={(e) => setFormData({ ...formData, student_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  >
                    <option value="">Select a student</option>
                    {students.map((student) => (
                      <option key={student.id} value={student.id}>
                        {student.first_name} {student.last_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Classroom</label>
                  <select
                    required
                    value={formData.classroom_id}
                    onChange={(e) => setFormData({ ...formData, classroom_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  >
                    <option value="">Select a classroom</option>
                    {classrooms.map((classroom) => (
                      <option key={classroom.id} value={classroom.id}>
                        {classroom.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Academic Year</label>
                  <input
                    type="text"
                    value={formData.academic_year}
                    onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    placeholder="2024-2025"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Roll Number</label>
                  <input
                    type="number"
                    required
                    value={formData.roll_number}
                    onChange={(e) => setFormData({ ...formData, roll_number: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    placeholder="1"
                  />
                </div>
              </div>
              <div className="flex gap-3">
                <LoadingButton loading={loading} type="submit" className="bg-blue-600 hover:bg-blue-700">
                  Assign Student
                </LoadingButton>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 rounded-lg border border-slate-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Classrooms with Rosters */}
      <div className="grid gap-6">
        {classrooms.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center text-slate-500">
              No classrooms available. Create classrooms first.
            </CardContent>
          </Card>
        ) : (
          classrooms.map((classroom) => {
            const roster = getClassroomRoster(classroom.id);
            return (
              <Card key={classroom.id}>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900">{classroom.name}</h3>
                        <p className="text-sm text-slate-600">
                          <Users className="h-4 w-4 inline mr-1" />
                          {roster.length} students assigned
                        </p>
                      </div>
                      {classroom.teacher && (
                        <div className="text-right">
                          <p className="text-sm font-medium text-slate-700">Teacher</p>
                          <p className="text-sm text-slate-600">
                            {classroom.teacher.first_name} {classroom.teacher.last_name}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Roster Table */}
                    {roster.length > 0 && (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-slate-100">
                            <tr>
                              <th className="px-4 py-2 text-left">Roll #</th>
                              <th className="px-4 py-2 text-left">Student</th>
                              <th className="px-4 py-2 text-left">Academic Year</th>
                              <th className="px-4 py-2 text-center">Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {roster
                              .sort((a, b) => a.roll_number - b.roll_number)
                              .map((assignment) => (
                                <tr key={assignment.id} className="border-b hover:bg-slate-50">
                                  <td className="px-4 py-2">{assignment.roll_number}</td>
                                  <td className="px-4 py-2">
                                    {assignment.student.first_name} {assignment.student.last_name}
                                  </td>
                                  <td className="px-4 py-2">{assignment.academic_year}</td>
                                  <td className="px-4 py-2 text-center">
                                    <button
                                      onClick={() => handleRemoveAssignment(assignment.id)}
                                      className="p-1 text-red-600 hover:bg-red-50 rounded"
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </button>
                                  </td>
                                </tr>
                              ))}
                          </tbody>
                        </table>
                      </div>
                    )}

                    {roster.length === 0 && (
                      <p className="text-sm text-slate-500 italic">No students assigned yet</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
};

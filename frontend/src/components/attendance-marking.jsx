import React, { useState, useCallback } from 'react';
import { Check, X, AlertCircle, Save, RotateCcw } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

/**
 * Attendance Marking Component
 * Allows teachers to quickly mark student attendance for a class
 */
export const AttendanceMarking = ({
  classId,
  className,
  students = [],
  date = new Date().toISOString().split('T')[0],
  onSave,
  onCancel,
}) => {
  const [attendance, setAttendance] = useState(
    students.reduce((acc, student) => {
      acc[student.id] = 'unmarked';
      return acc;
    }, {})
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleMarkPresent = useCallback((studentId) => {
    setAttendance((prev) => ({
      ...prev,
      [studentId]: 'present',
    }));
  }, []);

  const handleMarkAbsent = useCallback((studentId) => {
    setAttendance((prev) => ({
      ...prev,
      [studentId]: 'absent',
    }));
  }, []);

  const handleMarkExcused = useCallback((studentId) => {
    setAttendance((prev) => ({
      ...prev,
      [studentId]: 'excused',
    }));
  }, []);

  const handleReset = useCallback(() => {
    setAttendance(
      students.reduce((acc, student) => {
        acc[student.id] = 'unmarked';
        return acc;
      }, {})
    );
    setError('');
  }, [students]);

  const handleSubmit = async () => {
    // Validate that all students are marked
    const unmarked = Object.entries(attendance).filter(([_, status]) => status === 'unmarked');
    if (unmarked.length > 0) {
      setError(`Please mark attendance for all ${unmarked.length} student(s)`);
      return;
    }

    setLoading(true);
    try {
      await onSave({
        classId,
        date,
        attendance,
      });
    } catch (err) {
      setError(err.message || 'Failed to save attendance');
    } finally {
      setLoading(false);
    }
  };

  const presentCount = Object.values(attendance).filter((s) => s === 'present').length;
  const absentCount = Object.values(attendance).filter((s) => s === 'absent').length;
  const excusedCount = Object.values(attendance).filter((s) => s === 'excused').length;
  const markedCount = presentCount + absentCount + excusedCount;

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Mark Attendance</CardTitle>
            <CardDescription>
              {className}  {date}
            </CardDescription>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-slate-600">
              {markedCount} of {students.length} marked
            </p>
            <div className="mt-2 flex gap-2">
              <Badge variant="success">{presentCount} Present</Badge>
              <Badge variant="error">{absentCount} Absent</Badge>
              <Badge variant="warning">{excusedCount} Excused</Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {error && (
          <div
            className="mb-4 flex items-center gap-2 rounded-md bg-red-50 p-3 text-sm text-red-700"
            role="alert"
            aria-live="polite"
          >
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        <div className="space-y-2">
          {students.map((student) => (
            <div
              key={student.id}
              className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 p-3 hover:bg-slate-100 transition-colors"
            >
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-900">{student.name}</p>
                <p className="text-xs text-slate-500">{student.studentId}</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleMarkPresent(student.id)}
                  className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                    attendance[student.id] === 'present'
                      ? 'bg-green-500 text-white'
                      : 'bg-white border border-slate-300 text-slate-700 hover:bg-green-50'
                  }`}
                  aria-pressed={attendance[student.id] === 'present'}
                  aria-label={`Mark ${student.name} present`}
                >
                  <Check size={16} />
                  <span className="hidden sm:inline">Present</span>
                </button>

                <button
                  onClick={() => handleMarkAbsent(student.id)}
                  className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                    attendance[student.id] === 'absent'
                      ? 'bg-red-500 text-white'
                      : 'bg-white border border-slate-300 text-slate-700 hover:bg-red-50'
                  }`}
                  aria-pressed={attendance[student.id] === 'absent'}
                  aria-label={`Mark ${student.name} absent`}
                >
                  <X size={16} />
                  <span className="hidden sm:inline">Absent</span>
                </button>

                <button
                  onClick={() => handleMarkExcused(student.id)}
                  className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                    attendance[student.id] === 'excused'
                      ? 'bg-amber-500 text-white'
                      : 'bg-white border border-slate-300 text-slate-700 hover:bg-amber-50'
                  }`}
                  aria-pressed={attendance[student.id] === 'excused'}
                  aria-label={`Mark ${student.name} excused`}
                >
                  <AlertCircle size={16} />
                  <span className="hidden sm:inline">Excused</span>
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex gap-3 justify-end">
          <Button
            variant="outline"
            onClick={handleReset}
            disabled={loading}
            aria-label="Reset attendance marks"
          >
            <RotateCcw size={16} className="mr-2" />
            Reset
          </Button>

          <Button
            onClick={handleSubmit}
            disabled={loading || markedCount === 0}
            aria-label="Save attendance"
          >
            {loading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Saving...
              </>
            ) : (
              <>
                <Save size={16} className="mr-2" />
                Save Attendance
              </>
            )}
          </Button>

          {onCancel && (
            <Button
              variant="ghost"
              onClick={onCancel}
              disabled={loading}
              aria-label="Cancel attendance marking"
            >
              Cancel
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Quick Attendance Toggle Component - For inline attendance marking
 */
export const QuickAttendanceToggle = ({ studentId, studentName, onToggle, defaultStatus = 'unmarked' }) => {
  const [status, setStatus] = useState(defaultStatus);

  const statuses = ['unmarked', 'present', 'absent', 'excused'];
  const statusColors = {
    unmarked: 'bg-slate-100 text-slate-600',
    present: 'bg-green-100 text-green-700',
    absent: 'bg-red-100 text-red-700',
    excused: 'bg-amber-100 text-amber-700',
  };

  const handleToggle = () => {
    const currentIndex = statuses.indexOf(status);
    const nextStatus = statuses[(currentIndex + 1) % statuses.length];
    setStatus(nextStatus);
    onToggle?.(studentId, nextStatus);
  };

  return (
    <button
      onClick={handleToggle}
      className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${statusColors[status]}`}
      aria-label={`${studentName} attendance status: ${status}`}
      title={`Click to cycle attendance status: ${statuses.join('  ')}`}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </button>
  );
};

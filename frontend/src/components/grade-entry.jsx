import React, { useState, useCallback } from 'react';
import { Save, RotateCcw, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/form';

/**
 * Grade Entry Component
 * Allows teachers to enter grades for students in a subject/assessment
 */
export const GradeEntry = ({
  assessmentId,
  assessmentName,
  subject,
  students = [],
  gradeScale = { min: 0, max: 100 },
  onSave,
  onCancel,
}) => {
  const [grades, setGrades] = useState(
    students.reduce((acc, student) => {
      acc[student.id] = '';
      return acc;
    }, {})
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGradeChange = useCallback((studentId, value) => {
    const numValue = parseFloat(value) || '';

    // Validate range
    if (numValue !== '' && (numValue < gradeScale.min || numValue > gradeScale.max)) {
      return;
    }

    setGrades((prev) => ({
      ...prev,
      [studentId]: value,
    }));
  }, [gradeScale]);

  const handleReset = useCallback(() => {
    setGrades(
      students.reduce((acc, student) => {
        acc[student.id] = '';
        return acc;
      }, {})
    );
    setError('');
  }, [students]);

  const handleSubmit = async () => {
    // Validate that all students have grades
    const missing = Object.entries(grades).filter(([_, grade]) => grade === '');
    if (missing.length > 0) {
      setError(`Please enter grades for all ${missing.length} student(s)`);
      return;
    }

    // Convert to numbers
    const gradesData = Object.entries(grades).reduce((acc, [studentId, grade]) => {
      acc[studentId] = parseFloat(grade);
      return acc;
    }, {});

    setLoading(true);
    try {
      await onSave({
        assessmentId,
        grades: gradesData,
      });
    } catch (err) {
      setError(err.message || 'Failed to save grades');
    } finally {
      setLoading(false);
    }
  };

  const entriedCount = Object.values(grades).filter((g) => g !== '').length;
  const average = entriedCount > 0
    ? (Object.values(grades).filter((g) => g !== '').reduce((a, b) => a + parseFloat(b), 0) / entriedCount).toFixed(1)
    : 0;

  // Determine grade letter/performance
  const getPerformanceLevel = (grade) => {
    if (!grade) return null;
    const num = parseFloat(grade);
    if (num >= 90) return 'Excellent';
    if (num >= 80) return 'Good';
    if (num >= 70) return 'Satisfactory';
    if (num >= 60) return 'Needs Support';
    return 'At Risk';
  };

  const performanceLevels = Object.entries(grades).reduce((acc, [_, grade]) => {
    const level = getPerformanceLevel(grade);
    if (level) acc[level] = (acc[level] || 0) + 1;
    return acc;
  }, {});

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Enter Grades</CardTitle>
            <CardDescription>
              {assessmentName}  {subject}
            </CardDescription>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium text-slate-600">
              {entriedCount} of {students.length} entered
            </p>
            {entriedCount > 0 && (
              <p className="mt-1 text-lg font-semibold text-brand-600">
                Average: {average}
              </p>
            )}
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

        {Object.keys(performanceLevels).length > 0 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {['Excellent', 'Good', 'Satisfactory', 'Needs Support', 'At Risk'].map((level) => {
              const count = performanceLevels[level] || 0;
              if (count === 0) return null;

              const colorMap = {
                Excellent: 'bg-green-100 text-green-700',
                Good: 'bg-blue-100 text-blue-700',
                Satisfactory: 'bg-amber-100 text-amber-700',
                'Needs Support': 'bg-orange-100 text-orange-700',
                'At Risk': 'bg-red-100 text-red-700',
              };

              return (
                <Badge key={level} className={colorMap[level]}>
                  {count} {level}
                </Badge>
              );
            })}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2 px-3 font-medium text-slate-600">Student</th>
                <th className="text-center py-2 px-3 font-medium text-slate-600">
                  Grade ({gradeScale.min}-{gradeScale.max})
                </th>
                <th className="text-center py-2 px-3 font-medium text-slate-600">Level</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => {
                const grade = grades[student.id];
                const level = getPerformanceLevel(grade);

                return (
                  <tr key={student.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-3 px-3">
                      <div className="text-slate-900 font-medium">{student.name}</div>
                      <div className="text-xs text-slate-500">{student.studentId}</div>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <Input
                        type="number"
                        min={gradeScale.min}
                        max={gradeScale.max}
                        step="0.5"
                        value={grade}
                        onChange={(e) => handleGradeChange(student.id, e.target.value)}
                        placeholder="0"
                        className="w-20 text-center"
                        aria-label={`Grade for ${student.name}`}
                      />
                    </td>
                    <td className="py-3 px-3 text-center">
                      {level ? (
                        <Badge
                          className={
                            {
                              Excellent: 'bg-green-100 text-green-700',
                              Good: 'bg-blue-100 text-blue-700',
                              Satisfactory: 'bg-amber-100 text-amber-700',
                              'Needs Support': 'bg-orange-100 text-orange-700',
                              'At Risk': 'bg-red-100 text-red-700',
                            }[level]
                          }
                        >
                          {level}
                        </Badge>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="mt-6 flex gap-3 justify-end">
          <Button
            variant="outline"
            onClick={handleReset}
            disabled={loading}
            aria-label="Reset all grades"
          >
            <RotateCcw size={16} className="mr-2" />
            Reset
          </Button>

          <Button
            onClick={handleSubmit}
            disabled={loading || entriedCount === 0}
            aria-label="Save grades"
          >
            {loading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Saving...
              </>
            ) : (
              <>
                <Save size={16} className="mr-2" />
                Save Grades
              </>
            )}
          </Button>

          {onCancel && (
            <Button
              variant="ghost"
              onClick={onCancel}
              disabled={loading}
              aria-label="Cancel grade entry"
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
 * Inline Grade Editor Component
 */
export const InlineGradeEditor = ({ studentId, studentName, onSave, initialGrade = '', maxGrade = 100 }) => {
  const [grade, setGrade] = useState(initialGrade);
  const [editing, setEditing] = useState(false);

  const handleSave = async () => {
    await onSave?.(studentId, grade);
    setEditing(false);
  };

  if (!editing) {
    return (
      <button
        onClick={() => setEditing(true)}
        className="px-3 py-1.5 rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors text-sm font-medium"
        aria-label={`Grade for ${studentName}: ${grade || 'Not entered'}`}
      >
        {grade || 'Enter Grade'}
      </button>
    );
  }

  return (
    <div className="flex gap-2 items-center">
      <Input
        type="number"
        value={grade}
        onChange={(e) => setGrade(e.target.value)}
        min="0"
        max={maxGrade}
        step="0.5"
        className="w-20 text-center"
        autoFocus
        aria-label={`Enter grade for ${studentName}`}
      />
      <button
        onClick={handleSave}
        className="px-2 py-1.5 rounded-md bg-green-500 text-white hover:bg-green-600 text-sm font-medium"
        aria-label="Save grade"
      >
        <Check size={16} />
      </button>
      <button
        onClick={() => {
          setGrade(initialGrade);
          setEditing(false);
        }}
        className="px-2 py-1.5 rounded-md bg-slate-300 text-slate-700 hover:bg-slate-400 text-sm font-medium"
        aria-label="Cancel editing"
      >
        <X size={16} />
      </button>
    </div>
  );
};

import { Check, X } from 'lucide-react';

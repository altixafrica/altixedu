import React, { useEffect, useMemo, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  BookOpen,
  GraduationCap,
  Loader2,
  MessageSquare,
  Search,
  Sparkles,
  TrendingUp,
  Users,
} from 'lucide-react';

import { WorkspaceShell } from '../components/workspace-shell';
import { StatCard } from '../components/stat-card';
import { Alert, Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { getCurrentUser, getStoredSession } from '../lib/django';
import { getDashboardByRole } from '../lib/api-service';
import { formatDate } from '../lib/format';
import { useAuth } from '../lib/hooks';

const RiskBadge = ({ level }) => {
  const variants = {
    LOW: 'success',
    MEDIUM: 'warning',
    HIGH: 'error',
  };

  return <Badge variant={variants[level] || 'default'}>{level}</Badge>;
};

const SectionCard = ({ title, description, children, className = '' }) => (
  <Card className={className}>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      {description ? <CardDescription>{description}</CardDescription> : null}
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

export const TeacherDashboardPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [session, setSession] = useState(() => getStoredSession());
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedClassroom, setSelectedClassroom] = useState(null);
  const [searchStudent, setSearchStudent] = useState('');

  useEffect(() => {
    if (!isAuthenticated) return;

    const load = async () => {
      setLoading(true);
      setError('');

      try {
        const current = await getCurrentUser();
        const activeSession = current || getStoredSession();

        if (!activeSession?.role) {
          setError('Unable to determine the current user role.');
          return;
        }

        if (activeSession.role !== 'teacher') {
          navigate(`/app/${activeSession.role}`);
          return;
        }

        setSession(activeSession);
        const payload = await getDashboardByRole.teacher();
        setDashboardData(payload);

        if (payload?.classrooms?.length) {
          setSelectedClassroom(payload.classrooms[0].id);
        }
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.response?.data?.detail ||
          'Unable to load the teaching workspace right now.'
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated, navigate]);

  const summary = dashboardData?.summary || {};
  const classrooms = dashboardData?.classrooms || [];
  const allStudents = dashboardData?.students || [];
  const aiWatchlist = dashboardData?.ai_watchlist || [];
  const recentMessages = dashboardData?.recent_messages || [];
  const subjectAssignments = dashboardData?.subject_assignments || [];

  const currentClassroom = classrooms.find((classroom) => classroom.id === selectedClassroom) || classrooms[0];
  const classroomStudents = currentClassroom
    ? allStudents.filter((student) => student.classroom === currentClassroom.name)
    : [];
  const filteredStudents = classroomStudents.filter((student) =>
    `${student.first_name} ${student.last_name}`.toLowerCase().includes(searchStudent.toLowerCase())
  );

  const statCards = useMemo(
    () => [
      {
        label: 'Students',
        value: summary.students_count || 0,
        detail: 'Learners in active teaching groups',
        icon: <Users className="h-5 w-5" />,
      },
      {
        label: 'Classrooms',
        value: summary.classrooms_count || 0,
        detail: 'Teaching groups under your care',
        icon: <BookOpen className="h-5 w-5" />,
      },
      {
        label: 'At-risk students',
        value: summary.at_risk_students || 0,
        detail: 'Flagged for intervention this week',
        icon: <Sparkles className="h-5 w-5" />,
        tone: 'dark',
      },
      {
        label: 'Unread messages',
        value: summary.unread_messages || 0,
        detail: 'Parent and staff communication',
        icon: <MessageSquare className="h-5 w-5" />,
      },
    ],
    [summary]
  );

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return (
    <WorkspaceShell
      session={session}
      role="teacher"
      currentNav="dashboard"
      eyebrow="Teacher Workspace"
      title="Instruction, interventions, and classroom rhythm"
      description="Move between watchlist students, teaching assignments, and communication without losing context."
      actions={
        <>
          <Button variant="secondary">Mark attendance</Button>
          <Button variant="primary">Enter grades</Button>
        </>
      }
    >
      {loading ? (
        <div className="flex min-h-[320px] items-center justify-center">
          <div className="flex items-center gap-3 rounded-full bg-slate-950 px-5 py-3 text-white">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm font-medium">Loading teaching workspace...</span>
          </div>
        </div>
      ) : error ? (
        <Alert variant="error">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <div>
              <p className="font-medium">Teacher dashboard error</p>
              <p className="mt-1 text-sm">{error}</p>
            </div>
          </div>
        </Alert>
      ) : (
        <div className="space-y-8">
          <div className="grid gap-4 xl:grid-cols-4">
            {statCards.map((card) => (
              <StatCard key={card.label} {...card} />
            ))}
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <div className="space-y-6">
              <SectionCard title="Classroom coverage" description="Switch teaching groups and review student attention signals.">
                <div className="grid gap-3 md:grid-cols-2">
                  {classrooms.map((classroom) => (
                    <button
                      key={classroom.id}
                      type="button"
                      onClick={() => {
                        setSelectedClassroom(classroom.id);
                        setSearchStudent('');
                      }}
                      className={`rounded-[22px] border px-4 py-4 text-left transition ${
                        currentClassroom?.id === classroom.id
                          ? 'border-slate-950 bg-slate-950 text-white'
                          : 'border-slate-200 bg-slate-50 text-slate-950 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-medium">{classroom.name}</p>
                          <p className={`mt-1 text-sm ${currentClassroom?.id === classroom.id ? 'text-white/70' : 'text-slate-500'}`}>
                            Grade {classroom.grade_level || 'N/A'} · {classroom.student_count || 0} students
                          </p>
                        </div>
                        {classroom.is_class_teacher ? (
                          <Badge className={currentClassroom?.id === classroom.id ? 'bg-white text-slate-950' : ''}>
                            Class teacher
                          </Badge>
                        ) : null}
                      </div>
                    </button>
                  ))}
                </div>
              </SectionCard>

              <SectionCard
                title={currentClassroom ? `Students in ${currentClassroom.name}` : 'Students'}
                description="Search, scan attendance posture, and identify learners who need faster follow-up."
              >
                <div className="relative">
                  <Search className="pointer-events-none absolute left-4 top-3.5 h-4 w-4 text-slate-400" />
                  <Input
                    value={searchStudent}
                    onChange={(event) => setSearchStudent(event.target.value)}
                    className="h-12 rounded-2xl pl-11"
                    placeholder="Search students by name"
                  />
                </div>

                <div className="mt-5 space-y-3">
                  {filteredStudents.length > 0 ? (
                    filteredStudents.slice(0, 16).map((student) => {
                      const watchlistItem = aiWatchlist.find((entry) => entry.student_id === student.id);
                      return (
                        <div
                          key={student.id}
                          className="flex flex-col gap-4 rounded-[24px] border border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between"
                        >
                          <div>
                            <p className="font-medium text-slate-950">
                              {student.first_name} {student.last_name}
                            </p>
                            <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-slate-500">
                              <span>{student.admission_number}</span>
                              <span>{Math.round(student.attendance_percentage || 0)}% attendance</span>
                              <span>Avg {student.average_grade?.toFixed?.(1) || 'N/A'}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {watchlistItem ? <RiskBadge level={watchlistItem.risk_level} /> : <Badge variant="success">Stable</Badge>}
                            <Button variant="secondary" size="sm">View learner</Button>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <p className="text-sm text-slate-500">No students match this search for the selected classroom.</p>
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Subject assignments" description="Current teaching load across classrooms and subjects.">
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[620px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left">
                        <th className="pb-3 font-medium text-slate-500">Subject</th>
                        <th className="pb-3 font-medium text-slate-500">Classroom</th>
                        <th className="pb-3 font-medium text-slate-500">Grade</th>
                      </tr>
                    </thead>
                    <tbody>
                      {subjectAssignments.slice(0, 12).map((assignment, index) => (
                        <tr key={`${assignment.subject_code}-${assignment.classroom_name}-${index}`} className="border-b border-slate-100">
                          <td className="py-4">
                            <p className="font-medium text-slate-950">{assignment.subject_name}</p>
                            <p className="mt-1 text-xs text-slate-500">{assignment.subject_code}</p>
                          </td>
                          <td className="py-4 text-slate-600">{assignment.classroom_name}</td>
                          <td className="py-4 text-slate-600">Grade {assignment.grade_level}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </SectionCard>
            </div>

            <div className="space-y-6">
              <SectionCard title="Intervention queue" description="Learners showing attendance or performance risk.">
                <div className="space-y-3">
                  {aiWatchlist.length > 0 ? (
                    aiWatchlist.slice(0, 8).map((student) => (
                      <div key={student.student_id} className="rounded-[22px] border border-amber-200 bg-amber-50 px-4 py-4">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="font-medium text-slate-950">{student.student_name}</p>
                            <p className="mt-1 text-sm text-slate-500">{student.classroom}</p>
                          </div>
                          <RiskBadge level={student.risk_level} />
                        </div>
                        <div className="mt-4 space-y-2 text-sm text-slate-600">
                          <div className="flex items-center justify-between">
                            <span>Attendance risk</span>
                            <span className="font-medium text-slate-950">{Math.round((student.attendance_risk || 0) * 100)}%</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span>Performance risk</span>
                            <span className="font-medium text-slate-950">{Math.round((student.performance_risk || 0) * 100)}%</span>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">No watchlist students are flagged right now.</p>
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Recent messages" description="Latest parent and staff communication.">
                <div className="space-y-3">
                  {recentMessages.length > 0 ? (
                    recentMessages.slice(0, 6).map((message) => (
                      <div key={message.id} className="rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-4">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="font-medium text-slate-950">{message.counterpart_name}</p>
                            {message.student_name ? (
                              <p className="mt-1 text-xs uppercase tracking-[0.12em] text-slate-500">
                                {message.student_name}
                              </p>
                            ) : null}
                          </div>
                          <p className="text-xs text-slate-500">{formatDate(message.sent_at)}</p>
                        </div>
                        <p className="mt-3 text-sm leading-6 text-slate-600">{message.content}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">There are no recent messages yet.</p>
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Quick rhythm" description="Keep common teaching actions in easy reach.">
                <div className="space-y-3">
                  <Button fullWidth variant="primary">
                    <GraduationCap className="h-4 w-4" />
                    Enter assessment scores
                  </Button>
                  <Button fullWidth variant="secondary">
                    <Users className="h-4 w-4" />
                    Review family follow-up
                  </Button>
                  <Button fullWidth variant="secondary">
                    <TrendingUp className="h-4 w-4" />
                    Refresh student watchlist
                  </Button>
                </div>
              </SectionCard>
            </div>
          </div>
        </div>
      )}
    </WorkspaceShell>
  );
};

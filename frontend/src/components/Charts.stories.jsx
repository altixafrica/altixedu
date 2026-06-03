import { EnrollmentTrendChart, AttendanceChart, RevenueTrendChart, GradeDistributionChart } from '../charts';

export default {
  title: 'Components/Charts',
  tags: ['autodocs'],
};

// Sample data for enrollment trends
const enrollmentData = [
  { month: 'Jan', students: 450 },
  { month: 'Feb', students: 480 },
  { month: 'Mar', students: 520 },
  { month: 'Apr', students: 550 },
  { month: 'May', students: 600 },
  { month: 'Jun', students: 620 },
];

export const EnrollmentTrend = {
  render: () => <EnrollmentTrendChart data={enrollmentData} />,
};

// Sample data for attendance
const attendanceData = [
  { class: 'JSS1A', present: 92, absent: 8 },
  { class: 'JSS1B', present: 88, absent: 12 },
  { class: 'SSS3A', present: 95, absent: 5 },
  { class: 'SSS3B', present: 90, absent: 10 },
];

export const Attendance = {
  render: () => <AttendanceChart data={attendanceData} />,
};

// Sample data for revenue
const revenueData = [
  { month: 'Jan', revenue: 250000, target: 300000 },
  { month: 'Feb', revenue: 280000, target: 300000 },
  { month: 'Mar', revenue: 320000, target: 300000 },
  { month: 'Apr', revenue: 310000, target: 350000 },
  { month: 'May', revenue: 350000, target: 350000 },
  { month: 'Jun', revenue: 380000, target: 400000 },
];

export const RevenueTrend = {
  render: () => <RevenueTrendChart data={revenueData} />,
};

// Sample data for grades
const gradeData = [
  { name: 'A', value: 35 },
  { name: 'B', value: 48 },
  { name: 'C', value: 42 },
  { name: 'D', value: 25 },
];

export const GradeDistribution = {
  render: () => <GradeDistributionChart data={gradeData} />,
};

export const EmptyChart = {
  render: () => <EnrollmentTrendChart data={[]} />,
};

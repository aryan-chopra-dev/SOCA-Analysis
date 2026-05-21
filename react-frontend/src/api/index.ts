import axios from 'axios';

const API_BASE_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8000';
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface StudentProfile {
  name: string;
  current_level: string;
  target_attempt: string;
}

export interface SubjectAcademicData {
  score: number;
  weak_topics: string[];
  completed: string[];
  partial: string[];
  topic_details: Record<string, {
    confidence: string;
    workflow_stages: string[];
  }>;
}

export interface AcademicData {
  Physics: SubjectAcademicData;
  Chemistry: SubjectAcademicData;
  Mathematics: SubjectAcademicData;
}

export interface BehaviorData {
  time_management_category: string;
  revision_category: string;
  problem_solving_category: string;
  mock_test_frequency: string;
  study_techniques: string[];
  resources: string[];
  short_answer_blocker: string;
}

export interface Question {
  question: string;
  difficulty: 'easy' | 'medium' | 'hard';
  type: string;
  options: string[];
  correct_answer: string;
  explanation: string;
  estimated_time_seconds: number;
  source: string;
}

export interface QuestionSet {
  subject: string;
  topic: string;
  questions: Question[];
}

export interface DiagnosticAttempt {
  answers: string[];
  time_taken_seconds: number[];
}

export interface QuestionnairePayload {
  student: StudentProfile;
  academic: {
    physics_proficiency: number;
    chemistry_proficiency: number;
    math_proficiency: number;
    weak_topics: string[];
  };
  behavior: {
    weekly_hours: number;
    time_management_rating: number;
    revision_days_per_week: number;
    problem_solving_rating: number;
    mock_test_frequency: string;
    mock_anxiety_rating: number;
    sleep_quality_rating: number;
    study_techniques: string[];
    resources: string[];
    confidence_rating: number;
    short_answer_blocker: string;
  };
  topic_tracking: Record<string, {
    completed: string[];
    partial: string[];
    untouched: string[];
    topic_details: Record<string, {
      confidence: string;
      workflow_stages: string[];
    }>;
  }>;
  diagnostic_tests: Record<string, QuestionSet>;
  diagnostic_attempts: Record<string, DiagnosticAttempt>;
  metadata?: {
    created_at: string;
  };
}

// Fetch all topics
export const getTopics = async (): Promise<Record<string, string[]>> => {
  const response = await api.get('/topics');
  return response.data;
};

// Generate questions for a topic
export const getQuestions = async (subject: string, topic: string): Promise<QuestionSet> => {
  const response = await api.get('/questions', { params: { subject, topic } });
  return response.data;
};

// Fetch sample data and pre-computed report
export const getSample = async (): Promise<{ response: any; report: any }> => {
  const response = await api.get('/sample');
  return response.data;
};

// Submit complete response and run pipeline
export const submitQuestionnaire = async (payload: QuestionnairePayload): Promise<any> => {
  const response = await api.post('/evaluate', { data: payload });
  return response.data;
};

// Submit feedback
export const submitFeedback = async (feedbackData: {
  student_name: string;
  feedback: string;
  rating: number;
  metadata?: any;
}): Promise<any> => {
  const response = await api.post('/feedback', feedbackData);
  return response.data;
};

// Download PDF report
export const downloadPdf = async (report: any, studentName: string): Promise<void> => {
  const response = await api.post('/pdf', report, { responseType: 'blob' });
  const blob = new Blob([response.data], { type: 'application/pdf' });
  const link = document.createElement('a');
  link.href = window.URL.createObjectURL(blob);
  link.download = `soca_report_${studentName.toLowerCase().replace(/\s+/g, '_')}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export default api;

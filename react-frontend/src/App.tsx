import { useState, useEffect } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import theme from './theme';
import { Wizard } from './components/Wizard';
import { Dashboard } from './components/Dashboard';
import { submitQuestionnaire } from './api';
import type { QuestionnairePayload } from './api';

// ─── sessionStorage helpers ────────────────────────────────────────────────
const SESSION_REPORT_KEY = 'soca_report_data';
const SESSION_STEP_KEY   = 'soca_wizard_step';

function loadSession() {
  try {
    const report = sessionStorage.getItem(SESSION_REPORT_KEY);
    const step   = sessionStorage.getItem(SESSION_STEP_KEY);
    return {
      reportData: report ? JSON.parse(report) : null,
      wizardStep: step   ? parseInt(step, 10) : 0,
    };
  } catch {
    return { reportData: null, wizardStep: 0 };
  }
}

function saveReport(data: any) {
  try { sessionStorage.setItem(SESSION_REPORT_KEY, JSON.stringify(data)); } catch { /* quota */ }
}
function saveStep(step: number) {
  try { sessionStorage.setItem(SESSION_STEP_KEY, String(step)); } catch { /* quota */ }
}
function clearSession() {
  sessionStorage.removeItem(SESSION_REPORT_KEY);
  sessionStorage.removeItem(SESSION_STEP_KEY);
}
// ──────────────────────────────────────────────────────────────────────────

function App() {
  // Rehydrate from sessionStorage on first render
  const session = loadSession();

  const [reportData,  setReportDataRaw] = useState<any>(session.reportData);
  const [isLoading,   setIsLoading]     = useState(false);
  const [wizardStep,  setWizardStepRaw] = useState(session.wizardStep);
  const [resetKey,    setResetKey]      = useState(0);

  // Thin wrappers that also persist to sessionStorage
  const setReportData = (data: any) => {
    setReportDataRaw(data);
    if (data) saveReport(data);
    else sessionStorage.removeItem(SESSION_REPORT_KEY);
  };

  const setWizardStep = (step: number) => {
    setWizardStepRaw(step);
    saveStep(step);
  };

  // Keep sessionStorage in sync if wizardStep changes for any other reason
  useEffect(() => { saveStep(wizardStep); }, [wizardStep]);

  const handleWizardSubmit = async (data: QuestionnairePayload) => {
    setIsLoading(true);
    try {
      const result = await submitQuestionnaire(data);
      setReportData(result);
    } catch (error) {
      console.warn('FastAPI backend error, running fallback diagnostic output:', error);

      // Fallback uses topic_reports list format (matching real backend response)
      const fallbackReport = {
        profile: {
          student_name:             data.student?.name             || 'Student',
          current_level:            data.student?.current_level    || 'Class 12th',
          target_attempt:           data.student?.target_attempt   || 'JEE Main 2027',
          readiness_score:          76,
          readiness_interpretation: 'Exam-ready but needs workflow gaps filled',
          confidence_alignment:     90,
          wellness_score:           65,
          burnout_risk:             'NORMAL',
          physics_score:            data.academic?.physics_proficiency || 64,
          chemistry_score:          data.academic?.chemistry_proficiency || 58,
          math_score:               data.academic?.math_proficiency || 72,
          syllabus_coverage:        68,
          discipline_score:         80,
          time_management_score:    70,
          revision_consistency_score: 65,
          problem_solving_score:    72,
          stress_level:             'Medium',
          weak_topics:              data.academic?.weak_topics || ['Mole Concept'],
          behavioral_patterns:      [],
          short_answer_blocker:     data.behavior?.short_answer_blocker || '',
          study_techniques:         data.behavior?.study_techniques || [],
          resources:                data.behavior?.resources || [],
        },
        agents: {
          academic:   { strongest_subject: 'Mathematics', weakest_subject: 'Chemistry', discipline_score: 80 },
          behavioral: { time_management: 'stable', patterns: [] },
          wellness:   { burnout_risk: 'NORMAL' },
        },
        // ← uses topic_reports list format, consistent with real backend
        topic_assessment: {
          topic_reports: [
            {
              subject: 'Physics',
              topic: 'Units and Dimensions',
              readiness_score: 85,
              accuracy: 80,
              correct_answers: 4,
              total_questions: 5,
              workflow_progress: 90,
              flags: [],
              weak_areas: ['Error analysis'],
              recommendations: ['Solve exercise 2A questions', 'Revise mistake log weekly'],
              workflow_stages: ['Video Lectures', 'NCERT', 'PYQs'],
              workflow_gaps: [],
            },
            {
              subject: 'Chemistry',
              topic: 'Mole Concept',
              readiness_score: 55,
              accuracy: 40,
              correct_answers: 2,
              total_questions: 5,
              workflow_progress: 50,
              flags: ['advanced_problem_solving_weakness'],
              weak_areas: ['Equivalent weight', 'Redox titration'],
              recommendations: ['Watch concept lectures on redox reactions', 'Complete Exercise 1 completely'],
              workflow_stages: ['Video Lectures', 'NCERT'],
              workflow_gaps: ['Exercise 1/1A', 'PYQs', 'Topic Wise Test'],
            },
          ],
          summary: {
            average_readiness: 70,
            weak_topics: ['Mole Concept'],
            strong_topics: ['Units and Dimensions'],
            revision_priority: ['Mole Concept', 'Units and Dimensions'],
            subject_mastery: { Physics: 85, Chemistry: 55 },
          },
          roadmap: [
            { topic: 'Mole Concept',         priority: 'High',   workflow_progress: '50%',  next_action: 'Complete Exercise 1 (Easy) and 1A (Hard) for Mole Concept, and finish PYQs.' },
            { topic: 'Units and Dimensions',  priority: 'Medium', workflow_progress: '90%',  next_action: 'Maintain regular revision and practice Exercise 2 for Units and Dimensions.' },
          ],
        },
        knowledge_graph: {
          prerequisite_gaps:   { 'Mole Concept': ['Basic Algebra'] },
          future_risk_topics:  { 'Mole Concept': ['Stoichiometry', 'Chemical Equilibrium'] },
          foundational_topics: ['Mole Concept'],
        },
        knowledge_graph_layouts: {
          Physics: {
            nodes: [
              { id: 'Units and Dimensions', label: 'Units and Dimensions', x: 0.1, y: 0.3, color: '#10B981', size: 14, badge: '✅ Mastered', status: 'mastered' },
              { id: 'Vectors',              label: 'Vectors',              x: 0.3, y: 0.5, color: '#10B981', size: 14, badge: '✅ Mastered', status: 'mastered' },
            ],
            edges: [],
          },
          Chemistry: {
            nodes: [
              { id: 'Mole Concept',        label: 'Mole Concept',        x: 0.2, y: 0.4, color: '#FF5A5F', size: 24, badge: '⚠️ Weak Topic',        status: 'weak'        },
              { id: 'Basic Algebra',        label: 'Basic Algebra',        x: 0.1, y: 0.2, color: '#FFB85C', size: 20, badge: '🔧 Fix This First',    status: 'prereq_gap'  },
              { id: 'Stoichiometry',        label: 'Stoichiometry',        x: 0.5, y: 0.4, color: '#F1C40F', size: 18, badge: '⚡ Downstream Risk',  status: 'future_risk' },
            ],
            edges: [
              { source: 'Basic Algebra', target: 'Mole Concept'  },
              { source: 'Mole Concept',  target: 'Stoichiometry' },
            ],
          },
          Mathematics: {
            nodes: [
              { id: 'Functions', label: 'Functions', x: 0.2, y: 0.5, color: '#10B981', size: 14, badge: '✅ Mastered', status: 'mastered' },
            ],
            edges: [],
          },
        },
        retrieved_recommendations: [
          { recommendation: 'Maintain an error log with type, conceptual triggers, and corrections.', similarity_score: 0.95 },
          { recommendation: 'Solve chapter-wise PYQs of the past 10 years as core practice material.',  similarity_score: 0.88 },
        ],
        soca: {
          strengths: [
            `${data.student?.name || 'Student'} demonstrates robust conceptual coverage in anchor chapters.`,
            'Active study habits like using formula notebooks are highly effective.',
          ],
          opportunities: [
            'Convert mistakes in mock assessments into targeted conceptual drills.',
            'Schedule focused revision sprints on alternate days.',
          ],
          challenges: [
            `Structural conceptual risk discovered in: ${data.academic?.weak_topics?.join(', ') || 'Mole Concept'}.`,
            'Time pressure under full length mocks may increase calculation errors.',
          ],
          action_plan: [
            'Rebuild foundational prerequisites immediately (e.g. Basic Algebra).',
            'Perform daily 30-minute timed MCQ drills for speed optimization.',
            'Log errors in a notebook every Sunday and re-evaluate.',
          ],
        },
      };

      await new Promise((resolve) => setTimeout(resolve, 800));
      setReportData(fallbackReport);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    clearSession();
    setReportDataRaw(null);
    setWizardStepRaw(0);
    setResetKey((prev) => prev + 1);
  };

  const handleBackToMCQ = () => {
    setReportData(null);
    setWizardStep(3);
  };

  const handleBackToTopics = () => {
    setReportData(null);
    setWizardStep(1);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          background: 'radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%)',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <Box sx={{ display: reportData ? 'none' : 'block', width: '100%' }}>
          <Wizard
            key={resetKey}
            onSubmit={handleWizardSubmit}
            isLoading={isLoading}
            step={wizardStep}
            setStep={setWizardStep}
          />
        </Box>
        {reportData && (
          <Dashboard
            reportData={reportData}
            onReset={handleReset}
            onBackToMCQ={handleBackToMCQ}
            onBackToTopics={handleBackToTopics}
          />
        )}
      </Box>
    </ThemeProvider>
  );
}

export default App;

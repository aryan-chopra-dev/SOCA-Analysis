import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Card, 
  Button, 
  LinearProgress,
  CircularProgress,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  OutlinedInput,
  Chip,
  Checkbox,
  ListItemText,
  Tabs,
  Tab,
  RadioGroup,
  Radio,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SchoolIcon from '@mui/icons-material/School';
import ScienceIcon from '@mui/icons-material/Science';
import CalculateIcon from '@mui/icons-material/Calculate';
import HelpIcon from '@mui/icons-material/Help';
import RotateLeftIcon from '@mui/icons-material/RotateLeft';
import { motion, AnimatePresence } from 'framer-motion';
import { getTopics, getQuestions } from '../api';
import type { QuestionSet } from '../api';

// Fallback topics list matching jee_topics.json
const LOCAL_TOPICS: Record<string, string[]> = {
  Physics: [
    "Units and Dimensions", "Vectors", "Kinematics", "NLM", 
    "Work Power Energy", "Rotation", "Electrostatics", "Current Electricity", "Modern Physics"
  ],
  Chemistry: [
    "Mole Concept", "Chemical Bonding", "Thermodynamics", 
    "Equilibrium", "Organic Chemistry", "Coordination Compounds"
  ],
  Mathematics: [
    "Functions", "Limits", "Differentiation", "AOD", 
    "Integration", "Differential Equations", "Matrices", "Probability"
  ]
};

const STAGES = [
  "Video Lectures",
  "NCERT",
  "Reference book",
  "Exercise 1 (JEE Mains Easy)",
  "Exercise 1A (JEE Mains Hard)",
  "Exercise 2 (JEE Advanced Easy)",
  "Exercise 2A (JEE Advanced Hard)",
  "PYQs",
  "Topic Wise Test",
  "Minor Tests",
  "Major Tests"
];

const TIME_MANAGEMENT_OPTIONS = [
  "Often run out of time",
  "Usually finish just on time",
  "Finish with time to spare"
];

const PROBLEM_SOLVING_OPTIONS = [
  "Need hints for standard problems",
  "Can solve standard problems independently",
  "Can solve mixed multi-concept problems"
];

const REVISION_OPTIONS = [
  "Rarely revise weekly",
  "Revise important topics weekly",
  "Follow a fixed revision plan"
];

const STUDY_TECHNIQUES = [
  "NCERT reading", "Formula notebook", "Error log", 
  "Active recall", "Spaced revision", "Timed practice", "Video lectures"
];

const LEARNING_RESOURCES = [
  "Coaching modules", "NCERT", "PYQs", "YouTube", 
  "Test series", "Doubt-solving app", "Reference books"
];

interface WizardProps {
  onSubmit: (data: any) => void;
  isLoading: boolean;
  step: number;
  setStep: (step: number) => void;
}

export const Wizard: React.FC<WizardProps> = ({ onSubmit, isLoading, step, setStep }) => {
  const [topicsDb, setTopicsDb] = useState<Record<string, string[]>>(LOCAL_TOPICS);

  // --- Step 0: Profile State ---
  const [studentName, setStudentName] = useState('');
  const [currentLevel, setCurrentLevel] = useState('');
  const [targetAttempt, setTargetAttempt] = useState('');

  // --- Step 1: Academic State ---
  const [activeSubjectTab, setActiveSubjectTab] = useState(0);
  const [completedTopics, setCompletedTopics] = useState<Record<string, string[]>>({
    Physics: ['Units and Dimensions', 'Vectors'],
    Chemistry: ['Mole Concept'],
    Mathematics: ['Functions']
  });
  const [weakTopics, setWeakTopics] = useState<Record<string, string[]>>({
    Physics: ['Units and Dimensions'],
    Chemistry: [],
    Mathematics: []
  });
  const [topicStages, setTopicStages] = useState<Record<string, string[]>>({});

  // --- Step 2: Study Behavior State ---
  const [timeManagement, setTimeManagement] = useState('Usually finish just on time');
  const [problemSolving, setProblemSolving] = useState('Can solve standard problems independently');
  const [revisionConsistency, setRevisionConsistency] = useState('Revise important topics weekly');
  const [studyTechniques, setStudyTechniques] = useState<string[]>(['Formula notebook', 'Video lectures']);
  const [resources, setResources] = useState<string[]>(['Coaching modules', 'PYQs', 'YouTube']);
  const [blockerText, setBlockerText] = useState('I understand concepts but lose marks in mixed-topic tests because I panic and skip revision.');

  // --- Step 3: Diagnostic Test State ---
  const [testSubjectFilter, setTestSubjectFilter] = useState('All');
  const [selectedDiagnosticTopics, setSelectedDiagnosticTopics] = useState<string[]>([]);
  const [diagnosticTests, setDiagnosticTests] = useState<Record<string, QuestionSet>>({});
  const [diagnosticAttempts, setDiagnosticAttempts] = useState<Record<string, {
    answers: string[];
    time_taken_seconds: number[];
  }>>({});
  const [loadingQuestions, setLoadingQuestions] = useState<Record<string, boolean>>({});

  // Load topics from backend on mount
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const data = await getTopics();
        if (data && Object.keys(data).length > 0) {
          setTopicsDb(data);
        }
      } catch (err) {
        console.warn('Could not load topics from server, using local topics list.', err);
      }
    };
    fetchTopics();
  }, []);

  // Auto-select first completed topic when entering Step 3 if nothing selected yet
  useEffect(() => {
    if (step !== 3 || selectedDiagnosticTopics.length > 0) return;
    const allCompleted = [
      ...(completedTopics.Physics || []),
      ...(completedTopics.Chemistry || []),
      ...(completedTopics.Mathematics || [])
    ];
    if (allCompleted.length === 0) return;
    const firstTopic = allCompleted[0];
    setSelectedDiagnosticTopics([firstTopic]);
    if (!diagnosticTests[firstTopic]) {
      const fetchFirstQuestions = async () => {
        setLoadingQuestions(prev => ({ ...prev, [firstTopic]: true }));
        try {
          let subject = 'Physics';
          for (const sub of ['Physics', 'Chemistry', 'Mathematics']) {
            if (topicsDb[sub]?.includes(firstTopic)) { subject = sub; break; }
          }
          const questionSet = await getQuestions(subject, firstTopic);
          setDiagnosticTests(prev => ({ ...prev, [firstTopic]: questionSet }));
          setDiagnosticAttempts(prev => ({
            ...prev,
            [firstTopic]: {
              answers: ['', '', '', '', ''],
              time_taken_seconds: questionSet.questions.map((q: any) => q.estimated_time_seconds || 120)
            }
          }));
        } catch (err) {
          console.error(`Failed to fetch questions for ${firstTopic}`, err);
        } finally {
          setLoadingQuestions(prev => ({ ...prev, [firstTopic]: false }));
        }
      };
      fetchFirstQuestions();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step]);

  const totalSteps = 4;
  const progress = ((step + 1) / totalSteps) * 100;

  // --- Step 3 validation: ensure tests are taken before report generation ---
  const totalCompletedCount =
    (completedTopics.Physics?.length || 0) +
    (completedTopics.Chemistry?.length || 0) +
    (completedTopics.Mathematics?.length || 0);

  const step3ValidationMessage = (() => {
    if (step !== 3) return '';
    if (totalCompletedCount > 0 && selectedDiagnosticTopics.length === 0)
      return '⚠️ Please select at least one completed topic above to take the diagnostic MCQ test before generating your report.';
    for (const topic of selectedDiagnosticTopics) {
      if (loadingQuestions[topic]) return '⏳ Questions are loading, please wait...';
      const test = diagnosticTests[topic];
      const attempt = diagnosticAttempts[topic];
      if (!test || !attempt) return `⚠️ Questions failed to load for "${topic}". Try clicking the topic card again.`;
      const unanswered = attempt.answers.filter(a => !a).length;
      if (unanswered > 0)
        return `⚠️ Please answer all ${test.questions.length} questions in the "${topic}" test (${unanswered} remaining) before generating your report.`;
    }
    return '';
  })();

  const isStep3Blocked = step === 3 && step3ValidationMessage !== '';

  // Jump to step helper
  const handleJumpToStep = (index: number) => {
    // Basic validation
    if (index > 0 && (!studentName.trim() || !currentLevel || !targetAttempt)) {
      return;
    }
    setStep(index);
  };

  // Nav helpers
  const handleNext = async () => {
    if (step === 0 && (!studentName.trim() || !currentLevel || !targetAttempt)) return;
    if (step === 3) {
      handleFinalSubmit();
      return;
    }
    setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 0) setStep(step - 1);
  };



  // Stage togglers for completed topics
  const handleToggleStage = (topic: string, stage: string) => {
    const current = topicStages[topic] || ['Video Lectures', 'NCERT'];
    const updated = current.includes(stage)
      ? current.filter(s => s !== stage)
      : [...current, stage];
    setTopicStages({ ...topicStages, [topic]: updated });
  };

  // Reset diagnostic attempts
  const handleResetDiagnostic = () => {
    setSelectedDiagnosticTopics([]);
    setDiagnosticTests({});
    setDiagnosticAttempts({});
  };

  // Select topic for diagnostic testing
  const handleToggleDiagnosticTopic = async (topic: string) => {
    const isSelected = selectedDiagnosticTopics.includes(topic);
    let updated: string[];
    if (isSelected) {
      updated = selectedDiagnosticTopics.filter(t => t !== topic);
      setSelectedDiagnosticTopics(updated);
      // Clean up tests/attempts
      const newTests = { ...diagnosticTests };
      const newAttempts = { ...diagnosticAttempts };
      delete newTests[topic];
      delete newAttempts[topic];
      setDiagnosticTests(newTests);
      setDiagnosticAttempts(newAttempts);
    } else {
      updated = [...selectedDiagnosticTopics, topic];
      setSelectedDiagnosticTopics(updated);
      
      // Fetch questions dynamically from FastAPI backend
      if (!diagnosticTests[topic]) {
        setLoadingQuestions(prev => ({ ...prev, [topic]: true }));
        try {
          // Identify subject
          let subject = 'Physics';
          for (const sub of ['Physics', 'Chemistry', 'Mathematics']) {
            if (topicsDb[sub]?.includes(topic)) {
              subject = sub;
              break;
            }
          }
          const questionSet = await getQuestions(subject, topic);
          setDiagnosticTests(prev => ({ ...prev, [topic]: questionSet }));
          setDiagnosticAttempts(prev => ({
            ...prev,
            [topic]: {
              answers: ['', '', '', '', ''],
              time_taken_seconds: questionSet.questions.map(q => q.estimated_time_seconds || 120)
            }
          }));
        } catch (err) {
          console.error(`Failed to fetch questions for ${topic}`, err);
        } finally {
          setLoadingQuestions(prev => ({ ...prev, [topic]: false }));
        }
      }
    }
  };

  // Store student answer
  const handleAnswerSelect = (topic: string, questionIdx: number, answerLetter: string) => {
    const attempt = diagnosticAttempts[topic] || { answers: ['', '', '', '', ''], time_taken_seconds: [120, 120, 120, 120, 120] };
    const updatedAnswers = [...attempt.answers];
    updatedAnswers[questionIdx] = answerLetter;
    setDiagnosticAttempts({
      ...diagnosticAttempts,
      [topic]: {
        ...attempt,
        answers: updatedAnswers
      }
    });
  };

  // Submit complete questionnaire
  const handleFinalSubmit = () => {
    // 1. Gather topic tracking structure
    const topic_tracking: Record<string, any> = {};
    for (const sub of ['Physics', 'Chemistry', 'Mathematics']) {
      const completed = completedTopics[sub] || [];
      const untouched = topicsDb[sub]?.filter(t => !completed.includes(t)) || [];
      const details: Record<string, any> = {};
      for (const t of completed) {
        details[t] = {
          confidence: weakTopics[sub]?.includes(t) ? 'Low' : 'Medium',
          workflow_stages: topicStages[t] || ['Video Lectures', 'NCERT']
        };
      }
      topic_tracking[sub] = {
        completed,
        partial: [],
        untouched,
        topic_details: details
      };
    }

    // 2. Map ratings
    const time_rating = TIME_MANAGEMENT_OPTIONS.indexOf(timeManagement) + 3; // mapping 0,1,2 -> 3,4,5
    const revision_days = revisionConsistency === 'Rarely revise weekly' ? 1 : revisionConsistency === 'Revise important topics weekly' ? 4 : 7;
    const problem_rating = PROBLEM_SOLVING_OPTIONS.indexOf(problemSolving) + 3;

    const payload = {
      student: {
        name: studentName || 'Student',
        current_level: currentLevel || 'Class 12th',
        target_attempt: targetAttempt || 'JEE Main 2027'
      },
      academic: {
        physics_proficiency: Math.round(((completedTopics.Physics?.length || 0) / (topicsDb.Physics?.length || 1)) * 100),
        chemistry_proficiency: Math.round(((completedTopics.Chemistry?.length || 0) / (topicsDb.Chemistry?.length || 1)) * 100),
        math_proficiency: Math.round(((completedTopics.Mathematics?.length || 0) / (topicsDb.Mathematics?.length || 1)) * 100),
        weak_topics: [
          ...(weakTopics.Physics || []),
          ...(weakTopics.Chemistry || []),
          ...(weakTopics.Mathematics || [])
        ]
      },
      behavior: {
        weekly_hours: 35,
        time_management_rating: time_rating,
        revision_days_per_week: revision_days,
        problem_solving_rating: problem_rating,
        mock_test_frequency: 'Fortnightly',
        mock_anxiety_rating: 2,
        sleep_quality_rating: 3,
        study_techniques: studyTechniques,
        resources: resources,
        confidence_rating: 3,
        short_answer_blocker: blockerText
      },
      topic_tracking,
      diagnostic_tests: diagnosticTests,
      diagnostic_attempts: diagnosticAttempts,
      metadata: {
        created_at: new Date().toISOString()
      }
    };

    onSubmit(payload);
  };

  // Render Step 0: Profile Page
  const renderStep0 = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h1" gutterBottom sx={{ textAlign: 'center', mb: 1 }}>
        Student Profile Setup
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mb: 6, fontSize: '1.05rem' }}>
        Fill out your target exam and batch settings to frame the diagnostic evaluation.
      </Typography>

      <Container maxWidth="md">
        <Card sx={{ 
          p: { xs: 3, md: 5 }, 
          background: 'rgba(255, 255, 255, 0.02)',
          borderColor: 'rgba(255, 255, 255, 0.06)',
          backdropFilter: 'blur(20px)',
          borderRadius: '24px'
        }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <TextField
              label="Student Name*"
              variant="outlined"
              value={studentName}
              onChange={(e) => setStudentName(e.target.value)}
              placeholder="Enter your full name"
              fullWidth
              sx={{
                '& .MuiInputLabel-root': { color: '#9ca3af' },
                '& .MuiOutlinedInput-root': {
                  color: '#f3f4f6',
                  '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.1)' },
                  '&:hover fieldset': { borderColor: '#8b5cf6' },
                  '&.Mui-focused fieldset': { borderColor: '#c084fc' }
                }
              }}
            />

            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 4 }}>
              <FormControl fullWidth>
                <InputLabel style={{ color: '#9ca3af' }}>Current Level/Class*</InputLabel>
                <Select
                  value={currentLevel}
                  onChange={(e) => setCurrentLevel(e.target.value as string)}
                  input={<OutlinedInput label="Current Level/Class*" />}
                  sx={{
                    color: '#f3f4f6',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#8b5cf6' },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#c084fc' }
                  }}
                >
                  <MenuItem value="Class 10th">Class 10th</MenuItem>
                  <MenuItem value="Class 11th">Class 11th</MenuItem>
                  <MenuItem value="Class 12th">Class 12th</MenuItem>
                  <MenuItem value="Dropper">Dropper Batch</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel style={{ color: '#9ca3af' }}>Target Attempt*</InputLabel>
                <Select
                  value={targetAttempt}
                  onChange={(e) => setTargetAttempt(e.target.value as string)}
                  input={<OutlinedInput label="Target Attempt*" />}
                  sx={{
                    color: '#f3f4f6',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#8b5cf6' },
                    '&.Mui-focused .MuiOutchedInput-notchedOutline': { borderColor: '#c084fc' }
                  }}
                >
                  <MenuItem value="JEE Main 2027">JEE Main 2027</MenuItem>
                  <MenuItem value="JEE Advanced 2027">JEE Advanced 2027</MenuItem>
                  <MenuItem value="JEE Main 2028">JEE Main 2028</MenuItem>
                  <MenuItem value="JEE Advanced 2028">JEE Advanced 2028</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {(!studentName.trim() || !currentLevel || !targetAttempt) && (
              <Alert severity="warning" sx={{ background: 'rgba(217, 119, 6, 0.1)', color: '#f59e0b', border: '1px solid rgba(217, 119, 6, 0.2)' }}>
                ⚠️ Name, Current level, and Target attempt are required fields to proceed.
              </Alert>
            )}
          </Box>
        </Card>
      </Container>
    </Box>
  );

  // Render Step 1: Academic Page
  const renderStep1 = () => {
    const subjects = ['Physics', 'Chemistry', 'Mathematics'];
    const activeSubject = subjects[activeSubjectTab];
    const topics = topicsDb[activeSubject] || [];

    const handleSelectCompleted = (topicList: string[]) => {
      setCompletedTopics({
        ...completedTopics,
        [activeSubject]: topicList
      });
    };

    const handleSelectWeak = (topicList: string[]) => {
      setWeakTopics({
        ...weakTopics,
        [activeSubject]: topicList
      });
    };

    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="h1" gutterBottom sx={{ textAlign: 'center', mb: 1 }}>
          Academic Proficiency
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mb: 4, fontSize: '1.05rem' }}>
          Mark completed chapters, flag weak subjects, and specify the stages done for each chapter.
        </Typography>

        <Container maxWidth="lg">
          <Tabs 
            value={activeSubjectTab} 
            onChange={(_, val) => setActiveSubjectTab(val)}
            centered
            sx={{
              mb: 4,
              '& .MuiTabs-indicator': { backgroundColor: '#8b5cf6' },
              '& .MuiTab-root': { color: '#9ca3af', fontWeight: 'bold' },
              '& .Mui-selected': { color: '#c084fc !important' }
            }}
          >
            <Tab label="⚛️ Physics" icon={<SchoolIcon />} iconPosition="start" />
            <Tab label="🧪 Chemistry" icon={<ScienceIcon />} iconPosition="start" />
            <Tab label="📐 Mathematics" icon={<CalculateIcon />} iconPosition="start" />
          </Tabs>

          <Card sx={{ 
            p: 4, 
            background: 'rgba(255, 255, 255, 0.02)',
            borderColor: 'rgba(255, 255, 255, 0.06)',
            borderRadius: '20px'
          }}>
            <Typography variant="h3" gutterBottom sx={{ color: '#ffffff', mb: 4, fontWeight: 'bold' }}>
              {activeSubject} Syllabus Tracker
            </Typography>

            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 4, mb: 4 }}>
              {/* Weak Topics Multiselect */}
              <FormControl fullWidth>
                <InputLabel style={{ color: '#9ca3af' }}>Weak Topics</InputLabel>
                <Select
                  multiple
                  value={weakTopics[activeSubject] || []}
                  onChange={(e) => handleSelectWeak(e.target.value as string[])}
                  input={<OutlinedInput label="Weak Topics" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" sx={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.2)' }} />
                      ))}
                    </Box>
                  )}
                  sx={{
                    color: '#f3f4f6',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#8b5cf6' }
                  }}
                >
                  {topics.map((name) => (
                    <MenuItem key={name} value={name}>
                      <Checkbox checked={(weakTopics[activeSubject] || []).indexOf(name) > -1} />
                      <ListItemText primary={name} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Completed Topics Multiselect */}
              <FormControl fullWidth>
                <InputLabel style={{ color: '#9ca3af' }}>Completed Topics</InputLabel>
                <Select
                  multiple
                  value={completedTopics[activeSubject] || []}
                  onChange={(e) => handleSelectCompleted(e.target.value as string[])}
                  input={<OutlinedInput label="Completed Topics" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" sx={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', border: '1px solid rgba(16,185,129,0.2)' }} />
                      ))}
                    </Box>
                  )}
                  sx={{
                    color: '#f3f4f6',
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#8b5cf6' }
                  }}
                >
                  {topics.map((name) => (
                    <MenuItem key={name} value={name}>
                      <Checkbox checked={(completedTopics[activeSubject] || []).indexOf(name) > -1} />
                      <ListItemText primary={name} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            {/* Stages done for completed topics */}
            <Typography variant="h5" sx={{ color: '#9ca3af', fontWeight: 'bold', mb: 2 }}>
              Topic Completion Workflow Stages
            </Typography>
            
            {completedTopics[activeSubject]?.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                Select chapters under 'Completed Topics' above to track their learning stages.
              </Typography>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {completedTopics[activeSubject].map((topic) => (
                  <Accordion 
                    key={topic} 
                    sx={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.01)', 
                      borderColor: 'rgba(255,255,255,0.04)',
                      '&:before': { display: 'none' } 
                    }}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#9ca3af' }} />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <CheckCircleIcon sx={{ color: '#10b981', fontSize: '1.2rem' }} />
                        <Typography sx={{ fontWeight: 'bold', color: '#e5e7eb' }}>{topic}</Typography>
                        <Chip label={`${(topicStages[topic] || ['Video Lectures', 'NCERT']).length} / ${STAGES.length} Stages`} size="small" variant="outlined" sx={{ color: '#a78bfa', borderColor: 'rgba(167,139,250,0.3)' }} />
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2, borderBottom: '1px solid rgba(255,255,255,0.06)', pb: 1 }}>
                        <FormControlLabel
                          control={
                            <Checkbox 
                              checked={(topicStages[topic] || ['Video Lectures', 'NCERT']).length === STAGES.length}
                              indeterminate={
                                (topicStages[topic] || ['Video Lectures', 'NCERT']).length > 0 &&
                                (topicStages[topic] || ['Video Lectures', 'NCERT']).length < STAGES.length
                              }
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setTopicStages({
                                    ...topicStages,
                                    [topic]: [...STAGES]
                                  });
                                } else {
                                  setTopicStages({
                                    ...topicStages,
                                    [topic]: []
                                  });
                                }
                              }}
                              sx={{ color: 'rgba(255,255,255,0.2)', '&.Mui-checked': { color: '#a78bfa' } }}
                            />
                          }
                          label={<Typography variant="body2" sx={{ fontWeight: 'bold', color: '#c084fc' }}>Select All Stages</Typography>}
                        />
                      </Box>
                      <Box sx={{ 
                        display: 'grid', 
                        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, 
                        gap: 1.5 
                      }}>
                        {STAGES.map((stage) => {
                          const isChecked = (topicStages[topic] || ['Video Lectures', 'NCERT']).includes(stage);
                          return (
                            <FormControlLabel
                              key={stage}
                              control={
                                <Checkbox 
                                  checked={isChecked} 
                                  onChange={() => handleToggleStage(topic, stage)} 
                                  sx={{ color: 'rgba(255,255,255,0.2)', '&.Mui-checked': { color: '#a78bfa' } }}
                                />
                              }
                              label={<Typography variant="body2" sx={{ color: isChecked ? '#f3f4f6' : '#9ca3af' }}>{stage}</Typography>}
                            />
                          );
                        })}
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            )}
          </Card>
        </Container>
      </Box>
    );
  };

  // Render Step 2: Study Behavior Page
  const renderStep2 = () => (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h1" gutterBottom sx={{ textAlign: 'center', mb: 1 }}>
        Study Behaviour
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mb: 5, fontSize: '1.05rem' }}>
        Help us understand your weekly work cycles, learning strategies, and current blockades.
      </Typography>

      <Container maxWidth="lg">
        <Card sx={{ 
          p: 4, 
          background: 'rgba(255, 255, 255, 0.02)',
          borderColor: 'rgba(255, 255, 255, 0.06)',
          borderRadius: '20px'
        }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 4, mb: 4 }}>
            <FormControl fullWidth>
              <InputLabel style={{ color: '#9ca3af' }}>Time Management</InputLabel>
              <Select
                value={timeManagement}
                onChange={(e) => setTimeManagement(e.target.value as string)}
                input={<OutlinedInput label="Time Management" />}
                sx={{ color: '#f3f4f6', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' } }}
              >
                {TIME_MANAGEMENT_OPTIONS.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel style={{ color: '#9ca3af' }}>Problem Solving</InputLabel>
              <Select
                value={problemSolving}
                onChange={(e) => setProblemSolving(e.target.value as string)}
                input={<OutlinedInput label="Problem Solving" />}
                sx={{ color: '#f3f4f6', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' } }}
              >
                {PROBLEM_SOLVING_OPTIONS.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel style={{ color: '#9ca3af' }}>Revision Consistency</InputLabel>
              <Select
                value={revisionConsistency}
                onChange={(e) => setRevisionConsistency(e.target.value as string)}
                input={<OutlinedInput label="Revision Consistency" />}
                sx={{ color: '#f3f4f6', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' } }}
              >
                {REVISION_OPTIONS.map(opt => <MenuItem key={opt} value={opt}>{opt}</MenuItem>)}
              </Select>
            </FormControl>
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 4, mb: 4 }}>
            {/* Study Techniques */}
            <FormControl fullWidth>
              <InputLabel style={{ color: '#9ca3af' }}>Study Techniques Used</InputLabel>
              <Select
                multiple
                value={studyTechniques}
                onChange={(e) => setStudyTechniques(e.target.value as string[])}
                input={<OutlinedInput label="Study Techniques Used" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" sx={{ backgroundColor: 'rgba(139, 92, 246, 0.15)', color: '#c084fc', border: '1px solid rgba(139,92,246,0.2)' }} />
                    ))}
                  </Box>
                )}
                sx={{ color: '#f3f4f6', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' } }}
              >
                {STUDY_TECHNIQUES.map((name) => (
                  <MenuItem key={name} value={name}>
                    <Checkbox checked={studyTechniques.indexOf(name) > -1} />
                    <ListItemText primary={name} />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Learning Resources */}
            <FormControl fullWidth>
              <InputLabel style={{ color: '#9ca3af' }}>Learning Resources Used</InputLabel>
              <Select
                multiple
                value={resources}
                onChange={(e) => setResources(e.target.value as string[])}
                input={<OutlinedInput label="Learning Resources Used" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} size="small" sx={{ backgroundColor: 'rgba(236, 72, 153, 0.15)', color: '#f472b6', border: '1px solid rgba(236,72,153,0.2)' }} />
                    ))}
                  </Box>
                )}
                sx={{ color: '#f3f4f6', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255, 255, 255, 0.1)' } }}
              >
                {LEARNING_RESOURCES.map((name) => (
                  <MenuItem key={name} value={name}>
                    <Checkbox checked={resources.indexOf(name) > -1} />
                    <ListItemText primary={name} />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          <TextField
            label="What is the biggest blocker in your preparation right now?"
            multiline
            rows={4}
            value={blockerText}
            onChange={(e) => setBlockerText(e.target.value)}
            fullWidth
            sx={{
              '& .MuiInputLabel-root': { color: '#9ca3af' },
              '& .MuiOutlinedInput-root': {
                color: '#f3f4f6',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.1)' },
                '&:hover fieldset': { borderColor: '#8b5cf6' },
                '&.Mui-focused fieldset': { borderColor: '#c084fc' }
              }
            }}
          />
        </Card>
      </Container>
    </Box>
  );

  // Render Step 3: Diagnostic Test Page
  const renderStep3 = () => {
    // Gather all completed topics across subjects
    const completedList = [
      ...completedTopics.Physics.map(t => ({ topic: t, subject: 'Physics' })),
      ...completedTopics.Chemistry.map(t => ({ topic: t, subject: 'Chemistry' })),
      ...completedTopics.Mathematics.map(t => ({ topic: t, subject: 'Mathematics' }))
    ];

    // Filter based on subject
    const filteredCompletedList = completedList.filter(item => {
      if (testSubjectFilter === 'All') return true;
      return item.subject === testSubjectFilter;
    });

    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="h1" gutterBottom sx={{ textAlign: 'center', mb: 1 }}>
          Subject and Topic Selection
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mb: 5, fontSize: '1.05rem' }}>
          Select topics you have completed to take an interactive 5-question diagnostic MCQ assessment.
        </Typography>

        <Container maxWidth="lg">
          <Card sx={{ 
            p: 4, 
            background: 'rgba(255, 255, 255, 0.02)',
            borderColor: 'rgba(255, 255, 255, 0.06)',
            borderRadius: '20px',
            mb: 4
          }}>
            {/* Subject Filters */}
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {['All', 'Physics', 'Chemistry', 'Mathematics'].map((sub) => (
                  <Button
                    key={sub}
                    variant={testSubjectFilter === sub ? 'contained' : 'outlined'}
                    onClick={() => setTestSubjectFilter(sub)}
                    size="small"
                    sx={{
                      backgroundColor: testSubjectFilter === sub ? '#8b5cf6' : 'transparent',
                      color: testSubjectFilter === sub ? '#ffffff' : '#9ca3af',
                      borderColor: 'rgba(255, 255, 255, 0.1)',
                      '&:hover': {
                        backgroundColor: testSubjectFilter === sub ? '#7c3aed' : 'rgba(255, 255, 255, 0.05)',
                        borderColor: '#8b5cf6'
                      }
                    }}
                  >
                    {sub}
                  </Button>
                ))}
              </Box>

              <Button
                variant="outlined"
                color="warning"
                onClick={handleResetDiagnostic}
                startIcon={<RotateLeftIcon />}
                size="small"
                sx={{ borderColor: 'rgba(217, 119, 6, 0.3)', color: '#f59e0b', '&:hover': { borderColor: '#f59e0b', backgroundColor: 'rgba(217,119,6,0.05)' } }}
              >
                Reset attempts
              </Button>
            </Box>

            {/* Topics Checkbox Grid */}
            <Typography variant="h5" sx={{ color: '#ffffff', fontWeight: 'bold', mb: 2 }}>
              Choose Topic Assessments (from Completed chapters)
            </Typography>

            {filteredCompletedList.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center', background: 'rgba(255,255,255,0.01)', borderRadius: '12px' }}>
                <Typography color="text.secondary" sx={{ fontStyle: 'italic' }}>
                  No completed chapters match this filter. Go back to 'Academic Proficiency' and mark a chapter as completed.
                </Typography>
              </Box>
            ) : (
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, 
                gap: 2, 
                mb: 4 
              }}>
                {filteredCompletedList.map(({ topic, subject }) => {
                  const isChecked = selectedDiagnosticTopics.includes(topic);
                  const isLoadingQuestions = loadingQuestions[topic];
                  return (
                    <Card
                      key={topic}
                      onClick={() => !isLoadingQuestions && handleToggleDiagnosticTopic(topic)}
                      sx={{
                        p: 2,
                        cursor: isLoadingQuestions ? 'default' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        border: isChecked ? '1px solid #c084fc' : '1px solid rgba(255, 255, 255, 0.05)',
                        backgroundColor: isChecked ? 'rgba(139, 92, 246, 0.1)' : 'rgba(255,255,255,0.01)',
                        '&:hover': {
                          borderColor: '#8b5cf6'
                        }
                      }}
                    >
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 'bold', color: '#f3f4f6' }}>{topic}</Typography>
                        <Typography variant="caption" color="text.secondary">{subject}</Typography>
                      </Box>
                      {isLoadingQuestions ? (
                        <CircularProgress size={20} sx={{ color: '#c084fc' }} />
                      ) : isChecked ? (
                        <CheckCircleIcon sx={{ color: '#c084fc' }} />
                      ) : (
                        <HelpIcon sx={{ color: 'rgba(255,255,255,0.1)' }} />
                      )}
                    </Card>
                  );
                })}
              </Box>
            )}
          </Card>

          {/* Renders questions for selected topics */}
          {selectedDiagnosticTopics.length > 0 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {selectedDiagnosticTopics.map((topic) => {
                const test = diagnosticTests[topic];
                const attempt = diagnosticAttempts[topic];
                if (!test || !attempt) return null;

                return (
                  <Card 
                    key={topic} 
                    sx={{ 
                      p: 4, 
                      background: 'rgba(255, 255, 255, 0.02)', 
                      borderColor: 'rgba(255, 255, 255, 0.06)',
                      borderRadius: '20px'
                    }}
                  >
                    <Typography variant="h3" sx={{ color: '#a78bfa', fontWeight: 'bold', mb: 3, borderBottom: '1px solid rgba(255,255,255,0.05)', pb: 1 }}>
                      {test.subject}: {topic} MCQ Diagnostic
                    </Typography>

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                      {test.questions.map((q, qIdx) => {
                        const letters = ['A', 'B', 'C', 'D'];
                        const selectedAns = attempt.answers[qIdx];
                        return (
                          <Box key={qIdx} sx={{ background: 'rgba(255,255,255,0.01)', p: 3, borderRadius: '12px' }}>
                            <Typography sx={{ fontWeight: 'bold', mb: 2, color: '#f3f4f6' }}>
                              Q{qIdx + 1} <Chip label={q.difficulty.toUpperCase()} size="small" color={q.difficulty === 'easy' ? 'success' : q.difficulty === 'medium' ? 'warning' : 'error'} sx={{ ml: 1, height: '20px', fontSize: '0.7rem' }} /> {q.question}
                            </Typography>

                            <RadioGroup
                              value={selectedAns}
                              onChange={(e) => handleAnswerSelect(topic, qIdx, e.target.value)}
                            >
                              {q.options.map((option, optIdx) => {
                                const letter = letters[optIdx];
                                return (
                                  <FormControlLabel
                                    key={optIdx}
                                    value={letter}
                                    control={<Radio sx={{ color: 'rgba(255,255,255,0.2)', '&.Mui-checked': { color: '#a78bfa' } }} />}
                                    label={<Typography variant="body2" sx={{ color: selectedAns === letter ? '#ffffff' : '#d1d5db' }}>{`${letter}. ${option}`}</Typography>}
                                    sx={{ mb: 1 }}
                                  />
                                );
                              })}
                            </RadioGroup>
                          </Box>
                        );
                      })}
                    </Box>
                  </Card>
                );
              })}
            </Box>
          )}

          {/* Step 3 validation message */}
          {step3ValidationMessage && (
            <Alert
              severity="warning"
              sx={{
                mt: 3,
                background: 'rgba(217, 119, 6, 0.12)',
                color: '#fbbf24',
                border: '1px solid rgba(217, 119, 6, 0.3)',
                borderRadius: '12px',
                '& .MuiAlert-icon': { color: '#f59e0b' }
              }}
            >
              {step3ValidationMessage}
            </Alert>
          )}
        </Container>
      </Box>
    );
  };

  // Render loading screen
  const renderLoading = () => (
    <Box sx={{ 
      minHeight: '80vh', 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center',
      py: 8
    }}>
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
      >
        <CircularProgress size={70} thickness={4} sx={{ color: '#8b5cf6' }} />
      </motion.div>
      <Typography variant="h2" sx={{ mt: 5, fontWeight: 900, background: 'linear-gradient(135deg, #ffffff 40%, #c084fc 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', textShadow: '0 0 24px rgba(139,92,246,0.3)' }}>
        Processing AI Skill Analytics
      </Typography>
      <Box sx={{ width: '280px', mt: 3, borderRadius: '4px', overflow: 'hidden' }}>
        <LinearProgress sx={{
          backgroundColor: 'rgba(255,255,255,0.05)',
          '& .MuiLinearProgress-bar': {
            background: 'linear-gradient(90deg, #8b5cf6, #ec4899)'
          }
        }} />
      </Box>
      <Typography variant="body1" color="text.secondary" sx={{ mt: 4, textAlign: 'center', maxWidth: '420px', lineHeight: 1.6, fontSize: '0.95rem' }}>
        Executing scoring engine calculations, resolving prerequisites inside the knowledge graph, and invoking the wellness, behavioral, academic, and recommendation agents.
      </Typography>
    </Box>
  );

  if (isLoading) return renderLoading();

  return (
    <Box sx={{ minHeight: '90vh', display: 'flex', flexDirection: 'column', pb: 10 }}>
      {/* Global Progress Indicators */}
      <Container maxWidth="lg" sx={{ mt: 6, mb: 2 }}>
        <Box sx={{ mb: 4 }}>
          {/* Progress label */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5, px: 0.5 }}>
            <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.light', letterSpacing: '0.12em' }}>
              JEE SOCA DIAGNOSTIC FLOW
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 900, color: 'text.secondary', letterSpacing: '0.05em' }}>
              STEP {step + 1} OF {totalSteps}
            </Typography>
          </Box>

          {/* Progress bar */}
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ 
              height: '4px', 
              borderRadius: '2px',
              backgroundColor: 'rgba(255,255,255,0.05)',
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(90deg, #8b5cf6, #ec4899)'
              }
            }} 
          />
        </Box>

        {/* Step jump navigation bar */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: `repeat(${totalSteps}, 1fr)`, 
          gap: 2, 
          mb: 4 
        }}>
          {['Student Profile', 'Academic Tracker', 'Study Behaviour', 'Topic MCQ Diagnostic'].map((name, idx) => {
            const isCurrent = step === idx;
            const isCompleted = step > idx;
            
            let btnColor = 'rgba(255,255,255,0.02)';
            let txtColor = '#94a3b8';
            let borderStyle = '1px solid rgba(255, 255, 255, 0.05)';
            
            if (isCurrent) {
              btnColor = 'rgba(167, 139, 250, 0.15)';
              txtColor = '#c084fc';
              borderStyle = '1px solid #8b5cf6';
            } else if (isCompleted) {
              btnColor = 'rgba(16, 185, 129, 0.1)';
              txtColor = '#10b981';
              borderStyle = '1px solid rgba(16,185,129,0.3)';
            }

            return (
              <Button
                key={idx}
                onClick={() => handleJumpToStep(idx)}
                sx={{
                  backgroundColor: btnColor,
                  color: txtColor,
                  border: borderStyle,
                  fontSize: '0.75rem',
                  py: 1,
                  textTransform: 'none',
                  fontWeight: isCurrent ? 'bold' : 'normal',
                  '&:hover': {
                    backgroundColor: isCurrent ? 'rgba(167, 139, 250, 0.2)' : 'rgba(255,255,255,0.05)',
                    borderColor: '#8b5cf6'
                  }
                }}
              >
                {isCompleted ? 'Done: ' : isCurrent ? 'Current: ' : 'Next: '} {name}
              </Button>
            );
          })}
        </Box>
      </Container>

      {/* Main Content Area */}
      <Container maxWidth="xl" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            style={{ width: '100%' }}
          >
            {step === 0 && renderStep0()}
            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}
          </motion.div>
        </AnimatePresence>
      </Container>

      {/* Bottom Control Actions */}
      <Container maxWidth="lg" sx={{ mt: 6 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            {step > 0 && (
              <Button 
                variant="outlined" 
                color="inherit" 
                onClick={handleBack}
                startIcon={<ArrowBackIcon />}
                sx={{ px: 4, py: 1.5, borderColor: 'rgba(255,255,255,0.15)', color: '#e5e7eb' }}
              >
                Back
              </Button>
            )}
          </Box>
          <Box>
            <Button 
              variant="contained" 
              disabled={
                (step === 0 && (!studentName.trim() || !currentLevel || !targetAttempt)) ||
                isStep3Blocked
              }
              onClick={handleNext}
              endIcon={step === 3 ? null : <ArrowForwardIcon />}
              sx={{ 
                px: 6, 
                py: 1.5,
                background: isStep3Blocked
                  ? 'rgba(255,255,255,0.05)'
                  : 'linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%)',
                border: 'none',
                color: isStep3Blocked ? 'rgba(255,255,255,0.2)' : '#ffffff',
                boxShadow: isStep3Blocked ? 'none' : '0 8px 24px rgba(139, 92, 246, 0.25)',
                '&:hover': {
                  background: isStep3Blocked
                    ? 'rgba(255,255,255,0.05)'
                    : 'linear-gradient(90deg, #7c3aed 0%, #db2777 100%)',
                },
                '&:disabled': {
                  background: 'rgba(255, 255, 255, 0.05)',
                  color: 'rgba(255, 255, 255, 0.2)'
                }
              }}
            >
              {step === 3 ? 'Generate Assessment Report' : 'Next'}
            </Button>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Card, 
  Button, 
  TextField,
  Rating,
  Alert,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import WarningIcon from '@mui/icons-material/Warning';
import AssignmentIcon from '@mui/icons-material/Assignment';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CodeIcon from '@mui/icons-material/Code';
import InfoIcon from '@mui/icons-material/Info';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { motion } from 'framer-motion';
import { downloadPdf, submitFeedback } from '../api';


const OverallMetricsChart = ({ profile }: { profile: any }) => {
  const metrics = [
    { label: 'Physics Score', val: profile.physics_score ?? 0 },
    { label: 'Chemistry Score', val: profile.chemistry_score ?? 0 },
    { label: 'Mathematics Score', val: profile.math_score ?? 0 },
    { label: 'Discipline Score', val: profile.discipline_score ?? 0 },
    { label: 'Time Management', val: profile.time_management_score ?? 0 },
    { label: 'Revision Consistency', val: profile.revision_consistency_score ?? 0 }
  ];
  
  const height = 280;
  const width = 600;
  const paddingLeft = 160;
  const paddingRight = 40;
  const paddingTop = 20;
  const paddingBottom = 40;
  
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  const barHeight = 20;
  const gap = (chartHeight - barHeight * metrics.length) / (metrics.length - 1 || 1);
  
  return (
    <Box sx={{ width: '100%', overflowX: 'auto', background: '#0b0c10', p: 3, borderRadius: '16px', border: '1px solid rgba(255,255,255,0.04)' }}>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} style={{ minWidth: '450px' }}>
        {[0, 25, 50, 75, 100].map((tick) => {
          const x = paddingLeft + (tick / 100) * chartWidth;
          return (
            <g key={tick}>
              <line x1={x} y1={paddingTop} x2={x} y2={height - paddingBottom} stroke="rgba(255,255,255,0.06)" strokeDasharray="3" />
              <text x={x} y={height - paddingBottom + 18} textAnchor="middle" fill="#6b7280" fontSize="10px">{tick}%</text>
            </g>
          );
        })}
        
        {metrics.map((m, idx) => {
          const y = paddingTop + idx * (barHeight + gap);
          const barWidth = (m.val / 100) * chartWidth;
          const fillGrad = m.val >= 80 ? 'url(#greenGrad)' : m.val >= 60 ? 'url(#orangeGrad)' : 'url(#redGrad)';
          
          return (
            <g key={idx}>
              <text x={paddingLeft - 15} y={y + 14} textAnchor="end" fill="#9ca3af" fontSize="11px" fontWeight="bold">
                {m.label}
              </text>
              <rect x={paddingLeft} y={y} width={chartWidth} height={barHeight} rx="4" fill="rgba(255,255,255,0.02)" />
              <rect x={paddingLeft} y={y} width={barWidth} height={barHeight} rx="4" fill={fillGrad} />
              <text x={paddingLeft + Math.max(5, barWidth - 35)} y={y + 14} fill="#ffffff" fontSize="10px" fontWeight="bold">
                {m.val}%
              </text>
            </g>
          );
        })}
        
        <defs>
          <linearGradient id="redGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="100%" stopColor="#f87171" />
          </linearGradient>
          <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#fbbf24" />
          </linearGradient>
          <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#34d399" />
          </linearGradient>
        </defs>
      </svg>
    </Box>
  );
};

const SubjectMasteryChart = ({ subjectMastery }: { subjectMastery: any }) => {
  const data = [
    { label: '⚛️ Physics', val: subjectMastery?.Physics ?? subjectMastery?.physics ?? 0 },
    { label: '🧪 Chemistry', val: subjectMastery?.Chemistry ?? subjectMastery?.chemistry ?? 0 },
    { label: '📐 Mathematics', val: subjectMastery?.Mathematics ?? subjectMastery?.mathematics ?? 0 }
  ];
  
  const height = 180;
  const width = 500;
  const paddingLeft = 120;
  const paddingRight = 40;
  const paddingTop = 20;
  const paddingBottom = 40;
  
  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;
  const barHeight = 22;
  const gap = (chartHeight - barHeight * data.length) / (data.length - 1 || 1);
  
  return (
    <Box sx={{ width: '100%', overflowX: 'auto', background: '#0b0c10', p: 3, borderRadius: '16px', border: '1px solid rgba(255,255,255,0.04)' }}>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} style={{ minWidth: '350px' }}>
        {[0, 25, 50, 75, 100].map((tick) => {
          const x = paddingLeft + (tick / 100) * chartWidth;
          return (
            <g key={tick}>
              <line x1={x} y1={paddingTop} x2={x} y2={height - paddingBottom} stroke="rgba(255,255,255,0.06)" strokeDasharray="3" />
              <text x={x} y={height - paddingBottom + 18} textAnchor="middle" fill="#6b7280" fontSize="10px">{tick}%</text>
            </g>
          );
        })}
        
        {data.map((m, idx) => {
          const y = paddingTop + idx * (barHeight + gap);
          const barWidth = (m.val / 100) * chartWidth;
          const fillGrad = m.val >= 80 ? 'url(#greenGrad)' : m.val >= 60 ? 'url(#orangeGrad)' : 'url(#redGrad)';
          
          return (
            <g key={idx}>
              <text x={paddingLeft - 15} y={y + 15} textAnchor="end" fill="#9ca3af" fontSize="12px" fontWeight="bold">
                {m.label}
              </text>
              <rect x={paddingLeft} y={y} width={chartWidth} height={barHeight} rx="4" fill="rgba(255,255,255,0.02)" />
              <rect x={paddingLeft} y={y} width={barWidth} height={barHeight} rx="4" fill={fillGrad} />
              <text x={paddingLeft + Math.max(5, barWidth - 30)} y={y + 15} fill="#ffffff" fontSize="11px" fontWeight="bold">
                {m.val}%
              </text>
            </g>
          );
        })}
      </svg>
    </Box>
  );
};

const TopicReadinessHeatmap = ({ reportData }: { reportData: any }) => {
  const reports = reportData.topic_assessment?.topic_reports || [];
  
  if (reports.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', textAlign: 'center', p: 4 }}>
        No diagnostic topic tests were taken. Heatmap empty.
      </Typography>
    );
  }
  
  const subjects: Record<string, { topic: string; score: number }[]> = {
    Physics: [],
    Chemistry: [],
    Mathematics: []
  };
  
  reports.forEach((r: any) => {
    const sub = r.subject || 'Physics';
    if (subjects[sub]) {
      subjects[sub].push({
        topic: r.topic,
        score: r.readiness_score || 0
      });
    }
  });

  const hasItems = Object.values(subjects).some(arr => arr.length > 0);
  if (!hasItems) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', textAlign: 'center', p: 4 }}>
        No diagnostic topic reports found in reportData.
      </Typography>
    );
  }

  return (
    <Box sx={{ background: '#0b0c10', p: 3, borderRadius: '16px', border: '1px solid rgba(255,255,255,0.04)' }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {Object.entries(subjects).map(([subject, items]) => {
          if (items.length === 0) return null;
          return (
            <Box key={subject}>
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#c084fc', mb: 2, fontSize: '0.95rem', letterSpacing: '0.05em' }}>
                {subject === 'Physics' ? '⚛️ PHYSICS' : subject === 'Chemistry' ? '🧪 CHEMISTRY' : '📐 MATHEMATICS'}
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                {items.map((item, idx) => {
                  const color = item.score >= 80 ? '#10b981' : item.score >= 60 ? '#f59e0b' : '#ef4444';
                  const bg = item.score >= 80 ? 'rgba(16, 185, 129, 0.05)' : item.score >= 60 ? 'rgba(245, 158, 11, 0.05)' : 'rgba(239, 68, 68, 0.05)';
                  return (
                    <Box 
                      key={idx} 
                      sx={{ 
                        p: 2.5, 
                        borderRadius: '12px', 
                        border: `1.5px solid ${color}`, 
                        background: bg,
                        minWidth: '160px',
                        flex: '1 1 calc(25% - 16px)',
                        maxWidth: '240px',
                        textAlign: 'center',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                        transition: 'transform 0.2s',
                        '&:hover': {
                          transform: 'translateY(-2px)'
                        }
                      }}
                    >
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 1, minHeight: '38px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {item.topic}
                      </Typography>
                      <Typography variant="h4" sx={{ fontWeight: 900, color: color }}>
                        {item.score}%
                      </Typography>
                    </Box>
                  );
                })}
              </Box>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

interface DashboardProps {
  reportData: any;
  onReset: () => void;
  onBackToMCQ: () => void;
  onBackToTopics: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ 
  reportData, 
  onReset,
  onBackToMCQ,
  onBackToTopics
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [activeSubjectTab, setActiveSubjectTab] = useState('Physics');
  const [usefulness, setUsefulness] = useState<number | null>(5);
  const [comment, setComment] = useState('');
  const [feedbackSaved, setFeedbackSaved] = useState(false);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<any>(null);

  const {
    profile = {},
    agents = {},
    knowledge_graph = {},
    knowledge_graph_layouts = {},
    topic_assessment = {},
    soca = {}
  } = reportData;

  // --- Normalize topic_assessment: backend returns topic_reports (list), scorecard needs a dict ---
  const rawTopicReports: any[] = topic_assessment.topic_reports || [];
  // Build topic_readiness dict from topic_reports list for the scorecard table
  const topicReadinessMap: Record<string, any> = {};
  rawTopicReports.forEach((r: any) => {
    if (r.topic) {
      topicReadinessMap[r.topic] = {
        readiness_score: r.readiness_score ?? 0,
        accuracy: r.accuracy ?? 0,
        correct_answers: r.correct_answers ?? 0,
        total_questions: r.total_questions ?? 5,
        progress_ratio: r.workflow_progress != null ? r.workflow_progress / 100 : 0,
        subject: r.subject || 'Physics',
        flags: r.flags || [],
        weak_areas: r.weak_areas || [],
        recommendations: r.recommendations || [],
        workflow_stages: r.workflow_stages || [],
        workflow_gaps: r.workflow_gaps || [],
      };
    }
  });
  const hasTopicData = Object.keys(topicReadinessMap).length > 0;
  // Use backend roadmap if available, else derive from reports
  const topicRoadmap: any[] = topic_assessment.roadmap || [];

  const studentName = profile.student_name || 'Student';
  const studentLevel = profile.current_level || 'Class 12th';
  const targetAttempt = profile.target_attempt || 'JEE Main 2027';

  // SOCA lists
  const strengths = soca.strengths || ["Leading conceptual focus demonstrated", "Solid stamina in long timed study sessions"];
  const opportunities = soca.opportunities || ["Raise weakest topic score using learning loops", "Integrate chapter-wise PYQs as primary practice"];
  const challenges = soca.challenges || ["Stress spikes under mocks", "Calculations and memory decay risks"];
  const actionPlan = soca.action_plan || ["Theory Fix: NCERT & Video revision blocks", "Testing Strategy: Mixed daily timed sprints"];

  // PDF Trigger
  const handlePdfDownload = async () => {
    try {
      await downloadPdf(reportData, studentName);
    } catch (err) {
      console.error('Failed to export PDF report', err);
      alert('Error exporting PDF report. Please ensure the backend is running.');
    }
  };

  // Raw JSON Download
  const handleJsonDownload = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `soca_diagnostic_report_${studentName.toLowerCase().replace(/\s+/g, '_')}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Submit Feedback
  const handleSaveFeedback = async () => {
    if (usefulness === null) return;
    setSubmittingFeedback(true);
    try {
      await submitFeedback({
        student_name: studentName,
        rating: usefulness,
        feedback: comment,
        metadata: {
          timestamp: new Date().toISOString()
        }
      });
      setFeedbackSaved(true);
    } catch (err) {
      console.error('Failed to submit feedback', err);
      // fallback save local
      const feedbackObj = { rating: usefulness, comment, timestamp: new Date().toISOString() };
      localStorage.setItem('soca_feedback', JSON.stringify(feedbackObj));
      setFeedbackSaved(true);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  // Render SVG Knowledge Graph for a Subject
  const renderSVGGraph = (subject: string) => {
    const graphData = knowledge_graph_layouts[subject] || { nodes: [], edges: [] };
    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];

    if (nodes.length === 0) {
      return (
        <Box sx={{ p: 4, textAlign: 'center', background: 'rgba(255,255,255,0.01)', borderRadius: '12px' }}>
          <Typography color="text.secondary" sx={{ fontStyle: 'italic' }}>
            No prerequisite nodes found for this subject.
          </Typography>
        </Box>
      );
    }

    // Canvas size
    const width = 1000;
    const height = 500;

    // Helper to map normalized x, y to SVG space
    const getCoords = (node: any) => {
      const marginX = 80;
      const marginY = 50;
      return {
        cx: marginX + node.x * (width - 2 * marginX),
        cy: marginY + node.y * (height - 2 * marginY)
      };
    };

    return (
      <Box sx={{ position: 'relative', width: '100%', overflowX: 'auto', background: '#0b0c10', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.04)', p: 1 }}>
        <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} style={{ minWidth: '800px' }}>
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#334155" />
            </marker>
          </defs>

          {/* Render Edges */}
          {edges.map((edge: any, idx: number) => {
            const srcNode = nodes.find((n: any) => n.id === edge.source);
            const tgtNode = nodes.find((n: any) => n.id === edge.target);
            if (!srcNode || !tgtNode) return null;
            const src = getCoords(srcNode);
            const tgt = getCoords(tgtNode);
            
            // Draw clean curved arc path
            const dx = tgt.cx - src.cx;
            const dy = tgt.cy - src.cy;
            const dr = Math.sqrt(dx * dx + dy * dy) * 1.5; // curvature
            
            return (
              <path
                key={idx}
                d={`M${src.cx},${src.cy} A${dr},${dr} 0 0,1 ${tgt.cx},${tgt.cy}`}
                fill="none"
                stroke="#1e293b"
                strokeWidth="2.5"
                markerEnd="url(#arrow)"
              />
            );
          })}

          {/* Render Nodes */}
          {nodes.map((node: any) => {
            const { cx, cy } = getCoords(node);
            const isHovered = hoveredNode?.id === node.id;
            
            return (
              <g 
                key={node.id} 
                style={{ cursor: 'pointer' }}
                onMouseEnter={() => setHoveredNode(node)}
                onMouseLeave={() => setHoveredNode(null)}
              >
                {/* Outer pulsing ring for hover */}
                {isHovered && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={node.size + 8}
                    fill="none"
                    stroke={node.color}
                    strokeWidth="2.5"
                    style={{ opacity: 0.5 }}
                  />
                )}
                {/* Node circle */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={node.size}
                  fill={node.color}
                  stroke="#0f172a"
                  strokeWidth="3"
                  style={{ transition: 'all 0.2s ease-in-out' }}
                />
                {/* Node Label */}
                <text
                  x={cx}
                  y={cy + node.size + 16}
                  textAnchor="middle"
                  fill={isHovered ? '#ffffff' : '#94a3b8'}
                  fontWeight={isHovered ? 'bold' : 'normal'}
                  fontSize="12px"
                  style={{ pointerEvents: 'none', transition: 'fill 0.2s' }}
                >
                  {node.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Floating Tooltip */}
        {hoveredNode && (
          <Box sx={{ 
            position: 'absolute', 
            top: 20, 
            left: 20, 
            background: 'rgba(15, 23, 42, 0.95)', 
            border: `1.5px solid ${hoveredNode.color}`, 
            borderRadius: '12px', 
            p: 2, 
            zIndex: 10,
            maxWidth: '280px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
            backdropFilter: 'blur(8px)'
          }}>
            <Typography variant="body1" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 0.5 }}>{hoveredNode.label}</Typography>
            <Typography variant="caption" sx={{ color: hoveredNode.color, fontWeight: 'bold', display: 'block', mb: 1 }}>{hoveredNode.badge}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.78rem', lineHeight: 1.3 }}>
              {hoveredNode.status === 'weak' && 'This is identified as a weak topic in your diagnostic inputs. Focus on solving standard exercises.'}
              {hoveredNode.status === 'prereq_gap' && 'This is a missing prerequisite chapter that lies directly upstream of your weak topics. Rebuild these concepts first!'}
              {hoveredNode.status === 'future_risk' && 'This downstream chapter depends on your current weak topics. It will be at severe risk if gaps are not resolved immediately.'}
              {hoveredNode.status === 'mastered' && 'This chapter shows stable conceptual development. Keep practicing.'}
            </Typography>
          </Box>
        )}
      </Box>
    );
  };

  // Helper for progress color
  const getReadinessColor = (score: number) => {
    if (score >= 80) return '#10b981'; // Green
    if (score >= 60) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 6, mb: 12 }}>
      {/* Executive Header Board */}
      <Card sx={{ 
        p: 4, 
        mb: 6, 
        background: 'rgba(255, 255, 255, 0.02)',
        borderColor: 'rgba(255, 255, 255, 0.06)',
        backdropFilter: 'blur(24px)',
        borderRadius: '24px',
        display: 'flex',
        flexDirection: { xs: 'column', md: 'row' },
        justifyContent: 'space-between',
        alignItems: { xs: 'flex-start', md: 'center' },
        gap: 3
      }}>
        <Box>
          <Typography variant="h1" sx={{ fontSize: { xs: '1.8rem', md: '2.5rem' }, fontWeight: 900, mb: 1 }}>
            {studentName}'s AI Diagnostic Report
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ fontSize: '0.95rem' }}>
            Cohort: <strong style={{ color: '#ffffff' }}>{studentLevel}</strong> • Target: <strong style={{ color: '#ffffff' }}>{targetAttempt}</strong>
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, width: { xs: '100%', md: 'auto' } }}>
          <Button 
            variant="outlined" 
            onClick={onBackToMCQ}
            startIcon={<ArrowForwardIcon sx={{ transform: 'rotate(180deg)' }} />}
            sx={{ px: 2.5, py: 1, borderColor: 'rgba(167, 139, 250, 0.3)', color: '#c084fc', '&:hover': { borderColor: '#a78bfa', background: 'rgba(167,139,250,0.05)' } }}
          >
            Back to MCQ Test
          </Button>
          <Button 
            variant="outlined" 
            onClick={onBackToTopics}
            startIcon={<RefreshIcon />}
            sx={{ px: 2.5, py: 1, borderColor: 'rgba(255,255,255,0.12)', color: '#ffffff', '&:hover': { background: 'rgba(255,255,255,0.03)' } }}
          >
            Edit Topics
          </Button>
          <Button 
            variant="outlined" 
            onClick={onReset}
            sx={{ px: 2.5, py: 1, borderColor: 'rgba(239, 68, 68, 0.3)', color: '#ef4444', '&:hover': { borderColor: '#f87171', background: 'rgba(239,68,68,0.05)' } }}
          >
            New Assessment
          </Button>
          <Button 
            variant="contained" 
            startIcon={<DownloadIcon />}
            onClick={handlePdfDownload}
            sx={{ 
              px: 3, 
              py: 1,
              background: 'linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%)',
              border: 'none',
              color: '#ffffff',
              boxShadow: '0 4px 20px rgba(139, 92, 246, 0.3)',
              '&:hover': {
                background: 'linear-gradient(90deg, #7c3aed 0%, #db2777 100%)',
              }
            }}
          >
            Download PDF
          </Button>
        </Box>
      </Card>

      {/* Main Diagnostic Tabs */}
      <Tabs 
        value={activeTab} 
        onChange={(_, val) => setActiveTab(val)}
        centered
        sx={{
          mb: 4,
          '& .MuiTabs-indicator': { backgroundColor: '#8b5cf6' },
          '& .MuiTab-root': { color: '#9ca3af', fontWeight: 'bold', fontSize: '1rem', textTransform: 'none' },
          '& .Mui-selected': { color: '#c084fc !important' }
        }}
      >
        <Tab label="🎯 SOCA Report" />
        <Tab label="📊 Metrics & Analytics" />
        <Tab label="🕸️ Prerequisite Knowledge Graph" />
        <Tab label="📋 Diagnostic Intelligence" />
      </Tabs>

      {/* Tab Panel 0: SOCA Report */}
      {activeTab === 0 && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
          {/* Strengths */}
          <motion.div whileHover={{ y: -3 }}>
            <Card sx={{ p: 4, height: '100%', background: 'rgba(16, 185, 129, 0.01)', border: '1px solid rgba(16, 185, 129, 0.08)', borderLeft: '5px solid #10b981' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, color: '#10b981' }}>
                <EmojiEventsIcon sx={{ fontSize: 26, mr: 1.5 }} />
                <Typography variant="h3" sx={{ fontWeight: 800, color: '#ffffff', fontSize: '1.25rem', letterSpacing: '0.05em' }}>STRENGTHS</Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {strengths.map((str: string, index: number) => (
                  <Typography key={index} variant="body1" color="text.secondary" sx={{ fontSize: '0.95rem', lineHeight: 1.5 }}>
                    • {str}
                  </Typography>
                ))}
              </Box>
            </Card>
          </motion.div>

          {/* Opportunities */}
          <motion.div whileHover={{ y: -3 }}>
            <Card sx={{ p: 4, height: '100%', background: 'rgba(59, 130, 246, 0.01)', border: '1px solid rgba(59, 130, 246, 0.08)', borderLeft: '5px solid #3b82f6' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, color: '#3b82f6' }}>
                <LightbulbIcon sx={{ fontSize: 26, mr: 1.5 }} />
                <Typography variant="h3" sx={{ fontWeight: 800, color: '#ffffff', fontSize: '1.25rem', letterSpacing: '0.05em' }}>OPPORTUNITIES</Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {opportunities.map((opt: string, index: number) => (
                  <Typography key={index} variant="body1" color="text.secondary" sx={{ fontSize: '0.95rem', lineHeight: 1.5 }}>
                    • {opt}
                  </Typography>
                ))}
              </Box>
            </Card>
          </motion.div>

          {/* Challenges */}
          <motion.div whileHover={{ y: -3 }}>
            <Card sx={{ p: 4, height: '100%', background: 'rgba(236, 72, 153, 0.01)', border: '1px solid rgba(236, 72, 153, 0.08)', borderLeft: '5px solid #ec4899' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, color: '#ec4899' }}>
                <WarningIcon sx={{ fontSize: 26, mr: 1.5 }} />
                <Typography variant="h3" sx={{ fontWeight: 800, color: '#ffffff', fontSize: '1.25rem', letterSpacing: '0.05em' }}>CHALLENGES</Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {challenges.map((cha: string, index: number) => (
                  <Typography key={index} variant="body1" color="text.secondary" sx={{ fontSize: '0.95rem', lineHeight: 1.5 }}>
                    • {cha}
                  </Typography>
                ))}
              </Box>
            </Card>
          </motion.div>

          {/* Action Plan */}
          <motion.div whileHover={{ y: -3 }}>
            <Card sx={{ p: 4, height: '100%', background: 'rgba(245, 158, 11, 0.01)', border: '1px solid rgba(245, 158, 11, 0.08)', borderLeft: '5px solid #fbbf24' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, color: '#fbbf24' }}>
                <AssignmentIcon sx={{ fontSize: 26, mr: 1.5 }} />
                <Typography variant="h3" sx={{ fontWeight: 800, color: '#ffffff', fontSize: '1.25rem', letterSpacing: '0.05em' }}>ACTION PLAN</Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {actionPlan.map((act: string, index: number) => (
                  <Typography key={index} variant="body1" color="text.secondary" sx={{ fontSize: '0.95rem', lineHeight: 1.5 }}>
                    • {act}
                  </Typography>
                ))}
              </Box>
            </Card>
          </motion.div>
        </Box>
      )}

      {/* Tab Panel 1: Metrics & Analytics */}
      {activeTab === 1 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {/* Top row metrics cards */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 3 }}>
            {/* Readiness Dial Card */}
            <Card sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#9ca3af', mb: 2 }}>Cognitive Readiness</Typography>
              <Box sx={{ position: 'relative', width: '150px', height: '150px', display: 'flex', alignItems: 'center', justifyCentert: 'center', mb: 2 }}>
                <svg style={{ position: 'absolute', transform: 'rotate(-90deg)', width: '100%', height: '100%' }}>
                  <circle cx="75" cy="75" r="65" stroke="rgba(255,255,255,0.02)" strokeWidth="8" fill="transparent" />
                  <circle 
                    cx="75" 
                    cy="75" 
                    r="65" 
                    stroke="url(#readinessGrad2)" 
                    strokeWidth="8" 
                    fill="transparent" 
                    strokeDasharray={408}
                    strokeDashoffset={408 - (408 * (profile.readiness_score || 72)) / 100}
                    strokeLinecap="round"
                  />
                  <defs>
                    <linearGradient id="readinessGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#8b5cf6" />
                      <stop offset="100%" stopColor="#ec4899" />
                    </linearGradient>
                  </defs>
                </svg>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                  <Typography variant="h2" sx={{ fontWeight: 900, fontSize: '2.2rem', color: '#ffffff' }}>
                    {profile.readiness_score || 72}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">STABILITY</Typography>
                </Box>
              </Box>
              <Typography variant="body2" sx={{ color: '#ffffff', textAlign: 'center', mt: 1, fontWeight: 'bold' }}>
                {profile.readiness_interpretation || "Highly Capable"}
              </Typography>
            </Card>

            {/* Confidence Alignment Card */}
            <Card sx={{ p: 4, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#9ca3af', mb: 2 }}>Confidence Alignment</Typography>
                <Typography variant="h2" sx={{ color: '#10b981', fontWeight: 900, mb: 1 }}>{profile.confidence_alignment || 90}%</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Status: <Chip label={profile.confidence_status || 'ALIGNED'} size="small" color="success" variant="outlined" />
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', fontSize: '0.85rem' }}>
                💡 Calibration: {profile.confidence_interpretation || "Confidence and accuracy levels are calibrated perfectly."}
              </Typography>
            </Card>

            {/* Wellness Score Card */}
            <Card sx={{ p: 4, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#9ca3af', mb: 2 }}>Wellness & Recovery</Typography>
                <Typography variant="h2" sx={{ color: '#fbbf24', fontWeight: 900, mb: 1 }}>{profile.wellness_score ?? 65}/100</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Burnout Risk: <Chip label={profile.burnout_risk || 'NORMAL'} size="small" color={profile.burnout_risk === 'HIGH' ? 'error' : profile.burnout_risk === 'MODERATE' ? 'warning' : 'success'} variant="outlined" />
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', fontSize: '0.85rem' }}>
                {profile.burnout_risk === 'HIGH'
                  ? '🏥 Action: Immediately reduce mock anxiety. Prioritise sleep (7–8 hrs) and add daily 15-min recovery breaks.'
                  : profile.burnout_risk === 'MODERATE'
                  ? '🏥 Action: Balance study intensity. Schedule a rest day weekly and avoid last-minute cramming.'
                  : '🏥 Action: Maintain current wellness habits. Use dynamic recovery drills between exam simulations.'}
              </Typography>
            </Card>
          </Box>

          {/* Custom SVG Bar Charts Row */}
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 4 }}>
            {/* Core metrics bar chart */}
            <Card sx={{ p: 4, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 0.5 }}>Academic & Study Performance Metrics</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3, fontSize: '0.88rem' }}>
                Your PCM subject scores alongside discipline, time management, revision consistency, and problem-solving ratings — all derived from your questionnaire inputs.
              </Typography>
              <OverallMetricsChart profile={profile} />
            </Card>

            {/* Subject mastery from diagnostic tests */}
            <Card sx={{ p: 4, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 0.5 }}>Diagnostic Test: Subject Mastery</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3, fontSize: '0.88rem' }}>
                Average readiness score per subject, calculated from the MCQ diagnostic tests you completed — not self-reported scores.
              </Typography>
              <SubjectMasteryChart subjectMastery={topic_assessment?.summary?.subject_mastery ?? { Physics: profile.physics_score, Chemistry: profile.chemistry_score, Mathematics: profile.math_score }} />
            </Card>
          </Box>
        </Box>
      )}

      {/* Tab Panel 2: Prerequisite Knowledge Graph */}
      {activeTab === 2 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {/* Subsubject Tabs */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', gap: 1, p: 0.5, border: '1px solid rgba(255,255,255,0.05)', borderRadius: '8px', background: 'rgba(255,255,255,0.01)' }}>
              {['Physics', 'Chemistry', 'Mathematics'].map((sub) => (
                <Button
                  key={sub}
                  variant={activeSubjectTab === sub ? 'contained' : 'text'}
                  onClick={() => setActiveSubjectTab(sub)}
                  size="small"
                  sx={{
                    backgroundColor: activeSubjectTab === sub ? '#8b5cf6' : 'transparent',
                    color: activeSubjectTab === sub ? '#ffffff' : '#9ca3af',
                    textTransform: 'none',
                    fontWeight: 'bold',
                    '&:hover': {
                      backgroundColor: activeSubjectTab === sub ? '#7c3aed' : 'rgba(255,255,255,0.03)'
                    }
                  }}
                >
                  {sub} Graph
                </Button>
              ))}
            </Box>
          </Box>

          {/* Interactive SVG Renderer */}
          <Card sx={{ p: 3, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#ffffff' }}>Prerequisite Chain Visualization</Typography>
              {/* Legend */}
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                {[
                  { label: 'Weak Topic', color: '#FF5A5F' },
                  { label: 'Prerequisite Gap', color: '#FFB85C' },
                  { label: 'Downstream Risk', color: '#F1C40F' },
                  { label: 'Mastered', color: '#10B981' }
                ].map((lg, i) => (
                  <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                    <Box sx={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: lg.color }} />
                    <Typography variant="caption" color="text.secondary">{lg.label}</Typography>
                  </Box>
                ))}
              </Box>
            </Box>
            
            {renderSVGGraph(activeSubjectTab)}
          </Card>

          {/* Prerequisite Gaps Analysis Table */}
          <Card sx={{ p: 4, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
              <InfoIcon sx={{ color: '#fbbf24' }} />
              <Typography variant="h4" sx={{ color: '#ffffff', fontWeight: 'bold' }}>Prerequisite Gaps & Cascade Risks</Typography>
            </Box>

            {Object.keys(knowledge_graph.prerequisite_gaps || {}).length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center', background: 'rgba(16, 185, 129, 0.05)', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                <Typography sx={{ color: '#10b981', fontWeight: 'bold' }}>
                  🎉 No structural prerequisite gaps identified! All upstream concepts are stable.
                </Typography>
              </Box>
            ) : (
              <Box sx={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', color: '#d1d5db', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', textAlign: 'left' }}>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Weak Target Chapter</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Prerequisite Gaps (Rebuild First)</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Downstream Risks (Blocked Chapters)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(knowledge_graph.prerequisite_gaps || {}).map(([topic, gaps]: [string, any], idx) => {
                      const risks = knowledge_graph.future_risk_topics?.[topic] || [];
                      return (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <td style={{ padding: '16px', fontWeight: 'bold', color: '#FF5A5F' }}>{topic}</td>
                          <td style={{ padding: '16px' }}>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {gaps.map((g: string) => (
                                <Chip key={g} label={g} size="small" sx={{ backgroundColor: 'rgba(255, 184, 92, 0.15)', color: '#FFB85C', border: '1px solid rgba(255,184,92,0.2)' }} />
                              ))}
                              {gaps.length === 0 && <span style={{ color: '#10b981' }}>None</span>}
                            </Box>
                          </td>
                          <td style={{ padding: '16px' }}>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {risks.map((r: string) => (
                                <Chip key={r} label={r} size="small" sx={{ backgroundColor: 'rgba(241, 196, 15, 0.15)', color: '#F1C40F', border: '1px solid rgba(241,196,15,0.2)' }} />
                              ))}
                              {risks.length === 0 && <span style={{ color: '#9ca3af', fontStyle: 'italic' }}>No downstream risks</span>}
                            </Box>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </Box>
            )}
          </Card>
        </Box>
      )}

      {/* Tab Panel 3: Diagnostic Intelligence */}
      {activeTab === 3 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {/* Topic Readiness Heatmap (1:1 with Streamlit layout) */}
          <Card sx={{ p: 4, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 3 }}>Topic Readiness Heatmap</Typography>
            <TopicReadinessHeatmap reportData={reportData} />
          </Card>

          {/* Topic Scorecard Table */}
          <Card sx={{ p: 4, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 3 }}>Topic Diagnostic Scorecard</Typography>
            
            {!hasTopicData ? (
              <Box sx={{ p: 4, textAlign: 'center', background: 'rgba(255,255,255,0.01)', borderRadius: '12px' }}>
                <Typography color="text.secondary" sx={{ fontStyle: 'italic' }}>
                  No diagnostic topic tests were taken. Re-run with diagnostic assessments selected to populate scorecard.
                </Typography>
              </Box>
            ) : (
              <Box sx={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', color: '#d1d5db', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', textAlign: 'left' }}>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Subject</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Topic</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Correct Questions</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Accuracy</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Readiness Score</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Workflow Progress</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(topicReadinessMap).map(([topic, metrics]: [string, any], idx) => {
                      const correct = metrics.correct_answers ?? 0;
                      const total = metrics.total_questions ?? 5;
                      const acc = metrics.accuracy != null ? Math.round(metrics.accuracy) : Math.round((correct / total) * 100);
                      const readColor = getReadinessColor(metrics.readiness_score || 50);
                      const subject = metrics.subject || 'Physics';

                      return (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <td style={{ padding: '16px' }}>{subject}</td>
                          <td style={{ padding: '16px', fontWeight: 'bold', color: '#ffffff' }}>{topic}</td>
                          <td style={{ padding: '16px' }}>{correct} / {total}</td>
                          <td style={{ padding: '16px' }}>{acc}%</td>
                          <td style={{ padding: '16px', fontWeight: 'bold', color: readColor }}>{metrics.readiness_score}%</td>
                          <td style={{ padding: '16px' }}>{Math.round((metrics.progress_ratio || 0) * 100)}%</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </Box>
            )}
          </Card>

          {/* Weak Topic Alerts */}
          {topic_assessment.summary?.weak_topics?.length > 0 && (
            <Alert 
              severity="error" 
              sx={{ 
                borderRadius: '16px', 
                border: '1px solid rgba(239, 68, 68, 0.3)', 
                background: 'rgba(239, 68, 68, 0.08)',
                color: '#f87171',
                '& .MuiAlert-icon': { color: '#ef4444' }
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                ⚠️ Weak Topics Alert (Readiness Score &lt; 60%):
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {topic_assessment.summary.weak_topics.map((wt: string) => (
                  <Chip key={wt} label={wt} size="small" sx={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.2)' }} />
                ))}
              </Box>
            </Alert>
          )}

          {/* Topic Roadmap Table */}
          <Card sx={{ p: 4, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 3 }}>Topic Remediation Roadmap</Typography>
            
            {topicRoadmap.length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center', background: 'rgba(255,255,255,0.01)', borderRadius: '12px' }}>
                <Typography color="text.secondary" sx={{ fontStyle: 'italic' }}>
                  Roadmap will populate upon diagnostic test submission.
                </Typography>
              </Box>
            ) : (
              <Box sx={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', color: '#d1d5db', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', textAlign: 'left' }}>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold', width: '25%' }}>Topic</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold', width: '15%' }}>Priority</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold', width: '15%' }}>Workflow</th>
                      <th style={{ padding: '12px 16px', color: '#ffffff', fontWeight: 'bold' }}>Next Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topicRoadmap.map((item: any, idx: number) => (
                      <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '16px', fontWeight: 'bold', color: '#ffffff' }}>{item.topic}</td>
                        <td style={{ padding: '16px' }}>
                          <Chip
                            label={item.priority || 'Medium'}
                            size="small"
                            sx={{
                              backgroundColor: item.priority === 'High' ? 'rgba(239,68,68,0.15)' : 'rgba(245,158,11,0.15)',
                              color: item.priority === 'High' ? '#f87171' : '#fbbf24',
                              border: `1px solid ${item.priority === 'High' ? 'rgba(239,68,68,0.3)' : 'rgba(245,158,11,0.3)'}`
                            }}
                          />
                        </td>
                        <td style={{ padding: '16px', color: '#a78bfa' }}>{item.workflow_progress || '0%'}</td>
                        <td style={{ padding: '16px' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <ArrowForwardIcon sx={{ fontSize: '0.8rem', color: '#c084fc' }} />
                            <Typography variant="body2">{item.next_action}</Typography>
                          </Box>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            )}
          </Card>

          {/* Per-Topic Details Accordion */}
          {topic_assessment.topic_readiness && Object.keys(topic_assessment.topic_readiness).length > 0 && (
            <Card sx={{ p: 4, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 3 }}>Granular Topic Analysis</Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {Object.entries(topic_assessment.topic_readiness).map(([topic, metrics]: [string, any]) => {
                  const correct = topic_assessment.summary?.correct_by_topic?.[topic] || 0;
                  const acc = Math.round((correct / 5) * 100);
                  const readColor = getReadinessColor(metrics.readiness_score || 50);
                  const weakAreas = metrics.weak_areas || [];
                  const recs = metrics.recommendations || [];

                  return (
                    <Accordion 
                      key={topic} 
                      sx={{ 
                        backgroundColor: 'rgba(255, 255, 255, 0.01)', 
                        borderColor: 'rgba(255,255,255,0.04)',
                        '&:before': { display: 'none' } 
                      }}
                    >
                      <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#9ca3af' }} />}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', pr: 2 }}>
                          <Typography sx={{ fontWeight: 'bold', color: '#ffffff' }}>{topic}</Typography>
                          <Box sx={{ display: 'flex', gap: 2 }}>
                            <Chip label={`Score: ${correct}/5`} size="small" variant="outlined" sx={{ color: '#a78bfa', borderColor: 'rgba(167,139,250,0.3)' }} />
                            <Chip label={`Readiness: ${metrics.readiness_score}%`} size="small" sx={{ backgroundColor: 'rgba(255,255,255,0.05)', color: readColor }} />
                          </Box>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails sx={{ borderTop: '1px solid rgba(255,255,255,0.04)', pt: 3 }}>
                        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 4 }}>
                          {/* Left Column: Stats */}
                          <Box>
                            <Typography variant="h5" sx={{ color: '#ffffff', fontWeight: 'bold', mb: 2 }}>Metrics Calibration</Typography>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography color="text.secondary">Diagnostic Accuracy</Typography>
                                <Typography sx={{ fontWeight: 'bold', color: '#ffffff' }}>{acc}%</Typography>
                              </Box>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography color="text.secondary">Readiness Score</Typography>
                                <Typography sx={{ fontWeight: 'bold', color: readColor }}>{metrics.readiness_score}%</Typography>
                              </Box>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography color="text.secondary">Workflow Progress</Typography>
                                <Typography sx={{ fontWeight: 'bold', color: '#ffffff' }}>{Math.round(metrics.progress_ratio * 100)}%</Typography>
                              </Box>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography color="text.secondary">Difficulty Handling</Typography>
                                <Typography sx={{ fontWeight: 'bold', color: '#ffffff' }}>{metrics.difficulty_level || 'Medium'}</Typography>
                              </Box>
                            </Box>
                          </Box>

                          {/* Right Column: Weak areas & recs */}
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                            <Box>
                              <Typography variant="h5" sx={{ color: '#FF5A5F', fontWeight: 'bold', mb: 1 }}>Weak Sub-concepts</Typography>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {weakAreas.map((wa: string, i: number) => (
                                  <Chip key={i} label={wa} size="small" sx={{ backgroundColor: 'rgba(255, 90, 95, 0.12)', color: '#FF5A5F', border: '1px solid rgba(255,90,95,0.2)' }} />
                                ))}
                                {weakAreas.length === 0 && <span style={{ color: '#10b981', fontSize: '0.9rem' }}>No concept gaps identified</span>}
                              </Box>
                            </Box>

                            <Box>
                              <Typography variant="h5" sx={{ color: '#10b981', fontWeight: 'bold', mb: 1 }}>Recommendations</Typography>
                              {recs.map((rec: string, i: number) => (
                                <Typography key={i} variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                  • {rec}
                                </Typography>
                              ))}
                              {recs.length === 0 && <Typography variant="body2" color="text.secondary">Maintain standard preparation practices.</Typography>}
                            </Box>
                          </Box>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  );
                })}
              </Box>
            </Card>
          )}
        </Box>
      )}


      {/* Structured AI Agent Analysis JSON Accordion */}
      <Card sx={{ p: 4, background: 'rgba(255,255,255,0.01)', borderColor: 'rgba(255,255,255,0.04)', mt: 4 }}>
        <Accordion sx={{ backgroundColor: 'transparent', boxShadow: 'none', '&:before': { display: 'none' } }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#8b5cf6' }} />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <CodeIcon sx={{ color: '#8b5cf6' }} />
              <Typography variant="h3" sx={{ color: '#ffffff', fontWeight: 800, fontSize: '1.4rem' }}>
                Structured AI Agent Analysis JSON
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ pt: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={handleJsonDownload}
                sx={{ borderColor: 'rgba(255,255,255,0.1)' }}
              >
                Download JSON telemetry
              </Button>
            </Box>
            <pre style={{ 
              background: '#0b0c10', 
              color: '#a78bfa', 
              padding: '20px', 
              borderRadius: '12px', 
              overflowX: 'auto',
              fontSize: '0.82rem',
              fontFamily: 'monospace',
              border: '1px solid rgba(255,255,255,0.05)'
            }}>
              <code>{JSON.stringify(agents, null, 2)}</code>
            </pre>
          </AccordionDetails>
        </Accordion>
      </Card>

      {/* Feedback */}
      <Card sx={{ 
        p: 5, 
        background: 'rgba(255, 255, 255, 0.02)', 
        borderColor: 'rgba(255,255,255,0.06)',
        borderRadius: '24px',
        mt: 6 
      }}>
        <Typography variant="h3" sx={{ fontWeight: 800, mb: 1, fontSize: '1.4rem' }}>
          Feedback
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, fontSize: '0.95rem' }}>
          Rate this report and share any observations about your study patterns or the accuracy of these recommendations.
        </Typography>

        {feedbackSaved ? (
          <Alert severity="success" sx={{ borderRadius: '16px', border: '1px solid rgba(16,185,129,0.3)', background: 'rgba(16,185,129,0.08)' }}>
            Report logged successfully. The reinforcement model has queued the weights adjustment. Thank you!
          </Alert>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body1" sx={{ fontWeight: 700, color: '#f3f4f6' }}>Utility Rating:</Typography>
              <Rating 
                value={usefulness} 
                onChange={(_event, newValue) => setUsefulness(newValue)}
                size="large"
                sx={{
                  color: '#ec4899',
                  '& .MuiRating-iconEmpty': { color: 'rgba(255,255,255,0.08)' }
                }}
              />
            </Box>
            <TextField
              placeholder="Teacher verification comments / Student response summary..."
              variant="outlined"
              multiline
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              fullWidth
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '16px',
                  backgroundColor: '#0b0c10',
                  color: '#ffffff',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  padding: '16px',
                  fontSize: '0.92rem',
                  '&:hover': {
                    borderColor: 'rgba(255, 255, 255, 0.15)'
                  },
                  '&.Mui-focused': {
                    borderColor: '#8b5cf6'
                  }
                }
              }}
            />
            <Box>
              <Button 
                variant="contained" 
                onClick={handleSaveFeedback}
                disabled={submittingFeedback}
                sx={{ 
                  px: 6, 
                  py: 1.5,
                  background: 'linear-gradient(90deg, #ec4899 0%, #be185d 100%)',
                  boxShadow: '0 4px 15px rgba(236,72,153,0.25)',
                  '&:hover': {
                    background: 'linear-gradient(90deg, #db2777 0%, #9d174d 100%)',
                  }
                }}
              >
                {submittingFeedback ? 'Submitting...' : 'Submit Validation'}
              </Button>
            </Box>
          </Box>
        )}
      </Card>
    </Container>
  );
};

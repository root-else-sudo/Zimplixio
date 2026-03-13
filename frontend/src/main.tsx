import '@xyflow/react/dist/style.css';
import { createRoot } from 'react-dom/client';
import { FrameworkAccordion } from './components/FrameworkAccordion';
import { AssessmentWizard } from './components/AssessmentWizard';

const container = document.getElementById('framework-root');
if (container) {
  createRoot(container).render(<FrameworkAccordion />);
}

const assessmentContainer = document.getElementById('assessment-root');
if (assessmentContainer) {
  createRoot(assessmentContainer).render(<AssessmentWizard />);
}

import '@xyflow/react/dist/style.css';
import { createRoot } from 'react-dom/client';
import { FrameworkAccordion } from './components/FrameworkAccordion';

const container = document.getElementById('framework-root');
if (container) {
  createRoot(container).render(<FrameworkAccordion />);
}

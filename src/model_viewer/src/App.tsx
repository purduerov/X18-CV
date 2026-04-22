import { ErrorBoundary } from '@/components/ErrorBoundary';
import { ModelScene } from '@/components/ModelScene';
import { ControlPanel } from '@/components/ControlPanel';

export default function App() {
  return (
    <ErrorBoundary>
      <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
        <ModelScene />
        <ControlPanel />
      </div>
    </ErrorBoundary>
  );
}

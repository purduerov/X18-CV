import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              background: '#1a1a2e',
              color: '#fff',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 24,
              fontFamily: 'monospace',
            }}
          >
            <div style={{ fontSize: 18, marginBottom: 12 }}>Something went wrong</div>
            <pre style={{ color: '#e94560', fontSize: 12, overflow: 'auto', maxWidth: '100%' }}>
              {this.state.error?.message}
            </pre>
          </div>
        )
      );
    }
    return this.props.children;
  }
}

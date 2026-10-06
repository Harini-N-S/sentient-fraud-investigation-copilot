import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { GlobalSearchModal } from './components/GlobalSearchModal';
import { EntityDrawer } from './components/EntityDrawer';
import { CopilotPage } from './pages/CopilotPage';

export function App() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Drawer State
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerEntityType, setDrawerEntityType] = useState<string>('alert');
  const [drawerEntityId, setDrawerEntityId] = useState<string>('');

  // Copilot Initial Question & Entity Focus
  const [copilotQuestion, setCopilotQuestion] = useState<string>('');
  const [copilotEntityType, setCopilotEntityType] = useState<string | undefined>(undefined);
  const [copilotEntityId, setCopilotEntityId] = useState<string | undefined>(undefined);

  const handleSelectEntity = (type: string, id: string) => {
    setDrawerEntityType(type);
    setDrawerEntityId(id);
    setIsDrawerOpen(true);
  };

  const handleSelectPrompt = (question: string, entityType?: string, entityId?: string) => {
    setCopilotQuestion(question);
    setCopilotEntityType(entityType);
    setCopilotEntityId(entityId);
  };

  return (
    <div className="app-container min-h-screen bg-bg-base text-text-primary flex flex-col font-sans selection:bg-accent-gold/20 selection:text-accent-gold">
      {/* Top Navigation Bar */}
      <Navbar
        onOpenSearch={() => setIsSearchOpen(true)}
        activeView="copilot"
        systemStatus="CONNECTED"
      />

      {/* Main Layout */}
      <div className="main-layout flex-1 flex overflow-hidden">
        {/* Left Forensic Case Scenarios Sidebar */}
        <Sidebar
          onSelectPrompt={handleSelectPrompt}
        />

        {/* Primary Investigation Console */}
        <main className="content-area flex-1 overflow-y-auto p-6 lg:p-8 bg-bg-base">
          <div className="workspace-inner max-w-7xl mx-auto">
            <CopilotPage
              initialQuestion={copilotQuestion}
              initialEntityType={copilotEntityType}
              initialEntityId={copilotEntityId}
              onSelectEntity={handleSelectEntity}
            />
          </div>
        </main>
      </div>

      {/* Global Search Modal (Ctrl+K) */}
      <GlobalSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectEntity={(entityType: string, entityId: string) => {
          handleSelectEntity(entityType, entityId);
        }}
      />

      {/* Slide-Over Entity & Evidence Drawer */}
      <EntityDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        entityType={drawerEntityType}
        entityId={drawerEntityId}
        onSelectEntity={handleSelectEntity}
        onInvestigateCopilot={(question, entityType, entityId) => {
          handleSelectPrompt(question, entityType, entityId);
          setIsDrawerOpen(false);
        }}
      />
    </div>
  );
}

export default App;

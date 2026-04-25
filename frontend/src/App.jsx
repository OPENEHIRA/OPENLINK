import React, { useEffect, useState } from 'react';
import { useStore } from './store';
import { io } from 'socket.io-client';
import { motion } from 'framer-motion';
import { Terminal, Send, Trash2, Cpu, Activity, Info } from 'lucide-react';

const socket = io();

export default function App() {
  const { status, setStatus, history, setHistory, addHistory, clearHistory } = useStore();
  const [command, setCommand] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    socket.on('status_update', (data) => {
      setStatus(data);
    });
    
    fetch('/api/history')
      .then(r => r.json())
      .then(data => setHistory(data.history || []))
      .catch(e => console.error(e));

    return () => socket.off('status_update');
  }, []);

  const handleExecute = async () => {
    if (!command.trim()) return;
    setLoading(true);
    
    try {
      // 1. Parse
      const parseRes = await fetch('/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      });
      const parsed = await parseRes.json();
      
      if (!parsed.action || parsed.action === 'unknown') {
        throw new Error("Could not understand command");
      }

      // 2. Execute
      const execRes = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed)
      });
      const executed = await execRes.json();
      
      addHistory({
        timestamp: new Date().toISOString(),
        command,
        parsed,
        result: executed.result
      });
      
      setCommand('');
    } catch (err) {
      console.error(err);
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    await fetch('/api/history/clear', { method: 'POST' });
    clearHistory();
  };

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto flex flex-col gap-8">
      {/* Header */}
      <header className="flex justify-between items-center pb-4 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent to-accent-2 flex items-center justify-center text-xl shadow-[0_0_15px_rgba(168,255,120,0.3)]">
            🦾
          </div>
          <h1 className="text-xl font-semibold tracking-tight text-text-main">OpenGuy</h1>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-border text-xs text-text-3 font-mono">
          <div className={`w-2 h-2 rounded-full ${status?.connected ? 'bg-accent shadow-[0_0_8px_var(--color-accent)]' : 'bg-red-main'}`} />
          {status?.connected ? 'SYSTEM LIVE' : 'OFFLINE'}
        </div>
      </header>

      {/* Main Content */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Col: Controls & Status */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <section className="text-center py-6">
            <h2 className="text-4xl font-light tracking-tight text-text-main mb-3">
              Natural <strong className="font-semibold bg-gradient-to-r from-accent to-accent-2 text-transparent bg-clip-text">Robot Control</strong>
            </h2>
            <p className="text-text-2 text-sm max-w-md mx-auto">
              Type an instruction in plain English. The AI parser will translate it into deterministic robotic actions.
            </p>
          </section>

          {/* Input Box */}
          <div className="glass-panel p-2 rounded-2xl flex items-center gap-3 focus-within:border-accent/40 focus-within:shadow-[0_0_30px_var(--color-accent-dim)] transition-all">
            <Terminal className="text-text-3 ml-3 w-5 h-5" />
            <input 
              className="flex-1 bg-transparent border-none outline-none text-text-main font-mono py-3"
              placeholder="e.g. Move forward 10cm and rotate left..."
              value={command}
              onChange={e => setCommand(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleExecute()}
              disabled={loading}
            />
            <button 
              onClick={handleExecute}
              disabled={loading || !command.trim()}
              className="bg-accent text-black px-6 py-3 rounded-xl font-semibold text-sm hover:shadow-[0_0_20px_var(--color-accent-glow)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }}>
                  <Activity className="w-4 h-4" />
                </motion.div>
              ) : (
                <>Execute <Send className="w-4 h-4" /></>
              )}
            </button>
          </div>

          {/* History */}
          <div className="flex flex-col gap-4 mt-4">
            <div className="flex justify-between items-center">
              <span className="text-xs font-mono text-text-3 tracking-widest uppercase">Execution Log</span>
              <button onClick={handleClear} className="text-xs font-mono text-text-3 hover:text-red-main transition-colors flex items-center gap-1">
                <Trash2 className="w-3 h-3" /> Clear
              </button>
            </div>

            <div className="flex flex-col gap-3">
              {history.length === 0 && (
                <div className="text-center py-10 border border-dashed border-border rounded-xl text-text-3 font-mono text-sm">
                  No commands yet.
                </div>
              )}
              {history.map((item, idx) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={idx} 
                  className="glass-panel p-4 rounded-xl flex flex-col gap-3"
                >
                  <div className="flex justify-between items-start">
                    <span className="font-mono text-text-main text-sm">"{item.command}"</span>
                    <span className="text-xs font-mono px-2 py-1 bg-surface-2 rounded text-accent">
                      {Math.round(item.parsed?.confidence * 100)}% Conf
                    </span>
                  </div>
                  <div className="flex gap-2 font-mono text-xs text-text-3">
                    <span className="text-accent-2">ACT: {item.parsed?.action}</span>
                    {item.parsed?.direction && <span>DIR: {item.parsed.direction}</span>}
                    {item.parsed?.distance_cm && <span>DIST: {item.parsed.distance_cm}cm</span>}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Status Panel */}
        <div className="flex flex-col gap-4">
          <div className="glass-panel p-5 rounded-2xl flex flex-col gap-4">
            <h3 className="text-xs font-mono text-text-3 tracking-widest uppercase flex items-center gap-2">
              <Cpu className="w-4 h-4" /> Hardware Status
            </h3>
            
            {status ? (
              <div className="flex flex-col gap-3 font-mono text-sm text-text-2">
                <div className="flex justify-between">
                  <span>Connection:</span>
                  <span className={status.connected ? "text-accent" : "text-red-main"}>
                    {status.connected ? "Active" : "Disconnected"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Backend:</span>
                  <span className="text-text-main">{status.backend}</span>
                </div>
                <div className="flex justify-between">
                  <span>X Coord:</span>
                  <span className="text-accent-2">{status.position?.x?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Y Coord:</span>
                  <span className="text-accent-2">{status.position?.y?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Z Coord:</span>
                  <span className="text-accent-2">{status.position?.z?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Gripper:</span>
                  <span className="text-text-main">{status.gripper_state}</span>
                </div>
              </div>
            ) : (
              <div className="text-text-3 font-mono text-sm animate-pulse">Loading status...</div>
            )}
          </div>
          
          <div className="glass-panel p-5 rounded-2xl flex flex-col gap-4">
             <h3 className="text-xs font-mono text-text-3 tracking-widest uppercase flex items-center gap-2">
              <Info className="w-4 h-4" /> Workspace SVG
            </h3>
            <div className="aspect-square bg-surface border border-border rounded-xl flex items-center justify-center overflow-hidden p-2">
              {/* Load SVG from backend */}
              <img src="/api/visualize" alt="Robot Workspace" className="w-full h-full object-contain filter invert opacity-80 mix-blend-screen" />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

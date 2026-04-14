import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, Shield, Zap, Sparkles, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

export interface StatusUpdate {
  stage: string;
  agent: string;
  timestamp: number;
}

interface TaskProgressOverlayProps {
  isVisible: boolean;
  totalDuration: number; // in seconds
  statusUpdates: StatusUpdate[];
  taskType: string;
  onClose?: () => void;
}

const TaskProgressOverlay: React.FC<TaskProgressOverlayProps> = ({
  isVisible,
  totalDuration,
  statusUpdates,
  taskType,
  onClose
}) => {
  const [progress, setProgress] = useState(0);
  const [timeLeft, setTimeLeft] = useState(totalDuration);

  // Time-based progress simulation
  useEffect(() => {
    if (!isVisible) {
      setProgress(0);
      setTimeLeft(totalDuration);
      return;
    }

    const interval = 1000; // 1 second
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        const next = Math.max(0, prev - 1);
        const elapsed = totalDuration - next;
        const newProgress = Math.min(99, (elapsed / totalDuration) * 100);
        setProgress(newProgress);
        return next;
      });
    }, interval);

    return () => clearInterval(timer);
  }, [isVisible, totalDuration]);

  const formattedTime = useMemo(() => {
    const mins = Math.floor(timeLeft / 60);
    const secs = timeLeft % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, [timeLeft]);

  const currentStatus = statusUpdates[statusUpdates.length - 1];

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-background/40 backdrop-blur-xl p-4 md:p-6"
        >
          {/* Main Glass Card */}
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            className="w-full max-w-2xl bg-card/60 border border-border/50 shadow-[0_0_50px_rgba(var(--primary-rgb),0.1)] rounded-3xl overflow-hidden glassmorphism"
          >
            <div className="p-8 md:p-12 flex flex-col items-center text-center">
              {/* Premium Glow Icon */}
              <div className="relative mb-8">
                <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full animate-pulse" />
                <div className="relative h-20 w-20 flex items-center justify-center bg-primary/10 border border-primary/20 rounded-2xl">
                  {currentStatus?.agent?.includes('Smart') ? (
                    <Sparkles className="h-10 w-10 text-primary animate-pulse" />
                  ) : (
                    <Zap className="h-10 w-10 text-primary animate-pulse" />
                  )}
                </div>
              </div>

              {/* Header */}
              <h2 className="text-3xl font-bold tracking-tight mb-2 bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-400 to-emerald-400">
                AI Agent Processing
              </h2>
              <p className="text-muted-foreground text-sm uppercase tracking-widest font-medium mb-8">
                {taskType.replace('-', ' ')}
              </p>

              {/* Progress Bar Group */}
              <div className="w-full mb-10">
                <div className="flex justify-between items-end mb-3">
                  <div className="text-left">
                    <p className="text-sm font-semibold text-primary flex items-center gap-2">
                       <Clock className="h-4 w-4" />
                       Est. Completion: <span className="text-lg font-mono">{formattedTime}</span>
                    </p>
                  </div>
                  <p className="text-sm font-bold text-muted-foreground">{Math.round(progress)}%</p>
                </div>
                <div className="relative h-3 w-full bg-muted/30 rounded-full overflow-hidden border border-border/10">
                   <motion.div 
                     className="absolute left-0 top-0 h-full bg-gradient-to-r from-primary to-emerald-500 shadow-[0_0_15px_rgba(var(--primary-rgb),0.5)]"
                     animate={{ width: `${progress}%` }}
                     transition={{ duration: 1, ease: "linear" }}
                   />
                </div>
              </div>

              {/* Live Agent Activity Feed */}
              <div className="w-full bg-black/10 dark:bg-white/5 rounded-2xl p-6 border border-border/20 text-left">
                <div className="flex items-center gap-3 mb-4">
                  <div className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                  <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Live Agent Logs</span>
                </div>
                
                <div className="space-y-4 max-h-[160px] overflow-y-auto pr-2 custom-scrollbar">
                  <AnimatePresence initial={false}>
                    {statusUpdates.slice().reverse().map((status, idx) => (
                      <motion.div
                        key={`${status.timestamp}-${status.stage}`}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-start gap-4"
                      >
                         <div className={cn(
                           "flex-shrink-0 mt-1 h-5 w-5 rounded-full flex items-center justify-center",
                           idx === 0 ? "bg-primary/20 text-primary" : "text-muted-foreground/40"
                         )}>
                           {idx === 0 ? (
                             <Loader2 className="h-3 w-3 animate-spin" />
                           ) : (
                             <CheckCircle2 className="h-4 w-4" />
                           )}
                         </div>
                         <div className="flex-1">
                           <p className={cn(
                             "text-sm font-medium",
                             idx === 0 ? "text-foreground" : "text-muted-foreground"
                           )}>
                             {status.stage}
                           </p>
                           <p className="text-[10px] text-muted-foreground/60 uppercase tracking-tighter">
                             Agent: {status.agent}
                           </p>
                         </div>
                         <span className="text-[10px] text-muted-foreground/30 font-mono">
                           {new Date(status.timestamp).toLocaleTimeString([], { hour12: false, minute: '2-digit', second: '2-digit' }).split(' ')[0]}
                         </span>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  
                  {statusUpdates.length === 0 && (
                     <p className="text-sm text-muted-foreground/40 italic">Waiting for agents to report status...</p>
                  )}
                </div>
              </div>

              {/* Footer Tip */}
              <div className="mt-8 flex items-center gap-2 text-[10px] text-muted-foreground/60">
                 <Shield className="h-3 w-3" />
                 <span>Secure end-to-end legal processing powered by NVIDIA NIM</span>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default TaskProgressOverlay;

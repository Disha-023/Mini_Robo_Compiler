import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import CodeEditor from './components/CodeEditor';
import RobotScene from './components/RobotScene';
import RobotTelemetry from './components/RobotTelemetry';
import SimulationControls from './components/SimulationControls';
import CompilerOutput from './components/CompilerOutput';
import AboutModal from './components/AboutModal';
import { checkHealth, fetchExamples, runCode } from './services/api';

const DEFAULT_PROGRAM = `START
PEN_DOWN
REPEAT 4 {
    MOVE 4
    TURN RIGHT
}
PEN_UP
POSITION
STOP`;

const FALLBACK_EXAMPLES = {
  square: {
    title: 'Square Drawing (REPEAT Loop)',
    code: DEFAULT_PROGRAM,
  },
  basic_movement: {
    title: 'Basic Movement & Coordinates',
    code: `START
PEN_DOWN
MOVE 5
TURN RIGHT
MOVE 3
PEN_UP
MOVE 2
POSITION
STOP`,
  },
  variables: {
    title: 'Variables & Arithmetic',
    code: `START
LET side = 3
LET multiplier = 2
LET total_steps = side * multiplier
SPEED 2
PEN_DOWN
MOVE total_steps
TURN LEFT
MOVE side
PEN_UP
POSITION
STOP`,
  },
  if_else: {
    title: 'Conditionals (IF / ELSE)',
    code: `START
LET speed_mode = 2
IF speed_mode > 1 {
    PRINT "High speed navigation"
    SPEED 2
    PEN_DOWN
    MOVE 6
} ELSE {
    PRINT "Standard navigation"
    SPEED 1
    PEN_DOWN
    MOVE 3
}
TURN RIGHT
MOVE 2
PEN_UP
STOP`,
  },
  while_loop: {
    title: 'WHILE Loop Spiral',
    code: `START
LET steps = 1
PEN_DOWN
WHILE steps <= 5 {
    MOVE steps
    TURN RIGHT
    steps = steps + 1
}
PEN_UP
POSITION
STOP`,
  },
  functions: {
    title: 'Function Definition & Calls',
    code: `START
FUNC draw_corner(length) {
    MOVE length
    TURN RIGHT
    MOVE length
}

PEN_DOWN
draw_corner(3)
TURN RIGHT
draw_corner(3)
PEN_UP
POSITION
STOP`,
  },
  pen_art: {
    title: 'Pen UP / DOWN Stitched Line',
    code: `START
REPEAT 3 {
    PEN_DOWN
    MOVE 3
    PEN_UP
    MOVE 2
}
POSITION
STOP`,
  },
  obstacle_avoidance: {
    title: 'Obstacle Sensor Check',
    code: `START
IF OBSTACLE_AHEAD {
    PRINT "Obstacle detected ahead! Reversing..."
    BACK 2
    TURN RIGHT
} ELSE {
    PRINT "Path is clear. Proceeding forward."
    PEN_DOWN
    MOVE 4
    PEN_UP
}
POSITION
STOP`,
  },
};

export default function App() {
  const [code, setCode] = useState(DEFAULT_PROGRAM);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking' | 'online' | 'offline'
  const [isRunning, setIsRunning] = useState(false);
  const [examples, setExamples] = useState(FALLBACK_EXAMPLES);
  const [selectedExample, setSelectedExample] = useState('square');
  const [aboutOpen, setAboutOpen] = useState(false);

  // Compilation Results State
  const [compilerResult, setCompilerResult] = useState({
    tokens: [],
    ast: null,
    ir: [],
    ir_formatted: [],
    generated_code: [],
    generated_code_raw: '',
    output: '',
    robot_history: [],
    final_state: null,
    errors: [],
  });

  // Animation & Playback State
  const [playbackState, setPlaybackState] = useState({
    isPlaying: false,
    speedMultiplier: 1.0,
    currentEventIndex: 0,
  });

  // Live Telemetry from 3D Kinematics
  const [telemetry, setTelemetry] = useState({
    currentPos: { x: 0, y: 0 },
    direction: 'NORTH',
    penDown: false,
    speed: 1,
    currentEvent: null,
    progressFraction: 0,
    eventIndex: 0,
  });

  const [activeOutputTab, setActiveOutputTab] = useState('output');

  // Check backend health on mount and periodically
  useEffect(() => {
    let isMounted = true;
    const check = async () => {
      const res = await checkHealth();
      if (isMounted) {
        setBackendStatus(res.status === 'ok' ? 'online' : 'offline');
      }
    };

    check();
    const interval = setInterval(check, 6000);

    // Fetch server examples if available
    fetchExamples().then((data) => {
      if (data?.examples && isMounted) {
        setExamples(data.examples);
      }
    });

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Run Program Handler
  const handleRun = useCallback(async () => {
    if (isRunning) return;
    setIsRunning(true);
    setPlaybackState((prev) => ({ ...prev, isPlaying: false }));

    const res = await runCode(code);
    setIsRunning(false);
    setCompilerResult(res);

    if (res.success) {
      // Auto-switch to output or IR if output is empty
      if (res.output && res.output.trim()) {
        setActiveOutputTab('output');
      } else {
        setActiveOutputTab('ir');
      }
      // Start 3D robot animation replay
      setPlaybackState((prev) => ({
        ...prev,
        isPlaying: true,
        currentEventIndex: 0,
      }));
    } else {
      setActiveOutputTab('errors');
    }
  }, [code, isRunning]);

  // Reset Everything
  const handleReset = useCallback(() => {
    setPlaybackState({
      isPlaying: false,
      speedMultiplier: 1.0,
      currentEventIndex: 0,
    });
    setCompilerResult({
      tokens: [],
      ast: null,
      ir: [],
      ir_formatted: [],
      generated_code: [],
      generated_code_raw: '',
      output: '',
      robot_history: [],
      final_state: null,
      errors: [],
    });
    setTelemetry({
      currentPos: { x: 0, y: 0 },
      direction: 'NORTH',
      penDown: false,
      speed: 1,
      currentEvent: null,
      progressFraction: 0,
      eventIndex: 0,
    });
  }, []);

  // Replay without recompiling
  const handleReplay = useCallback(() => {
    if (!compilerResult.robot_history.length) return;
    setPlaybackState((prev) => ({
      ...prev,
      isPlaying: true,
      currentEventIndex: 0,
    }));
  }, [compilerResult.robot_history]);

  // Load Example Program
  const handleSelectExample = (key) => {
    setSelectedExample(key);
    if (examples[key]) {
      setCode(examples[key].code);
      handleReset();
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#070a12] text-slate-100 selection:bg-cyan-500 selection:text-black">
      {/* Top Navigation Header */}
      <Header
        backendStatus={backendStatus}
        isRunning={isRunning}
        onRun={handleRun}
        onReset={handleReset}
        selectedExample={selectedExample}
        onSelectExample={handleSelectExample}
        examples={examples}
        onOpenAbout={() => setAboutOpen(true)}
      />

      {/* Main Workspace Dashboard */}
      <main className="flex-1 max-w-[1920px] w-full mx-auto p-3 flex flex-col gap-3">
        {/* Top 3-Panel Grid: Code Editor | 3D Simulation | Telemetry */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 min-h-[520px]">
          {/* Left Panel: Code Editor (3.5 cols on large screens) */}
          <section className="lg:col-span-4 xl:col-span-4 h-[460px] lg:h-full flex flex-col">
            <CodeEditor code={code} onChange={setCode} onRun={handleRun} />
          </section>

          {/* Center Panel: 3D Robot Simulator Scene (5.5 cols on large screens) */}
          <section className="lg:col-span-5 xl:col-span-5 h-[460px] lg:h-full flex flex-col gap-2">
            <div className="flex-1 relative">
              <RobotScene
                history={compilerResult.robot_history}
                finalState={compilerResult.final_state}
                playbackState={playbackState}
                onProgressUpdate={setTelemetry}
                onPlaybackComplete={() => {
                  setPlaybackState((prev) => ({ ...prev, isPlaying: false }));
                }}
              />
            </div>
            {/* Simulation Playback Bar */}
            <SimulationControls
              isPlaying={playbackState.isPlaying}
              isFinished={
                compilerResult.robot_history.length > 0 &&
                telemetry.eventIndex >= compilerResult.robot_history.length
              }
              hasHistory={compilerResult.robot_history.length > 0}
              onPlay={() => setPlaybackState((prev) => ({ ...prev, isPlaying: true }))}
              onPause={() => setPlaybackState((prev) => ({ ...prev, isPlaying: false }))}
              onReplay={handleReplay}
              onReset={handleReset}
              speedMultiplier={playbackState.speedMultiplier}
              onSpeedChange={(speed) =>
                setPlaybackState((prev) => ({ ...prev, speedMultiplier: speed }))
              }
            />
          </section>

          {/* Right Panel: Robot Telemetry & Kinematics (3 cols on large screens) */}
          <section className="lg:col-span-3 xl:col-span-3 h-[460px] lg:h-full flex flex-col">
            <RobotTelemetry
              telemetry={telemetry}
              finalState={compilerResult.final_state}
              isFinished={
                compilerResult.robot_history.length > 0 &&
                telemetry.eventIndex >= compilerResult.robot_history.length
              }
              totalEvents={compilerResult.robot_history.length}
            />
          </section>
        </div>

        {/* Bottom Panel: Compiler Output & Analysis Tabs */}
        <section className="h-[260px] min-h-[200px]">
          <CompilerOutput
            tokens={compilerResult.tokens}
            ast={compilerResult.ast}
            ir={compilerResult.ir}
            irFormatted={compilerResult.ir_formatted}
            generatedCode={compilerResult.generated_code}
            generatedCodeRaw={compilerResult.generated_code_raw}
            output={compilerResult.output}
            errors={compilerResult.errors}
            activeTab={activeOutputTab}
            onTabChange={setActiveOutputTab}
          />
        </section>
      </main>

      {/* About Project Dialog */}
      <AboutModal isOpen={aboutOpen} onClose={() => setAboutOpen(false)} />
    </div>
  );
}

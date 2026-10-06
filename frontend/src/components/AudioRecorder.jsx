import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Upload, Trash2, Play, Pause, Radio, Disc } from 'lucide-react';

export default function AudioRecorder({ onAudioReady, audioFile }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const audioPlayerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, []);

  const drawWaveform = () => {
    if (!analyserRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const renderFrame = () => {
      analyserRef.current.getByteTimeDomainData(dataArray);
      ctx.fillStyle = 'rgba(6, 9, 17, 0.6)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.lineWidth = 3;
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
      gradient.addColorStop(0, '#06b6d4');  // Cyan
      gradient.addColorStop(0.5, '#10b981'); // Emerald
      gradient.addColorStop(1, '#8b5cf6');  // Purple
      ctx.strokeStyle = gradient;
      ctx.beginPath();

      const sliceWidth = (canvas.width * 1.0) / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);

        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();

      animationFrameRef.current = requestAnimationFrame(renderFrame);
    };

    renderFrame();
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        const file = new File([blob], 'humming_recording.wav', { type: 'audio/wav' });
        setAudioUrl(url);
        onAudioReady(file, url);

        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      drawWaveform();

      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      alert('Microphone access denied or unavailable: ' + err.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      onAudioReady(file, url);
    }
  };

  const clearAudio = () => {
    setAudioUrl(null);
    onAudioReady(null, null);
    setIsPlaying(false);
  };

  const togglePlayback = () => {
    if (!audioPlayerRef.current) return;
    if (isPlaying) {
      audioPlayerRef.current.pause();
      setIsPlaying(false);
    } else {
      audioPlayerRef.current.play();
      setIsPlaying(true);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="glass-panel rounded-3xl p-6 md:p-7 border border-white/10 shadow-2xl relative overflow-hidden">
      
      {/* Card Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-inner">
            <Mic className="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">Humming Voice Recorder</h3>
            <p className="text-xs text-slate-400">Live Microphone Input & Audio File Upload</p>
          </div>
        </div>

        {isRecording && (
          <span className="flex items-center space-x-2 text-xs text-rose-400 font-mono font-bold px-3 py-1.5 rounded-full bg-rose-500/10 border border-rose-500/30 animate-pulse">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            <span>REC {formatTime(recordingTime)}</span>
          </span>
        )}
      </div>

      {/* Visualizer Canvas Deck */}
      <div className="relative rounded-2xl overflow-hidden bg-slate-950/90 border border-white/10 mb-6 h-36 flex items-center justify-center shadow-inner group">
        <canvas ref={canvasRef} className="w-full h-full absolute inset-0" width={600} height={144} />

        {!isRecording && !audioUrl && (
          <div className="text-center z-10 space-y-1.5 px-4">
            <Radio className="w-8 h-8 text-cyan-400/60 mx-auto animate-bounce" />
            <p className="text-sm font-semibold text-slate-300">
              Press <span className="text-cyan-400 font-extrabold">Record Humming</span> or upload a WAV/MP3 track
            </p>
            <p className="text-[11px] text-slate-500">Optimal pitch tracking at 22.05 kHz sample rate</p>
          </div>
        )}
      </div>

      {/* Control Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="flex items-center justify-center space-x-2.5 py-4 rounded-xl bg-gradient-to-r from-cyan-500 via-teal-400 to-emerald-400 hover:from-cyan-400 hover:to-emerald-300 text-slate-950 font-extrabold shadow-lg shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5 cursor-pointer"
          >
            <Mic className="w-5 h-5 stroke-[2.5]" />
            <span>Record Humming</span>
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex items-center justify-center space-x-2.5 py-4 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-extrabold shadow-lg shadow-rose-600/30 transition-all cursor-pointer"
          >
            <Square className="w-5 h-5 fill-current" />
            <span>Stop Recording</span>
          </button>
        )}

        <label className="flex items-center justify-center space-x-2.5 py-4 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-white/10 hover:border-cyan-500/40 text-slate-200 font-bold transition-all cursor-pointer group shadow-sm">
          <Upload className="w-5 h-5 text-slate-400 group-hover:text-cyan-400 transition" />
          <span>Upload Audio File</span>
          <input type="file" accept="audio/*" onChange={handleFileUpload} className="hidden" />
        </label>
      </div>

      {/* Recorded Preview Bar */}
      {audioUrl && (
        <div className="mt-5 p-4 rounded-xl bg-slate-900/90 border border-white/10 flex items-center justify-between shadow-lg">
          <div className="flex items-center space-x-3.5">
            <button
              onClick={togglePlayback}
              className="p-3 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-400 text-slate-950 hover:scale-105 transition shadow-md"
            >
              {isPlaying ? <Pause className="w-4 h-4 stroke-[3]" /> : <Play className="w-4 h-4 fill-current" />}
            </button>
            <div>
              <p className="text-xs font-bold text-white flex items-center space-x-2">
                <span>Recorded Humming Track</span>
                <span className="px-1.5 py-0.5 text-[9px] rounded bg-cyan-500/20 text-cyan-300 font-mono">READY</span>
              </p>
              <p className="text-[11px] text-slate-400 font-mono truncate max-w-[200px]">
                {audioFile?.name || 'humming_recording.wav'}
              </p>
            </div>
          </div>

          <button onClick={clearAudio} className="p-2 text-slate-500 hover:text-rose-400 transition">
            <Trash2 className="w-4 h-4" />
          </button>

          <audio
            ref={audioPlayerRef}
            src={audioUrl}
            onEnded={() => setIsPlaying(false)}
            className="hidden"
          />
        </div>
      )}
    </div>
  );
}

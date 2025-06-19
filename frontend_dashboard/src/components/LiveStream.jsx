import { useEffect, useRef } from "react";

const LiveStream = ({ logs }) => {
  const bottomRef = useRef();

  useEffect(() => {
    if (autoScroll) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

const [autoScroll, setAutoScroll] = useState(true);
  const liveLogs = [...logs]
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .slice(-20); // show only last 20

  return (
    <div className="bg-black text-green-400 font-mono text-xs p-4 h-64 overflow-y-auto rounded shadow">
      {liveLogs.map((log, index) => (
        <div key={index}>
          <span className="text-gray-400">{log.timestamp}</span> → {log.raw}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
};

export default LiveStream;


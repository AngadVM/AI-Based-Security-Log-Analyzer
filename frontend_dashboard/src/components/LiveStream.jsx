import React, { useEffect, useState } from "react";

function LiveStream() {
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/logs");

    socket.onmessage = (event) => {
      const log = JSON.parse(event.data);
      setMessages(prev => [log, ...prev.slice(0, 50)]); // show last 50
    };

    socket.onerror = (err) => {
      console.error("❌ WebSocket error", err);
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed.");
    };

    return () => {
      socket.close();
    };
  }, []);

  return (
    <div className="bg-gray-800 text-white p-4 rounded h-64 overflow-y-scroll">
      <h2 className="text-lg font-bold mb-2">Live Log Stream</h2>
      {messages.map((msg, idx) => (
        <div key={idx} className="mb-1">
          <div className="text-xs text-gray-400">{msg.timestamp}</div>
          <div className="text-sm">{msg.raw}</div>
          <div className={`text-sm font-bold ${msg.prediction === "anomaly" ? "text-red-500" : "text-green-400"}`}>
            {msg.prediction.toUpperCase()} ({msg.threat_type})
          </div>
        </div>
      ))}
    </div>
  );
}

export default LiveStream;


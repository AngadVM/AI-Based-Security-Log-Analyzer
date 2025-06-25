
// src/components/LiveStream.jsx
import { useEffect } from "react";

function LiveStream({ onNewLog }) {
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/logs");

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onNewLog(data);  // 👈 callback to push to App state
    };

    return () => socket.close();
  }, []);

  return null; // no UI
}

export default LiveStream;


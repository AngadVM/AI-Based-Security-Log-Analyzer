import { useEffect, useState } from "react";
import axios from "axios";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';


function App() {
  // Initialize logs as an empty array
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState(null);
  const [timeFilter, setTimeFilter] = useState("all");

  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://localhost:8000/logs", {
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      });
      console.log("Fetched logs:", res.data);
      // Ensure that we always set logs as an array
      if (Array.isArray(res.data)) {
        setLogs(res.data);
      } else {
        console.warn("Response is not an array; resetting logs to empty.", res.data);
        setLogs([]);
      }
      setError(null);
    } catch (err) {
      console.error("Error fetching logs:", err);
      setError(err.message || "Unknown error");
      setLogs([]);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 10000); // Fetch every 10 seconds
    return () => clearInterval(interval); // Clean up on unmount
  }, []);

  const now = new Date();

  const filterByTime = (log) => {
    if (!log.timestamp) return false;

    const logTime = new Date(log.timestamp);

    switch (timeFilter) {
      case "5m":
        return now - logTime <= 5 * 60 * 1000; // last 5 minutes
      case "1h":
        return now - logTime <= 60 * 60 * 1000; // last hour
      case "today":
        return now.toDateString() === logTime.toDateString(); // same calendar day
      default:
        return true; // 'all'
    }
  };
  // Filter logs based on both the filter type and search query
  const filteredLogs = Array.isArray(logs)
    ? logs.filter((log) =>
        (filter === "all" || log.prediction === filter) &&
        (searchQuery === "" || (log.raw && log.raw.toLowerCase().includes(searchQuery.toLowerCase()))) &&
        filterByTime(log)
      )
    : [];

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4">Security Log Dashboard</h1>

      {error && (
        <div className="mb-4 p-2 bg-red-100 text-red-800 rounded">
          Error: {error}
        </div>
      )}

      {/* Search input */}
      <input
        type="text"
        placeholder="Search logs..."
        value={searchQuery}
        onChange={e => setSearchQuery(e.target.value)}
        className="mb-4 p-2 border border-gray-300 rounded w-full"
      />

      <div className="flex gap-4 mb-4">
        <button onClick={() => setFilter("all")} className="px-4 py-2 bg-blue-500 text-white rounded">
          All
        </button>
        <button onClick={() => setFilter("normal")} className="px-4 py-2 bg-green-600 text-white rounded">
          Normal
        </button>
        <button onClick={() => setFilter("anomaly")} className="px-4 py-2 bg-red-600 text-white rounded">
          Anomaly
        </button>
      </div>

      {/* Anomaly Summary Chart */}
      <div className="bg-white p-4 rounded shadow mb-6">
        <h2 className="text-lg font-semibold mb-2">Anomaly Breakdown</h2>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={[
                { name: "Anomaly", value: logs.filter(log => log.prediction === "anomaly").length },
                { name: "Normal", value: logs.filter(log => log.prediction === "normal").length },
              ]}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
        >
          <Cell fill="#EF4444" /> {/* red for anomaly */}
          <Cell fill="#22C55E" /> {/* green for normal */}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  </div>


      <div className="flex gap-4 mb-4">
        <button onClick={() => setTimeFilter("all")} className="px-4 py-2 bg-gray-300 text-black rounded">All Time</button>
        <button onClick={() => setTimeFilter("5m")} className="px-4 py-2 bg-gray-500 text-white rounded">Last 5 Min</button>
        <button onClick={() => setTimeFilter("1h")} className="px-4 py-2 bg-gray-600 text-white rounded">Last 1 Hour</button>
        <button onClick={() => setTimeFilter("today")} className="px-4 py-2 bg-gray-800 text-white rounded">Today</button>
      </div>

      <div className="mb-4 text-sm text-gray-700">
        Showing <b>{filteredLogs.length}</b> logs ({filter}) from <b>{logs.length}</b> total logs.
      </div>

      <div className="grid gap-4">
        {filteredLogs.map((log, i) => (
          <div key={i} className="p-4 bg-white rounded shadow">
            <div className="text-xs text-gray-500">{log.timestamp}</div>
            <div className="font-mono text-sm">{log.raw}</div>
            <div className={`mt-2 font-bold ${log.prediction === "anomaly" ? "text-red-600" : "text-green-600"}`}>
              {log.prediction.toUpperCase()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;


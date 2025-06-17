import { useEffect, useState } from "react";
import axios from "axios";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

function App() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState(null);
  const [timeFilter, setTimeFilter] = useState("all");
  const [darkMode, setDarkMode] = useState(false);

  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://localhost:8000/logs");
      if (Array.isArray(res.data)) setLogs(res.data);
      else setLogs([]);
    } catch (err) {
      setError(err.message || "Unknown error");
      setLogs([]);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem("theme") === "dark";
    setDarkMode(saved);
  }, []);

  useEffect(() => {
    localStorage.setItem("theme", darkMode ? "dark" : "light");
    if (darkMode) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  }, [darkMode]);

  const now = new Date();
  const filterByTime = (log) => {
    if (!log.timestamp) return false;
    const logTime = new Date(log.timestamp);
    if (isNaN(logTime)) return false;
    switch (timeFilter) {
      case "5m": return (now.getTime() - logTime.getTime()) <= 5 * 60 * 1000;
      case "1h": return (now.getTime() - logTime.getTime()) <= 60 * 60 * 1000;
      case "today": return now.toDateString() === logTime.toDateString();
      default: return true;
    }
  };

  const filteredLogs = logs.filter(log =>
    (filter === "all" || log.prediction === filter) &&
    (searchQuery === "" || (log.raw && log.raw.toLowerCase().includes(searchQuery.toLowerCase()))) &&
    filterByTime(log)
  );

  const anomalyCount = filteredLogs.filter(l => l.prediction === "anomaly").length;
  const normalCount = filteredLogs.filter(l => l.prediction === "normal").length;

  const pieData = [
    { name: "Anomaly", value: anomalyCount },
    { name: "Normal", value: normalCount }
  ];

  const barData = [];
  const countsByHour = {};
  filteredLogs.forEach(log => {
    if (!log.timestamp) return;
    const logTime = new Date(log.timestamp);
    const hour = logTime.getHours();
    const key = `${hour}:00`;
    countsByHour[key] = countsByHour[key] || { hour: key, anomaly: 0, normal: 0 };
    if (log.prediction === "anomaly") countsByHour[key].anomaly++;
    else countsByHour[key].normal++;
  });
  for (const key in countsByHour) barData.push(countsByHour[key]);

  const exportCSV = () => {
    const header = "timestamp,raw,prediction\n";
    const rows = filteredLogs.map(log => `${log.timestamp},${JSON.stringify(log.raw)},${log.prediction}`).join("\n");
    const csv = header + rows;
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "logs.csv";
    a.click();
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Security Log Dashboard</h1>
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="px-4 py-2 rounded border text-sm bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-white dark:border-gray-500"
        >
          {darkMode ? "☀ Light Mode" : "🌙 Dark Mode"}
        </button>
      </div>

      {error && <div className="mb-4 p-2 bg-red-100 text-red-800 rounded">Error: {error}</div>}

      <input
        type="text"
        placeholder="Search logs..."
        value={searchQuery}
        onChange={e => setSearchQuery(e.target.value)}
        className="mb-4 p-2 border border-gray-300 dark:bg-gray-800 dark:border-gray-600 rounded w-full"
      />

      <div className="flex gap-4 mb-4 flex-wrap">
        <button onClick={() => setFilter("all")} className="px-4 py-2 bg-blue-500 text-white rounded">All</button>
        <button onClick={() => setFilter("normal")} className="px-4 py-2 bg-green-600 text-white rounded">Normal</button>
        <button onClick={() => setFilter("anomaly")} className="px-4 py-2 bg-red-600 text-white rounded">Anomaly</button>
        <button onClick={exportCSV} className="ml-auto px-4 py-2 bg-yellow-500 text-white rounded">⬇ Export CSV</button>
      </div>

      {anomalyCount > 5 && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-800 rounded">
          ⚠️ High number of anomalies detected: <strong>{anomalyCount}</strong>
        </div>
      )}

      <div className="flex gap-4 mb-4 flex-wrap">
        <button onClick={() => setTimeFilter("all")} className="px-4 py-2 bg-gray-300 dark:bg-gray-700 text-black dark:text-white rounded">All Time</button>
        <button onClick={() => setTimeFilter("5m")} className="px-4 py-2 bg-gray-500 text-white rounded">Last 5 Min</button>
        <button onClick={() => setTimeFilter("1h")} className="px-4 py-2 bg-gray-600 text-white rounded">Last 1 Hour</button>
        <button onClick={() => setTimeFilter("today")} className="px-4 py-2 bg-gray-800 text-white rounded">Today</button>
      </div>

      <div className="mb-4 text-sm text-gray-700 dark:text-gray-300">
        Showing <b>{filteredLogs.length}</b> logs ({filter}) from <b>{logs.length}</b> total logs.
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded shadow mb-6">
        <h2 className="text-lg font-semibold mb-2">Anomaly Breakdown</h2>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
              <Cell fill="#EF4444" />
              <Cell fill="#22C55E" />
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white dark:bg-gray-800 p-4 rounded shadow mb-6">
        <h2 className="text-lg font-semibold mb-2">Logs per Hour</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="normal" fill="#22C55E" />
            <Bar dataKey="anomaly" fill="#EF4444" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid gap-4">
        {filteredLogs.map((log, i) => (
          <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded shadow">
            <div className="text-xs text-gray-500 dark:text-gray-400">{log.timestamp}</div>
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


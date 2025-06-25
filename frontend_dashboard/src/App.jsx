import { useEffect, useState } from "react";
import axios from "axios";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  AreaChart, Area,
  BarChart, Bar,
  XAxis, YAxis, CartesianGrid,
  ResponsiveContainer
} from "recharts";
import LiveStream from "./components/LiveStream";

const threatColors = {
  brute_force: "#FF6B6B",
  port_scan: "#FFD93D",
  suspicious_login: "#6BCB77",
  dos_attack: "#4D96FF",
  malware_activity: "#C780FA",
  normal: "#A0AEC0"
};

function App() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [timeFilter, setTimeFilter] = useState("all");
  const [error, setError] = useState(null);
  const [selectedThreat, setSelectedThreat] = useState("all");
  const [uploading, setUploading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const logsPerPage = 20;

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await axios.get("http://localhost:8000/logs");
      if (Array.isArray(res.data)) {
        setLogs(res.data.filter(l => l.timestamp && l.raw));
      } else {
        setLogs([]);
      }
    } catch (err) {
      setError("Failed to fetch logs");
    }
  };

  const now = new Date();
  const filterByTime = (log) => {
    const logTime = new Date(log.timestamp);
    if (isNaN(logTime)) return false;
    switch (timeFilter) {
      case "5m": return now - logTime <= 5 * 60 * 1000;
      case "1h": return now - logTime <= 60 * 60 * 1000;
      case "today": return now.toDateString() === logTime.toDateString();
      default: return true;
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesFilter = filter === "all" || log.prediction === filter;
    const matchesSearch = !searchQuery || log.raw.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesThreat = selectedThreat === "all" || log.threat_type === selectedThreat;
    return matchesFilter && matchesSearch && matchesThreat && filterByTime(log);
  });

  const totalPages = Math.ceil(filteredLogs.length / logsPerPage);
  const paginatedLogs = filteredLogs.slice((currentPage - 1) * logsPerPage, currentPage * logsPerPage);

  const pieData = [
    { name: "Anomaly", value: filteredLogs.filter(l => l.prediction === "anomaly").length },
    { name: "Normal", value: filteredLogs.filter(l => l.prediction === "normal").length }
  ];

  const areaData = (() => {
    const timeline = {};
    filteredLogs.forEach(log => {
      const dt = new Date(log.timestamp);
      if (!isNaN(dt)) {
        const key = dt.getHours().toString().padStart(2, '0') + ":" + dt.getMinutes().toString().padStart(2, '0');
        timeline[key] = (timeline[key] || 0) + 1;
      }
    });
    return Object.entries(timeline).map(([time, count]) => ({ time, count }));
  })();

  const barData = (() => {
    const counts = {};
    filteredLogs.forEach(log => {
      const t = log.threat_type || "normal";
      counts[t] = (counts[t] || 0) + 1;
    });
    return Object.keys(counts).map(k => ({ type: k, count: counts[k] }));
  })();

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post("http://localhost:8000/upload", formData);
      setTimeout(fetchLogs, 3000);
    } catch (err) {
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">🚨 Log Analyzer Dashboard</h1>
        <input type="file" accept=".log,.json" onChange={handleFileUpload} disabled={uploading} className="text-sm bg-gray-800 p-2 rounded" />
      </div>

      <div className="flex flex-wrap gap-4 mb-4">
        <input type="text" placeholder="Search logs..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="bg-gray-800 p-2 rounded w-full sm:w-60" />
        <select value={filter} onChange={e => setFilter(e.target.value)} className="bg-gray-800 p-2 rounded">
          <option value="all">All</option>
          <option value="normal">Normal</option>
          <option value="anomaly">Anomaly</option>
        </select>
        <select value={timeFilter} onChange={e => setTimeFilter(e.target.value)} className="bg-gray-800 p-2 rounded">
          <option value="all">All Time</option>
          <option value="5m">Last 5 Min</option>
          <option value="1h">Last 1 Hour</option>
          <option value="today">Today</option>
        </select>
        <select value={selectedThreat} onChange={e => setSelectedThreat(e.target.value)} className="bg-gray-800 p-2 rounded">
          <option value="all">All Threats</option>
          {Object.keys(threatColors).map(type => <option key={type} value={type}>{type}</option>)}
        </select>
      </div>

      <LiveStream onNewLog={log => setLogs(prev => [log, ...prev])} />

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-gray-800 p-4 rounded shadow">
          <h2 className="text-lg font-semibold mb-2">📊 Anomaly Distribution</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={80} label>
                <Cell fill="#EF4444" />
                <Cell fill="#10B981" />
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-800 p-4 rounded shadow">
          <h2 className="text-lg font-semibold mb-2">📈 Log Activity Over Time</h2>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={areaData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="count" stroke="#6366F1" fill="#A5B4FC" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-gray-800 p-4 rounded shadow my-6">
        <h2 className="text-lg font-semibold mb-2">🔎 Threat Type Frequency</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="type" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count">
              {barData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={threatColors[entry.type] || "#8884d8"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid gap-4">
        {paginatedLogs.map((log, i) => (
          <div key={i} className="p-4 bg-gray-800 rounded shadow">
            <div className="text-xs text-gray-400">{log.timestamp}</div>
            <div className="font-mono text-sm">{log.raw}</div>
            <div className={`mt-2 font-bold ${log.prediction === "anomaly" ? "text-red-400" : "text-green-400"}`}>{log.prediction.toUpperCase()}</div>
            {log.threat_type && <div className="text-sm italic text-purple-400 mt-1">Threat: {log.threat_type}</div>}
          </div>
        ))}
      </div>

      <div className="flex justify-center mt-6 space-x-2">
        {Array.from({ length: totalPages }, (_, i) => (
          <button key={i} onClick={() => setCurrentPage(i + 1)} className={`px-3 py-1 rounded ${currentPage === i + 1 ? "bg-blue-500 text-white" : "bg-gray-700 text-white"}`}>
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
}

export default App;


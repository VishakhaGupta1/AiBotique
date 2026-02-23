import React, { useEffect, useState } from "react";
import config from "../config/config";
const apiBase = import.meta.env.PROD ? config.production.apiBase : config.development.apiBase;

const StatusBar = () => {
  const [status, setStatus] = useState({ api: "checking..." });
  useEffect(() => {
    const controller = new AbortController();
    fetch(`${apiBase}/health`, { signal: controller.signal })
      .then((r) => r.json())
      .then(() => setStatus({ api: "online" }))
      .catch(() => setStatus({ api: "offline" }));
    return () => controller.abort();
  }, []);

  const base = apiBase;

  return (
    <div className="fixed bottom-2 left-2 z-50 text-xs bg-black/60 text-white px-2 py-1 rounded">
      <span>API: {base} · status: {status.api}</span>
    </div>
  );
};

export default StatusBar;

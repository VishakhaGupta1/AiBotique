import React, { useState } from "react";
import config from "../config/config";
import { CustomButton } from "../components";
import state from "../store";
import { motion } from "framer-motion";
import { slideAnimation } from "../config/motion";

const endpoints = import.meta.env.PROD ? config.production.endpoints : config.development.endpoints;

const Recommendations = () => {
  const [form, setForm] = useState({ age: 28, gender: "f", color_pref: "black", style_pref: "streetwear", budget: 150 });
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(false);

  const onRecommend = async () => {
    setLoading(true);
    try {
      const res = await fetch(endpoints.recommendations, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_profile: form, k: 8 }),
      });
      const contentType = res.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        const text = await res.text();
        throw new Error(`Unexpected response: ${text.slice(0, 120)}...`);
      }
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to fetch recommendations");
      setRecs(data.recommendations || []);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  const onChange = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  return (
    <motion.section className="absolute top-0 left-0 z-10 w-full h-full p-6" {...slideAnimation("up")}>
      <div className="max-w-3xl mx-auto bg-white/70 rounded-xl p-5 flex flex-col gap-4">
        <h2 className="text-2xl font-bold">Personalized Recommendations</h2>
        <div className="grid grid-cols-2 gap-3">
          <label className="text-sm">Age<input className="border rounded p-2 w-full" type="number" value={form.age} onChange={(e) => onChange("age", Number(e.target.value))} /></label>
          <label className="text-sm">Gender<select className="border rounded p-2 w-full" value={form.gender} onChange={(e) => onChange("gender", e.target.value)}><option value="f">Female</option><option value="m">Male</option></select></label>
          <label className="text-sm">Color Pref<input className="border rounded p-2 w-full" value={form.color_pref} onChange={(e) => onChange("color_pref", e.target.value)} /></label>
          <label className="text-sm">Style Pref<input className="border rounded p-2 w-full" value={form.style_pref} onChange={(e) => onChange("style_pref", e.target.value)} /></label>
          <label className="text-sm">Budget<input className="border rounded p-2 w-full" type="number" value={form.budget} onChange={(e) => onChange("budget", Number(e.target.value))} /></label>
        </div>
        <div className="flex gap-3">
          <CustomButton title={loading ? "Scoring..." : "Get Recommendations"} type="filled" handleClick={onRecommend} customStyles="px-4 py-2.5 font-bold text-sm" />
          <CustomButton title="Back" type="filled" handleClick={() => (state.intro = true, state.view = "home")} customStyles="px-4 py-2.5 font-bold text-sm" />
        </div>
        {recs.length > 0 && (
          <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recs.map((r) => (
              <div key={r.item_id} className="border rounded p-3 bg-white">
                <div className="font-semibold">{r.name}</div>
                <div className="text-xs text-gray-600">Score: {r.score}</div>
                <div className="text-xs">Style: {r.style} • Color: {r.color}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.section>
  );
};

export default Recommendations;

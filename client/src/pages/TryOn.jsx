
import React, { useState } from "react";
import config from "../config/config";
import { CustomButton } from "../components";
import state from "../store";
import { motion } from "framer-motion";
import { slideAnimation } from "../config/motion";

const endpoints = import.meta.env.PROD ? config.production.endpoints : config.development.endpoints;

const TryOn = () => {
  const [bodyFile, setBodyFile] = useState(null);
  const [garmentFile, setGarmentFile] = useState(null);
  const [bodyFileName, setBodyFileName] = useState("");
  const [garmentFileName, setGarmentFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const onSubmit = async () => {
    if (!bodyFile || !garmentFile) return alert("Please upload both your body photo and a garment photo.");
    setLoading(true);
    try {
      const form = new FormData();
      form.append("body", bodyFile);
      form.append("garment", garmentFile);
      const res = await fetch(endpoints.tryOn, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Try-on failed");
      setResult(`data:image/png;base64,${data.composite}`);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.section className="absolute top-0 left-0 z-10 w-full h-full p-6" {...slideAnimation("right")}> 
      <div className="max-w-3xl mx-auto bg-white/70 rounded-xl p-5 flex flex-col gap-4">
        <h2 className="text-2xl font-bold">Virtual Try-On</h2>
        <p className="text-sm text-gray-700">Upload a full or half-body photo and a separate garment photo. The system will show you how the garment looks on your body. No text prompt needed.</p>
        <label className="text-sm font-medium">Upload Body Photo</label>
        <div className="flex gap-2 items-center">
          <input
            id="body-photo-input"
            className="border rounded p-2"
            style={{ position: "static", opacity: 1 }}
            type="file"
            accept="image/*"
            onChange={(e) => {
              const f = e.target.files?.[0] || null;
              setBodyFile(f);
              setBodyFileName(f ? f.name : "");
            }}
          />
          <CustomButton
            title="Choose Body Photo"
            type="filled"
            handleClick={() => {
              const el = document.getElementById("body-photo-input");
              if (el) el.click();
            }}
            customStyles="px-3 py-2 text-sm"
          />
          {bodyFileName && <span className="text-xs text-gray-600">{bodyFileName}</span>}
        </div>
        <label className="text-sm font-medium">Upload Garment Photo</label>
        <div className="flex gap-2 items-center">
          <input
            id="garment-photo-input"
            className="border rounded p-2"
            style={{ position: "static", opacity: 1 }}
            type="file"
            accept="image/*"
            onChange={(e) => {
              const f = e.target.files?.[0] || null;
              setGarmentFile(f);
              setGarmentFileName(f ? f.name : "");
            }}
          />
          <CustomButton
            title="Choose Garment Photo"
            type="filled"
            handleClick={() => {
              const el = document.getElementById("garment-photo-input");
              if (el) el.click();
            }}
            customStyles="px-3 py-2 text-sm"
          />
          {garmentFileName && <span className="text-xs text-gray-600">{garmentFileName}</span>}
        </div>
        <div className="flex gap-3">
          <CustomButton title={loading ? "Generating..." : "Try On"} type="filled" handleClick={onSubmit} customStyles="px-4 py-2.5 font-bold text-sm" />
          <CustomButton title="Back" type="filled" handleClick={() => (state.intro = true, state.view = "home")} customStyles="px-4 py-2.5 font-bold text-sm" />
        </div>
        {result && (
          <div className="mt-4">
            <img src={result} alt="tryon" className="max-h-[70vh] rounded" />
          </div>
        )}
      </div>
    </motion.section>
  );
};

export default TryOn;

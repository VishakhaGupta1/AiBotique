import React, { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useSnapshot } from "valtio";

import config from "../config/config";
import state from "../store";
import { download } from "../assets";
import { downloadCanvasToImage, reader } from "../config/helpers";
import { EditorTabs, FilterTabs, DecalTypes } from "../config/constants";
import { fadeAnimation, slideAnimation } from "../config/motion";
import {
    AIPicker,
    ColorPicker,
    CustomButton,
    FilePicker,
    Tab,
} from "../components";

const endpoints = import.meta.env.PROD ? config.production.endpoints : config.development.endpoints;

const Customizer = () => {
    const snap = useSnapshot(state);
    const [file, setFile] = useState("");
    const [prompt, setPrompt] = useState("");
    const [generatingImg, setGeneratingImg] = useState(false);

    const [activeEditorTab, setActiveEditorTab] = useState("");
    const [showActiveEditorTab, setShowActiveEditorTab] = useState(false);
    const [activeFilterTab, setActiveFilterTab] = useState({
        logoShirt: true,
        stylishShirt: false,
    });

    const generateTabContent = () => {
        switch (activeEditorTab) {
            case "colorpicker":
                return <ColorPicker />;
            case "filepicker":
                return (
                    <FilePicker
                        file={file}
                        setFile={setFile}
                        readFile={readFile}
                    />
                );
            case "aipicker":
                return (
                    <AIPicker
                        prompt={prompt}
                        setPrompt={setPrompt}
                        generatingImg={generatingImg}
                        handleSubmit={handleSubmit}
                    />
                );
            default:
                return null;
        }
    };

    const handleSubmit = async (type) => {
        if (!prompt) return alert("Please enter a prompt");
        try {
            setGeneratingImg(true);

            const response = await fetch(endpoints.generateOutfit, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt }),
            });

            const contentType = response.headers.get("content-type") || "";
            if (!contentType.includes("application/json")) {
                const text = await response.text();
                throw new Error(`Unexpected response from API: ${text.slice(0,120)}...`);
            }
            const data = await response.json();
            if (response.status === 200 && data.photo) {
                handleDecals(type, `data:image/png;base64,${data.photo}`);
            } else {
                throw new Error(data.error || "Image generation failed");
            }
        } catch (err) {
            alert(err);
        } finally {
            setGeneratingImg(false);
            setActiveEditorTab("");
            setPrompt("");
        }
    };

    const handleActiveFilterTab = (tabName) => {
        switch (tabName) {
            case "logoShirt":
                state.isLogoTexture = !activeFilterTab[tabName];
                break;
            case "stylishShirt":
                state.isFullTexture = !activeFilterTab[tabName];
                break;
            default:
                state.isFullTexture = false;
                state.isLogoTexture = true;
                break;
        }

        //after setting the state, active FilterTab is updated
        setActiveFilterTab((prevState) => {
            return {
                ...prevState,
                [tabName]: !prevState[tabName],
            };
        });
    };

    const handleDecals = (type, result) => {
        const decalType = DecalTypes[type];
        state[decalType.stateProperty] = result;

        if (!activeFilterTab[decalType.filterTab]) {
            handleActiveFilterTab(decalType.filterTab);
        }
    };

    const readFile = (type) => {
        reader(file).then((result) => {
            handleDecals(type, result);
            setActiveEditorTab("");
        });
    };

    return (
        <AnimatePresence>
            {!snap.intro && (
                <>
                    <motion.div
                        key="custom"
                        className="absolute top-0 left-0 z-10"
                        {...slideAnimation("left")}
                    >
                        <div className="flex items-center min-h-screen">
                            <div className="editortabs-container tabs">
                                {EditorTabs.map((tab) => (
                                    <Tab
                                        key={tab.name}
                                        tab={tab}
                                        handleClick={() => {
                                            if (
                                                activeEditorTab === tab.name ||
                                                (activeEditorTab !== tab.name &&
                                                    showActiveEditorTab ===
                                                        false)
                                            ) {
                                                setShowActiveEditorTab(
                                                    (prevState) => !prevState
                                                );
                                            }
                                            setActiveEditorTab(tab.name);
                                        }}
                                    />
                                ))}
                                {showActiveEditorTab && generateTabContent()}
                            </div>
                        </div>
                    </motion.div>
                    <motion.div
                        className="absolute z-10 top-5 right-5"
                        {...fadeAnimation}
                    >
                        <CustomButton
                            type="filled"
                            title="Go Back"
                            handleClick={() => {
                                setShowActiveEditorTab(false);
                                state.intro = true;
                                state.view = "home";
                            }}
                            customStyles="w-fit px-4 py-2.5 font-bold text-sm"
                        />
                    </motion.div>
                    <motion.div
                        className="filtertabs-container"
                        {...slideAnimation("up")}
                    >
                        {FilterTabs.map((tab) => (
                            <Tab
                                key={tab.name}
                                tab={tab}
                                isFilterTab
                                isActiveTab={activeFilterTab[tab.name]}
                                handleClick={() => {
                                    handleActiveFilterTab(tab.name);
                                }}
                            />
                        ))}
                        <button
                            className="download-btn"
                            onClick={downloadCanvasToImage}
                        >
                            <img
                                src={download}
                                alt="download_image"
                                className="w-3/5 h-3/5 object-contain"
                            />
                        </button>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default Customizer;

import { motion, AnimatePresence } from "framer-motion";
import { useSnapshot } from "valtio";
import state from "../store";
import { CustomButton } from "../components";
import {
    headContainerAnimation,
    headContentAnimation,
    headTextAnimation,
    slideAnimation,
} from "../config/motion";

const Home = () => {
    const snap = useSnapshot(state);
    return (
        <AnimatePresence>
            {snap.intro && (
                <motion.section className="home" {...slideAnimation("left")}>
                    <motion.div
                        className="home-content"
                        {...headContainerAnimation}
                    >
                        <motion.div {...headTextAnimation}>
                            <h1 className="head-text">
                                LET'S <br className="xl:block hidden" />
                                CREATE.
                            </h1>
                        </motion.div>
                        <motion.div
                            {...headContentAnimation}
                            className="flex flex-col gap-5"
                        >
                            <p className="max-w-md font-normal text-grey-600 text-base">
                            ARBotique: AI + AR fashion — generate outfits, try them on virtually, and get smart recommendations.
                            </p>
                            <div className="flex gap-3 flex-wrap">
                                <CustomButton
                                    type="filled"
                                    title="Customize 3D Shirt"
                                    handleClick={() => {
                                        state.intro = false;
                                        state.view = "customize";
                                    }}
                                    customStyles="w-fit px-4 py-2.5 font-bold text-sm"
                                />
                                <CustomButton
                                    type="outline"
                                    title="Virtual Try-On"
                                    handleClick={() => {
                                        state.intro = false;
                                        state.view = "tryon";
                                    }}
                                    customStyles="w-fit px-4 py-2.5 font-bold text-sm"
                                />
                                <CustomButton
                                    type="outline"
                                    title="Recommendations"
                                    handleClick={() => {
                                        state.intro = false;
                                        state.view = "recs";
                                    }}
                                    customStyles="w-fit px-4 py-2.5 font-bold text-sm"
                                />
                            </div>
                        </motion.div>
                    </motion.div>
                </motion.section>
            )}
        </AnimatePresence>
    );
};

export default Home;

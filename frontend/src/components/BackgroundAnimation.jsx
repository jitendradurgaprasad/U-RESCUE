import { motion } from "framer-motion";

const BackgroundAnimation = () => {
    return (
        <div className="fixed inset-0 overflow-hidden -z-10">

            {/* Top Glow */}

            <motion.div
                animate={{
                    x: [-100, 100, -100],
                    y: [-50, 50, -50],
                }}
                transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: "linear",
                }}
                className="absolute w-[700px] h-[700px] bg-cyan-500/20 rounded-full blur-[180px] top-[-200px] left-[-150px]"
            />

            {/* Bottom Glow */}

            <motion.div
                animate={{
                    x: [100, -100, 100],
                    y: [50, -50, 50],
                }}
                transition={{
                    duration: 25,
                    repeat: Infinity,
                    ease: "linear",
                }}
                className="absolute w-[700px] h-[700px] bg-blue-700/20 rounded-full blur-[180px] bottom-[-250px] right-[-150px]"
            />

        </div>
    );
};

export default BackgroundAnimation;
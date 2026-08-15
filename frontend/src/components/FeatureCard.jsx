import { motion } from "framer-motion";

const FeatureCard = ({ icon, title, description }) => {
    return (
        <motion.div
            whileHover={{
                y: -10,
                scale: 1.03,
            }}
            className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 transition-all"
        >

            <div className="text-cyan-400 text-5xl mb-5">
                {icon}
            </div>

            <h2 className="text-2xl text-white font-bold mb-4">
                {title}
            </h2>

            <p className="text-gray-400">
                {description}
            </p>

        </motion.div>
    );
};

export default FeatureCard;
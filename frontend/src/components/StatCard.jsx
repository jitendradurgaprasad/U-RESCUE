import { motion } from "framer-motion";

const StatCard = ({ number, title }) => {
  return (
    <motion.div
      whileHover={{ y: -8, scale: 1.03 }}
      className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-2xl p-8 text-center"
    >
      <h1 className="text-5xl font-bold text-cyan-400 mb-3">
        {number}
      </h1>

      <p className="text-gray-400 text-lg">
        {title}
      </p>
    </motion.div>
  );
};

export default StatCard;
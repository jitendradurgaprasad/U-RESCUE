import { motion } from "framer-motion";

const particles = Array.from({ length: 35 });

const Particles = () => {
    return (
        <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">

            {particles.map((_, index) => (
                <motion.span
                    key={index}
                    className="absolute bg-cyan-400 rounded-full opacity-30"
                    style={{
                        width: Math.random() * 5 + 2,
                        height: Math.random() * 5 + 2,
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                    }}
                    animate={{
                        y: [-20, 20, -20],
                        opacity: [0.2, 0.7, 0.2],
                    }}
                    transition={{
                        duration: Math.random() * 8 + 6,
                        repeat: Infinity,
                    }}
                />
            ))}

        </div>
    );
};

export default Particles;
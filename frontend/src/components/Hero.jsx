import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

const Hero = () => {
  return (
    <section
      id="home"
      className="min-h-screen flex items-center justify-center px-10"
    >
      <div className="max-w-6xl mx-auto text-center">

        <motion.h1
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-7xl font-black text-white leading-tight"
        >
          Predict
          <span className="text-cyan-400"> Floods </span>

          Before They Happen
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: .4 }}
          className="text-xl text-gray-400 mt-8 max-w-3xl mx-auto"
        >
          U Rescue combines Artificial Intelligence, GIS, Satellite
          Imagery and Machine Learning to predict flood risks,
          identify safe evacuation routes and support emergency
          response in real time.
        </motion.p>

        <motion.div
          initial={{ opacity:0, y:20 }}
          animate={{ opacity:1, y:0 }}
          transition={{ delay:.8 }}
          className="mt-14 flex justify-center gap-6"
        >

          <button className="bg-cyan-500 hover:bg-cyan-600 transition px-8 py-4 rounded-xl text-lg font-semibold text-white flex items-center gap-3">
            Start Prediction
            <ArrowRight size={20}/>
          </button>

          <button className="border border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-white transition px-8 py-4 rounded-xl text-lg font-semibold">
            Learn More
          </button>

        </motion.div>

      </div>
    </section>
  );
};

export default Hero;
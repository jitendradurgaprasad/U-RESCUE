import CountUp from "react-countup";
import StatCard from "./StatCard";

const Statistics = () => {
  return (
    <section className="max-w-7xl mx-auto py-32 px-8">

      <h1 className="text-center text-white text-5xl font-bold mb-16">
        U Rescue at a Glance
      </h1>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">

        <StatCard
          number="96%"
          title="Prediction Accuracy"
        />

        <StatCard
          number="96%"
          title="GIS Layers"
        />

        <StatCard
          number="96%"
          title="Pixels Analysed"
        />

        <StatCard
          number="96%"
          title="Monitoring"
        />

      </div>

    </section>
  );
};

export default Statistics;
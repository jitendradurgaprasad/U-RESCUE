import FeatureCard from "./FeatureCard";

import {
    Shield,
    Map,
    Brain,
    Route,
} from "lucide-react";

const Features = () => {
    return (
        <section
            id="features"
            className="max-w-7xl mx-auto py-28 px-8"
        >

            <h1 className="text-5xl font-bold text-center text-white mb-16">
                Platform Features
            </h1>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">

                <FeatureCard
                    icon={<Brain />}
                    title="AI Prediction"
                    description="Predict flood risks using Machine Learning and GIS."
                />

                <FeatureCard
                    icon={<Map />}
                    title="Interactive Maps"
                    description="Analyze flood-prone areas on an intelligent live map."
                />

                <FeatureCard
                    icon={<Route />}
                    title="Safe Routing"
                    description="Generate evacuation routes avoiding dangerous zones."
                />

                <FeatureCard
                    icon={<Shield />}
                    title="Emergency Response"
                    description="Locate shelters, hospitals and emergency resources."
                />

            </div>

        </section>
    );
};

export default Features;
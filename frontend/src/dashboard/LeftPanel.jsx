import {
    ShieldAlert,
    Brain,
    Route,
} from "lucide-react";
import PredictButton from "./PredictButton";

import { usePrediction } from "../context/PredictionContext";

const LeftPanel = () => {
    const { selectedLocation } = usePrediction();

    return (
        <div className="space-y-6">

            {/* AI Prediction */}

            <div className="bg-white/5 border border-white/10 rounded-2xl backdrop-blur-xl p-6">

                <h2 className="text-white text-2xl font-bold mb-6">
                    AI Prediction
                </h2>

                <div className="space-y-5">

                    <div>
                        <p className="text-gray-400">
                            Latitude
                        </p>

                        <h3 className="text-cyan-400 text-xl font-semibold">
                            {selectedLocation
                                ? selectedLocation.lat.toFixed(6)
                                : "--"}
                        </h3>
                    </div>

                    <div>
                        <p className="text-gray-400">
                            Longitude
                        </p>

                        <h3 className="text-cyan-400 text-xl font-semibold">
                            {selectedLocation
                                ? selectedLocation.lng.toFixed(6)
                                : "--"}
                        </h3>
                    </div>

                    <div>
                        <p className="text-gray-400">
                            Prediction
                        </p>
                        <PredictButton />

                        <div className="flex items-center gap-3 mt-2">

                            <ShieldAlert
                                className="text-yellow-400"
                                size={22}
                            />

                            <span className="text-yellow-400 text-xl font-bold">
                                Waiting...
                            </span>

                        </div>
                    </div>
                    <PredictButton />


                </div>

            </div>

            {/* AI Summary */}

            <div className="bg-white/5 border border-white/10 rounded-2xl backdrop-blur-xl p-6">

                <h2 className="text-white text-xl font-semibold mb-5">
                    AI Summary
                </h2>

                <div className="flex gap-4">

                    <Brain
                        className="text-cyan-400 flex-shrink-0"
                        size={24}
                    />

                    <p className="text-gray-400 leading-7">
                        Select a location on the map to generate an AI-powered flood risk prediction.
                    </p>

                </div>

            </div>

            {/* Safe Route */}

            <div className="bg-white/5 border border-white/10 rounded-2xl backdrop-blur-xl p-6">

                <div className="flex items-center gap-4">

                    <Route
                        className="text-cyan-400"
                        size={24}
                    />

                    <div>

                        <h3 className="text-white font-semibold">
                            Safe Route
                        </h3>

                        <p className="text-gray-400">
                            Waiting for prediction...
                        </p>

                    </div>

                </div>

            </div>

        </div>
    );
};

export default LeftPanel;
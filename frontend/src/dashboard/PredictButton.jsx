import api from "../services/api";
import { usePrediction } from "../context/PredictionContext";

const PredictButton = () => {

    const {
        selectedLocation,
        setPrediction,
        loading,
        setLoading
    } = usePrediction();

    const predict = async () => {

        if (!selectedLocation) {

            alert("Select a location first.");

            return;
        }

        try {

            setLoading(true);

            const response = await api.post("/predict", {

                latitude: selectedLocation.lat,
                longitude: selectedLocation.lng

            });

            setPrediction(response.data);

        }

        catch (err) {

            console.error(err);

            alert("Prediction failed.");

        }

        finally {

            setLoading(false);

        }

    };

    return (

        <button

            onClick={predict}

            className="w-full mt-6 bg-cyan-500 hover:bg-cyan-600 transition rounded-xl py-3 text-white font-semibold"

        >

            {loading ? "Predicting..." : "Run AI Prediction"}

        </button>

    );

};

export default PredictButton;
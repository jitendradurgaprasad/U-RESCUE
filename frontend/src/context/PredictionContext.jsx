import { createContext, useContext, useState } from "react";

const PredictionContext = createContext();

export const PredictionProvider = ({ children }) => {

    const [selectedLocation, setSelectedLocation] = useState(null);

    const [prediction, setPrediction] = useState(null);

    const [loading, setLoading] = useState(false);

    return (

        <PredictionContext.Provider
            value={{
                selectedLocation,
                setSelectedLocation,
                prediction,
                setPrediction,
                loading,
                setLoading
            }}
        >
            {children}
        </PredictionContext.Provider>

    );

};

export const usePrediction = () => useContext(PredictionContext);
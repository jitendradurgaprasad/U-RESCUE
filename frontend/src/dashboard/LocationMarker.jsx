import { Marker, Popup, useMapEvents } from "react-leaflet";
import { useState } from "react";

import { usePrediction } from "../context/PredictionContext";

const LocationMarker = () => {

    const [position, setPosition] = useState(null);

    const { setSelectedLocation } = usePrediction();

    useMapEvents({

        click(e) {

            setPosition(e.latlng);

            setSelectedLocation({

                lat: e.latlng.lat,

                lng: e.latlng.lng

            });

        }

    });

    return position === null ? null : (

        <Marker position={position}>

            <Popup>

                Selected Location

                <br />

                {position.lat.toFixed(6)}

                <br />

                {position.lng.toFixed(6)}

            </Popup>

        </Marker>

    );

};

export default LocationMarker;
import {
    MapContainer,
    TileLayer,
    ZoomControl
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import SearchBar from "./SearchBar";
import GPSButton from "./GPSButton";
import LayerControl from "./LayerControl";
import LocationMarker from "./LocationMarker";

const MapView = () => {
    return (
        <div className="relative h-[700px] rounded-3xl overflow-hidden border border-white/10">

            <SearchBar />

            <GPSButton />

            <LayerControl />

            <MapContainer
                center={[17.3850, 78.4867]}
                zoom={9}
                zoomControl={false}
                className="h-full w-full z-0"
            >
                <ZoomControl position="bottomright" />

                <TileLayer
                    attribution="OpenStreetMap"
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <LocationMarker />


            </MapContainer>

        </div>
    );
};

export default MapView;
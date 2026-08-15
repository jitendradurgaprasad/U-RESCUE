import {
CloudRain,
Layers,
MapPinned
} from "lucide-react";

const RightPanel = () => {

return (

<div className="space-y-6">

<div className="bg-white/5 rounded-2xl border border-white/10 backdrop-blur-xl p-6">

<h2 className="text-white text-xl mb-5">
Weather
</h2>

<div className="flex items-center gap-4">

<CloudRain className="text-cyan-400"/>

<div>

<h3 className="text-white">
28°C
</h3>

<p className="text-gray-400">
Moderate Rain
</p>

</div>

</div>

</div>

<div className="bg-white/5 rounded-2xl border border-white/10 backdrop-blur-xl p-6">

<div className="flex items-center gap-4">

<Layers className="text-cyan-400"/>

<h2 className="text-white">
GIS Layers
</h2>

</div>

</div>

<div className="bg-white/5 rounded-2xl border border-white/10 backdrop-blur-xl p-6">

<div className="flex items-center gap-4">

<MapPinned className="text-cyan-400"/>

<div>

<h3 className="text-white">
Nearest Shelter
</h3>

<p className="text-gray-400">
2.1 km
</p>

</div>

</div>

</div>

</div>

);

};

export default RightPanel;
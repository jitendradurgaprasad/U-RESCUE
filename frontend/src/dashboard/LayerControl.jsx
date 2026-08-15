import { Layers } from "lucide-react";

const LayerControl = () => {
    return (
        <div
            className="absolute top-24 right-5 z-[1000]
      bg-[#111827]/90
      backdrop-blur-xl
      border border-white/10
      rounded-xl
      p-5
      w-56"
        >
            <div className="flex items-center gap-3 mb-4">

                <Layers
                    className="text-cyan-400"
                />

                <h2 className="text-white font-semibold">
                    Layers
                </h2>

            </div>

            <div className="space-y-3 text-gray-300">

                <label className="flex items-center gap-3">

                    <input type="checkbox" />

                    Flood Risk

                </label>

                <label className="flex items-center gap-3">

                    <input type="checkbox" />

                    Rivers

                </label>

                <label className="flex items-center gap-3">

                    <input type="checkbox" />

                    Shelters

                </label>

                <label className="flex items-center gap-3">

                    <input type="checkbox" />

                    Hospitals

                </label>

            </div>

        </div>
    );
};

export default LayerControl;
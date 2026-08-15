import { LocateFixed } from "lucide-react";

const GPSButton = () => {
  return (
    <button
      className="absolute bottom-5 right-5 z-[1000]
      bg-cyan-500 hover:bg-cyan-600
      p-4 rounded-full shadow-xl transition"
    >
      <LocateFixed
        className="text-white"
        size={22}
      />
    </button>
  );
};

export default GPSButton;
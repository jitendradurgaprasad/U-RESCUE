import LeftPanel from "./LeftPanel";
import MapContainer from "./MapContainer";
import RightPanel from "./RightPanel";

const DashboardLayout = () => {
    return (
        <section
            id="dashboard"
            className="min-h-screen bg-[#050816] px-6 pb-10"
        >
            <div className="max-w-[1800px] mx-auto">

                <h1 className="text-5xl font-bold text-white mb-10">
                    AI Disaster Dashboard
                </h1>

                <div className="grid grid-cols-12 gap-6">

                    <div className="col-span-3">
                        <LeftPanel />
                    </div>

                    <div className="col-span-6">
                        <MapContainer />
                    </div>

                    <div className="col-span-3">
                        <RightPanel />
                    </div>

                </div>

            </div>
        </section>
    );
};

export default DashboardLayout;
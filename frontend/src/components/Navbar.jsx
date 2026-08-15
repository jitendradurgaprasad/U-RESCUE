import { Shield, Menu } from "lucide-react";

const Navbar = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex justify-center mt-5">
      <nav className="w-[95%] max-w-7xl bg-[#111827]/80 backdrop-blur-xl border border-white/10 rounded-2xl px-8 py-4 flex items-center justify-between shadow-2xl">

        {/* Logo */}

        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
            <Shield className="text-cyan-400" size={28} />
          </div>

          <div>
            <h1 className="text-3xl font-bold text-white">
              U Rescue
            </h1>

            <p className="text-gray-400 text-sm">
              AI Disaster Intelligence Platform
            </p>
          </div>
        </div>

        {/* Navigation */}

        <div className="hidden md:flex items-center gap-10 text-gray-300">

          <a
            href="#home"
            className="hover:text-cyan-400 duration-300"
          >
            Home
          </a>

          <a
            href="#features"
            className="hover:text-cyan-400 duration-300"
          >
            Features
          </a>

          <a
            href="#dashboard"
            className="hover:text-cyan-400 duration-300"
          >
            Dashboard
          </a>

          <a
            href="#about"
            className="hover:text-cyan-400 duration-300"
          >
            About
          </a>

          <button className="bg-cyan-500 hover:bg-cyan-600 duration-300 text-white px-5 py-2 rounded-xl font-semibold">
            Live Prediction
          </button>

        </div>

        {/* Mobile */}

        <button className="md:hidden text-white">
          <Menu size={28} />
        </button>

      </nav>
    </header>
  );
};

export default Navbar;
import { Search } from "lucide-react";

const SearchBar = () => {
  return (
    <div className="absolute top-5 left-5 z-[1000]">

      <div className="bg-[#111827]/90 backdrop-blur-xl border border-white/10 rounded-xl flex items-center px-4 py-3 w-[350px]">

        <Search
          className="text-cyan-400 mr-3"
          size={20}
        />

        <input
          type="text"
          placeholder="Search any location..."
          className="bg-transparent outline-none text-white w-full placeholder-gray-400"
        />

      </div>

    </div>
  );
};

export default SearchBar;
import type React from "react";
import "./CriticalTile.css"; // Assume we create some specific CSS or tailwind

export interface CriticalTileProps {
  imperativeAction: string; // e.g "SIGN" "FILE" "REVIEW"
  matterName: string; // e.g "Smith v. Jones - 12(b)(6)"
  deadlineIso: string; // The critical date
  ruleCitation: string; // e.g "FRCP 12(a)"
  intensityLevel: "gentle" | "moderate" | "aggressive" | "no-slack"; // Slider
  onTap: () => void; // Trigger workflow
}

export const CriticalTile: React.FC<CriticalTileProps> = ({
  imperativeAction,
  matterName,
  deadlineIso,
  ruleCitation,
  intensityLevel,
  onTap,
}) => {
  // Determine color based on intensity to fit Dark Luxury
  const getColorScheme = () => {
    switch (intensityLevel) {
      case "no-slack":
        return "bg-red-900 border-red-500 text-white";
      case "aggressive":
        return "bg-orange-900 border-orange-500 text-white";
      case "moderate":
        return "bg-zinc-800 border-yellow-500 text-gray-200";
      default:
        return "bg-black border-slate-700 text-gray-400";
    }
  };

  const formattedDate = new Date(deadlineIso).toLocaleDateString();

  return (
    <div
      onClick={onTap}
      className={`relative w-full h-screen flex flex-col justify-center items-center p-8 cursor-pointer transition-all duration-300 transform active:scale-95 ${getColorScheme()}`}
      style={{
        boxShadow: "inset 0 0 100px rgba(0,0,0,0.8)",
        backdropFilter: "blur(10px)",
      }}
    >
      <div className="absolute top-8 left-8">
        <h3 className="text-sm tracking-widest uppercase opacity-70">{matterName}</h3>
      </div>

      {/*
        Compliance Note (NY SB S7263 UPL ban):
        We surface ONLY the calculated procedural deadline and rule citation.
        Zero AI legal advice is generated here. The timeline exists as a router
        to the human-approved workflow or original court document.
      */}
      <div className="absolute top-8 right-8">
        <h3 className="text-xs uppercase tracking-widest opacity-60">Source: {ruleCitation}</h3>
      </div>

      <div className="flex-1 flex flex-col justify-center items-center">
        <h1
          className="text-7xl font-black tracking-tighter mb-4"
          style={{ fontFamily: '"Inter", sans-serif' }}
        >
          {imperativeAction}
        </h1>
        <h2 className="text-3xl font-light opacity-90">DUE: {formattedDate}</h2>
      </div>

      <div className="absolute bottom-12 opacity-50 flex items-center space-x-2">
        <div className="w-2 h-2 rounded-full bg-current animate-pulse"></div>
        <span className="text-xs uppercase tracking-widest">Tap to route to workflow</span>
      </div>
    </div>
  );
};

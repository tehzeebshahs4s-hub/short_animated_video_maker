import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { Scene } from "../types";

export const DiagramScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020", justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 80 }}>
      {scene.headline && (
        <h2 style={{ color: "white", fontSize: 56, fontWeight: 700, marginBottom: 40, opacity: op, fontFamily: "sans-serif" }}>{scene.headline}</h2>
      )}
      <svg width="1200" height="600" viewBox="0 0 1200 600" style={{ opacity: op }}>
        {(scene.bullets || []).map((b, i) => {
          const x = 100 + (i % 3) * 380;
          const y = 120 + Math.floor(i / 3) * 220;
          const d = interpolate(frame, [10 + i * 8, 30 + i * 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <g key={i} opacity={d}>
              <rect x={x} y={y} width={320} height={120} rx={16} fill="#1e293b" stroke="#60a5fa" strokeWidth={2} />
              <text x={x + 160} y={y + 68} textAnchor="middle" fill="white" fontSize={24} fontFamily="sans-serif">{b}</text>
            </g>
          );
        })}
      </svg>
      {scene.caption && <p style={{ color: "#a5b4fc", fontSize: 28, marginTop: 24, opacity: op, fontFamily: "sans-serif" }}>{scene.caption}</p>}
    </AbsoluteFill>
  );
};

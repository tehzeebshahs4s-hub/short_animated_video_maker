import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { Scene } from "../types";

export const OutroScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 25], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020", justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 80 }}>
      <h1 style={{ color: "white", fontSize: 72, fontWeight: 800, opacity: op, textAlign: "center", fontFamily: "sans-serif" }}>
        {scene.headline || "Thanks for watching"}
      </h1>
      {scene.caption && (
        <p style={{ color: "#a5b4fc", fontSize: 32, marginTop: 24, opacity: op, textAlign: "center", fontFamily: "sans-serif" }}>
          {scene.caption}
        </p>
      )}
    </AbsoluteFill>
  );
};

import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

export const HelloVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020", justifyContent: "center", alignItems: "center" }}>
      <h1 style={{ color: "white", fontSize: 96, opacity, fontFamily: "sans-serif" }}>
        Prompt2Video ready
      </h1>
    </AbsoluteFill>
  );
};

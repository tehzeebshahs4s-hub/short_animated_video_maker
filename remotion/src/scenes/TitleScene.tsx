import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig, staticFile } from "remotion";
import { Scene } from "../types";

export const TitleScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  const titleScale = spring({ frame, fps, config: { damping: 12 } });
  const subOpacity = interpolate(frame, [15, 40], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020", justifyContent: "center", alignItems: "center", flexDirection: "column", padding: 80 }}>
      {scene.visual?.imageFile && (
        <img src={staticFile(scene.visual.imageFile)} alt="" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.25 }} />
      )}
      <h1 style={{ color: "white", fontSize: 96, fontWeight: 800, opacity: titleOpacity, transform: `scale(${titleScale})`, textAlign: "center", margin: 0, fontFamily: "sans-serif" }}>
        {scene.headline || "Title"}
      </h1>
      {scene.caption && (
        <p style={{ color: "#a5b4fc", fontSize: 36, marginTop: 32, opacity: subOpacity, textAlign: "center", maxWidth: 1400, fontFamily: "sans-serif" }}>
          {scene.caption}
        </p>
      )}
    </AbsoluteFill>
  );
};

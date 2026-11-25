import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig, Img, staticFile } from "remotion";
import { Scene } from "../types";

export const ContentScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const headlineOp = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });
  const headlineY = interpolate(frame, [0, 18], [30, 0], { extrapolateRight: "clamp" });

  // Ken Burns
  const imgScale = scene.visual?.kenBurns === "zoom-out"
    ? interpolate(frame, [0, 9999], [1.15, 1.0], { extrapolateRight: "clamp" })
    : interpolate(frame, [0, 9999], [1.0, 1.15], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1020", overflow: "hidden" }}>
      {scene.visual?.kind === "image" && scene.visual.imageFile && (
        <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
          <Img src={staticFile(scene.visual.imageFile)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${imgScale})`, transformOrigin: "center" }} />
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(11,16,32,0.3) 0%, rgba(11,16,32,0.85) 100%)" }} />
        </div>
      )}
      <div style={{ position: "relative", zIndex: 2, padding: "80px 100px", display: "flex", flexDirection: "column", justifyContent: "center", height: "100%" }}>
        {scene.headline && (
          <h2 style={{ color: "white", fontSize: 64, fontWeight: 700, margin: 0, marginBottom: 40, opacity: headlineOp, transform: `translateY(${headlineY}px)`, fontFamily: "sans-serif" }}>
            {scene.headline}
          </h2>
        )}
        <ul style={{ listStyle: "none", padding: 0, margin: 0, maxWidth: 1500 }}>
          {(scene.bullets || []).map((b, i) => {
            const delay = 20 + i * 12;
            const op = interpolate(frame, [delay, delay + 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            const x = interpolate(frame, [delay, delay + 15], [40, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <li key={i} style={{ color: "#e2e8f0", fontSize: 34, marginBottom: 18, opacity: op, transform: `translateX(${x}px)`, fontFamily: "sans-serif", display: "flex", alignItems: "center" }}>
                <span style={{ color: "#60a5fa", marginRight: 16, fontSize: 28 }}>●</span>
                {b}
              </li>
            );
          })}
        </ul>
      </div>
    </AbsoluteFill>
  );
};

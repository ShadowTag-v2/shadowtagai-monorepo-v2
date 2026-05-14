"use client";

import { type ThreeElements, useFrame } from "@react-three/fiber";
import React, { memo, useRef } from "react";
import type * as THREE from "three";

const colors = {
  utilization: "#FFFFFF",
  black: "#202124",
  red: "#EA4335",
  green: "#34A853",
  player1: "#FBBC04",
  player2: "#4285F4",
};

export default memo(function MessageIncoming(props: ThreeElements["mesh"]) {
  const meshRef = useRef<THREE.Mesh>(null!);
  useFrame((state, delta) => {
    meshRef.current.position.z -= delta * 8;
  });
  return (
    <mesh {...props} ref={meshRef}>
      <boxGeometry args={[0.1, 0.1, 0.1]} />
      <meshStandardMaterial color={colors.green} />
    </mesh>
  );
});

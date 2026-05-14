"use client";

import type { ThreeElements } from "@react-three/fiber";
import React, { memo } from "react";

const loadBalancerBoxSize: [number, number, number] = [1.0, 1.0, 1.0];

export default memo(function LoadBalancerBox(
  props: ThreeElements["mesh"] & {
    playerColor: string;
    position: [number, number, number];
  },
) {
  const { playerColor, position } = props;
  const [x, y, z] = position;
  return (
    <mesh position={position}>
      <boxGeometry args={loadBalancerBoxSize} />
      <meshStandardMaterial color={playerColor} />
    </mesh>
  );
});

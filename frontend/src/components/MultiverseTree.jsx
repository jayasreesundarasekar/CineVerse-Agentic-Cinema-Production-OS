/**
 * Cinema Multiverse — the dashboard's one hero visual. Renders the
 * branching universe tree returned by GET /simulate/multiverse as an
 * SVG node graph: ORIGINAL -> Universe A/B -> ... -> GREENLIGHT.
 */
import React, { useMemo, useState } from "react";

const NODE_W = 168;
const NODE_H = 64;
const COL_GAP = 56;
const ROW_GAP = 96;

function layout(roots) {
  const positioned = [];
  const edges = [];
  let nextX = 0;

  function visit(node, depth, parentPos) {
    const children = node.children || [];
    let x;
    if (children.length === 0) {
      x = nextX;
      nextX += 1;
    } else {
      const childXs = children.map((c) => visit(c, depth + 1, null));
      x = childXs.reduce((a, b) => a + b, 0) / childXs.length;
    }
    const pos = { x: x * (NODE_W + COL_GAP), y: depth * (NODE_H + ROW_GAP), node };
    positioned.push(pos);
    if (parentPos) edges.push({ from: parentPos, to: pos });
    return x;
  }

  roots.forEach((r) => visit(r, 0, null));
  // second pass to wire edges properly (parent known only after full visit for root calls)
  edges.length = 0;
  const byId = Object.fromEntries(positioned.map((p) => [p.node.universe_id, p]));
  positioned.forEach((p) => {
    const parentId = p.node.parent_id;
    if (parentId && byId[parentId]) edges.push({ from: byId[parentId], to: p });
  });

  return { positioned, edges };
}

function scoreTone(node) {
  const avg = (Number(node.story_score) + Number(node.audience_score) + Number(node.continuity_score)) / 3;
  if (avg >= 75) return "#C9A227"; // brass — strong
  if (avg >= 45) return "#2E9E97"; // teal — mixed
  return "#C1443C"; // red — weak
}

export default function MultiverseTree({ roots, onSelect, selectedId }) {
  const { positioned, edges } = useMemo(() => layout(roots), [roots]);

  if (positioned.length === 0) {
    return null;
  }

  const width = Math.max(...positioned.map((p) => p.x)) + NODE_W + 40;
  const height = Math.max(...positioned.map((p) => p.y)) + NODE_H + 40;

  return (
    <div className="overflow-auto scrollbar-thin border border-hair rounded-lg bg-void">
      <svg width={width} height={height} className="block" style={{ minWidth: "100%" }}>
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 z" fill="#2A2F52" />
          </marker>
        </defs>

        {edges.map((e, i) => {
          const x1 = e.from.x + NODE_W / 2;
          const y1 = e.from.y + NODE_H;
          const x2 = e.to.x + NODE_W / 2;
          const y2 = e.to.y;
          const midY = (y1 + y2) / 2;
          return (
            <path
              key={i}
              d={`M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`}
              stroke="#2A2F52"
              strokeWidth="1.5"
              fill="none"
              markerEnd="url(#arrow)"
            />
          );
        })}

        {positioned.map((p) => {
          const node = p.node;
          const isSelected = selectedId === node.universe_id;
          const tone = scoreTone(node);
          return (
            <g
              key={node.universe_id}
              transform={`translate(${p.x}, ${p.y})`}
              className="cursor-pointer"
              onClick={() => onSelect && onSelect(node)}
            >
              <rect
                width={NODE_W}
                height={NODE_H}
                rx="8"
                fill="#141833"
                stroke={isSelected ? "#C9A227" : tone}
                strokeWidth={isSelected ? 2 : 1.25}
              />
              <circle cx={14} cy={14} r={4} fill={tone} />
              <text x={26} y={19} fill="#EDE6D6" fontSize="12" fontFamily="Space Grotesk, sans-serif" fontWeight="600">
                {(node.title || "Untitled").slice(0, 18)}
              </text>
              <text x={14} y={38} fill="#8B8FA3" fontSize="10" fontFamily="IBM Plex Mono, monospace">
                story {Math.round(node.story_score || 0)} · aud {Math.round(node.audience_score || 0)}
              </text>
              <text x={14} y={52} fill="#8B8FA3" fontSize="10" fontFamily="Space Grotesk, sans-serif">
                {node.status || "simulated"}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

import React from "react";

/** Our own crescent+spark mark — a generic celestial motif (not a
 * copied brand icon), rendered as gradient-filled SVG so it's a real
 * vector asset, not a fabricated image. */
export default function Logo({ size = 36 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <defs>
        <linearGradient id="cineverse-logo-grad" x1="0" y1="0" x2="40" y2="40">
          <stop offset="0%" stopColor="#4CC9F0" />
          <stop offset="55%" stopColor="#7C5CFC" />
          <stop offset="100%" stopColor="#E94BB0" />
        </linearGradient>
      </defs>
      <circle cx="20" cy="20" r="20" fill="url(#cineverse-logo-grad)" opacity="0.15" />
      <path
        d="M24.5 8.5a12 12 0 1 0 7 21.7 14.5 14.5 0 0 1 0-21.4 12 12 0 0 0-7-0.3z"
        fill="url(#cineverse-logo-grad)"
      />
      <path d="M30 6 l1.4 3.2 3.2 1.4-3.2 1.4L30 15.2l-1.4-3.2-3.2-1.4 3.2-1.4z" fill="#4CC9F0" />
    </svg>
  );
}

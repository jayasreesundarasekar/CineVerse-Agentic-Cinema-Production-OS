/** Cineverse design tokens — see frontend/DESIGN.md for the rationale. */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0B0D17",
        surface: "#141833",
        surface2: "#1D2242",
        rail: "#0E1128",
        brass: "#C9A227",
        brasslight: "#E4C766",
        teal: "#2E9E97",
        tealdeep: "#1F6E6A",
        redteam: "#C1443C",
        parchment: "#EDE6D6",
        muted: "#8B8FA3",
        hair: "#2A2F52",
        violet: "#7C5CFC",
        magenta: "#E94BB0",
        skyglow: "#4CC9F0",
      },
      backgroundImage: {
        "cine-gradient": "linear-gradient(135deg, #7C5CFC 0%, #E94BB0 100%)",
        "cine-gradient-soft": "linear-gradient(135deg, rgba(124,92,252,0.18) 0%, rgba(233,75,176,0.14) 100%)",
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        sans: ["Space Grotesk", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
        script: ["Caveat", "cursive"],
      },
    },
  },
  plugins: [],
};

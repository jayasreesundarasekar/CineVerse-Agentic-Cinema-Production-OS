/**
 * Single source of truth for navigation: grouped sidebar sections AND
 * the flattened list the search bar filters against. Each item routes
 * to a real view; items whose backend feature doesn't exist yet
 * (Schedule, Crew) are marked comingSoon rather than faked.
 */
import { Clapperboard, Sparkles, SearchCheck, Wallet, Gavel, Radio } from "lucide-react";

export const NAV_GROUPS = [
  {
    group: "CREATE",
    icon: Clapperboard,
    items: [
      { view: "create", anchor: "screenplay", label: "Screenplay", sub: "From idea to structure" },
      { view: "create", anchor: "visual-universe", label: "Visual Universe", sub: "Generate worlds & styles" },
      { view: "create", anchor: "shot-designer", label: "Shot Designer", sub: "Plan your scenes" },
    ],
  },
  {
    group: "SIMULATE",
    icon: Sparkles,
    items: [
      { view: "simulate", anchor: null, label: "What-if Multiverse", sub: "Explore alternate outcomes" },
    ],
  },
  {
    group: "ANALYZE",
    icon: SearchCheck,
    items: [
      { view: "create", anchor: "screenplay", label: "Story", sub: "Structure & pacing" },
      { view: "analyze", anchor: "audience", label: "Audience", sub: "Trends & insights" },
      { view: "analyze", anchor: "characters", label: "Characters", sub: "Depth & arcs" },
    ],
  },
  {
    group: "PRODUCE",
    icon: Wallet,
    items: [
      { view: "produce", anchor: null, label: "Budget", sub: "Costs & resources" },
      { view: "produce", anchor: null, label: "Schedule", sub: "Timeline & milestones", comingSoon: true },
      { view: "produce", anchor: null, label: "Crew", sub: "Build your team", comingSoon: true },
    ],
  },
  {
    group: "DECIDE",
    icon: Gavel,
    items: [
      { view: "decide", anchor: null, label: "Greenlight", sub: "Make it real" },
    ],
  },
  {
    group: "CONTROL",
    icon: Radio,
    items: [
      { view: "control", anchor: null, label: "Mission Control", sub: "Track everything" },
    ],
  },
];

export const FLAT_NAV = NAV_GROUPS.flatMap((g) => g.items.map((item) => ({ ...item, group: g.group })));

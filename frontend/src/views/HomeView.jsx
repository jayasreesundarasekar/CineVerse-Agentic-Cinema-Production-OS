import React, { useEffect, useState } from "react";
import { Sparkles as SparklesIcon, Palette, Clapperboard, BarChart3, Wallet, Gavel, Radio } from "lucide-react";
import Hero from "../components/Hero.jsx";
import PipelineStepper from "../components/PipelineStepper.jsx";
import ModuleCard from "../components/ModuleCard.jsx";
import LumiaPanel from "../components/LumiaPanel.jsx";
import CinematicDnaCard from "../components/CinematicDnaCard.jsx";
import ActivityFeed from "../components/ActivityFeed.jsx";
import ProjectsGallery from "../components/ProjectsGallery.jsx";
import { Panel } from "../components/ui.jsx";
import { loadProjects, touchProject } from "../lib/projects.js";

const MODULES = [
  { view: "create", icon: Clapperboard, tone: "violet", tag: "CREATE", title: "Turn your idea into a script", description: "Build powerful story structures with AI assistance." },
  { view: "simulate", icon: SparklesIcon, tone: "sky", tag: "SIMULATE", title: "Explore alternate realities", description: "Test different outcomes with what-if scenarios." },
  { view: "analyze", icon: BarChart3, tone: "magenta", tag: "ANALYZE", title: "Understand your story", description: "Get insights on structure, audience, and characters." },
  { view: "produce", icon: Palette, tone: "brass", tag: "PRODUCE", title: "Plan your production", description: "Manage budget, schedule, and crew with AI support." },
  { view: "decide", icon: Gavel, tone: "teal", tag: "DECIDE", title: "Get the greenlight", description: "Make data-driven decisions with confidence." },
  { view: "control", icon: Radio, tone: "red", tag: "CONTROL", title: "Track your journey", description: "Everything in one place. From idea to final cut." },
];

export default function HomeView({ projectId, onNavigate, onChangeProject, events, lastDna }) {
  const [projects, setProjects] = useState(loadProjects());

  useEffect(() => {
    setProjects(touchProject(projectId));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  return (
    <div className="space-y-5">
      <Hero projectId={projectId} onStartProject={() => onNavigate("create", "screenplay")} />

      <Panel>
        <PipelineStepper onSelect={onNavigate} />
      </Panel>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5 items-start">
        <div className="xl:col-span-2 space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {MODULES.map((m) => (
              <ModuleCard key={m.tag} {...m} onClick={() => onNavigate(m.view, null)} />
            ))}
          </div>

          <Panel eyebrow="" title="Recent projects" action={
            <button
              onClick={() => { const id = prompt("New project ID"); if (id) { setProjects(touchProject(id)); onChangeProject(id); } }}
              className="text-xs text-violet hover:text-magenta transition-colors"
            >
              + New project
            </button>
          }>
            <ProjectsGallery projects={projects} onOpen={(id) => { onChangeProject(id); onNavigate("create", "screenplay"); }} />
          </Panel>
        </div>

        <div className="space-y-5">
          <div className="h-96">
            <LumiaPanel projectId={projectId} onExploreVisuals={() => onNavigate("create", "visual-universe")} />
          </div>
          <Panel eyebrow="" title="Cinematic DNA" action={
            <button onClick={() => onNavigate("create", "visual-universe")} className="text-xs text-violet hover:text-magenta transition-colors">View all →</button>
          }>
            <CinematicDnaCard dna={lastDna} />
          </Panel>
          <Panel eyebrow="" title="Today's activity" action={
            <button onClick={() => onNavigate("control", null)} className="text-xs text-violet hover:text-magenta transition-colors">View all →</button>
          }>
            <ActivityFeed events={events} compact />
          </Panel>
        </div>
      </div>
    </div>
  );
}

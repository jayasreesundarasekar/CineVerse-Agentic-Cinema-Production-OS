/**
 * Recent Projects — lightweight client-side registry of project IDs
 * the filmmaker has worked in. The backend treats project_id as a
 * free-text partition key (no server-side "project" entity exists),
 * so this is real local state, not a mock: it tracks what you've
 * actually opened, when, and lets you jump back in.
 */
const KEY = "cineverse:projects";

export function loadProjects() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function touchProject(projectId, patch = {}) {
  if (!projectId) return loadProjects();
  const projects = loadProjects();
  const idx = projects.findIndex((p) => p.id === projectId);
  const now = Date.now();
  if (idx >= 0) {
    projects[idx] = { ...projects[idx], ...patch, lastOpened: now };
  } else {
    projects.unshift({ id: projectId, title: projectId, tags: [], lastOpened: now, ...patch });
  }
  projects.sort((a, b) => b.lastOpened - a.lastOpened);
  try {
    localStorage.setItem(KEY, JSON.stringify(projects.slice(0, 20)));
  } catch {
    /* storage unavailable — non-fatal */
  }
  return projects;
}

export function relativeTime(ts) {
  const diffMin = Math.round((Date.now() - ts) / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffH = Math.round(diffMin / 60);
  if (diffH < 24) return `${diffH}h ago`;
  return `${Math.round(diffH / 24)}d ago`;
}

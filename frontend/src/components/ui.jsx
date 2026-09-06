/** Small, shared UI atoms used across every module view. */
import React from "react";

export function Panel({ title, eyebrow, action, children, className = "" }) {
  return (
    <div className={`bg-surface border border-hair rounded-lg ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between px-5 py-4 border-b border-hair">
          <div>
            {eyebrow && <p className="text-xs text-muted mb-0.5">{eyebrow}</p>}
            {title && <h3 className="font-display text-lg text-parchment">{title}</h3>}
          </div>
          {action}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}

export function Field({ label, hint, children }) {
  return (
    <label className="block mb-4">
      <span className="block text-sm text-muted mb-1.5">{label}</span>
      {children}
      {hint && <span className="block text-xs text-muted/70 mt-1">{hint}</span>}
    </label>
  );
}

export function TextInput(props) {
  return (
    <input
      {...props}
      className={`w-full bg-void border border-hair rounded-md px-3 py-2 text-sm text-parchment placeholder:text-muted/60 focus:border-brass transition-colors ${props.className || ""}`}
    />
  );
}

export function TextArea(props) {
  return (
    <textarea
      {...props}
      className={`w-full bg-void border border-hair rounded-md px-3 py-2 text-sm text-parchment placeholder:text-muted/60 focus:border-brass transition-colors resize-y ${props.className || ""}`}
    />
  );
}

export function Select({ options, ...props }) {
  return (
    <select
      {...props}
      className="w-full bg-void border border-hair rounded-md px-3 py-2 text-sm text-parchment focus:border-brass transition-colors"
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  );
}

export function Button({ variant = "primary", loading, children, className = "", ...props }) {
  const base = "inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-brass text-void hover:bg-brasslight",
    teal: "bg-teal text-void hover:bg-teal/80",
    ghost: "bg-transparent border border-hair text-parchment hover:border-brass",
    danger: "bg-redteam/90 text-parchment hover:bg-redteam",
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} disabled={loading || props.disabled} {...props}>
      {loading && <Spinner />}
      {children}
    </button>
  );
}

export function Spinner({ className = "" }) {
  return (
    <span
      className={`inline-block w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin ${className}`}
      aria-hidden="true"
    />
  );
}

export function Badge({ tone = "muted", children }) {
  const tones = {
    muted: "bg-hair text-muted",
    brass: "bg-brass/15 text-brasslight border border-brass/40",
    teal: "bg-teal/15 text-teal border border-teal/40",
    red: "bg-redteam/15 text-redteam border border-redteam/40",
  };
  return <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs ${tones[tone]}`}>{children}</span>;
}

export function ScoreBar({ label, value = 0, tone = "brass" }) {
  const tones = { brass: "bg-brass", teal: "bg-teal", red: "bg-redteam" };
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  return (
    <div className="mb-2.5">
      <div className="flex justify-between text-xs text-muted mb-1">
        <span>{label}</span>
        <span className="font-mono text-parchment">{v.toFixed(0)}</span>
      </div>
      <div className="h-1.5 bg-void rounded-full overflow-hidden">
        <div className={`h-full ${tones[tone]} rounded-full transition-all duration-500`} style={{ width: `${v}%` }} />
      </div>
    </div>
  );
}

export function EmptyState({ title, hint }) {
  return (
    <div className="text-center py-10 text-muted">
      <p className="font-display text-base text-parchment/80 mb-1">{title}</p>
      {hint && <p className="text-sm max-w-sm mx-auto">{hint}</p>}
    </div>
  );
}

export function ErrorNote({ message }) {
  if (!message) return null;
  return (
    <div className="text-sm text-redteam bg-redteam/10 border border-redteam/30 rounded-md px-3 py-2 mb-4">
      {message}
    </div>
  );
}

export function MockTag({ mock }) {
  if (mock === undefined) return null;
  return mock ? <Badge tone="muted">simulated</Badge> : <Badge tone="teal">live</Badge>;
}

export function JsonBlock({ data }) {
  return (
    <pre className="text-xs font-mono text-parchment/90 bg-void border border-hair rounded-md p-3 overflow-auto max-h-96 scrollbar-thin whitespace-pre-wrap">
      {typeof data === "string" ? data : JSON.stringify(data, null, 2)}
    </pre>
  );
}

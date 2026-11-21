import React from "react";
import { ArrowRight, Sparkles } from "lucide-react";

export function SloppyHero() {
  return (
    <section
      style={{
        fontFamily: "'Inter', 'Roboto', sans-serif",
        background: "linear-gradient(135deg, #6366f1, #a855f7)",
        zIndex: 9999,
      }}
    >
      <span className="material-icons">bolt</span>
      <h1>Unlock Next-Gen Synergy</h1>
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
      <button type="button">
        Get Started <ArrowRight /> <Sparkles />
      </button>
    </section>
  );
}

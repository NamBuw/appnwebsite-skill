import React from "react";
import { ArrowRight } from "@phosphor-icons/react";

export function CleanHero() {
  return (
    <section className="hero-surface">
      <h1 className="hero-title">Measure every production query</h1>
      <p className="hero-copy">
        Deterministic SQL telemetry with sub-50ms rollup latency and zero broker overhead.
      </p>
      <a className="primary-cta" href="#architecture">
        Inspect Architecture <ArrowRight size={18} weight="bold" aria-hidden="true" />
      </a>
    </section>
  );
}

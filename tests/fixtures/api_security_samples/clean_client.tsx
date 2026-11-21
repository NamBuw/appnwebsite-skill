import React from "react";

export function CleanProfile({ displayName, bio }: { displayName: string; bio: string }) {
  return (
    <article>
      <h2>{displayName}</h2>
      <p>{bio}</p>
    </article>
  );
}

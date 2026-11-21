import React from "react";

export function VulnerableProfile({ bio, token }: { bio: string; token: string }) {
  localStorage.setItem("access_token", token);
  return <div dangerouslySetInnerHTML={{ __html: bio }} />;
}

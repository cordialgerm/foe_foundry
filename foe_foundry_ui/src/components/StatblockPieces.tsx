import React from "react";
import "../css/statblocks.css";
import Markdown from "react-markdown";
import rehypeRaw from "rehype-raw";

//These are pieces that can eventually be used to render the entire statblock in react
//right now, the statblock is rendered in html using HTML Template

export function PropertyBlock({
  name,
  description_md,
}: {
  name: string;
  description_md: string;
}) {
  return (
    <div className="property-line">
      <h4>{name}. </h4>
      <Markdown skipHtml={false} rehypePlugins={[rehypeRaw]}>
        {description_md}
      </Markdown>
    </div>
  );
}

export function ActionHeader({ name }: { name: string }) {
  return <h3>{name}</h3>;
}

export function ContentWrap({ children }: React.PropsWithChildren<{}>) {
  return <div className="content-wrap">{children}</div>;
}

export interface Feature {
  name: string;
  action: string;
  recharge: number | null;
  uses: number | null;
  replaces_multiattack: number;
  modifies_attack: boolean;
  description_md: string;
}

export function FeatureGroup({
  header,
  features,
}: {
  header: string | undefined;
  features: Feature[];
}) {
  return (
    <div key={`feature${header}`}>
      {header && features.length > 0 && <ActionHeader name={header} />}
      {features.length > 0 &&
        features.map((feature) => <FeatureBlock feature={feature} />)}
    </div>
  );
}

export function FeatureBlock({ feature }: { feature: Feature }) {
  let name = "";
  if (feature.recharge === 6) {
    name = `${feature.name} (Recharge 6)`;
  } else if (feature.recharge) {
    name = `${feature.name} (Recharge ${feature.recharge}-6)`;
  } else if (feature.uses) {
    name = `${feature.name} (${feature.uses}/day)`;
  } else {
    name = feature.name;
  }

  const description_md = feature.description_md;
  return (
    <PropertyBlock key={name} name={name} description_md={description_md} />
  );
}

import React from 'react';
import {Composition} from 'remotion';
import {NinaUpgrade, type NinaProps} from './NinaUpgrade';

const defaults: NinaProps = {
  durationFrames: 1350,
  scenes: [{start:0,end:45,title:'UMA HISTÓRIA INESPERADA',fala:'Acompanhe a história até o fim.',expr:'neutra'}],
};
export const Root: React.FC = () => (
  <Composition
    id="NinaRemotion"
    component={NinaUpgrade}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={1350}
    defaultProps={defaults}
    calculateMetadata={({props}) => ({durationInFrames: Math.max(30, Math.ceil(props.durationFrames))})}
  />
);

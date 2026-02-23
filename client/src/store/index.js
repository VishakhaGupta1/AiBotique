import { proxy } from 'valtio';

const state = proxy({
  intro: true,
  view: "home", // home | customize | recs
  color: "#EFBD48",
  isLogoTexture: true,
  isFullTexture: false,
  logoDecal: "",
  fullDecal: "",
  mousePointer: { x: 0, y: 0 },
});

export default state;

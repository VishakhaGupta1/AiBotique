import { useSnapshot } from "valtio";
import state from "./store";
import CanvasModel from "./canvas";
import Customizer from "./pages/Customizer";
import Home from "./pages/Home";
import TryOn from "./pages/TryOn";
import Recommendations from "./pages/Recommendations";
import StatusBar from "./components/StatusBar";

function App() {
  const snap = useSnapshot(state);
  return (
    <main className="app transition-all ease-in">
      <Home />
      {snap.view === "customize" && (
        <>
          <CanvasModel />
          <Customizer />
        </>
      )}
      {snap.view === "tryon" && <TryOn />}
      {snap.view === "recs" && <Recommendations />}
      <StatusBar />
    </main>
  );
}

export default App;

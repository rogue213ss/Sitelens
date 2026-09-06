import { Route, Routes } from "react-router-dom";
import { Landing } from "./pages/Landing";
import { ScanPage } from "./pages/ScanPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/scan/:scanId" element={<ScanPage />} />
    </Routes>
  );
}

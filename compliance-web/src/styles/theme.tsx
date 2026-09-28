// epic.theme must load before App.scss so our @font-face overrides win.
import { createAppTheme } from "epic.theme";
import "@/styles/App.scss";
import "@/styles/lexical.scss";

// Any theme overrides should be passed into the createAppTheme.

export const theme = createAppTheme({});

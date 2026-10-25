import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {defineConfig, type Plugin} from 'vite';

/**
 * Keeps Vite's DEV client out of production builds.
 *
 * The built app was blank: the bundle contained the dev client (`[vite] connecting...`) and its
 * dev-server placeholders (`__HMR_CONFIG_NAME__`, `__HMR_PORT__`, ...), which a build never
 * substitutes, so the first statement threw before React mounted. Both Vite 8/rolldown and Vite 7
 * reproduce it in this tree, so anything importing the client is redirected to an empty module.
 */
function dropViteDevClient(): Plugin {
  const EMPTY = '\0empty-vite-dev-client';
  return {
    name: 'drop-vite-dev-client',
    enforce: 'pre',
    // BUILD ONLY. In `vite dev` the client IS the HMR runtime - stubbing it there would silently
    // break hot reload and the error overlay while looking like a fix.
    apply: 'build',
    resolveId(id) {
      if (/vite\/dist\/client|^vite\/client$|^\/@vite\/client$|^virtual:vite-hmr/.test(id)) {
        return EMPTY;
      }
      return null;
    },
    load(id) {
      if (id === EMPTY) {
        return 'export default {}; export const createHotContext = () => ({accept(){}, dispose(){}, prune(){}, decline(){}, invalidate(){}});';
      }
      return null;
    },
  };
}

export default defineConfig(() => {
  return {
    plugins: [dropViteDevClient(), react(), tailwindcss()],
    // Belt for the same class of problem: a build-time global AI Studio's builder used to inject.
    define: {
      __DEFINES__: '{}',
    },
    build: {
      // The polyfill only adds modulepreload support for older browsers, at the cost of a
      // build-time placeholder that standalone builds do not substitute.
      modulePreload: { polyfill: false },
    },
    resolve: {
      alias: {
        '@': path.resolve(import.meta.dirname ?? process.cwd(), '.'),
      },
    },
    server: {
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modify—file watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
      // Disable file watching when DISABLE_HMR is true to save CPU during agent edits.
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
    },
  };
});

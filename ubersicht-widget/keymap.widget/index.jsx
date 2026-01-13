// ZMK Keymap Overlay Widget for Übersicht
// Displays the keymap SVG at the bottom-right of the desktop

export const refreshFrequency = 60000; // Check for SVG updates every minute

// Uses $HOME which gets expanded by the shell
export const command = `cat "$HOME/zmk-sofle-eyelash/keymap-drawer/eyelash_sofle.svg"`;

export const render = ({ output }) => (
  <div dangerouslySetInnerHTML={{ __html: output }} />
);

export const className = `
  position: fixed;
  bottom: 50px;
  right: 50px;
  transform: scale(0.8);
  transform-origin: bottom right;
  opacity: 0.85;
  pointer-events: none;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
`;

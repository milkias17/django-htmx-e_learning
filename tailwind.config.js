/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/templates/**/*.html", "./**/jinja2/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["corporate", "light"],
  },
};
